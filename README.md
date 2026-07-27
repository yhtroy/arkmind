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

## 文档（先读这四份，再谈代码）

| 文档 | 回答的问题 |
| --- | --- |
| [VISION.md](VISION.md) | 这个产品五年以后是什么 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 系统有哪五层，边界在哪 |
| [DATA_MODEL.md](DATA_MODEL.md) | Knowledge 长什么样（最重要） |
| [ROADMAP.md](ROADMAP.md) | 三个 Milestone，不多不少 |

## 四条铁律（ADR）

1. [ADR-0001 永远不要为了 AI 而设计系统](ADR/ADR-0001-never-design-for-ai.md) — 模型只是插件
2. [ADR-0002 不要过早设计（YAGNI）](ADR/ADR-0002-yagni.md) — 需要的时候再长出来
3. [ADR-0003 知识必须可以重新理解，而不是重新生成](ADR/ADR-0003-reinterpret-not-regenerate.md) — 只存事实，不存 AI 结论
4. [ADR-0004 Human Override First](ADR/ADR-0004-human-override-first.md) — AI 不能写 Knowledge，必须人 Approve
5. [ADR-0005 数据哲学：三状态](ADR/ADR-0005-data-philosophy-three-states.md) — Observed → Approved → Derived，无 candidate/draft

## 技术选型（每一项都有引入理由，不是因为它火）

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

## 目录

```
arkmind/
├── ADR/              # 架构决策记录
├── docs/canon/       # 知识语法 Canon（rules / examples / taxonomy / provenance）
├── VISION.md
├── ARCHITECTURE.md
├── DATA_MODEL.md
├── ROADMAP.md
└── README.md
```

代码目录（arkmind-core、arkmind-pipeline、arkmind-api……）在 M1 动工时按需长出来——遵守 ADR-0002，不预建空目录。

## 当前状态

M0：Review 意见已全部落实，等待 Architecture Freeze 宣布后 commit 并打 tag `v0.1.0-m0`。下一步见 [ROADMAP.md](ROADMAP.md) 的 M1。
