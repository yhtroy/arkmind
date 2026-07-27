# ROADMAP

只排三个 Milestone。不排时间表，不排一年计划。

每个 Milestone 的定义方式：**做什么、不做什么、怎么算完成。**

## Milestone Gate（每个里程碑的收尾流程）

```
Develop → Review → Refactor → Freeze → Tag → Next
```

- Freeze 之前不 commit 里程碑成果，避免第一天就开始改地基。
- Freeze 由 Chief Architect 宣布，Tag 命名：`v0.x.0-mN`。
- M0（文档阶段）同样适用：Draft → Review → Architecture Freeze → Commit。

---

## M1 — 一本书变成 Knowledge

**做什么**

- PDF 入库（source / document / fragment / knowledge 四张表跑通）
- CLI：`ingest` 一本书 → 解析 → 切分 → 提取知识候选 → 作者逐条 Approve（ADR-0004）

**不做什么**

- ❌ 写作、文章生成（M1 根本不关心知乎和小红书）
- ❌ Agent
- ❌ Web 前端
- ❌ 第二种输入格式

**完成标准（Success Criteria）**

> **一本书可以 100% 恢复：Source → Knowledge。**
>
> 具体地：一本得到 PDF 完整进入数据库，原文在 fragment 层无损可查；作者 Approve 过一批 knowledge，每一条都能回链到原文页码。
>
> 衡量的是「事实 → 知识」的保真度，不是「知识 → 文章」的产出。Knowledge 失败，后面全部失败。

---

## M2 — Knowledge 生成内容

**做什么**

- Reasoning 层启用并建模（推理产物属于本层，不进 Knowledge 层，见 ADR-0003）：基于 approved knowledge 做推理
- 生成知乎、小红书两种格式的草稿
- 草稿必须经作者 Approve 才算产出（ADR-0004）

**不做什么**

- ❌ 自动发布
- ❌ 更多渠道
- ❌ Memory / Feedback

**完成标准**

> 从已入库的 knowledge 出发，产出一篇作者愿意署名发布的知乎文章和一篇小红书笔记。

---

## M3 — Memory 与 Feedback 闭环

**做什么**

- 记录作者对草稿的修改与取舍（这就是最初的 Feedback 数据）
- 让下一轮生成能利用这些偏好

**不做什么**

- ❌ 读者数据抓取、平台 API 对接（等真的需要再说）

**完成标准**

> 第二次生成的草稿，能明显体现第一次 Approve/修改中表达出的偏好。

---

## M3 之后

不排。到时候根据 M1–M3 的真实反馈再定。任何"顺便把 XX 也做了"的提议，先读 [ADR-0002](ADR/ADR-0002-yagni.md)。
