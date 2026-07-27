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

---

## M1 — Source → Approved Knowledge

> **M1 首要原则（ADR 候选，未编号）：如果 Human 都无法稳定判断一条知识是否应该进入 Knowledge Layer，那么 AI 也不允许决定。**

M1 的目标不是「让 AI 理解一本书」，而是「让系统准确保存一个 Source 中可核验的知识事实」。**Approved = Human 确认（ADR-0005）**，不是 AI；旧措辞 Verified 听起来像 AI 在验证，Approved 永远指向人。

### 输入不是 PDF，是 Source

M1 第一件事不是写 PDF Parser，而是定义 **Source 抽象**（`SourceProvider` 接口，见 [ARCHITECTURE.md](ARCHITECTURE.md)）。PDF 只是第一个实现（`PdfSourceProvider`）；图片、Markdown、EPUB、网页……以后都是同一接口的新实现。

### 范围：不是一本书，是十页

```
Book → Chapter → 10 Pages → Gold Standard
```

在 10 页上把 Knowledge 定义磨对，返工成本是几分钟；在一本 200 页上磨错了，返工成本是两百页。

### 第一批 Gold Standard 选什么：不用被转述过的书

**第一批 Gold Standard 不用《每天听本书》之类的解读稿。** 它已经经过编辑→讲书人→文稿至少两次人为加工，是 Interpretation，不是 Source。我们建立的是 Knowledge Grammar，不是“得到 Grammar”。

第一批数据应满足三个条件：

1. **来源简单** — 一手文本，不是别人解读后的书。
2. **逻辑简单** — 不要哲学/心理学/管理学（Interpretation 太多）。
3. **事实边界清晰** — 技术书、说明书这类。

最佳首选：**RFC 文档**（Definition / Requirement / Constraint / Example 天然存在，知识边界极清楚）；或 Markdown 官方教程、Python 官方 Tutorial、SQLite / Docker 官方文档。

> 因为我们现在训练的是**知识分类器**，不是读书助手；验证的是 Knowledge Definition，不是 AI。

### M1.1 — 建立 Human Gold Standard（先行，无代码）

- 三方（作者 / Chief Architect / Qoder）人工对同一 10 页提取知识，建立金标准。
- 不用 AI、不用 Prompt、不用 Agent。产出是定稿的 [docs/canon/knowledge_rules.md](docs/canon/knowledge_rules.md) 与 [knowledge_examples.md](docs/canon/knowledge_examples.md)（v1.0）。
- 完成标准：三方对这 10 页的提取结果能稳定收敛；Canon 定稿。

### M1.2 — AI 学习 Gold Standard

- AI 在同样 10 页上产出候选，对照 M1.1 金标准同时计算 **Fidelity（保真度）与 Coverage（覆盖度）**。
- 顺序不能反：先有人的金标准，再让 AI 学。

**不做什么**

- ❌ Knowledge Extraction 自动化（M1.1 完成前不写任何提取代码）
- ❌ 写作、文章生成（M1 根本不关心知乎和小红书）
- ❌ Agent / Web 前端
- ❌ 一次处理整本书

### M1 只有三个 Deliverable

不是五个，不是十个。三个。

1. **Source Interface** — 一个 `SourceProvider`，一个 PDF 实现，结束。Source 先登记（`sources/<id>/source.yaml`）再解析，暂不用 `data/`。
2. **Gold Standard** — 10 页的 Knowledge Candidate 经 Human Approve，得到金标准（status：Observed → Approved）。
3. **Knowledge Fidelity + Coverage** — 两个指标能够计算（现在只要定义，计算方式以后再设计）。

> Extraction / AI / Agent / Prompt 都**不是** Deliverable。

### M1 第一个 PR 不是代码

第一个 PR 不是 Python / Docker / API，而是手工跑通这条链（Excel / Markdown / JSON 都行）：

```
Book → Page → Fragment → Knowledge Candidate → Human Review → Approved Knowledge
```

因为我们不是在开发 OCR，而是在定义 ArkMind 的**知识语法**。M1 第一周不属于 AI，属于 Knowledge Engineering。交付物是三份 Canon：[knowledge_rules.md](docs/canon/knowledge_rules.md)、[knowledge_examples.md](docs/canon/knowledge_examples.md)、[provenance.md](docs/canon/provenance.md)。

### 工程格言

> **Slow is smooth. Smooth is fast.** 宁愿第一周只有 10 页，但十年后这 10 页仍不用返工。

**完成标准（Success Criteria）**

> **M1 核心 KPI 是 Knowledge Fidelity（保真度）+ Coverage（覆盖度），不是提取数量，不是 Accuracy/Recall/Precision。两者必须同时报告。**
>
> 定义与度量方式见 [docs/canon/knowledge_rules.md](docs/canon/knowledge_rules.md)。取向：宁可漏提，不可失真（Fidelity 优先于 Coverage）。
>
> 达标：在那 10 页上，AI 产出的候选对照 Gold Standard 的 Fidelity 与 Coverage 达到三方认可的阈值。

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
