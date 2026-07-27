# ENGINEERING.md — ArkMind Engineering Baseline v1

> ADR / Canon / ROADMAP 回答「**系统应该是什么**」（Domain Architecture，与语言无关）；
> 本文件回答「**系统应该怎么造**」（Engineering Baseline）。两个层次必须分开。
>
> 本文件是**工程基线，不是架构**。所有 RFC / Task 必须遵守它。Qoder 不再对语言、框架做技术决策——本文件已规定。
> 冻结为 **v1**；修改须由 Architecture Owner 裁决，遵守 [ROADMAP.md](ROADMAP.md)「Architecture Budget / Ownership / Discussion Closed」。

## 一、语言与运行时

- **语言：Python 3.12+**，统一单语言，不引入第二语言。
- 理由：ArkMind 是知识处理项目（PDF / OCR / LLM / Embedding / NLP），核心生态（PyMuPDF、pdfplumber、PaddleOCR、spaCy、sentence-transformers、LiteLLM、FastAPI）几乎都是 Python 一等公民。用 Java 会不可避免地滑向 Polyglot Hell（多语言地狱）。

## 二、包管理与环境

- **包管理：uv**（不是 pip，不是 poetry）。
- **虚拟环境：`.venv`**（统一）。
- 依赖声明与锁定：`pyproject.toml` + `uv.lock`。

## 三、项目目录结构

```
src/        # 源码（模块化，按需生长，不预建空目录）
tests/      # pytest 测试
docs/       # 文档（含 canon/）
sources/    # 数据集登记（Dataset-000x/source.yaml）
```

## 四、技术栈（冻结）

| 领域 | 选型 | 引入阶段 |
| --- | --- | --- |
| 语言 | Python 3.12+ | 现在 |
| API | FastAPI | 需要时 |
| 数据校验 | Pydantic v2 | 需要时 |
| 数据库 | 无（M1）→ PostgreSQL 17 | M2 |
| ORM | SQLAlchemy 2.x | M2 |
| 迁移 | Alembic | M2 |
| 测试 | pytest | 现在 |
| 格式化 | ruff + black | 现在 |
| 类型检查 | mypy | 现在 |
| YAML | PyYAML | 现在 |
| PDF | PyMuPDF | 需要时 |
| OCR | PaddleOCR | 以后 |
| LLM 接入 | LiteLLM | 以后 |
| Embedding | 未定（今天禁止讨论） | — |

## 五、编码规范

- 格式化：**ruff + black**，提交前必须通过。
- 类型：**mypy** 通过；公共函数与接口标注类型。
- 命名：模块/文件 `snake_case`，类 `PascalCase`，函数/变量 `snake_case`。
- **禁止占位式代码**：不写 `TODO` / `Future` / 「以后支持」/「先留接口」/「先写抽象」。需要时再长（YAGNI，ADR-0002）。
- Knowledge 层禁止调用 LLM（既有硬约束）。

## 六、依赖规范

- 只用 `uv` 增删依赖，并锁定进 `uv.lock`。
- 每引入一个依赖必须有明确用途（pay rent）；不因为「它火」而引入。
- 不预装「以后可能用」的库，不保留未使用依赖。

## 七、测试规范

- 框架 **pytest**；测试放 `tests/`，文件命名 `test_*.py`。
- 核心路径必须有单元测试（例如 `SourceRegistry`、Checksum）。
- 不为尚不存在的功能写测试。

## 八、Git 规范

- **Conventional Commits**：`type(scope): subject`，例 `feat(source): implement source registration`。
- 一个 PR 对应一个 Task / RFC 项，标题形如 `PR-0001`。
- **Tag 只属于 Architecture Freeze**（见 ROADMAP「两种 Commit」）；Working Draft 随时 commit、绝不打 Tag。
