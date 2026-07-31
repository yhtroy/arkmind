# RESEARCH-0005 — Topic

> Product Discovery（P1 阶段）。只读事实分析，回答"Topic 到底是什么，它与 Knowledge 的边界在哪里"，作为 M2（Creative Engine）Topic 层的事实输入。
> 本文档不设计模型、不写 RFC、不改代码、不提出解决方案。对 ArkMind 现状的描述基于 `main` 当前代码（commit 参考 `a3f946f`）。

**准入门槛回答**：本研究直接服务"一本书 → 一篇优秀博文"链路的最上游——若 Topic 定义错，其后 Insight/Outline/Title/Renderer 全部失焦。故它缩短链路，进入主线。

---

## 0. 先锚定 Knowledge 的当前事实（对照基准）

在谈 Topic 之前，先固定 Knowledge 在当前代码中的确切事实，作为边界对照：

- 一条 `Knowledge` = 一个 `Fragment` = 书里的一页（当前粒度，见 ANALYSIS-0001：941 条 Knowledge 对应 941 页）。
- `knowledge_id` = sha256(`fragment_id\ntext`)，**内容寻址**、确定性、天然唯一。
- Knowledge 是**从单一 Fragment 抽取**的、**贴着原文**的结构化片段；它有 `kind`（分类）、`normalized`（归一），并通过 `Provenance` 回溯到 `fragment → source`。
- Knowledge **不含判断、不含主题归属**：它只是"书里这一页说了什么"，不回答"这属于什么话题"。

一句话：**Knowledge 是"书里有什么"的最小可追溯单元，且与页面物理结构绑定。**

---

## 1. Topic 与 Knowledge 有什么区别

| 维度 | Knowledge | Topic |
|---|---|---|
| 本质 | 书里某一页说了什么（原文片段） | 一篇文章"要谈什么"（表达单元） |
| 粒度来源 | 由**书的物理结构**决定（一页一条） | 由**表达意图**决定，与页码无关 |
| 数量级 | 多（一本书 941 条） | 少（一本书通常几个到几十个） |
| 是否含判断 | 否，只陈述原文 | 是，Topic 已经隐含"这值得单独谈" |
| 边界由谁定 | 内容寻址自动确定 | 需要**跨多条 Knowledge 聚合**才能浮现 |
| 稳定性 | 内容不变则 id 不变 | 随聚合口径/意图变化，非天然唯一 |
| 面向对象 | 面向"忠实记录" | 面向"读者/文章" |

核心区别（事实）：**Knowledge 是输入侧的单元（书里有什么），Topic 是输出侧的单元（文章谈什么）。** 两者不在同一坐标系——Knowledge 沿书的结构切分，Topic 沿表达意图切分。这正是 RESEARCH-0004 指出的"分界点＝Topic"在数据层的体现。

---

## 2. 一本书里 Topic 是天然存在，还是需要聚合

事实分析：
- **书里有"天然的结构信号"**：章节标题、小节、目录——这些是作者给的组织线索，但它们是**书的结构**，不等于**文章的主题**。
- **Topic 不天然等于章节**：一个好博文的 Topic（如"为什么长期主义重要"）可能横跨多个章节的零散段落；也可能一个章节里包含多个可独立成文的 Topic。
- 在 ArkMind 当前数据里，Knowledge 是**按页**切的，连章节边界都没保留，因此 Topic **更不可能**从单条 Knowledge 直接读出。

结论（事实）：**Topic 需要聚合。** 它不是从某一条 Knowledge 里"读"出来的，而是把分散在多条 Knowledge（可能跨页、跨章）里、指向同一表达意图的内容**聚**起来才浮现。章节标题至多是聚合的**线索**，不是 Topic 本身。

---

## 3. 一个 Topic 可以对应多少条 Knowledge

事实层面（非设计）：
- 下界：至少 1 条（极端情况下一条金句就能撑起一个小 Topic），但这罕见。
- 常态：**多条**。一个有观点的 Topic 通常需要"定义 + 若干支撑 + 例证 + 可能的反例"，天然是 N 条 Knowledge 的集合。
- 上界：无固定上限，受"这篇文章想讲多深"约束，而非技术约束。

关系性质：**Topic → Knowledge 是一对多。**

---

