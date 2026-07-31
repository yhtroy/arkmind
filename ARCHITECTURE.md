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

- `content` 保存完整 Markdown。
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

字段冻结如下：

| 字段            | 类型          |
| -------------- | ------------ |
| Title          | Title        |
| Book           | Text         |
| Author         | Text         |
| Content        | Rich Text    |
| Status         | Select       |
| Publish Target | Multi Select |
| Created Time   | Date         |
| Updated Time   | Date         |
| Word Count     | Number       |
| Topic Count    | Number       |
| Asset Count    | Number       |

**冻结。** 以后允许新增字段。禁止删除已有字段。

---

## 6. Publish Target

Publish Target 不代表已经发布。它只是"未来计划同步的平台"。

例如：知乎、头条、百家、公众号、Notion Only。

目前 MVP：

```
Notion Only
```

以后扩展：

```
Notion
      │
      ├── Zhihu
      ├── Toutiao
      ├── Xiaohongshu
      └── WeChat
```

Publisher 不需要改 Writer。

---

## 7. Status Workflow

Status：

```
Draft
Review
Published
Archived
```

生命周期：

```
Writer
   ↓
Draft
   ↓
人工 Review
   ↓
Published
   ↓
Archive
```

冻结。

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
