# Knowledge Rules（Canon v0.1）

- 状态：**Draft** —— 等待三方（作者、Chief Architect、Qoder）在 M1.1 中用真实书页校准后定稿
- 本文档是 AI 学习的对象。AI 学习的不是 Prompt，是这份 Canon。

> **M1 首要原则（ADR 候选）：**
> **如果 Human 都无法稳定判断一条知识是否应该进入 Knowledge Layer，那么 AI 也不允许决定。**

---

## 判定总纲：进入 Knowledge Layer 的四道门槛

一条候选（candidate）必须**同时**通过以下四道门槛，缺一即打回：

| 门槛 | 判定问题 |
| --- | --- |
| 1. 事实性 | 这是原文陈述的事实吗？（不是修辞、过渡、情绪、跨段归纳） |
| 2. 忠实性 | 表述里有没有原文不存在的概念、外部知识、强度改变？ |
| 3. 可回链 | 能指向具体的 fragment 和页码吗？ |
| 4. 可核验 | 第三个人拿着原文，能机械地判断"原文支持/不支持这句话"吗？ |

任何一道门槛上 Human 判断不稳定（三方意见分裂且无法收敛）→ 该条**不进入** Knowledge Layer。这不是遗憾，这是原则。

---

## 十条规则（v0.1）

### Rule 1 — 一个 Definition 是一条

原文给某个概念下了定义或赋予了性质，即一条，kind = `definition`。

### Rule 2 — 一个 Evidence 是一条

一个主体 + 一个现象/结果 = 一条，kind = `evidence`。
实验、案例、观察各自成条；同一实验的不同结果，各自成条。

### Rule 3 — 一个 Quote 是一条

原样引用，一字不改，kind = `quote`。长度以"表达一个完整意思"为限——整段照抄不是 Quote，是偷懒。

### Rule 4 — Action 不是事实，不入 Knowledge Layer

**M1 架构裁决（2026-07-27）：kind 不新增 `action`。** 指令/动作不是事实（Fact），而是对事实的用途（Usage）。

原文「站直，把肩膀向后打开」是 `quote` 或 `evidence`（作者陈述了什么），不是 action。因为一旦标成 action，不同人会提炼出「保持开放姿态」「改善体态」「提高自信」——这已经进入解释（Interpretation），不再是原文事实。

用途/行动建议以后由 **Reasoning 层动态生成**，永不进入 Knowledge Layer。kind 枚举固定为 `concept / definition / evidence / quote / data`。

### Rule 5 — 不要混合，必须拆

复合句必须拆开。`因为 A，所以 B` → A 一条、B 一条。
因果关系本身是不是知识？——现在不建模（Relation 属于"明确不建模"清单），拆完即可。

### Rule 6 — 忠于原文，禁止升华

statement 不得引入原文没有的词汇、概念、外部知识；不得改变强度（"可能有助于" ≠ "能显著提升"）；不得把比喻升华成道理。
**"没有错"不等于"忠实"。** 判定标准只有一个：原文写了吗？

### Rule 7 — 出处强制

没有 fragment_ids 和页码的候选，直接打回，不进入人工评审。无出处 = 不存在。

### Rule 8 — 裸概念不是知识

`血清素` 三个字不是一条知识。`血清素是一种神经递质（原文定义）` 才是。
Concept 只有在原文赋予它定义、性质或角色时才成条（kind = `concept` 或 `definition`）。

### Rule 9 — 不提取修辞、比喻、过渡、情绪

作者的抒情、章节过渡语、幽默、反问，一律不提取。它们是文笔，不是事实。

### Rule 10 — 归纳总结属于 Reasoning，禁止入库

跨段落、跨章节的概括（"本章告诉我们……"）是理解，不是事实。它属于 Reasoning 层，写进 Knowledge 层即污染（ADR-0003）。

---

## Knowledge Fidelity（知识保真度）—— M1 唯一 KPI

### 定义

> 一批知识候选中，经 Human 对照原文判定为"忠实原文事实"的比例。

```
Knowledge Fidelity = faithful candidates / total candidates
```

### 判定方式

每条候选由人对照 fragment 原文，回答一个二元问题：

> **"这句话是原文陈述的事实吗？"**

- 是 → faithful
- 否（升华、外推、混入外部知识、强度失真、归纳总结）→ unfaithful

### 与传统指标的区别

- 不是 Accuracy：`保持自信` 这条提取"没有错"，但原文没写，Fidelity 记为 unfaithful。
- 不是 Recall：**漏提不扣 Fidelity**。M1 的取向是"宁可漏提，不可失真"。
- 不是 Precision：Precision 问"对不对"，Fidelity 问"是不是原文事实"。

### M1 的考核方式

M1.2 中，AI 在同样 10 页上产出候选，对照 M1.1 的 Human Gold Standard 计算 Fidelity。提取数量不是 KPI，永远不是。

---

## 本文档的修订纪律

- Canon 的每次修订都要有真实案例驱动（"这一条在第 X 页判不下去了"），不接受凭空增改。
- 修订须三方过目，由 Chief Architect 拍板。
- 定稿版本号从 v1.0 开始，之前都是 Draft。

## 示例标注约定

所有例子必须标明来源，不得混用：

- `Example (Synthetic)` —— 为演示规则而编写的示意文本。
- `Example (Verified)` —— 来自真实书页、已经回链核验的文本。

一旦混用，以后无人分得清哪些是真、哪些是假。Gold Standard 定稿时，示意文本必须全部替换为 `Example (Verified)`。
