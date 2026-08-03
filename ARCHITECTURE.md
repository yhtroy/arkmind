# ArkMind Product Architecture V2.0

## Notion-Centric Publishing Pipeline (Frozen)

- **Status:** APPROVED
- **Owner:** Chief Architect
- **Date:** 2026-07-31

> 本文件由 Chief Architect 冻结批准。V2.0 取代先前的架构版本（V1 Renderer 链路与更早的五层模型）。

---

## 1. Purpose

ArkMind 的目标不是生成 Markdown 文件。

ArkMind 的目标是持续沉淀一个可运营、可检索、可复用、可持续发布的知识库。

因此，原先的：

```
Markdown
    ↓
人为中间产物
```

调整为：

```
Book
    ↓
Source
    ↓
Asset
    ↓
Topic
    ↓
Writer（唯一 AI）
    ↓
Article
    ↓
Publisher(Notion)
```

- Notion 成为唯一正式发布介质。
- Markdown 不再作为产品输出。

---

## 2. Frozen Pipeline

```
Book
    │
    ▼
Source
    │
    ▼
Asset
    │
    ▼
Topic
    │
    ▼
Writer (LLM)
    │
    ▼
Article
    │
    ▼
Publisher
    │
    ▼
Notion Database
```

**Frozen Rules：**

- Source 永远负责一本书
- Asset 永远负责知识提炼
- Topic 永远负责聚合
- Writer 永远负责文章生成
- Publisher 永远负责输出

任何模块不得跨层。

---

## 3. Writer Output Contract

Writer 不再输出 `article.md`。

Writer 输出 `Article`。

数据模型：

```text
Article

article_id
title
content
created_at
metadata
```

- 正文（`content`）保存于 Notion Page Body（Blocks），不进入任何 Property。
- Writer 不负责平台。
- Writer 不负责数据库。
- Writer 不负责发布。

---

## 4. Publisher Responsibility

Publisher 是唯一输出层。

职责只有：

```
Article
      ↓
Publish
      ↓
Notion
```

禁止：

- AI
- 改写
- 润色
- 摘要
- SEO
- 标签生成
- 标题优化

Publisher 永远只是 Adapter。

---

## 5. Notion Database

数据库：`Articles`

字段冻结如下（Editorial Database v2，2026-07-27）：

| 字段        | 类型       | 说明                         |
| ---------- | --------- | --------------------------- |
| Title      | Title     | 文章标题                      |
| Book       | Rich Text | 来源书籍（Writer 透传）        |
| Author     | Rich Text | 作者（Writer 透传）           |
| Status     | Select    | Draft / Editing / Done      |
| Word Count | Number    | 正文近似字数（去空白）          |

**Properties 只保存管理元数据。正文不进入 Property。**

正文写入 Page Body（Blocks）。Page 创建后固定生成如下结构：

```text
（AI 生成正文，Markdown 转换为 Blocks；第一个 H1 即文章标题）

---

## Editor Notes

---

## Review
```

正文直接开始，不使用占位 Heading（文章标题就是真正的大标题）。

冻结。以后允许新增字段。禁止删除已有字段。

---

## 6. Publishing（人工）

发布完全由人工完成：编辑完成后，手动将正文分发到各平台（知乎、头条、公众号等）。

数据库不保存平台/发布字段（Platform / Publish Record 于 2026-07-27 移除：当前无人填写）。

---

## 7. Status Workflow

Status：

```
Draft
Editing
Done
```

生命周期：

```
Writer
   ↓
Draft
   ↓
人工编辑
   ↓
Editing
   ↓
Done
   ↓
人工发布（数据库不记录）
```

冻结。以后真开始运营，再增加状态。

---

## 8. Notion as Single Source of Truth

生成后的文章，唯一正式版本：

```
Notion
```

Git 不保存 `article.md`。

Git 保存：代码、Prompt、RFC、Architecture。

内容资产全部沉淀在 Notion。

---

## 9. Future Extension

未来：

```
Article
   ↓
Publisher
   ↓
Notion
   ↓
Platform Publisher
   ↓
知乎 → 头条 → 公众号
```

新增平台：只新增 Publisher Adapter。Writer 完全不用修改。

---

## 10. Module Boundary

- Writer：`Topic → Article`
- Publisher：`Article → Notion`
- Notion：`Storage`
- 平台：`Distribution`

四层永久隔离。

---

## 11. Project Structure

```
arkmind/
    writer/
    publisher/
    notion/
    runtime/
    asset/
    topic/
```

- Publisher 为新模块。
- Notion Client 属于 Publisher 内部。
- Writer 永不依赖 Notion。

---

## 12. Milestone

| 里程碑 | 范围                    | 状态   |
| ----- | ---------------------- | ----- |
| M1    | Book → Source          | ✅    |
| M2    | Source → Asset         | ✅    |
| M3    | Asset → Topic          | ✅    |
| M4    | Topic → Writer         | ✅    |
| M5    | Writer → Notion Publisher | NEXT |

---

## 13. Frozen Decision

最终产品架构冻结：

```
Book
    ↓
Source
    ↓
Asset
    ↓
Topic
    ↓
Writer (唯一 AI)
    ↓
Publisher
    ↓
Notion Database
```

- 所有文章首先进入 Notion。
- Markdown 文件退出产品架构，仅可作为调试产物。
- Notion 成为 ArkMind 唯一内容中心（Single Source of Truth）。
