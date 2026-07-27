# ADR-0005：数据哲学 —— 三状态 Observed → Approved → Derived

- 状态：Accepted
- 日期：2026-07-27

## 决策

ArkMind 所有数据只有三种状态，全局统一：

```
Observed  →  Approved  →  Derived
```

- **Observed**：来自世界的观测。OCR、人工录入、Source 解析出的原文（source / document / fragment）。忠于来源，不含任何人的判断。
- **Approved**：经 Human 确认、进入 Knowledge 的原始事实。**只有人能把 Observed 变成 Approved**（见 ADR-0004）。
- **Derived**：从 Approved Knowledge 推理出来的一切——Insight、文章、视频、Reasoning 产物，全部是 Derived，随时可重建（见 ADR-0003）。

**不使用** `Draft` / `Candidate` / `Final` / `Published` 这类状态词。它们描述的是工作流阶段，会随渠道和工具漂移；三状态描述的是数据的**认识论身份**（它从哪来、谁为它负责），十年不变。

## 背景

真正决定系统寿命的不是第一万行代码，而是第一百个数据字段。代码可以重写、API 可以重构、LLM 可以替换，但错误的数据哲学会伴随项目很多年。因此在写任何 Parser 之前，先把「什么是知识、知识从哪来、知识如何被批准」定义清楚。

`Candidate` 曾在 DATA_MODEL / ADR-0004 中作为 knowledge 的初始 status，现统一为 `Observed`——它更准确：那条数据只是被观测到了，还没有被任何人认可。

## 后果

- knowledge.status 的取值为 `observed` / `approved`；不存在 `candidate` / `draft`。
- Derived 数据不进 DATA_MODEL.md（属于 Reasoning 层，M2 单独建模）。
- 状态迁移方向单向：Observed → Approved 只能由 Human 触发；Derived 由 Approved 推导，不能反向写回 Approved/Observed。
- M1 的目标据此从「Source → Verified Knowledge」改为「**Source → Approved Knowledge**」：Verified 听起来像 AI 在验证，Approved 永远指向 Human。这是哲学，不是命名。

## 违规判定

代码或文档中出现 `candidate` / `draft` / `final` / `published` 作为数据状态，直接打回，改用三状态。
