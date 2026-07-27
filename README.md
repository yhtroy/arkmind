# ArkMind

> **Build Your Second Brain, Not Your Second Hard Drive.**

**ArkMind 不是内容生成器。不是 Prompt 集合。不是 AI 写作工具。**

**ArkMind 是一个长期演化的 Personal Knowledge Operating System（个人知识操作系统）。**

所有知识进入这里，不断积累，不断演化。文章、视频、课程、Agent——都只是它之上的插件。

> 不是让 AI 替我们思考，而是让 AI 帮我们积累可以反复思考的知识。

## Project Principle

```
Everything is Knowledge.
Everything derives from Knowledge.
Nothing bypasses Knowledge.
```

> **一切输入都会进入知识层；一切输出都来源于知识层；任何模块都不得绕过知识层。**

这是整个 ArkMind 最大的原则。所有设计与评审，以此为最终标准。

> **如果 Human 都无法稳定判断一条知识是否应该进入 Knowledge Layer，那么 AI 也不允许决定。**

这句话决定了 ArkMind 究竟是一个“AI 自动化工具”，还是一个真正值得长期积累的“知识操作系统”。

> **RAG 检索的是 Document；ArkMind 检索的是 Knowledge。** 这是 ArkMind 与所有 RAG 最大的区别（详见 [VISION.md](VISION.md)）。Document 只是来源，**真正的资产是 Knowledge**。

## 文档（先读这几份，再谈代码）

前四份回答「系统是什么」（Domain），ENGINEERING 回答「系统怎么造」（工程基线）：

| 文档 | 回答的问题 |
| --- | --- |
| [VISION.md](VISION.md) | 这个产品五年以后是什么 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 系统有哪五层，边界在哪 |
| [DATA_MODEL.md](DATA_MODEL.md) | Knowledge 长什么样（最重要） |
| [ROADMAP.md](ROADMAP.md) | 三个 Milestone，不多不少 |
| [ENGINEERING.md](ENGINEERING.md) | 系统应该怎么造（语言 / 目录 / 规范，工程基线 v1） |

## 四条铁律（ADR）

1. [ADR-0001 永远不要为了 AI 而设计系统](ADR/ADR-0001-never-design-for-ai.md) — 模型只是插件
2. [ADR-0002 不要过早设计（YAGNI）](ADR/ADR-0002-yagni.md) — 需要的时候再长出来
3. [ADR-0003 知识必须可以重新理解，而不是重新生成](ADR/ADR-0003-reinterpret-not-regenerate.md) — 只存事实，不存 AI 结论
4. [ADR-0004 Human Override First](ADR/ADR-0004-human-override-first.md) — AI 不能写 Knowledge，必须人 Approve
5. [ADR-0005 数据哲学：三状态](ADR/ADR-0005-data-philosophy-three-states.md) — Observed → Approved → Derived，无 candidate/draft

## 技术选型（每一项都有引入理由，不是因为它火）

> 工程基线的 canonical home 是 [ENGINEERING.md](ENGINEERING.md)（含包管理 / 目录 / 编码 / 依赖 / 测试 / Git 规范）；下表是摘要。

| 层 | 技术 |
| --- | --- |
| 语言 | Python |
| 数据库 | PostgreSQL（向量：pgvector；全文检索：PG FTS） |
| PDF 解析 | PyMuPDF + pdfplumber |
| OCR | PaddleOCR（本地） |
| LLM 接入 | LiteLLM（统一 Adapter） |
| Workflow | 自写简单 Pipeline（不用 Dify / LangGraph） |
| API | FastAPI |
| 前端 | 暂无（CLI + API 足够） |
| 部署 | Docker Compose |

## Canon（知识语法：五份，职责单一、互不重叠）

`docs/canon/` 下五份 Canon 是 AI 的学习对象。M1 的成功标准不是文档越来越多，而是**互相引用、不重复解释**：一个概念只在它的 canonical home 定义一次，其他文档引用而不重述。

| Canon | 单一职责（canonical home） | 不负责（引用它处） |
| --- | --- | --- |
| [knowledge_rules.md](docs/canon/knowledge_rules.md) | 判定规则（十条）+ 四道门槛 + Fidelity/Coverage 指标 | 类型枚举 → taxonomy；出处结构 → provenance |
| [knowledge_taxonomy.md](docs/canon/knowledge_taxonomy.md) | `kind` 分类体系 + Type Discovery + Unknown 过渡态 | 判定流程 → rules；评审清单 → review |
| [knowledge_examples.md](docs/canon/knowledge_examples.md) | 正/误提取案例（规则的示例化） | 规则本身 → rules |
| [provenance.md](docs/canon/provenance.md) | 来源链结构 + `provenance` 抽象 + `extractor` 可追责 | 出处是否必需 → rules Rule 7 |
| [review_guidelines.md](docs/canon/review_guidelines.md) | 人工评审 Checklist（五问）+ Gold Standard 构成 | 抽样/BCS → ROADMAP；出处细则 → provenance |