## 4. 一个 Knowledge 可以属于多少 Topic

事实层面：
- 同一条 Knowledge（如"复利效应"的定义）可以同时服务"长期主义""理财观""习惯养成"等**多个 Topic**。
- 因此 **Knowledge → Topic 也是一对多**。

综合 §3、§4：**Topic 与 Knowledge 是多对多关系。** 这是一个关键事实——它意味着 Topic 不能作为 Knowledge 的一个属性字段（那样只能一对一或多对一），而必然是一层**独立于 Knowledge 的组织**。（此处只陈述关系事实，不给模型方案。）

---

## 5. Topic 是否必须可追溯到原文

事实与既有优势：
- ArkMind 最大的差异化就是 **Provenance 来源链**（Knowledge → Fragment → Source）。RESEARCH-0004 已指出"观点可回溯到书"是相对同类工具的潜在优势。
- 若 Topic **不可追溯**，则基于它生成的 Insight/文章将失去"每句话都能指回原书"的能力，退化为 AI 幻觉风险区——这正是用户明确要规避的（第二层 Evidence 的立论）。
- Topic 本身是聚合出来的抽象，它不直接"来自某一页"，但它**必须能展开为其支撑的 Knowledge 集合**，而每条 Knowledge 已经可追溯到 Fragment/Source。

结论（事实）：**Topic 必须可追溯——但不是直接追溯到某段原文，而是通过"Topic → 它聚合的 Knowledge 集合 → 各自的 Provenance"间接、完整地追溯到原文。** 可追溯性由底层 Knowledge 继承而来，Topic 层不可切断这条链。

---

## 6. 一本书 vs 多本书的 Topic 有什么区别

| 维度 | 单本书的 Topic | 多本书的 Topic |
|---|---|---|
| 来源 | 聚合同一本书内的 Knowledge | 聚合跨书的 Knowledge |
| 作用 | "这本书讲了哪些主题" | "关于这个主题，不同书怎么说" |
| 是否含对比/分歧 | 通常无（同一作者口径） | **可含支持/反对/互补**（不同书立场不同） |
| 追溯 | 指向单一 source | 指向多个 source |
| 对创作的价值 | 忠实复述一本书 | 产生**跨书 Insight**（RESEARCH-0004 中"好博文 vs 知识罗列"的分水岭） |

关键事实：**Topic 的定义必须从一开始就允许"跨书聚合"**，否则多本书的 Topic 无法承载"哪些书支持、哪些书反对"这类结构（正是用户第三层 Insight 的核心）。单本书 Topic 是多本书 Topic 的退化特例（source 集合大小为 1）。

---

## 最终回答：Topic 到底是什么，它与 Knowledge 的边界在哪里

**Topic 是什么（事实归纳）**：
- Topic 是**输出侧、面向文章的表达单元**——"这篇要谈什么"，是创作的最小单位（用户已冻结）。
- Topic 是**聚合产物**，不天然存在于某一条 Knowledge，也不天然等于书的章节。
- Topic 与 Knowledge 是**多对多**关系，因此 Topic 必然是**独立于 Knowledge 的一层**，不能是 Knowledge 的属性。
- Topic **可跨书**；单本书 Topic 只是 source 集合为 1 的特例。
- Topic **必须可追溯**，但方式是"Topic → 其 Knowledge 集合 → Provenance → 原文"的间接完整追溯，继承自底层，不可切断。

**边界在哪里（一句话）**：
> **Knowledge 是"书里有什么"（输入侧、按书的物理结构切分、单一来源、无判断、天然可追溯的最小单元）；Topic 是"文章谈什么"（输出侧、按表达意图聚合、可跨书、隐含取舍、追溯性靠聚合的 Knowledge 继承）。分界线就是"记录"与"表达"的分界，也就是从 Knowledge Factory 迈向 Creative System 的那一步。**

以上为事实分析，不含模型设计、不含 RFC、不含解决方案。

---

## DoD 自检

- 纯事实分析 ✅　不设计模型 ✅　不写 RFC ✅　不改代码/测试 ✅　不提出解决方案 ✅
- 仅产出本 Markdown（`docs/research/RESEARCH-0005-topic.md`）✅

RESEARCH-0005 完成。等待 Architect 基于此定义 Topic 层。
