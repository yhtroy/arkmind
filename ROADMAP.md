# ROADMAP

只排三个 Milestone。不排时间表，不排一年计划。

每个 Milestone 的定义方式：**做什么、不做什么、怎么算完成。**

## Milestone Gate（每个里程碑的收尾流程）

```
Develop → Review → Refactor → Architecture Sign-off → Freeze → Commit → Tag → Next
```

- Sign-off 与 Freeze 由 Chief Architect 宣布。没有 Sign-off 就没有 Freeze。

### 两种 Commit（修正旧纪律）

Git 首先是历史，不是 Release 工具。不能因为没 Freeze 就丢掉演进过程：

| 类型 | 对象 | 能 Commit | 能 Tag |
| --- | --- | --- | --- |
| Architecture Freeze | VISION / ADR / ARCHITECTURE / DATA_MODEL 等地基文档 | ✅（Freeze 后） | ✅ `v0.x.0-mN`（附注标签） |
| Working Draft | Canon Draft、过程产物、开发中代码 | ✅（随时） | ❌ 绝不打 Tag |

- **Tag 只属于 Freeze。** Working Draft 可以随时 commit（例：`M1: Canon draft (working)`），但绝不打 Tag。

### 收敛机制：每次 Architecture Review 必答三问

为防止“数据模型追着类型字典跑”式的膨胀，每次 Review 都回答：

1. **有没有新增概念？**
2. **有没有新增字段？**
3. **有没有新增状态？**

三个都是“没有” → 这一轮大概率是在**完善**，健康。出现两个以上“新增” → **停下来重新 Review**，警惕膨胀。

> 配套设计哲学（DATA_MODEL 原则 7）：**不为了让数据符合模型而修改数据；只在证据足够时才演化模型。**

### 文档收敛原则：引用，不重复

M1 的成功标准不是文档越来越多，而是**文档之间开始互相引用，而不是重复解释**。一个原则只在一处定义（其 canonical home），其他文档直接引用、不再解释——否则半年后文档会开始漂移。五份 Canon 职责边界见 [README](README.md)。

---

## M1 — Source → Approved Knowledge

> **M1 首要原则（ADR 候选，未编号）：如果 Human 都无法稳定判断一条知识是否应该进入 Knowledge Layer，那么 AI 也不允许决定。**

M1 的目标不是「让 AI 理解一本书」，而是「让系统准确保存一个 Source 中可核验的知识事实」。**Approved = Human 确认（ADR-0005）**，不是 AI；旧措辞 Verified 听起来像 AI 在验证，Approved 永远指向人。

### 输入不是 PDF，是 Source

M1 第一件事不是写 PDF Parser，而是定义 **Source 抽象**（`SourceProvider` 接口，见 [ARCHITECTURE.md](ARCHITECTURE.md)）。PDF 只是第一个实现（`PdfSourceProvider`）；图片、Markdown、EPUB、网页……以后都是同一接口的新实现。

### 范围：不是一本书，是代表性抽取的十个 Fragment

```
Book → Chapter → 代表性 10 Fragments → Gold Standard
```

在 10 个 Fragment 上把 Knowledge 定义磨对，返工成本是几分钟；在一本 200 页上磨错了，返工成本是两百页。

### 第一份 Gold Standard（已拍板）：SQLite 官方文档 CREATE TABLE 章节

**不用《每天听本书》之类解读稿**（经过编辑→讲书人→文稿多次人为加工，是 Interpretation 不是 Source）；**也不用 RFC 2119**（知识类型太单一，几乎只有 Definition/Constraint/Requirement，建出来的是 Specification Grammar 而非 Knowledge Grammar）。

正式选定：**SQLite 官方文档的 `CREATE TABLE` 章节**。理由：知识类型丰富（Definition / Example / SQL / Constraint / Note / Warning / Cross Reference / Diagram），几乎覆盖 ArkMind 以后会遇到的大多数知识类型；且版权开放、来源稳定、版本明确。这将成为 ArkMind 第一份 **Verified Gold Standard**。

**锁定版本：`sqlite-3.46.x`（不追最新版）**。最新版会变，金标准需要一个冻结的参系；Source 的 `id / version / checksum` 全部固定，**M1 完成之前绝不升级**。

筛选三条件（仍适用）：来源简单（一手文本）、逻辑简单（不要哲学/心理/管理）、事实边界清晰。

> 因为我们现在训练的是**知识分类器**，不是读书助手；验证的是 Knowledge Grammar 能不能覆盖真实世界，不是 AI。

### 抽样策略：代表性抽样 Representative Sampling（不是 Random）

