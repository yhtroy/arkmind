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
| 2026-07-27 | 《黑天鹅》 | ✅ | 待评估 | 待填 | 待填 | 第一篇基准样本；笔记来源：历史资产转换（M3 v16）非人工；v2 重建（Editorial Database v2：Content 字段删除致 V1 正文丢失，v2 链路重建，正文入 Page Body，Book/Author 落库）；Page ID 3b1353d2-d441-814e-b109-c97c3e4fb23c |
| 2026-07-27 | 《浪潮之巅》 | ✅ | 待评估 | 待填 | 待填 | 第二篇；笔记来源：PDF 原文提炼（非历史资产）；《思考快与慢》PDF 无文本层改跑本篇；v2 重建（同左）；Page ID 3b1353d2-d441-8181-bbc7-c8518cb45916 |
| 2026-07-27 | 《低智商社会》 | ✅ | 待评估 | 待填 | 待填 | 类型：社会（大前研一）；笔记来源：epub 原文提取 + LLM 两轮提炼（M5.5 生产批次一）；Page ID 3b2353d2-d441-8113-8175-d81de1464c40 |
| 2026-07-27 | 《反直觉询问》 | ✅ | 待评估 | 待填 | 待填 | 类型：心理（莱恩·莱韦斯）；epub + LLM 提炼；Page ID 3b2353d2-d441-811d-b737-fdba664b6bdc |
| 2026-07-27 | 《好好赚钱》 | ✅ | 待评估 | 待填 | 待填 | 类型：商业/理财（简七）；epub + LLM 提炼；Page ID 3b2353d2-d441-816a-8f97-ffafa3ef7b66 |
| 2026-07-27 | 《富可敌国》 | ✅ | 待评估 | 待填 | 待填 | 类型：经济/金融史（塞巴斯蒂安·马拉比）；epub + LLM 提炼；Page ID 3b2353d2-d441-8164-b40a-f7a24f82f48b |
| 2026-07-27 | 《帝国的惆怅》 | ✅ | 待评估 | 待填 | 待填 | 类型：历史（易中天）；epub + LLM 提炼；Page ID 3b2353d2-d441-81af-9a34-cce833874aa5 |
| 2026-07-27 | 《机器人时代》 | ✅ | 待评估 | 待填 | 待填 | 类型：科技（马丁·福特）；epub + LLM 提炼；Page ID 3b2353d2-d441-8146-a48c-e635145cba9b |
| 2026-07-27 | 《简明逻辑学》 | ✅ | 待评估 | 待填 | 待填 | 类型：逻辑/个人成长（普里斯特）；epub + LLM 提炼；M5.5 生产批次一全链路验证篇（模板修正后第一篇）；Page ID 3b2353d2-d441-8154-9510-c78c9c80f0cb |
| 2026-07-27 | 《经济指标简史》 | ✅ | 待评估 | 待填 | 待填 | 类型：经济（扎卡里·卡拉贝尔）；epub + LLM 提炼；首次批量 SSL 瞬时错误，重试成功；Page ID 3b2353d2-d441-816d-9bbd-d793d326fdbc |
| 2026-07-27 | 《金融科技》 | ✅ | 待评估 | 待填 | 待填 | 类型：科技/商业（余丰慧）；epub + LLM 提炼；Page ID 3b2353d2-d441-8100-8fe5-c1e0ab88ab22 |
| 2026-07-27 | 《风格与幸福》 | ✅ | 待评估 | 待填 | 待填 | 类型：个人成长（石琴娥编）；epub + LLM 提炼；Page ID 3b2353d2-d441-81fe-b7b0-e7ffed865735 |

## Coverage Checklist (10 篇选题覆盖)

- [x] 偏商业（管理、战略）——《好好赚钱》《金融科技》
- [x] 偏科技（AI、互联网）——《机器人时代》《金融科技》
- [x] 偏心理学——《反直觉询问》
- [x] 偏历史——《帝国的惆怅》
- [x] 偏经济——《富可敌国》《经济指标简史》
- [x] 偏个人成长——《风格与幸福》《简明逻辑学》

## Backlog（先记录，不改）

> Observations collected during M5.5. No implementation until the validation
> is over and Writer Contract v2 is frozen.

- [x] **BACKLOG-001：Notion Page Body vs Content Property**（来源：M5.5 第一篇《黑天鹅》2026-07-27）
      观察：正文存储在 Content Rich Text 属性，阅读体验一般，无法充分利用 Notion Block 编辑能力。
      结论：2026-07-27 CEO 裁定实施 Editorial Database v2——正文进 Page Body，Content 字段删除，Properties 只保留 Title/Book/Author/Status/Word Count。已实施（commit ef199a3）。2026-07-27 后续修正（commit 9a579c4）：去掉 AI Draft 占位 Heading，正文直接开始，Editor Notes / Review 降为 H2 页脚。
- [ ] asset-full.json（219 条历史产物）content 全部为 "None"，不可用——历史数据问题非 M5 Bug，M5.5 不修（Review ⑥，2026-07-27）
- [ ] **BACKLOG-002：Notion create_page 无网络重试，SSL 瞬时错误需人工重跑**（来源：M5.5 生产批次一，2026-07-27）
      观察：批量跑 9 本 + 抽查 10 本期间，2 次出现 `SSL: UNEXPECTED_EOF_WHILE_READING`（api.notion.com 握手中断），重试即成功，未造成数据问题。
      影响：网络抖动时单本整篇重跑（LLM 重新生成），浪费 token 和时间。
      建议（不实施，等 10 篇后统一评估）：NotionClient HTTP 层加指数退避重试（仅幂等安全操作）。
