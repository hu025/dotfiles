#!/usr/bin/env python3
"""
ai_text_detector.py - AI写作特征检测脚本

检测AI小说的统计特征：词汇、句式、结构三大类
输出每个类别的违规数量和具体位置，供人工逐条修复

用法:
    python3 ai_text_detector.py <章节文件> [--verbose]
    python3 ai_text_detector.py chapters/第58章.txt --verbose
"""

import re
import sys
import argparse
from dataclasses import dataclass, field
from typing import List, Tuple

# ============================================================
# 词表定义
# ============================================================

# 关卡1：原有禁用词
STAGE1_FORBIDDEN = [
    (r"仿佛", "仿佛 → 像/如同/就好像"),
    (r"逐渐", "逐渐 → 慢慢/一点一点"),
    (r"^[　\s]*然后", "句首'然后' → 之后/接着/删掉"),
    (r"^[　\s]*其实", "句首'其实' → 实际上"),
    (r"竟然", "竟然 → 居然/哪来"),
]

# 关卡2：AI高频词（叙述语/旁白禁用）
STAGE2_AI_WORDS = [
    (r"深入", "深入 → 细细/认真/仔细"),
    (r"彰显", "彰显 → 体现/显示/说明"),
    (r"不可或缺", "不可或缺 → 必不可少/必须有"),
    (r"不可或缺地", "不可或缺地 → 必不可少的"),
    (r"日益", "日益 → 越来越/一天比一天"),
    (r"显著", "显著 → 明显/很大/突出"),
    (r"逐步", "逐步 → 一点点/慢慢/渐渐"),
    (r"持续", "持续 → 一直/不停（注意：和'不断'互换无效！需改结构）"),
    (r"不断", "不断 → 一直/不停（注意：和'持续'互换无效！需改结构）"),
    (r"极为", "极为 → 特别/非常/十分"),
    (r"极其", "极其 → 特别/非常"),
    (r"尤为", "尤为 → 特别/尤其"),
    (r"相当", "相当 → 很/挺/颇"),
    (r"颇为", "颇为 → 很/挺"),
    (r"而言", "而言 → 说来/来看"),
    (r"确保", "确保 → 保证/让/使"),
    (r"旨在", "旨在 → 目的是/是为了/为了"),
    (r"有助于", "有助于 → 能/可以/帮助"),
    (r"得以", "得以 → 能够/终于/总算"),
    (r"随着", "随着 → 跟着/顺手/这会儿"),
    (r"重新", "重新 → 再/又/第二遍"),
    (r"再次", "再次 → 又/再/第二回（'再次闪烁'等组合也命中）"),
    (r"缓缓", "缓缓 → 慢慢/一点一点"),
    (r"突然", "突然 → 猛地/倏地/一下（AI滥用，真实写作按需使用）"),
    (r"悄然", "悄然 → 悄悄/静默/无声（AI过度使用）"),
    (r"闪烁", "闪烁 → 闪了一下/亮了一瞬/抖了一下"),
]

# 关卡3：AI固定句式（段落开头禁用）
STAGE3_FIXED_PATTERNS = [
    (r"在这一刻", "禁用句式 '在这一刻……' → 删或改写"),
    (r"不得不说", "禁用句式 '不得不说……' → 删或改写"),
    (r"值得注意的是", "禁用句式 '值得注意的是……' → 删或改写"),
    (r"从这个角度来看", "禁用句式 '从这个角度来看……' → 删或改写"),
    (r"正因如此", "禁用句式 '正因如此……' → 删或改写"),
    (r"正是在这种背景下", "禁用句式 '正是在这种背景下……' → 删或改写"),
    (r"毫无疑问", "禁用句式 '毫无疑问……' → 删或改写"),
    (r"从某种意义上说", "禁用句式 '从某种意义上说……' → 删或改写"),
]

# AI模型家族特征词（英文/混合文本用）
MODEL_FINGERPRINTS = {
    "GPT-4/ChatGPT": ["delve", "tapestry", "landscape", "leverage", "multifaceted",
                       "it's important to note", "undergoes", "undermines", "facilitates"],
    "Claude": ["certainly", "I'd be happy to", "straightforward", "I should note",
               "meticulous", "comprehensive", "meticulously"],
    "Gemini": ["crucial", "here's a breakdown", "keep in mind", "delve deeper",
               "holistic", "game-changer"],
    "Llama": ["awesome", "fantastic", "hope this helps", "amazing", "incredible"],
    "Mistral": ["indeed", "moreover", "hence", "noteworthy", "furthermore"],
}

# Tricolon检测：三个X、Y、Z枚举
TRICOLON_PATTERN = re.compile(
    r"^[^，。！？\n]{2,30}[、][^，。！？\n]{2,30}[、][^，。！？\n]{2,30}[，。]?[ ]*$",
    re.MULTILINE
)

# em/en dash
EM_EN_DASH = re.compile(r"[\u2014\u2013]")


@dataclass
class Violation:
    line: int
    column: int
    text: str
    category: str
    rule: str
    suggestion: str


