# RESEARCH-0002 — Edge Target

> Architecture Research（非开发）。只读分析，作为 RFC-0014 的设计输入，承接 RESEARCH-0001。
> 本文档不做设计、不做决定、不改代码。所有结论基于 `main` 当前代码（commit 参考 `a3f946f`）。

**核心问题：Knowledge Graph 的 Edge，到底应该连接什么？**

---

## 1. 枚举所有可能的 Edge Target

依据当前代码中真实存在的对象与字段（[`Knowledge`](file:///f:/arkmind/src/arkmind/knowledge/models.py)、[`Fragment`](file:///f:/arkmind/src/arkmind/fragment/models.py)、[`SourceMetadata`](file:///f:/arkmind/src/arkmind/source/models.py)、[`Provenance`](file:///f:/arkmind/src/arkmind/provenance/models.py)、[`KnowledgeReference`](file:///f:/arkmind/src/arkmind/knowledge/reference.py)）。仅列举已有对象，不设计。

| Target | 当前是否存在对象 | 是否有稳定 ID | ID 字段 / 说明 |
|---|---|---|---|
| Knowledge | 是 | 是 | `knowledge_id`（sha256(fragment_id\ntext)） |
| Fragment | 是 | 是 | `fragment_id`（sha256(source_id\npage_number\nsequence\ntext)） |
| Source | 是 | 是 | `SourceMetadata.id`（即 `source_id`，人工指定，如 `postgis-3.6-en`） |
| Function（如 `ST_Area`） | 否 | 否 | 仅 `KnowledgeReference.to_function` 中的**字符串**，无对象、无 ID |
| Provenance | 是（对象） | 否 | 无自身 ID，仅 `{knowledge_id, fragment_id, source_id}` 组合 |
| kind（constraint/example/…） | 否 | 否 | `Knowledge.kind` 属性值，无对象 |

观察（非结论）：当前**具备稳定 ID 且是一等对象**的仅 Knowledge / Fragment / Source 三者。Function 只是从 text 中正则提取的字符串，Provenance 是无独立 ID 的派生记录，kind 是属性值。

---

## 2. 分析 Function 的身份

现状：`ST_Area` 等来自正则 `\bST_[A-Za-z]+\b`，仅以字符串形式存在于 `KnowledgeReference.to_function`，不去重、不建对象、无 ID。三种可能定位分析如下（不做决定）：

### 方案 A：Function 属于 Knowledge
将函数视作一条 Knowledge（或映射到已有 Knowledge 节点）。
- 优点：图内只有一种节点类型，Edge 永远是 Knowledge↔Knowledge，模型最简。
- 缺点：函数并非从某个 Fragment 抽取的知识条目，当前没有对应 `knowledge_id`；强行归为 Knowledge 需要"造节点"，与"Knowledge = 一 Fragment 一条"的现有语义冲突；`knowledge_id` 依赖 `fragment_id`，函数没有来源 Fragment。

### 方案 B：Function 是独立 Entity（一等节点）
新增一类 Entity 节点（如 `FunctionEntity`），有自己的稳定 ID（如按函数名规范化生成）。
- 优点：语义最准确（函数是被引用的外部实体，不是知识条目）；未来可承载"函数定义在哪、被谁引用"等更多边；Edge target 从此有稳定 ID。
- 缺点：引入第二种节点类型，图模型与输出结构更复杂；需要定义 Entity 的 ID 生成规则、去重规则、生命周期；影响面最大。

### 方案 C：Function 只是字符串（维持现状语义）
Edge 的 target 允许是纯标签字符串，不要求是节点。
- 优点：零迁移、与现有 `to_function` 一致、实现最轻。
- 缺点：`ST_Area` 无法成为可被其他边指向的节点（无法表达"函数 X 定义于 Knowledge Y"）；图退化为"带字符串标签的出边"，扩展性受限；同名函数无法聚合统计。

三方案的分歧点本质是：**Edge 的终点是否必须是拥有稳定 ID 的节点。**

---

## 3. Edge 是否允许异构 Target

问题：一条 Edge 的终点是否允许在 Knowledge / Fragment / Source / Function 间任意取值。

### 若允许异构 target
需要的字段（分析，非设计）：
- 一个 **target 类型判别字段**（如 `to_type`：knowledge / fragment / source / function…）；
- 一个 **target 标识字段**（`to_id` 或 `to_ref`），其取值空间随 `to_type` 变化——指向 Knowledge/Fragment/Source 时是稳定 ID，指向 Function 时（在方案 C 下）是字符串标签；
- 可能还需 **from 类型判别**（若未来起点也异构）。
- 代价：`to_id` 成为"多态外键"，无法在模型层强约束其一定指向某类真实节点；校验与一致性需额外规则。

### 若不允许异构 target（例如强制 Edge 只能 Knowledge↔Knowledge）
- 限制：`REFERENCES → Function`、`Knowledge → Source`、`Knowledge → Fragment` 这些**现有代码已能产生的关系**无法用统一 Edge 表达，除非先把 Function/Source/Fragment 都"提升"为 Knowledge 节点（回到方案 A 的造节点问题）。
- 换言之：不允许异构，就必须先统一节点类型；否则会丢失当前已具备的三类关系表达能力。

（不设计最终模型，仅陈述两条路径各自的约束。）

---

## 4. Stable Identifier Analysis

现有稳定 ID（全部为字符串）：

| Stable ID | 所属对象 | 生成方式 | 稳定性依据 |
|---|---|---|---|
| `source_id` | Source | 人工指定（`SourceMetadata.id`） | 注册时固定，写入 `source.yaml` |
| `fragment_id` | Fragment | sha256(source_id\npage_number\nsequence\ntext) | 内容寻址，输入不变则不变 |
| `knowledge_id` | Knowledge | sha256(fragment_id\ntext) | 内容寻址，派生自 fragment |

**没有稳定 ID 的对象 / 概念：**
- **Function（`ST_Area` 等）**：只有字符串，无 ID、无对象。
- **KnowledgeReference**：关系记录本身无 `id`（仅 `{source_id, from_knowledge_id, to_function}` 三字段）。
- **Provenance**：无自身 ID（由 `{knowledge_id, fragment_id, source_id}` 组合标识）。
- **kind**：属性值，无 ID、无对象。

含义（非结论）：若要求 Edge 两端都是"有稳定 ID 的节点"，则 Function 必须先获得 ID 生成规则（对应 §2 方案 B），否则只能走字符串标签（方案 C）。

---

## 5. Migration Risk — 若 Function 未来变成真正对象

场景：现在 `to_function` 存字符串，未来把 Function 提升为一等对象（有稳定 ID）。评估现有 Reference 数据能否迁移。

**能否迁移**：能。现有关系载体是 `KnowledgeReference.to_function`（字符串函数名），迁移时可对每个不同函数名生成对应 Function 对象/ID，再把边的终点从"字符串"替换为"Function ID"。因为函数名是确定性提取的、且 `to_function` 已完整保留原始字符串，理论上是一次可重放的确定性转换。

| 维度 | 内容 |
|---|---|
| 风险 | ① Function ID 生成规则一旦选定即成契约，改规则会使历史边失效；② 同名函数的大小写/别名归一化策略需先定，否则聚合口径不稳；③ 若此前已把 `to_function` 写入任何持久化输出（目前**未**持久化，见下），需同步重刷；④ 破坏 `KnowledgeReference` 现有字段契约与其 7 项测试。 |
| 优点 | ① 迁移是确定性重算，可从 Knowledge.text 完全重建，无信息丢失风险；② 目前 `KnowledgeReference` **尚未进入任何输出文件**（未持久化），此刻迁移的历史包袱最小；③ 越早统一，后续关系类型（CITES/SEE_ALSO…）越不必二次迁移。 |
| 成本 | ① 需新增 Function 对象模型 + ID 规则 + 去重规则；② 改 detector 产出/或加映射层；③ 更新 `test_reference.py` 及后续 edge/output 相关测试；④ 若届时已输出 `edges.json`，需版本化重刷。 |

关键有利事实：**当前 `KnowledgeReference` 未持久化、不进 `knowledge/provenance/summary.json`**，因此"函数升格为对象"的迁移窗口现在成本最低——越晚（尤其在 `edges.json` 落地后）成本越高。

---

## DoD 自检

- 不改代码 ✅　不改测试 ✅　不提交 PR ✅　不生成 RFC ✅
- 仅产出本 Markdown（`docs/research/RESEARCH-0002-edge-target.md`）✅

以上供 Architect 冻结 RFC-0014 使用。**未实现 KnowledgeEdge，未对 Function 身份做决定。**
