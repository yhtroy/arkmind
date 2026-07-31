# RESEARCH-0003 — Graph Node

> Architecture Research（非开发）。只读分析，作为 RFC-0014（Graph Node Model）的最终设计输入，承接 RESEARCH-0001 / 0002。
> 本文档只整理当前事实，不设计、不新增接口、不改代码。所有结论基于 `main` 当前代码（commit 参考 `a3f946f`）。

---

## 1. 当前系统中所有可成为 Graph Node 的对象

| 对象 | 已有稳定 ID | 已有模型 | 已有生命周期 | 已进入 Pipeline | 一等对象? |
|---|---|---|---|---|---|
| Source | 是（`source_id`） | 是（[`SourceMetadata`](file:///f:/arkmind/src/arkmind/source/models.py)） | 是（`registered→captured→verified`，`SourceStatus`） | 是（作为输入，`source_id` 贯穿全程） | 是 |
| Fragment | 是（`fragment_id`，内容哈希） | 是（[`Fragment`](file:///f:/arkmind/src/arkmind/fragment/models.py)） | 否（无状态机，一次性产出） | 是（`FragmentExtractor` 产出） | 是 |
| Knowledge | 是（`knowledge_id`，内容哈希） | 是（[`Knowledge`](file:///f:/arkmind/src/arkmind/knowledge/models.py)） | 否（无状态机，但经 taxonomy/normalize/dedup 逐步补属性） | 是（`KnowledgeExtractor` 产出，后续阶段加工） | 是 |
| Function（`ST_*`） | 否（仅字符串） | 否（无独立模型） | 否 | 否（`KnowledgeReferenceDetector` 未接入 Pipeline） | 否 |
| Provenance | 否（无自身 ID，`{knowledge_id, fragment_id, source_id}` 组合） | 是（[`Provenance`](file:///f:/arkmind/src/arkmind/provenance/models.py)） | 否 | 是（`ProvenanceBuilder` 产出） | 否 — 见下 |
| kind | 否 | 否（是 `Knowledge.kind` 属性） | 否 | 是（`KnowledgeTaxonomy` 写入） | 否 — 见下 |

**为什么 Provenance 不是 Node**：它不是实体，而是一条**已物化的关系/追溯记录**——把 Knowledge→Fragment→Source 三个真实对象的 ID 打包在一起。它没有自身身份（无独立 ID），删掉三者中任一后它便无意义。它天然是"边/追溯"，不是"点"。

**为什么 kind 不是 Node**：它是 `Knowledge` 上的一个**属性取值**（constraint / example / …），来自关键词规则分类。它没有对象、没有 ID，是对 Knowledge 的标注而非独立节点；同一个 kind 值在语义上是标签而非可被引用的实体。

---

## 2. Graph Node 最小公共属性

只对四类**候选节点**（Source / Fragment / Knowledge / Function）列举现有字段事实，不设计。

| 候选属性 | Source | Fragment | Knowledge | Function | 是否真正公共 |
|---|---|---|---|---|---|
| 稳定 ID | `id`(source_id) | `fragment_id` | `knowledge_id` | ✗（仅字符串） | **否**（Function 缺失） |
| 类型标识 | 隐含（模型即类型） | 隐含 | 隐含 | 隐含 | 目前均**无显式 `node_type` 字段** |
| 文本/标签 | `title` | `text` | `text` / `normalized` | 函数名字符串本身 | 各有"某种文本"，但**字段名/语义不统一** |
| 归属 source | 自身即 Source | ✗（Fragment **不存** source_id） | `source_id` | 经 `KnowledgeReference.source_id` | **否**（Fragment 不带、Source 自身即是） |

事实结论（非设计）：
- 真正**四类都已具备**的公共属性 —— **没有**。最接近的是"稳定 ID"，但 Function 缺失。
- `node_type`、统一的 `label` 在当前代码中**都不存在**，是需要新引入的概念（属 RFC 设计范畴，本文不提方案）。
- 若以现状为准，只有 Source / Fragment / Knowledge 三者天然共享"有稳定 ID"这一条属性。

---

## 3. Node ID Strategy（只列事实）

| 对象 | 当前 ID 事实 |
|---|---|
| Source | 已有 `source_id`，人工指定（注册时写入 `source.yaml`，如 `postgis-3.6-en`） |
| Fragment | 已有 `fragment_id` = sha256(`source_id\npage_number\nsequence\ntext`)，内容寻址 |
| Knowledge | 已有 `knowledge_id` = sha256(`fragment_id\ntext`)，内容寻址（派生自 Fragment） |
| Function | **目前没有 ID，仅 `KnowledgeReference.to_function` 中的字符串**（如 `ST_Area`） |

若 Function 成为 Node，需要先解决的问题（事实层面的缺口，非方案）：
- **ID 从哪来**：Source/Fragment/Knowledge 要么人工指定、要么内容哈希；Function 目前两者都没有。
- **归一化口径**：大小写（`ST_Area` vs `st_area`）、别名、可能的 schema 前缀是否视为同一 Function，直接决定 ID 唯一性。
- **作用域**：Function ID 是**全局唯一**还是**按 source 隔离**（同名函数跨数据集是否同一节点）。
- **去重**：同一函数在多条 Knowledge、多次出现时如何折叠成一个节点（当前 detector 明确不去重）。

（以上仅指出"要成为 Node 必须先回答的问题"，不给答案。）

---

## 4. Node Type 枚举（只统计当前代码能确定性产出的候选）

```
SOURCE      — 已有对象 + 稳定 ID
FRAGMENT    — 已有对象 + 稳定 ID
KNOWLEDGE   — 已有对象 + 稳定 ID
FUNCTION    — 仅字符串，无对象 / 无 ID
```

合计 **4** 类候选节点类型。其中前三类是一等对象，第四类目前仅为字符串。（是否采纳、如何取舍由 RFC-0014 决定，本文不讨论。）

---

## 5. Graph Evolution（未来可能、但目前不存在的节点）

以下节点类型在 PostGIS 领域**语义上可能存在**，但当前代码**无任何模型、无任何抽取器能确定性产出**：

```
Table
Operator
Type
Raster
Extension
SQL Keyword
……
```

**为什么现在不要支持**（事实与既有纪律）：
- 当前唯一能被**确定性、无 AI**提取的实体是 `ST_*` 函数（正则 `\bST_[A-Za-z]+\b`）；上述类型**没有任何现成检测器**，支持它们就必须先造抽取逻辑。
- 提前建这些节点属于"占位/预留设计"，违反项目既定纪律"禁止占位与预留设计""代码实现即需即用（YAGNI）"。
- 它们尚无真实失败问题驱动，不满足"架构修改准入门槛：真实失败问题"。
- 过早纳入会使 Node/Edge 模型承载未验证的假设，正是本轮"先冻结最小 Node 模型"要规避的风险。

结论（事实层面）：RFC-0014 应基于**当前已确定性存在**的对象来冻结最小 Node 模型；新增节点类型留待其"确定性抽取能力"真实落地时再按同一节奏（RFC → 实现）扩展。

---

## 输出原则自检

- 不设计 ✅　不新增接口 ✅　不改代码/测试/pyproject/Pipeline ✅　不提交 PR ✅
- 仅整理当前事实，产出本 Markdown（`docs/research/RESEARCH-0003-graph-node.md`）✅

---

RESEARCH-0003 完成。
未修改代码。
等待 RFC-0014。
