# novel-writing-ai-free 参考文件

## scripts/

### ai_text_detector.py

AI写作特征检测脚本，检测三大类违规：

**用法：**
```bash
python3 scripts/ai_text_detector.py <章节文件> [--verbose]
python3 scripts/ai_text_detector.py chapters/第58章.txt
python3 scripts/ai_text_detector.py chapters/第58章.txt --verbose
```

**输出内容：**
- 关卡1 禁用词违规（行号+位置+上下文+替换建议）
- 关卡2 AI高频词违规（行号+位置+上下文+替换建议）
- 关卡3 AI固定句式违规
- 三连排比（Tricolon）检测
- Em/En破折号检测
- 句子长度分布分析（AI特征：过度均匀）
- 段落长度分布分析

**exit code：** 0 = 全部PASS，1 = 有违规

---

## 快速命令

```bash
# 本地AI检测（需安装 lmscan）
lmscan scan <file.txt>

# 句级评分（需安装 uncanny）
uncanny scan <file.txt> --deep

# 本工具：AI特征扫描
python3 ~/dotfiles/skills/novel-writing-ai-free/scripts/ai_text_detector.py <章节文件>

# 补扫：句首"然后"
grep -n '^[\s]*然后' <章节文件>

# 补扫：AI高频词
grep -n '深入\|彰显\|不可或缺\|日益\|显著\|逐步\|持续\|不断\|极为\|确保' <章节文件>
```
