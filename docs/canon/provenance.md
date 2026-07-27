# Provenance（来源链 Canon v0.1）

- 状态：**Draft** —— 与 [knowledge_rules.md](knowledge_rules.md)、[knowledge_examples.md](knowledge_examples.md) 配套
- 本文档只回答一个问题：

> **任何一条 Knowledge，如何追溯到它最初的 Source？**

这是知识系统和 Chat 的根本区别。Chat 只给答案；知识系统必须能在一分钟内回答「这句话哪来的」。

---

## 完整来源链

每一条 Knowledge 必须挂在一条**完整、不断裂**的链上：

```
Knowledge
   ↓ provenance（抽象出处，不绑死单一 fragment_ids）
Fragment
   ↓ location.page
Page
   ↓ document_id
Document
   ↓ source_id
Source
   ↓ version
Version（Source 的具体版本，如 SQLite 3.48）
```

链上任意一环缺失，该条 Knowledge 视为**无出处**，直接打回（对应 knowledge_rules.md Rule 7）。无出处 = 不存在。

### Provenance 是抽象，不是 fragment_ids

Knowledge 到 Fragment 这一环，**用抽象的 `provenance` 承载，绝不绑死 `fragment_ids`**。因为一条 Knowledge 可能：

- 来自同一文档的第 1 页和第 9 页（跨 fragment）；
- 甚至跨多个 Document / Source（跨源合并）。

所以 `provenance` 内部是一组引用，每个引用各自指向一个 Fragment，并各自解析出完整的下游链（Page → Document → Source → Version）。这是平台设计：**不要把第一种实现（单个 fragment）当成最终模型。**

### 为什么必须记到 Version

官方文档会更新。SQLite 3.48 与 3.52 对同一术语的 Definition 可能不同。一条 Knowledge 必须知道它来自**哪个版本**，否则十年以后无法追溯——「这句话当时是对的，但你不知道是哪一版的对」。Version 属于 Source 的一个具体快照。

## 每一环的追溯字段

| 环 | 由谁指向上一环 | 关键定位信息 |
| --- | --- | --- |
| Knowledge → Fragment | `knowledge.provenance`（抽象出处，可跨多个 fragment / document / source） | 哪几段原文支撑这条知识 |
| Fragment → Page | `fragment.location`（JSONB，含 page、章节） | 原文在第几页、哪一章 |
| Fragment → Document | `fragment.document_id` | 出自哪一次解析 |
| Document → Source | `document.source_id` | 哪一次解析、用什么解析器（parser / parser_version） |
| Source → Version | `source.version`（如 `sqlite-3.48`） | 来自 Source 的哪个版本快照 |
| Source → 原件 | `source.file_path` + `source.file_hash` | 原始文件及其指纹，原件永久保留 |

> Document 之所以独立于 Source：同一 Source 可以被多次、多版本解析（解析器升级后重跑）。追溯时必须能说清「这条知识来自哪一次解析」，否则解析器升级后出处会含糊。

## 一分钟追溯（验收动作）

拿任意一条 approved knowledge，必须能机械地走完：

1. 读 `knowledge.statement` 与 `fragment_ids`；
2. 取出对应 `fragment.text` 与 `location.page`；
3. 打开 `source.file_path` 指向的原件，翻到该页；
4. 用肉眼确认：原文确实支持这条 statement。

走不通任何一步 → 该条知识的 Provenance 不合格。

## Provenance 与三状态（ADR-0005）

- **Observed**：Source / Document / Fragment 天然携带来源（它们就是来源本身）。
- **Approved**：Knowledge 通过 `fragment_ids` 继承 Observed 的来源链，人在 Approve 时必须看到这条链。
- **Derived**：Reasoning 产物不直接挂 Source，而是挂它所依据的 `knowledge_ids`——顺着 Approved 再往上，仍能追回 Source（M2 建模时遵守）。

## 硬约束

1. **来源链只能补全，不能篡改。** Fragment 的原文与 location 一旦写入，永不修改（ADR-0003）。
2. **Approve 界面必须展示来源链**，人不能在看不见出处的情况下批准（ADR-0004）。
3. **删除 Source 前必须先处理其下游**：不允许存在指向已删除 Source 的 Knowledge（悬空出处）。
4. 跨 Source 合并的知识（一条 Knowledge 的 fragment_ids 跨越多个 Document/Source）允许，但每个 fragment 各自的链都必须完整。
