# Knowledge Taxonomy（知识分类学 Canon v0.1 Draft）

- 状态：**Draft** —— 配套 [knowledge_rules.md](knowledge_rules.md)（规则）、[knowledge_examples.md](knowledge_examples.md)（例子）、[provenance.md](provenance.md)（出处）
- 本文档回答一个问题：

> **一段内容到底是哪一种知识？它属于 Knowledge Layer 还是 Reasoning Layer？**

我们维护的不是一个「词典（Dictionary）」，而是一套**知识分类学（Taxonomy）**——强调的是分类体系，会随真实证据长期演化，而不是一张固定词表。

`knowledge_rules.md` 讲「一条候选合不合格」（规则）；本文档讲「合格的东西是什么类型」（分类）。以后 AI 学的不是 Prompt，而是**这套分类学**。

---

## 两条铁律

1. **只有 Observed 的、忠于原文的类型，才属于 Knowledge Layer。** 任何需要"综合、判断、升华"的类型属于 Reasoning Layer（Derived，见 ADR-0005）。
2. **分类学由真实数据演化，不由想象决定。** 见下方 Type Discovery。

---

## Type Discovery（类型发现）—— 本项目的收敛机制

数据模型**不追着分类学跑**。流程不是「先设计 kind → 再提取知识」，而是：

```
Knowledge Taxonomy（全集，本文档）
        ↓
真实 Source（SQLite CREATE TABLE 章节）
        ↓
Unknown Type（分不了类的先记为 unknown）
        ↓
统计（哪些 unknown、出现多少次）
        ↓
Architecture Review
        ↓
是否进入 kind（证据足够才演化）
```

- **Unknown 不是失败，是信号。** 它是系统在告诉我们「Grammar 不够」——这是好事，说明真实世界超出了当前分类学，该补的是分类学，不是把数据硬塞进已有类型。
- **kind 的最终取值由数据决定，不由本文档拍板。** 分类学先记录全集（下表），持久化枚举 `kind` 何时扩展，取决于 Type Discovery 的统计证据。

> 设计哲学：**不要为了让数据符合模型而修改数据；应该让模型在证据足够时再演化。** 数据模型必须克制——这是知识系统与业务系统最大的不同。

---

## 类型全集（Taxonomy，待 Type Discovery 验证）

### 属于 Knowledge Layer（忠于原文的事实）

| 类型 | 含义 | 判定要点 |
| --- | --- | --- |
| **Definition** | 对某个术语/概念的定义 | 原文明确「X 是……」 |
| **Fact** | 原文陈述的一个客观事实 | 可核验、无判断成分 |
| **Observation** | 原文记录的一次观察/现象 | 描述"发生了什么"，非解释 |
| **Evidence** | 支撑某结论的原文证据/数据点 | 引用得出，非自行推断 |
| **Constraint** | 限制条件（不允许/上限/前提） | 原文写明的硬约束 |
| **Requirement** | 要求（MUST/SHOULD 级别） | 原文写明的规范性要求 |
| **Warning / Note** | 原文的警告/注意事项 | 原文显式标注 |
| **Example** | 原文给出的示例（含代码/SQL） | 原样保留，不改写 |
| **Data / Formula** | 数值、公式、表格数据 | 原样保留 |
| **Quote** | 逐字引用 | 一字不改 |
| **Unknown** | 暂时无法归类 | **过渡态**，见下 |

### 属于 Reasoning Layer（Derived，永不进 Knowledge Layer）

| 类型 | 为什么是 Reasoning |
| --- | --- |
| **Interpretation** | 对事实的解读、升华（如把"站直"升华成"保持自信"） |
| **Action / Advice** | 用途、行动建议（Action 是 Usage 不是 Fact，见 rules Rule 4） |
| **Summary** | 跨片段归纳总结 |
| **Opinion** | 观点、评价 |
| **Cross Reference（关系）** | 见下方特别说明 |

---

## Unknown 是过渡态，不是长期分类

`unknown` **只表示"我们现在还不会分类"**，绝不是最终分类，永不进入长期 Taxonomy。它比"硬塞进 evidence"健康得多——后者会污染知识，前者只是诚实地承认边界。

- 一条标 `unknown` 的候选**不能** Approved（status 停在 observed），进入 Type Discovery 的统计队列。
- 当某类 unknown 反复出现、证据足够，经 Architecture Review 才决定：给它一个正式类型 + 是否进入 `kind` 枚举。
- 目标是让 unknown 随时间**收敛到 0**，而不是长期共存。

---

## 特别说明：Cross Reference 是关系，不是知识

Cross Reference（如 SQLite 文档里"参见 CREATE INDEX")本身**不是一条 Knowledge**，而是两条 Knowledge / Source 之间的**关系**。M1 不建模关系（DATA_MODEL 已明确排除 Relation / 知识图谱，YAGNI）。M1.1 遇到交叉引用：只记录它指向的目标进入 provenance/备注，不新建一条 Knowledge。

---

## 与 DATA_MODEL.kind 的关系（已裁决：C = 延迟决策）

不选 A（收敛并入 evidence），不选 B（现在扩展枚举），选 **C：现在不决定，让真实数据决定**。

当前 `DATA_MODEL.kind` 枚举：`concept / definition / evidence / data / quote / unknown`（`unknown` 为过渡态）。`Constraint / Requirement / Warning` 等类型**暂不进入 kind**，先在校准表里以本分类学的类型名标注、并在需要落库时记为 `unknown`，交给 Type Discovery 统计。何时扩展 `kind`，由证据 + Architecture Review 决定。

### `concept` 同样走 Type Discovery

`concept` 未出现在上方分类学表中（表里是 Definition/Fact/…），但**现在不删**——这是 Type Discovery，不是拍脑袋。先让它存在；M1.1 结束后看真实频次：一次都没出现→删掉，大量出现→保留。**证据决定模型。**
