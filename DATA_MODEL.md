# DATA_MODEL

> 数据结构决定寿命。代码以后都能改，数据不能乱。

## 设计原则

1. **本文件只建模 Knowledge 层。** AI 推理产物（总结、观点、草稿）属于 Reasoning 层，**永远不会出现在本文件里**——那是两个世界，不能混。
2. **Knowledge 只保存原始事实 + 出处**，不保存 AI 结论。总结永远可以重新生成，事实不能。
3. 每一条数据都能回答：「你从哪里来？」（provenance 链完整）。
4. 只为 M1 建模。M2/M3 需要的表，到时候再长出来（YAGNI）。
5. 任何数据进入 knowledge 表之前，必须经作者 Approve（ADR-0004）。
6. 全局数据只有三种状态：`Observed` → `Approved` → `Derived`（ADR-0005）。本文件只建模 Observed 与 Approved；Derived 属于 Reasoning 层。
7. **克制演化：不为了让数据符合模型而修改数据；只在真实证据持续表明需要时才演化模型。** 新类型先进 Type Discovery 统计（见 [docs/canon/knowledge_taxonomy.md](docs/canon/knowledge_taxonomy.md)），证据足够 + Architecture Review 后才改 `kind`。

## 存储选型

PostgreSQL 单库。向量用 pgvector 扩展，全文检索用 PG FTS。不引入第二种存储。

## 核心实体（M1 范围）

```
source ──< document ──< fragment ──< knowledge
```

到此为止。没有第五个实体。

### source — 输入源

一本书 / 一个 PDF 的登记信息。

| 字段 | 说明 |
| --- | --- |
| id | UUID |
| type | 目前只有 `pdf` |
| title / author | 书名、作者 |
| file_path / file_hash | 原件位置与指纹（原件永远保留） |
| version | Source 的具体版本快照。**M1 锁定 `sqlite-3.46.x`，M1 完成前绝不升级**（官方文档会变，版本是 Provenance 链的必须一环，见 provenance.md）。 |
| provider / license | 来源登记信息（对应 sources/source.yaml，见 ARCHITECTURE Source 层） |
| created_at | |

### document — 解析结果

一次解析产出的结构化文档（同一 source 允许多次解析，解析器升级后可重跑）。

| 字段 | 说明 |
| --- | --- |
| id | UUID |
| source_id | → source |
| parser / parser_version | 例如 `pymupdf 1.24` |
| status | `parsed` / `failed` |
| created_at | |

### fragment — 原文片段

书的原文，按章节/段落切分。**这是最底层的事实，永不修改、永不删除。**

| 字段 | 说明 |
| --- | --- |
| id | UUID |
| document_id | → document |
| seq | 在文中的顺序 |
| text | 原文（一字不改） |
| location | 章节、页码等定位信息（JSONB） |
| embedding | vector（pgvector，用于检索） |

### knowledge — 知识单元

从 fragment 中提取的**原始事实**，必须能回链到原文。保存的是事实，不是理解。

| 字段 | 说明 |
| --- | --- |
| id | UUID |
| provenance | 结构化出处（抽象）。一条知识可跨多个 fragment、跨多个 document / source / version；内部是一组引用，每个各自解析到完整链（见 [docs/canon/provenance.md](docs/canon/provenance.md)）。**不得用 `fragment_ids` 字段绑死单一实现。** |
| extractor | 这条知识是谁提取的：`human` / `ocr-v1` / `pdf-parser-v2` ……。**可追责（Traceability）**：某个 Extractor 事后发现 Bug 时，能定位受影响的知识。 |
| statement | 事实的规范化表述（忠于原文，不加观点、不做总结） |
| kind | `concept` / `definition` / `evidence` / `data` / `quote` / `unknown`（分类学见 [docs/canon/knowledge_taxonomy.md](docs/canon/knowledge_taxonomy.md)；`unknown` 为**过渡态**，不进长期分类，枚举扩展由 Type Discovery 决定） |
| status | `observed` / `approved`（作者 Approve 后才算资产，见 ADR-0004 / ADR-0005；不使用 candidate/draft） |
| embedding | vector |
| created_at / approved_at | |

**这张表永远不会有 `summary` 字段。** 总结是 Reasoning 层的产物，可以随时重新生成；事实不能。

> 判别标准：GPT-7 出来那天，这张表里的任何一行都**不需要重新生成**，只需要被重新理解。如果某个字段做不到这一点，它就不属于 Knowledge 层，属于 Reasoning 层——从本文件删掉。

## 明确不建模的东西（现在）

- ❌ **AI 推理产物（观点、总结、草稿）** —— 属于 Reasoning 层，M2 在 Reasoning 层单独建模，永不进本文件
- ❌ 知识间关系（Relation）/ 知识图谱（没有图查询需求，Neo4j 更不需要）
- ❌ 用户、权限（单人系统）
- ❌ content / feedback 相关表（M2 / M3 再长出来）
