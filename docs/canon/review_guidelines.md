# Review Guidelines（人工评审 Canon v0.1 Draft）

- 状态：**Draft** —— 第五份 Canon，配套 [knowledge_rules.md](knowledge_rules.md)（规则）、[knowledge_examples.md](knowledge_examples.md)（例子）、[knowledge_taxonomy.md](knowledge_taxonomy.md)（分类学）、[provenance.md](provenance.md)（出处）。
- 本文档回答一个问题：

> **人工 Approve 一条 Knowledge 候选时，到底该按什么清单逐条核？**

**这里只写 Review Checklist，不写 Prompt。** 我们训练的是判定标准，不是提示词。以后任何 Reviewer（人或 AI）都按同一份清单走，Review 靠 Checklist 而不是靠感觉。

---

## Review Checklist（五问，逐条回答）

对每一条候选，Reviewer 必须逐条回答，任何一问不通过 → 打回或改判类型，不得 Approve。

### Q1 — 这一条是不是可验证事实？

是不是 Observed、忠于原文、可回到原件核验的事实？若掺了判断/升华 → 属 Reasoning 层，打回（见 taxonomy）。

### Q2 — 有没有混入 Interpretation？

有没有把原文没说的解读、结论、"言外之意"写进 statement？有 → 剥离，只留原文事实。

### Q3 — 有没有脱离 Provenance？

来源链是否完整、`extractor` 是否记录？任一环缺失即无出处，直接打回（判定细则见 [provenance.md](provenance.md)，另见 rules Rule 7）。

### Q4 — 有没有多个 Knowledge 混在一起？

一条候选是否塞了不止一个独立事实？是 → 拆分成多条，各自独立 Approve（一条 Knowledge = 一个最小事实单位）。

### Q5 — 换一个 Reviewer，会不会得到一样的结果？

判定是否可复现？若换个人大概率会分歧 → 说明标准不清或这条本身模糊，记为分歧项进入统计，不强行 Approve。

---

## Gold Standard = Gold Samples + Gold Review

Gold Standard 不只是一批被批准的样本，它有两部分：

### Part 1 — Gold Samples

被独立批准的样本本身：`GS-001 / GS-002 / … / GS-010`。每一个独立评审、独立批准。

### Part 2 — Gold Review

**每个判定背后的理由**：为什么判 Definition？为什么判 Quote？为什么记 Unknown？全部写出来。

> 因为以后 AI 学的不是**结果**（这条是 Definition），而是**判定过程**（凭什么判成 Definition）。没有 Gold Review 的 Gold Samples 只是答案，没有解题步骤——训练不出判断力。

> **Gold Standard 永远不是 Truth，只是 Best Current Standard（BCS）。** 它可以被修订，但只能通过 Version（v1.0 → v1.1 → v2.0）而非推翻，每次修订必须说明为什么。（BCS 目前是非阻塞设计备注，见 [ROADMAP.md](../../ROADMAP.md) 附录 Future Notes。）

---

## 校准表列（承载 Gold Samples + Gold Review）

在 ROADMAP 的人工校准表基础上，Review 理由落在「备注 / Gold Review」列：

| Sample | Fragment | 初步类型 | Provenance | Q1–Q5 是否通过 | 是否 Approved | Gold Review（判定理由 / 分歧） |
| --- | --- | --- | --- | --- | --- | --- |
| GS-001 | F-001 | Definition | P12 | ✅ | ✅ | 原文"X 是……"，无解读 |
| GS-002 | F-007 | Unknown | P13 | 部分 | ❌ | Taxonomy 无对应类型，等 Type Discovery |
| GS-003 | F-011 | Quote | P13 | ✅ | ✅ | 逐字引用，一字未改 |

---

## 与 Type Discovery 的关系

Review 过程中记为 `unknown` 或产生分歧的样本，都是 Type Discovery 的输入。Reviewer 不负责"把它归进某个已有类型凑数"，只负责如实标注 + 写清理由；何时演化分类学/字段，由后续统计 + Architecture Review 决定（见 knowledge_taxonomy.md、ROADMAP 收敛机制）。
