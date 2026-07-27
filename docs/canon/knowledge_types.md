# Knowledge Types（知识类型字典 Canon v0.1 Draft）

- 状态：**Draft** —— 配套 [knowledge_rules.md](knowledge_rules.md)（规则）、[knowledge_examples.md](knowledge_examples.md)（例子）、[provenance.md](provenance.md)（出处）
- 本文档回答一个问题：

> **一段内容到底是哪一种知识？它属于 Knowledge Layer 还是 Reasoning Layer？**

`knowledge_rules.md` 讲「一条候选合不合格」（规则）；本文档讲「合格的东西是什么类型」（词典）。以后 AI 学的不是 Prompt，而是**这本字典**。

---

## 两条铁律

1. **只有 Observed 的、忠于原文的类型，才属于 Knowledge Layer。** 任何需要"综合、判断、升华"的类型属于 Reasoning Layer（Derived，见 ADR-0005）。
2. **字典由真实数据验证，不由想象决定。** M1.1 拿 SQLite `CREATE TABLE` 章节逐条比对：如果出现一种本字典无法归类的知识，说明 **Grammar 不完整**，改字典——不是硬塞进现有类型。

---

## 类型清单（候选，待 M1.1 验证）

### 属于 Knowledge Layer（忠于原文的事实）

| 类型 | 含义 | 判定要点 | 对应 DATA_MODEL.kind（待并轨） |
| --- | --- | --- | --- |
| **Definition** | 对某个术语/概念的定义 | 原文明确「X 是……」 | `definition` |
| **Fact** | 原文陈述的一个客观事实 | 可核验、无判断成分 | `evidence`（暂并入） |
| **Observation** | 原文记录的一次观察/现象 | 描述"发生了什么"，非解释 | `evidence`（暂并入） |
| **Evidence** | 支撑某结论的原文证据/数据点 | 引用得出，非自行推断 | `evidence` |
| **Constraint** | 限制条件（不允许/上限/前提） | 原文写明的硬约束 | 🟡 现无对应枚举 |
| **Requirement** | 要求（MUST/SHOULD 级别） | 原文写明的规范性要求 | 🟡 现无对应枚举 |
| **Warning / Note** | 原文的警告/注意事项 | 原文显式标注 | 🟡 现无对应枚举 |
| **Example** | 原文给出的示例（含代码/SQL） | 原样保留，不改写 | `quote`（暂并入） |
| **Data / Formula** | 数值、公式、表格数据 | 原样保留 | `data` |
| **Quote** | 逐字引用 | 一字不改 | `quote` |

### 属于 Reasoning Layer（Derived，永不进 Knowledge Layer）

| 类型 | 为什么是 Reasoning |
| --- | --- |
| **Interpretation** | 对事实的解读、升华（如把"站直"升华成"保持自信"） |
| **Action / Advice** | 用途、行动建议（Action 是 Usage 不是 Fact，见 rules Rule 4） |
| **Summary** | 跨片段归纳总结 |
| **Opinion** | 观点、评价 |
| **Cross Reference（关系）** | 见下方特别说明 |

---

## 特别说明：Cross Reference 是关系，不是知识

Cross Reference（如 SQLite 文档里"参见 CREATE INDEX")本身**不是一条 Knowledge**，而是两条 Knowledge / Source 之间的**关系**。M1 不建模关系（DATA_MODEL 已明确排除 Relation / 知识图谱，YAGNI）。M1.1 遇到交叉引用：只记录它指向的目标进入 provenance/备注，不新建一条 Knowledge。

---

## 与 DATA_MODEL.kind 的并轨（🟡 待你拍板的开放问题）

当前 `DATA_MODEL.kind` 只有 5 个值：`concept / definition / evidence / data / quote`。
本字典候选类型更丰富，其中 **Constraint / Requirement / Warning 现无对应枚举**。

有两条路，**请你裁决**：

- **A（收敛）**：坚持 5 值枚举，把 Constraint/Requirement/Warning 都并入 `evidence`，类型细分只作为标签/备注，不进 kind。枚举稳定，代价是类型粒度粗。
- **B（扩展）**：kind 枚举扩为字典里的 Knowledge 类型。表达力强，代价是枚举更长、需要重新冻结。

我的建议：**先不改 kind，等 M1.1 用 SQLite `CREATE TABLE` 章节跑一遍**——用真实出现的类型频次来决定该收敛还是扩展，而不是现在拍脑袋。字典先记录全集，kind 的最终值由数据说话。
