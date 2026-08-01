# RESEARCH-0007 — Knowledge Assets

> Product Discovery（P1 / Sprint A）。只读事实分析，回答"一本优秀的非虚构书籍最终真正值得长期保存的知识资产有哪些"，作为 M2（Creative Engine）Asset Taxonomy 的事实输入。
> 本文档不设计模型、不设计字段、不写 RFC、不提实现方案、不改任何源码。对 ArkMind 现状的描述基于 `main` 当前代码（commit 参考 `a3f946f`）。

**准入门槛回答**：本研究定义"Knowledge Factory 到底生产什么资产"。这是"一本书 → 一篇优秀博文"链路最上游的资产定义——资产选错，其后 Topic/Insight/Outline/Renderer 全部建立在错误的地基上。故它缩短链路，进入主线。

---

## 1. 候选知识资产清单

从一本优秀非虚构书籍中，读者/创作者实际会想长期留存的东西（枚举，不限于示例，不代表结论）：

| 资产 | 是什么 | 典型形态 |
|---|---|---|
| Concept（概念） | 一个被命名的抽象 | "复利"、"长期主义"、"心流" |
| Definition（定义） | 对某概念的精确界定 | "心流是指……的状态" |
| Principle（原则） | 一条被主张为普遍成立的规律 | "延迟满足带来长期收益" |
| Method（方法） | 可操作的做法/步骤 | "如何建立每日复盘" |
| Framework（框架） | 多个概念/步骤组成的结构化模型 | "SWOT"、"第一性原理四步" |
| Model（心智模型） | 用于理解世界的思考工具 | "复利模型"、"供需模型" |
| Case（案例） | 真实发生的完整事例 | "某公司如何靠复利增长" |
| Story（故事） | 带叙事张力的经历 | 作者的亲身经历 |
| Quote（金句/引用） | 高度凝练、可直接引用的原话 | 名人原话、作者警句 |
| Question（问题） | 值得追问的开放问题 | "为什么多数人做不到长期主义？" |
| Fact / Data（事实/数据） | 可核验的客观信息 | 统计数字、历史事件 |
| Argument（论证） | 支撑某观点的推理链 | "因为 A 所以 B" |
| Counterpoint（反例/反论） | 与主张相冲突的证据或观点 | "但在 X 情况下不成立" |
| Analogy（类比） | 用熟悉事物解释陌生事物 | "习惯像复利" |
| Checklist（清单） | 可执行的要点列表 | "决策前的 5 个自查" |

（以上为候选池，是否全部采纳属 Asset Taxonomy 的设计决策，本文不做。）

---

## 2. "书里的事实" vs "读者可长期复用的知识"

按"绑定这本书 / 脱离这本书仍有价值"二分（事实层面）：

**A. 书里的事实（强绑定本书，脱离书就失去意义或需重新溯源）**
- Fact / Data：属于这本书引用的具体信息，换个语境要重新核验。
- Case / Story：常与作者的具体叙事、人物绑定。
- Quote：绑定"谁说的、在哪本书说的"——它的价值一部分来自出处本身。
- Argument：绑定作者的具体论证语境。

**B. 读者可长期复用的知识（脱离本书仍独立成立、可迁移到新场景）**
- Concept / Definition：一旦理解，可用于任何场景。
- Principle：主张普遍成立，天生可迁移。
- Method / Framework / Model / Checklist：是"拿来就能用"的工具，复用性最强。
- Analogy：可迁移到解释其他事物。
- Question：可反复用于激发不同主题的思考。

关键观察（事实）：A 类是**证据/素材**（Evidence 的原料，价值在"可追溯、可引用"）；B 类是**可迁移的思维工具**（价值在"脱离原书仍成立"）。一篇好博文往往是 **B 类作骨架、A 类作血肉**——用可复用的 Concept/Principle/Method 立论，用本书的 Case/Quote/Data 佐证。

---

## 3. 跨书价值 vs 单书专属

| 资产 | 跨书复用价值 | 说明 |
|---|---|---|
| Concept | 最高 | 同一概念在多本书反复出现，是跨书聚合的天然锚点 |
| Principle | 最高 | 不同书对同一原则可支持/补充/反驳 → 跨书 Insight 的核心 |
| Method / Framework | 高 | 工具类知识天然可跨书对比"谁的方法更好" |
| Model / Analogy | 高 | 思维工具可迁移 |
| Question | 高 | 同一问题可汇聚多本书的不同回答 |
| Quote | 中 | 可跨书汇成"关于 X 的金句集"，但绑定出处 |
| Case / Story | 低 | 强绑定具体人物/情境，跨书主要作为对照例证 |
| Fact / Data | 低 | 绑定具体来源与时点，跨书需重新核验 |

