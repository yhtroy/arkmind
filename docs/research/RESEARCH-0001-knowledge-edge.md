# RESEARCH-0001 — Knowledge Edge

> Architecture Research（非开发）。只读分析，作为 RFC-0014 的设计输入。
> 本文档不做设计、不做决定、不改代码。所有结论基于 `main` 当前代码（commit 参考 `a3f946f`）。

---

## 1. 当前 Knowledge 生命周期

主干编排见 [`DatasetPipeline.run`](file:///f:/arkmind/src/arkmind/pipeline/dataset_pipeline.py)。
`KnowledgeReferenceDetector` **不在** Pipeline 内（独立模块，RFC-0013 明确暂不接入）。

| # | 步骤 | 输入 | 输出 | 新对象? | 说明 |
|---|---|---|---|---|---|
| 0 | `PdfSourceProvider.extract` | `pdf_path: Path` | `pages: list[str]` | 新（字符串） | 抽取每页文本，无模型对象 |
| 1 | `FragmentExtractor.extract` | `pages`, `source_id` | `list[Fragment]` | **新建 Fragment** | 段落切分；`fragment_id = sha256(source_id\npage_number\nsequence\ntext)` |
| 2 | `KnowledgeExtractor.extract` | `list[Fragment]`, `source_id` | `list[Knowledge]` | **新建 Knowledge** | 一 Fragment 一 Knowledge，text 逐字复制；`knowledge_id = sha256(fragment_id\ntext)` |
| 3 | `KnowledgeTaxonomy.classify` | `list[Knowledge]` | 同一 `list[Knowledge]` | 否，**原地修改** | 直接写 `item.kind`，返回同一批对象引用 |
| 4 | `KnowledgeNormalizer.normalize` | `list[Knowledge]` | `list[Knowledge]` | **新副本** | `model_copy(update={"normalized": ...})`，写 `normalized` |
| 5 | `KnowledgeDeduplicator.deduplicate` | `list[Knowledge]` | `list[Knowledge]` | **新副本** | `model_copy(update={"duplicate": ...})`，按 `normalized` 标记 |
| 6 | `ProvenanceBuilder.build` | `list[Knowledge]` | `list[Provenance]` | **新建 Provenance** | 复制 `knowledge_id/fragment_id/source_id`，一 Knowledge 一 Provenance |
| — | `KnowledgeReferenceDetector.detect` | `list[Knowledge]` | `list[KnowledgeReference]` | **新建 KnowledgeReference** | 未接入 Pipeline；正则 `\bST_[A-Za-z]+\b` 从 `text` 提取 |

数据流（实线为 Pipeline 内，虚线为独立模块）：

```
Source(source.yaml)
   │  PdfSourceProvider
   ▼
pages: list[str]
   │  FragmentExtractor        → 新建 Fragment
   ▼
Fragment[]
   │  KnowledgeExtractor       → 新建 Knowledge（一对一）
   ▼
Knowledge[]
   │  KnowledgeTaxonomy        → 原地写 kind
   │  KnowledgeNormalizer      → 副本写 normalized
   │  KnowledgeDeduplicator    → 副本写 duplicate
   ▼
Knowledge[](final)
   │  ProvenanceBuilder        → 新建 Provenance（一对一）
   ▼
DatasetResult{source_id, fragments[], knowledge[], provenance[]}

（独立，未接入）Knowledge[] ┈┈▶ KnowledgeReferenceDetector ┈┈▶ KnowledgeReference[]
```

关键观察（供 RFC-0014 参考，非结论）：
- **只有第 3 步是原地修改**，其余生成新对象或产出新集合。
- `DatasetResult` 当前**没有** references/edges 字段，`KnowledgeReference` 目前不进入任何输出。
- `Fragment` 模型**不存 `source_id`**（`source_id` 只在生成 `fragment_id` 时参与哈希），因此 Fragment→Source 关系目前只能经由 `Knowledge`/`Provenance` 间接得到。

---

## 2. 枚举所有可能的 Edge（不设计，仅列现有代码已能产生的关系）

字段依据：[`Fragment`](file:///f:/arkmind/src/arkmind/fragment/models.py)、[`Knowledge`](file:///f:/arkmind/src/arkmind/knowledge/models.py)、[`Provenance`](file:///f:/arkmind/src/arkmind/provenance/models.py)、[`KnowledgeReference`](file:///f:/arkmind/src/arkmind/knowledge/reference.py)。

| 关系 | 起点 | 终点 | 已存在? | 确定性? | 需要 AI? | 承载位置 |
|---|---|---|---|---|---|---|
| Knowledge→Fragment | `Knowledge.knowledge_id` | `Fragment.fragment_id` | 是 | 是 | 否 | `Knowledge.fragment_id` 字段 |
| Knowledge→Source | `Knowledge.knowledge_id` | `SourceMetadata.id` | 是 | 是 | 否 | `Knowledge.source_id` 字段 |
| Fragment→Source | `Fragment.fragment_id` | `SourceMetadata.id` | 间接 | 是 | 否 | 未直接存储（仅经 Knowledge/Provenance） |
| Provenance(Knowledge→Fragment→Source) | `Knowledge` | (`Fragment`,`Source`) | 是 | 是 | 否 | `Provenance` 对象（已物化的三元追溯） |
| Knowledge→Function（REFERENCES） | `Knowledge.knowledge_id` | 函数名字符串（如 `ST_Area`） | 是 | 是 | 否 | `KnowledgeReference{source_id, from_knowledge_id, to_function}` |
| Knowledge→Knowledge（DUPLICATE_OF） | 后出现的 Knowledge | 首个同 `normalized` 的 Knowledge | 部分 | 是 | 否 | 当前仅有 `Knowledge.duplicate: bool`，**未记录指向哪一条**（无 target id） |
| Knowledge→kind（分类） | `Knowledge.knowledge_id` | 分类标签（constraint/example/…） | 是 | 是 | 否 | `Knowledge.kind` 字段（属性，非节点间边） |

分类说明（非结论）：
- **真正的 Knowledge↔Knowledge 边**：目前只有潜在的 `DUPLICATE_OF`，且现状只有布尔标记、缺 target，需要 RFC 决定是否补 target。
- **Knowledge→外部实体边**：`REFERENCES`（→ 函数名，注意终点是**字符串标签**，不是 `knowledge_id`）、`→Fragment`、`→Source`。
- **属性而非边**：`kind`、`normalized`、`duplicate` 是 Knowledge 自身字段，是否升格为"边/节点"由 RFC-0014 决定。
- 全部关系当前均为**确定性、无 AI**。

---

## 3. 统一关系模型（`KnowledgeEdge`）影响分析

若未来引入统一的 `KnowledgeEdge`（假想形态：`from` / `to` / `type` / 可能的 `source_id`），受影响模块如下（仅列影响面，不做设计）：

| 层 | 文件 | 影响 |
|---|---|---|
| models | `src/arkmind/knowledge/reference.py` | 现有 `KnowledgeReference` 需决定保留/废弃/包装/转换（见 §5） |
| models | 新增（如 `src/arkmind/knowledge/edge.py`） | 新 `KnowledgeEdge` 模型 + 边类型枚举 |
| models | `src/arkmind/pipeline/models.py` | `DatasetResult` 若要带边，需新增 `edges: list[KnowledgeEdge]`（当前 `extra="forbid"`，加字段是破坏性变更） |
| pipeline | `src/arkmind/pipeline/dataset_pipeline.py` | 若接入，需在 `run()` 增加"边检测"阶段并填充 `DatasetResult.edges` |
| runner | `src/arkmind/runner/dataset_runner.py` | 需写 `edges.json`，并在 `summary.json` 增加 `edges` 计数 |
| output | `sources/<id>/output/` | 新增 `edges.json` |
| tests | `tests/knowledge/test_reference.py` | 若 `KnowledgeReference` 变更，测试需相应调整 |
| tests | `tests/pipeline/test_dataset_pipeline.py` | 若 `DatasetResult` 加 `edges`，构造/断言需更新 |
| tests | `tests/runner/test_runner.py` | 断言输出文件的用例需覆盖 `edges.json` 与 summary 新计数 |
| tests | 新增（如 `tests/knowledge/test_edge.py`） | `KnowledgeEdge` / 边检测单测 |

注：现有各模型均为 `ConfigDict(extra="forbid")`，任何新增字段都是显式契约变更，不能被"额外字段"静默吸收。

---

## 4. Pipeline 输出分析

当前输出（由 [`DatasetRunner.run`](file:///f:/arkmind/src/arkmind/runner/dataset_runner.py) 写出，`json.dumps(indent=2, ensure_ascii=False)`）：

| 文件 | 内容 | 来源 |
|---|---|---|
| `knowledge.json` | `list[Knowledge]`（`model_dump(mode="json")`） | `result.knowledge` |
| `provenance.json` | `list[Provenance]` | `result.provenance` |
| `summary.json` | `{source_id, fragments, knowledge, provenance}`（后三者为计数） | 各列表长度 |

若增加 `edges.json`，需更新的测试（当前实际存在的输出相关用例）：

- [`tests/runner/test_runner.py`](file:///f:/arkmind/tests/runner/test_runner.py)
  - 断言三文件存在的用例 → 需加 `edges.json` 存在断言；
  - 空数据集用例（断言 `knowledge.json == []` 等）→ 需加 `edges.json == []`；
  - `summary.json` 断言 → 需加 `edges` 计数键。
- 若 `edges` 进入 `DatasetResult`：[`tests/pipeline/test_dataset_pipeline.py`](file:///f:/arkmind/tests/pipeline/test_dataset_pipeline.py) 相关构造/断言需更新。

事实澄清：仓库当前 `tests/gold/` 下**只有** `test_capture_postgis.py`，**没有** gold pipeline / 字节级确定性测试；输出文件的断言目前集中在 `tests/runner/test_runner.py`。

---

## 5. Migration Analysis — `KnowledgeReference` 去留（只分析，不决定）

现状关键约束：`KnowledgeReference.to_function` 是**函数名字符串**（如 `ST_Area`），**不是** `knowledge_id`；即它是"Knowledge → 外部实体（函数）"的边，终点不是图中已有的 Knowledge 节点。这是任何统一模型都要正面回答的问题：`KnowledgeEdge.to` 到底是节点 id 还是任意标签，函数本身是否作为节点。

| 方案 | 做法 | 优点 | 缺点 |
|---|---|---|---|
| 保留 | `KnowledgeReference` 与 `KnowledgeEdge` 并存 | 改动最小、RFC-0013 成果零回归 | 出现两套关系模型，正是 Architect 想避免的"每种关系各一套"碎片化 |
| 废弃 | 移除 `KnowledgeReference`，`REFERENCES` 直接建成 `KnowledgeEdge` | 单一模型、输出结构统一 | 需先解决"终点是函数字符串而非 knowledge_id"；破坏现有 detector API 与测试 |
| 包装 | `KnowledgeReference` 保留为薄适配层/子类型，对外产出 `KnowledgeEdge` | detector 接口稳定、渐进迁移 | 多一层间接，语义上仍是两个名字 |
| 转换 | detector 仍产 `KnowledgeReference`，另设 mapper 转 `KnowledgeEdge` | 检测与表示解耦、职责清晰 | 增加一层转换代码与测试维护成本 |

共性待答问题（留给 RFC-0014）：
- `KnowledgeEdge.to` 的类型契约（节点 id vs 标签）；
- 函数（`ST_*`）是否升格为一等节点；
- `type` 取值集合（`REFERENCES` 起步，未来 `CITES`/`SEE_ALSO`/`DEPENDS_ON`…）如何枚举与约束；
- 是否顺带把 `DUPLICATE_OF`（当前仅布尔）纳入统一边模型。

---

## DoD 自检

- 不改代码 ✅　不改测试 ✅　不提交 PR ✅　不生成 RFC ✅
- 仅产出本 Markdown（`docs/research/RESEARCH-0001-knowledge-edge.md`）✅

以上供 Architect 编写 RFC-0014 使用。**未实现 KnowledgeEdge。**
