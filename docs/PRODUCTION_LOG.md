# ArkMind Production Log (M5.5)

> Purpose: **accumulate facts, not analysis.** Each row is one production run.
> After ≥10 articles this log becomes the primary design input for
> **Writer Contract v2** — fields, gaps and pain points are read from real
> production data, not from imagination.
>
> Discipline (M5.5): **no new features except bug fixes.** Only crashes, data
> errors, cannot-run and production-blocking issues get fixed. Everything else
> (prompt quality, fluency, titles, extra Notion fields, ...) goes to the
> Backlog below and stays untouched until the validation is over.
>
> Source discipline: **transcript.md is never edited** (no deletion, polish or
> re-layout — the source stays traceable). Only notes.md may be edited.

## Log

| 日期 | 书名 | 成功入 Notion | 需人工大改 | 人工修改时间 | 是否发布 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-07-27 | 《黑天鹅》 | ✅ | 待评估 | 待填 | 待填 | 第一篇基准样本；笔记来源：历史资产转换（M3 v16）非人工；Page ID 3b1353d2-d441-817b-89b1-c3be4bf37ba1 |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |

## Coverage Checklist (10 篇选题覆盖)

- [ ] 偏商业（管理、战略）
- [ ] 偏科技（AI、互联网）
- [ ] 偏心理学
- [ ] 偏历史
- [ ] 偏经济
- [ ] 偏个人成长

## Backlog（先记录，不改）

> Observations collected during M5.5. No implementation until the validation
> is over and Writer Contract v2 is frozen.

- [ ] **BACKLOG-001：Notion Page Body vs Content Property**（来源：M5.5 第一篇《黑天鹅》2026-07-27）
      观察：正文存储在 Content Rich Text 属性，阅读体验一般，无法充分利用 Notion Block 编辑能力。
      当前决定：保持冻结设计，继续收集 10 篇真实使用反馈。
      进入：Writer Contract v2 候选。预判（CEO）：若多篇后编辑体验仍差，v2 第一条 = 正文进 Page Body，Properties 只保存元数据。
- [ ] asset-full.json（219 条历史产物）content 全部为 "None"，不可用——历史数据问题非 M5 Bug，M5.5 不修（Review ⑥，2026-07-27）