事实结论：**跨书价值最高的是 Concept 与 Principle**（其次 Method/Framework/Model/Question）——它们能成为把多本书连起来的"共同锚点"，正是 RESEARCH-0005 里"Topic 跨书聚合"和 RESEARCH-0004 里"跨书 Insight"的物质基础。**只能存在于单本书的是 Case/Story/具体 Fact**——它们是那本书专属的证据，跨书时只能作为例证被引用，无法作为聚合锚点。

---

## 4. 可确定性抽取 vs 未来需要 AI

以 ArkMind 已冻结的纪律"Knowledge 处理禁用 AI、确定性优先"为对照，按"是否能用规则/模式确定性识别"分层：

**A. 可完全（或高度）确定性抽取**
- Quote：引号、破折号署名、缩进引用块等有稳定排版特征。
- Definition：常有"X 是指…""X 定义为…"等句式模式。
- Fact / Data：数字、日期、单位有正则可循。
- Question：以问号结尾、疑问词开头。
- Checklist：编号/项目符号列表结构。
- 已验证先例：`ST_*` 函数引用就是纯正则确定性抽取（RFC-0013）。

**B. 部分可确定性、边界模糊**
- Concept / Term：术语（首字母大写、黑体、术语表）有信号，但"哪些才是**关键**概念"需判断。
- Method / Framework：步骤列表、"三步法"等有结构信号，但完整边界常需理解。

**C. 未来一定需要 AI（或人工判断）**
- Principle：把散落表述归纳成一条普遍规律，是抽象行为。
- Argument / Counterpoint：识别推理链与立场冲突需语义理解。
- Insight（跨书判断）：本就是 RESEARCH-0004 定义的"组织好的观点"，非抽取而是组织+判断。
- Story 的"要点/寓意"：叙事压缩需理解。

事实结论：**越靠近"原文形态"的资产越可确定性抽取（Quote/Definition/Fact/Question/Checklist）；越靠近"抽象与判断"的资产越依赖 AI（Principle/Argument/Insight）。** 这条分界与 §2 的 A/B 分类高度重合——证据类可确定性抽取，思维工具类的高阶归纳需要 AI。这意味着 Knowledge Factory 可以**先确定性地沉淀证据类资产**，把需要 AI 的抽象层留到 Creative Engine 上层，符合"确定性优先、AI 后置"的既有纪律。

---

## 5. 最终回答：Knowledge Factory 最终真正应该生产哪些资产

按"复用价值 × 可确定性 × 对博文创作的贡献"综合，事实归纳如下（分析，非设计、非取舍决定）：

**第一梯队——最该生产（跨书价值最高，是创作锚点）**
- **Concept**：跨书聚合与 Topic 形成的天然锚点。
- **Principle**：跨书 Insight（支持/反对/互补）的核心载体。

**第二梯队——高价值可复用工具（应生产）**
- **Method / Framework / Model**：读者"拿来即用"，跨书可对比。
- **Question**：可汇聚多书答案，驱动选题。

**第三梯队——证据素材（应生产，作 Evidence 支撑，且大多可确定性抽取）**
- **Quote / Definition / Fact-Data / Case / Story**：为观点提供可追溯佐证，绑定出处正是 ArkMind 的 Provenance 优势所在。

**跨梯队的一个事实**：
- 当前 ArkMind 的 `Knowledge` 是"一页一条的原文片段"，它其实是**上述资产的原料/容器**，而不是任何一种成型资产。也就是说，从"页级 Knowledge"到"资产（Concept/Principle/…）"之间，目前存在一整层**尚不存在的萃取**。这与 RESEARCH-0004 的 Gap、RESEARCH-0005 的"Knowledge≠Topic"结论一致：Knowledge Factory 现在生产的是**原料**，还没生产**资产**。

**一句话结论**：
> Knowledge Factory 最终应生产的核心资产是**跨书可复用的思维工具（Concept、Principle、Method/Framework/Model、Question）**，以及支撑它们的**可追溯证据（Quote、Definition、Fact、Case、Story）**；前者是创作的锚点与骨架、多数需 AI 归纳，后者是血肉与可信度、多数可确定性抽取。当前系统只生产到"页级原料"，尚未生产任何成型资产——这正是 M2 要补的第一层。

以上为事实分析，不含模型/字段设计、不含 RFC、不含实现方案。

---

## DoD 自检

- 只读分析 ✅　不写代码 ✅　不写 RFC ✅　不提方案 ✅　不设计模型/字段 ✅　未改任何源码 ✅
- 仅产出本 Markdown（`docs/research/RESEARCH-0007-knowledge-assets.md`）✅

RESEARCH-0007 完成。停止，等待 Review。