目标不是统计意义上的**随机**，而是**代表性**——覆盖知识空间。随机只是控制偏差的一种手段，不是目的：若一章 60% 是 Definition，真随机抽 10 条很可能 Definition×9 + Example×1——它随机，但不代表，Taxonomy 校验会偏。

改为：从 SQLite `CREATE TABLE` 章节按知识空间**代表性抽取 10 个 Fragment**（单位是 **Fragment 而非 Page**，Fragment 才是 Knowledge 最小单位）。类别内部用随机还是人工选，是实现细节，不在现阶段决定。

#### Coverage Design（覆盖设计，非 Coverage KPI）

第一批 Gold Samples 至少覆盖下表（这是 **Sampling Plan** 而非 Taxonomy）：

| 类型 | 最少样本 |
| --- | ---: |
| Definition | 2 |
| Example | 2 |
| Constraint | 2 |
| Quote | 1 |
| Warning | 1 |
| Cross Reference | 1 |
| Unknown | 不主动追求，出现就记录 |

#### Sampling Plan（M1.1 新增交付物，一页纸）

每份 Gold Standard 都必须随带一份 Sampling Plan，回答一句话：**这批 Gold Standard 为什么被认为具有代表性**。没有 Sampling Plan，就不知道“为什么抽的是这些”。（以后甚至可能有 `SamplingProvider`——先定接口，再讨论实现。）

### M1.1 — 建立 Human Gold Standard（先行，无代码）

- 三方（作者 / Chief Architect / Qoder）人工对**同一批代表性抽取的 10 个 Fragment**（见上方抽样策略）提取知识，建立金标准。
- 不用 AI、不用 Prompt、不用 Agent。产出是五份 Canon 定稿（v1.0）：[knowledge_rules.md](docs/canon/knowledge_rules.md)、[knowledge_examples.md](docs/canon/knowledge_examples.md)、[knowledge_taxonomy.md](docs/canon/knowledge_taxonomy.md)、[provenance.md](docs/canon/provenance.md)、[review_guidelines.md](docs/canon/review_guidelines.md)。
- **M1.1 目标不是提取完所有知识，而是验证 Knowledge Grammar 能不能覆盖真实世界。** 如果出现一种无法分类的知识，先记为 `unknown`（不是失败，是 Grammar 不足的信号，见 Type Discovery）——改分类学，不硬塞。
- 完成标准：三方对这 10 个 Fragment 的提取结果能稳定收敛；Canon 定稿。

### M1.2 — AI 学习 Gold Standard

- AI 在**同一批 10 个 Fragment** 上产出候选，对照 M1.1 金标准同时计算 **Fidelity（保真度）与 Coverage（覆盖度）**。
- 顺序不能反：先有人的金标准，再让 AI 学。

#### Gold Standard 永远不是 Truth，只是 Best Current Standard（BCS）

Gold Standard 不是真理，只是**当下最佳标准**。半年后可能发现 Taxonomy 有缺陷、Checklist 有漏洞、某条 Gold Sample 判错——不推翻，而是 **Version**（v1.0 → v1.1 → v2.0），每次修改必须说明为什么（与 SQLite 文档 Version 同一哲学）。
- **规划（M1.2，尚未创建）**：一页纸的极小 Canon `gold_standard_versioning.md`，只回答“Gold Standard 如何升级”。现在先记下 BCS 原则（否则到时历史已丢），文档本体留到 M1.2。

**不做什么**

- ❌ Knowledge Extraction 自动化（M1.1 完成前不写任何提取代码）
- ❌ 写作、文章生成（M1 根本不关心知乎和小红书）
- ❌ Agent / Web 前端
- ❌ 一次处理整本书

### M1.1 最终交付物：人工校准表（Gold Samples + Gold Review）

M1.1 第一版交付的不是 JSON、不是数据库，而是一张人工校准表——**这张表就是 Gold Standard**。以后任何 Parser / LLM / OCR 都必须和这张表对比。

**Gold Standard = Gold Samples + Gold Review**（见 [review_guidelines.md](docs/canon/review_guidelines.md)）：

- **Part 1 Gold Samples**：独立批准的样本 GS-001 … GS-010。
- **Part 2 Gold Review**：每个判定的理由（为什么 Definition / 为什么 Quote / 为什么 Unknown）。AI 学的不是结果，而是**判定过程**。