@dataclass
class DetectionResult:
    path: str
    total_lines: int
    violations: List[Violation] = field(default_factory=list)

    # 统计
    stage1_count: int = 0
    stage2_count: int = 0
    stage3_count: int = 0
    tricount_count: int = 0
    dash_count: int = 0
    structure_issues: List[str] = field(default_factory=list)

    # 句子分析
    sentence_lengths: List[int] = field(default_factory=list)
    paragraph_lengths: List[int] = field(default_factory=list)

    def print_report(self, verbose: bool = False):
        print(f"\n{'='*60}")
        print(f"  AI写作特征检测报告: {self.path}")
        print(f"{'='*60}")
        print(f"  总行数: {self.total_lines}")

        total_violations = len(self.violations)
        print(f"\n  【违规总览】")
        print(f"  关卡1（禁用词）    : {self.stage1_count}")
        print(f"  关卡2（AI高频词）  : {self.stage2_count}")
        print(f"  关卡3（固定句式）  : {self.stage3_count}")
        print(f"  三连排比（Tricolon）: {self.tricount_count}")
        print(f"  Em/En破折号        : {self.dash_count}")
        print(f"  ─────────────────────────────")
        print(f"  违规合计            : {total_violations}")

        # 结构分析
        self._print_structure_report()

        if total_violations > 0:
            print(f"\n  【详细违规】")
            by_category = {}
            for v in self.violations:
                by_category.setdefault(v.category, []).append(v)

            for cat, items in by_category.items():
                print(f"\n  [{cat}]")
                for v in items[:20]:  # 最多显示20条
                    context = v.text[:60] + ("..." if len(v.text) > 60 else "")
                    print(f"    行{v.line}: {context}")
                    print(f"         → {v.suggestion}")

        if verbose and total_violations > 20:
            print(f"\n  （共{total_violations}处违规，以上显示前20条）")

        print(f"\n{'='*60}")
        if total_violations == 0:
            print("  ✅ 全部 PASS")
        else:
            print(f"  ❌ {total_violations} 处违规需修复")
        print(f"{'='*60}\n")

    def _print_structure_report(self):
        if not self.sentence_lengths:
            return

        avg_sentence = sum(self.sentence_lengths) / len(self.sentence_lengths)
        min_sentence = min(self.sentence_lengths)
        max_sentence = max(self.sentence_lengths)

        short_sentences = sum(1 for l in self.sentence_lengths if l <= 5)
        long_sentences = sum(1 for l in self.sentence_lengths if l >= 35)
        uniform_sentences = sum(1 for l in self.sentence_lengths if 15 <= l <= 25)

        print(f"\n  【结构分析】")
        print(f"  句子长度 - 均值: {avg_sentence:.1f}字, 范围: {min_sentence}-{max_sentence}字")
        print(f"  短句(≤5字)   : {short_sentences} 个 {'⚠️ 太少' if short_sentences == 0 else '✅'}")
        print(f"  长句(≥35字)  : {long_sentences} 个")
        print(f"  中等句(15-25字): {uniform_sentences} 个 {'⚠️ AI倾向' if uniform_sentences > len(self.sentence_lengths)*0.7 else '✅'}")

        if self.paragraph_lengths:
            avg_para = sum(self.paragraph_lengths) / len(self.paragraph_lengths)
            one_liners = sum(1 for l in self.paragraph_lengths if l == 1)
            long_paras = sum(1 for l in self.paragraph_lengths if l >= 6)
            print(f"  段落长度 - 均值: {avg_para:.1f}句, 1句段落: {one_liners}, 6+句段落: {long_paras}")

        # AI模式警告
        issues = []
        if uniform_sentences > len(self.sentence_lengths) * 0.7:
            issues.append("句长过于均匀（AI特征）")
        if short_sentences == 0:
            issues.append("缺少短句（无节奏变化）")
        if self.dash_count > self.total_lines * 0.5:
            issues.append(f"破折号过多（{self.dash_count}处）")

        if issues:
            print(f"\n  【AI模式警告】")
            for issue in issues:
                print(f"    ⚠️  {issue}")


def split_sentences(text: str) -> List[Tuple[int, str]]:
    """将文本分割为句子，返回 (行号, 句子内容) 列表"""
    sentences = []
    lines = text.split("\n")
    current = []
    current_line = 1

    for i, line in enumerate(lines):
        line_num = i + 1
        stripped = line.strip()
        if not stripped:
            if current:
                sentences.append((current_line, "".join(current).strip()))
                current = []
            continue

        # 简单按句号/问号/感叹号分割
        j = 0
        while j < len(stripped):
            # 找句子结束符
            end = len(stripped)
            for punct in ["。", "！", "？", ".", "!", "?"]:
                pos = stripped.find(punct, j)
                if pos != -1 and pos < end:
                    end = pos + 1

            sentence = stripped[j:end]
            # 去掉引号和空格
            sentence = sentence.strip("""""''""「」『』""")
            if sentence:
                sentences.append((line_num, sentence))
            j = end

        current_line = line_num

    if current:
        sentences.append((current_line, "".join(current).strip()))

    return sentences