## 目录

```
arkmind/
├── ADR/              # 架构决策记录
├── docs/canon/       # 知识语法 Canon（rules / examples / taxonomy / provenance / review，职责边界见上表）
├── sources/          # 数据集登记（Dataset-000x/source.yaml）
├── VISION.md
├── ARCHITECTURE.md
├── DATA_MODEL.md
├── ROADMAP.md
├── ENGINEERING.md    # 工程基线（系统怎么造）
└── README.md
```

代码（`src/` 与 `tests/`）在 M1 动工时按需长出来——遵守 ADR-0002 与 [ENGINEERING.md](ENGINEERING.md)，不预建空目录。

## 协作模式（Project Charter — Execution Phase）

ArkMind 已从「设计项目」切换为「工程项目」。**Project Charter: Approved / Architecture: Discussion Closed / Execution Phase: Started。** 三个角色按**职责**锁死，不再漂移：

| 角色 | 职责 | 不做 |
| --- | --- | --- |
| **CEO / Product Owner** | 只回答三个问题：做什么 / 为什么做 / 结果满意吗；决定产品方向与取舍 | 不做技术选型（DB / 语言 / 框架）、不设计表与接口、不当技术中转站 |
| **Chief Architect（Technical Lead）** | 拥有**整个技术方案**：架构 / 模块划分 / 数据库 / 技术选型 / 接口 / 工程规范 / Git / 测试策略 / 性能目标 / 部署 / 风险 / Roadmap，乃至排期（今天写哪个模块）；产出**可直接开发的 RFC（工程设计）**，承担技术结果 | 不做产品价值判断（那是 CEO） |
| **Production Engineer（Qoder）** | **施工**：按 RFC / Task 高质量落地（Parser / Extraction / SQLite / Python / OCR / CI / Git / 测试 / Bug），提 PR，随 Review 迭代直到通过 | 不做设计：遇问题回来**汇报**、不自行重设计；少问「设计要不要改」，多问「API 怎么定义 / 单测怎么写 / 性能怎么验证」 |

**工程流程**：CEO 提需求（要什么）→ Chief Architect 出 RFC（Engineering Design：目标 / 方案 / 数据库 / 接口 / 目录 / 风险 / 验收）→ Qoder 施工 → Architect Review → 通过 → CEO 验收。RFC 是工程输入，区别于 ADR（决策记录）；面对「还能更优」先问 **Fatal Issue？** 不是 → `Reject`（治理见 [ROADMAP.md](ROADMAP.md)）。

## 当前状态

- **M0**：已 Freeze 并打 tag `v0.1.0-m0`（五层架构 / 五份 ADR / 地基文档冻结）。
- **M1 Architecture**：已建立 **Architecture Baseline**（commit，不打 Tag）。**讨论状态 = Discussion Closed**（设计不再讨论，除 **Fatal Issue** 外一律 `Reject`）；**验证状态 = Frozen (Pending Validation)**。冻结集合：五层架构、Source → Knowledge、Provenance、Approved 流程、Taxonomy、Review Checklist、Gold Standard、Coverage / Fidelity、ADR 铁律（0001–0005）。任何修改必须先回答「不改会失败在哪里？」，否则直接 `Reject`（治理见 [ROADMAP.md](ROADMAP.md)「Architecture Budget / Ownership / Discussion Closed」）。待第一批 Gold Sample 验证通过 → `Architecture Validated` → 才打 Release Tag `v0.2.0-m1`。
- **Execution Phase**：已启动（Project Charter Approved）。**Engineering Baseline v1（Python 3.12+ / uv / FastAPI / Pydantic v2 / pytest / ruff+black / mypy）已冻结**，见 [ENGINEERING.md](ENGINEERING.md)（回答「系统怎么造」，与 Domain Architecture 分离，所有 RFC 必须遵守）。**RFC-0001（Source Module）语言冲突已解除（统一 Python），待 Chief Architect 恢复开发**。当前工作 = **M1.1 第一步：建立 Dataset-0001**（见 [ROADMAP.md](ROADMAP.md) M1.1）。