| Sample | Fragment | 初步类型 | Provenance | 是否 Approved | Gold Review（判定理由 / 分歧） |
| --- | --- | --- | --- | --- | --- |
| GS-001 | F-001 | Definition | P12 | ✅ | 原文“X 是……”，无解读 |
| GS-002 | F-007 | Unknown | P13 | ❌ | Taxonomy 无对应类型，等 Type Discovery |
| GS-003 | F-011 | Quote | P13 | ✅ | 逐字引用，一字未改 |

### M1.1 真正的开始方式（五步）

不是“处理前十页”，而是：

1. 锁定 SQLite `3.46.x` 对应文档。
2. 从 `CREATE TABLE` 章节按 Coverage Design **代表性抽取 10 个 Fragment**（覆盖不同类型，不是连续页），并写下 Sampling Plan。
3. 建立第一批 **Gold Samples**。
4. 用 [review_guidelines.md](docs/canon/review_guidelines.md) 做人工评审（Checklist 五问，不凭感觉）。
5. 完成后再回头统计：`unknown` 出现多少？`concept` 出现多少？哪些类型最易产生分歧？

**最后才讨论 Data Model 是否需要演化。** 节奏：先观察再分类，先积累证据再改模型，永远不为了让模型好看而让真实数据迁就模型。

### M1 只有三个 Deliverable

不是五个，不是十个。三个。

1. **Source Interface** — 一个 `SourceProvider`，一个 PDF 实现，结束。Source 先登记（`sources/<id>/source.yaml`）再解析，暂不用 `data/`。
2. **Gold Standard** — 代表性抽取的 10 个 Fragment 经 Human Approve，打包为：Sampling Plan（为何代表）+ Gold Samples + Gold Review（status：Observed → Approved）。
3. **Knowledge Fidelity + Coverage** — 两个指标能够计算（现在只要定义，计算方式以后再设计）。

> Extraction / AI / Agent / Prompt 都**不是** Deliverable。

### M1 第一个 PR 不是代码

第一个 PR 不是 Python / Docker / API，而是手工跑通这条链（Excel / Markdown / JSON 都行）：

```
Book → Page → Fragment → Knowledge Candidate → Human Review → Approved Knowledge
```

因为我们不是在开发 OCR，而是在定义 ArkMind 的**知识语法**。M1 第一周不属于 AI，属于 Knowledge Engineering。交付物是五份 Canon：[knowledge_rules.md](docs/canon/knowledge_rules.md)（规则）、[knowledge_examples.md](docs/canon/knowledge_examples.md)（例子）、[knowledge_taxonomy.md](docs/canon/knowledge_taxonomy.md)（分类学）、[provenance.md](docs/canon/provenance.md)（出处）、[review_guidelines.md](docs/canon/review_guidelines.md)（评审）。

### 工程格言

> **Slow is smooth. Smooth is fast.** 宁愿第一周只有 10 个 Fragment，但十年后这 10 个仍不用返工。

**完成标准（Success Criteria）**

> **M1 核心 KPI 是 Knowledge Fidelity（保真度）+ Coverage（覆盖度），不是提取数量，不是 Accuracy/Recall/Precision。两者必须同时报告。**
>
> 定义与度量方式见 [docs/canon/knowledge_rules.md](docs/canon/knowledge_rules.md)。取向：宁可漏提，不可失真（Fidelity 优先于 Coverage）。
>
> 达标：在那 10 个 Fragment 上，AI 产出的候选对照 Gold Standard 的 Fidelity 与 Coverage 达到三方认可的阈值。

---

## M2 — Knowledge 生成内容

**做什么**

- Reasoning 层启用并建模（推理产物属于本层，不进 Knowledge 层，见 ADR-0003）：基于 approved knowledge 做推理
- 生成知乎、小红书两种格式的草稿
- 草稿必须经作者 Approve 才算产出（ADR-0004）

**不做什么**

- ❌ 自动发布
- ❌ 更多渠道
- ❌ Memory / Feedback

**完成标准**

> 从已入库的 knowledge 出发，产出一篇作者愿意署名发布的知乎文章和一篇小红书笔记。

---

## M3 — Memory 与 Feedback 闭环

**做什么**

- 记录作者对草稿的修改与取舍（这就是最初的 Feedback 数据）
- 让下一轮生成能利用这些偏好

**不做什么**

- ❌ 读者数据抓取、平台 API 对接（等真的需要再说）

**完成标准**

> 第二次生成的草稿，能明显体现第一次 Approve/修改中表达出的偏好。

---

## M3 之后

不排。到时候根据 M1–M3 的真实反馈再定。任何"顺便把 XX 也做了"的提议，先读 [ADR-0002](ADR/ADR-0002-yagni.md)。