def analyze_structure(text: str) -> Tuple[List[int], List[int]]:
    """分析句子长度和段落长度分布"""
    sentences = split_sentences(text)
    sentence_lengths = [len(s[1]) for s in sentences if s[1]]

    paragraphs = text.split("\n\n")
    paragraph_lengths = []
    for para in paragraphs:
        para_stripped = para.strip()
        if para_stripped:
            # 估算段落中的句子数
            sentence_count = len(re.findall(r"[。！？]", para_stripped))
            sentence_count = max(1, sentence_count)
            paragraph_lengths.append(sentence_count)

    return sentence_lengths, paragraph_lengths


def detect_file(path: str, verbose: bool = False) -> DetectionResult:
    """检测单个文件"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ 文件未找到: {path}")
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"❌ 编码错误: {path}")
        sys.exit(1)

    lines = content.split("\n")
    result = DetectionResult(path=path, total_lines=len(lines))

    # ---- 结构分析 ----
    result.sentence_lengths, result.paragraph_lengths = analyze_structure(content)

    # ---- 检测破折号 ----
    for i, line in enumerate(lines, 1):
        if EM_EN_DASH.search(line):
            result.dash_count += 1
            result.violations.append(Violation(
                line=i, column=0, text=line[:50],
                category="破折号",
                rule="em/en dash检测",
                suggestion="em dash(—)和en dash(–)需替换为单 hyphen(-)"
            ))

    # ---- 关卡1：原有禁用词 ----
    for i, line in enumerate(lines, 1):
        for pattern, suggestion in STAGE1_FORBIDDEN:
            for match in re.finditer(pattern, line):
                result.stage1_count += 1
                start = match.start()
                context = line[max(0, start-5):start+20]
                result.violations.append(Violation(
                    line=i, column=start, text=context,
                    category="关卡1-禁用词",
                    rule=pattern,
                    suggestion=suggestion
                ))

    # ---- 关卡2：AI高频词 ----
    for i, line in enumerate(lines, 1):
        for pattern, suggestion in STAGE2_AI_WORDS:
            for match in re.finditer(pattern, line):
                # 排除代码块和对话中的使用
                # 简单判断：跳过引号内的
                before = line[:match.start()]
                if before.count('"') % 2 == 1:
                    continue
                result.stage2_count += 1
                start = match.start()
                context = line[max(0, start-5):start+20]
                result.violations.append(Violation(
                    line=i, column=start, text=context,
                    category="关卡2-AI高频词",
                    rule=pattern,
                    suggestion=suggestion
                ))

    # ---- 关卡3：AI固定句式 ----
    for i, line in enumerate(lines, 1):
        for pattern, suggestion in STAGE3_FIXED_PATTERNS:
            for match in re.finditer(pattern, line):
                result.stage3_count += 1
                start = match.start()
                context = line[max(0, start-5):start+40]
                result.violations.append(Violation(
                    line=i, column=start, text=context,
                    category="关卡3-AI固定句式",
                    rule=pattern,
                    suggestion=suggestion
                ))

    # ---- 三连排比检测 ----
    for i, line in enumerate(lines, 1):
        # Tricolon: X、Y、Z 格式，独立一行或独立分句
        # 放宽：允许标点后还有内容
        stripped = line.strip()
        # 匹配 X、Y、Z 结构（中间用顿号分割，3项以上）
        tricount = re.findall(r"[^，、。！？\n]{2,15}[、][^，、。！？\n]{2,15}[、][^，、。！？\n]{2,15}", stripped)
        if len(tricount) >= 2:  # 同一行有多个三连 → 违规
            result.tricount_count += 1
            result.violations.append(Violation(
                line=i, column=0, text=stripped[:60],
                category="三连排比",
                rule="X、Y、Z三连枚举",
                suggestion="1000字内不超过1次。建议：拆成两句/改动态/删除列举"
            ))
        elif len(tricount) == 1:
            # 单个三连，检查上下文是否附近还有更多
            result.tricount_count += 1
            result.violations.append(Violation(
                line=i, column=0, text=stripped[:60],
                category="三连排比",
                rule="X、Y、Z三连枚举",
                suggestion="检查是否AI堆砌。如是角色台词/引用则可保留"
            ))

    return result


def main():
    parser = argparse.ArgumentParser(
        description="AI写作特征检测脚本 - 检测小说章节的AI痕迹",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python3 ai_text_detector.py chapters/第58章.txt
    python3 ai_text_detector.py chapters/第58章.txt --verbose
        """
    )
    parser.add_argument("file", help="要检测的章节文件路径")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="显示更多详细信息")
    args = parser.parse_args()

    result = detect_file(args.file, verbose=args.verbose)
    result.print_report(verbose=args.verbose)

    # exit code: 0 = 全部通过, 1 = 有违规
    sys.exit(1 if result.violations else 0)


if __name__ == "__main__":
    main()
