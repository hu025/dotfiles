---
name: agentforge
description: 轻量模块化LLM Agent框架，技能抽象+统一后端接口+YAML配置，SkillDAG并行组合，87-93%任务完成率，开发时间减少62-78%。触发词：模块化agent/SkillDAG/YAML配置/轻量框架
triggers:
  - AgentForge
  - 模块化agent
  - SkillDAG
  - YAML配置
  - 轻量框架
---

# AgentForge — 轻量模块化LLM Agent框架

## 核心定位
- **模块化技能架构**: 每个Skill有明确input-output契约
- **统一后端接口**: OpenAI/Groq/HuggingFace无缝切换
- **声明式YAML配置**: 行为与实现分离
- **学术验证**: 论文发布，87-93%任务完成率，MIT许可

## 核心概念

### Skill抽象
```python
from agentforge.core import Skill, SkillRegistry

class SentimentAnalysisSkill(Skill):
    name = "sentiment_analysis"
    description = "Classifies sentiment"
    requires_llm = True

    def execute(self, input_data, llm=None):
        backend = self.resolve_llm(llm)
        response = backend.generate(f"Classify: {input_data['text']}")
        return {**input_data, "sentiment": response.text.strip().lower()}

SkillRegistry().register("sentiment_analysis", SentimentAnalysisSkill)
```

### SkillDAG（技能有向无环图）
```python
from agentforge.composition import SkillDAG

graph = SkillDAG()
graph.add_node("scrape", WebScraperSkill())
graph.add_node("analyse", DataAnalysisSkill())
graph.add_node("summarise", ContentGenerationSkill())
graph.add_edge("scrape", "analyse")
graph.add_edge("scrape", "summarise")

pipeline = graph.compile()
```
- 顺序组合: A输出→B输入
- 并行组合: 独立技能共享输入，输出合并
- 循环检测: 有环边自动拒绝

### 后端统一接口
```python
from agentforge.integrations import OpenAIBackend, GroqBackend, HuggingFaceBackend

OpenAIBackend(model="gpt-4o-mini")
GroqBackend(model="llama-3.1-70b-versatile")
HuggingFaceBackend(model="mistralai/Mistral-7B-Instruct-v0.2", load_in_4bit=True)
```

## YAML配置示例
```yaml
name: news_analyzer
version: "1.0"

llm:
  backend: openai
  model: gpt-4o-mini
  temperature: 0.7

skills:
  - web_scraper
  - skill: content_generation
    default_template: summarize
    max_tokens: 500

options:
  continue_on_error: false
```

## 内置技能
| 技能 | 能力 | 需要LLM |
|------|------|---------|
| web_scraper | 网页抓取解析 | No |
| data_analysis | 表格描述统计 | No |
| content_generation | 模板文本生成 | Yes |
| image_generation | 扩散图像合成 | No |
| voice_synthesis | 文本转语音 | No |

## CLI工具
```bash
agentforge init my_project           # 项目脚手架
agentforge run config.yaml --trace   # 执行+计时
agentforge list-skills --verbose     # 列举技能
agentforge validate config.yaml      # 配置校验
```

## 性能指标（论文数据）
- **任务完成率**: 87-93%（4基准测试）
- **开发时间**: 比LangChain/AutoGen减少62-78%
- **编排开销**: <100ms，支持实时应用
- **开发者调研**: 250人，p < 0.001

## 安装
```bash
pip install agentforge-llm
pip install "agentforge-llm[openai]"   # OpenAI后端
pip install "agentforge-llm[all]"      # 所有后端
```

## 与现有技能差异化
- **vs smolagents**: AgentForge有DAG编排，smolagents是代码优先
- **vs LightAgent**: AgentForge偏技能组合，LightAgent偏记忆+ToT
- **适合Hermes场景**: YAML配置+DAG适合工作流编排

## 参考
- https://github.com/001shahab/agentforge
- https://arxiv.org/pdf/2601.13383
