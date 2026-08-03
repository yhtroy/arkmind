# ArkMind Content Pipeline

> Status: FROZEN — M5 Final Sign-off (Architect Approved, 2026-07-27).
> Read this first: it defines ArkMind's product boundary.

## Product Positioning

**Knowledge → Content Pipeline** (the earlier "Personal Knowledge OS" framing no
longer reflects the product).

## Frozen Pipeline

```
Source
    ↓
Knowledge
    ↓
Writer
    ↓
Notion
    ↓
Human Review
    ↓
Publishing
```

Automation ends at Notion. Everything after Notion is manual.

## Responsibilities

| Step | Owner | Responsibility |
|---|---|---|
| **Source** | Extractor | Ingest raw material (books, PDFs); register provenance (Source Registry, `sources/<id>/source.yaml`). |
| **Knowledge** | Extractor / Normalizer | Extract, normalize and deduplicate knowledge from sources. |
| **Writer** | Writer (sole AI layer) | Generate content from Topics + Assets; store it directly in Notion (`create_page`), returning the page id. No Markdown file is produced. |
| **Notion** | NotionClient (`arkmind/notion`) | Product database — the System of Record. Not an export target. |
| **Human Review** | Human | Edit and curate pages in Notion. |
| **Publishing** | Human | Manually distribute to platforms (Toutiao, WeChat, Xiaohongshu, Zhihu, ...). |

## Principles

1. **Notion is the product database, not an export target.**
2. **Generate → Store**: all automation ends at Notion; there is no
   Generate → Publish and no Generate → Export.
3. Markdown is not a business object — it exists only as a Writer-internal
   implementation detail.
4. No automated publishing: code must never contain Publisher / Publish /
   Publishing semantics; distribution is manual by design.
5. The Writer is the only AI layer in the pipeline.

## Current Implementation State

- Source Registry: landed (`arkmind/source`).
- Knowledge: module skeleton landed (`arkmind/knowledge`); the Writer input is
  still **Topic + Asset** (Knowledge-driven Writer input is a later milestone).
- Writer → Notion direct store: landed (`arkmind/notion`, `create_page` returns
  page id; CLI prints `Created Notion Page` / `Page ID`).
- Notion Articles database (Editorial Database v2, 2026-07-27): management
  properties populated by the Writer — Title / Book / Author / Status (Draft) /
  Word Count; the body is written to the **Page Body** (fixed template `AI Draft`
  / `Editor Notes` / `Review`, Markdown converted to blocks). Content is never
  stored in a property.

## Milestones

- **M5 — Content Pipeline: CLOSED** (Publisher removed, Markdown output
  removed, System of Record = Notion).
- **M5.5 — Real Production Validation: NEXT** — run ≥10 real articles
  ("每天听本书") end-to-end, edit in Notion, publish manually; the collected
  production data then drives **Writer Contract v2**.
