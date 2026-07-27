# ADR-0001：永远不要为了 AI 而设计系统

- 状态：Accepted
- 日期：2026-07-27

## 决策

系统的核心是 Knowledge，不是任何一个模型。所有模型接入必须经过统一的 LLM Adapter 层（LiteLLM），模型对系统而言只是可替换的插件。

```
Knowledge → Capability → LLM Adapter → GPT / Claude / Gemini / DeepSeek / Qwen
```

## 背景

大量 AI 项目把架构建立在「PDF → 某模型 → 某 Prompt → 文章」的直连管道上。模型升级、Prompt 更换、厂商变动都会导致整体重写，系统没有沉淀任何资产。

## 后果

- 任何业务代码不得直接 import 某个模型 SDK，只能调用 Adapter。
- Prompt 属于 Reasoning 层的实现细节，按版本管理，可整体废弃。
- 换掉任何一家模型厂商，Knowledge 层与数据不受任何影响。哪天 OpenAI 倒闭，系统照跑。

## 违规判定

代码评审时看到模型名出现在 Adapter 层以外的任何地方，直接打回。
