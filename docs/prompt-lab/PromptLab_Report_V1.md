# PromptLab Report V1

> 每本书一份。用于回答一个问题：Prompt 到底是在变好，还是只是碰巧。
> 本报告数据由工程执行产出，质量裁定由 CEO + Architect 完成。

---

## Prompt Version

| Asset 类型 | 版本 | 状态 |
|---|---|---|
| Concept | V1.6 | Frozen |
| Definition | V1.1 | Frozen |
| Quote | V1.1 | Frozen |

冻结提交：main `ec3b80d`（Prompt Lab 第一阶段结束）。

### 冻结的 Asset Contract 三原则
1. Asset 是最小知识单元（一条知识，不是一段回答）。
2. 一个 Asset 只表达一个思想（禁止 A+B+C 打包）。
3. 无法满足标准宁可输出 `None`，不硬抽。

---

## Validation Book

- 书目：《黑天鹅》（干货版）
- source_id：`black-swan-cn`
- Provider：OpenAI 兼容端点（DeepSeek）
- Model：`deepseek-v4-pro`
- 环境：`ARKMIND_LLM_BASE_URL=https://api.deepseek.com/v1`

---

## Knowledge Count

- Knowledge：**73**
- 输入文件：`sources/black-swan-cn/output/knowledge.json`（181195 bytes，U+FFFD=0）
- Knowledge 层已冻结验证为健康输入（TASK-VALIDATION-001）。

---

## Asset Count

调用：73 × 3 = **219 次 LLM 调用**，产出 **219 Asset**。

| 类型 | 总数 | None | 有效 | None 率 |
|---|---|---|---|---|
| CONCEPT | 73 | 5 | 68 | 7% |
| DEFINITION | 73 | 28 | 45 | 38% |
| QUOTE | 73 | 5 | 68 | 7% |
| **合计** | **219** | 38 | 181 | 17% |

**Output Contract 违规（一个 Asset 装多条 / 出现 `---`）= 0 / 219。** 粒度约束在全书规模稳住。

---

## Gold Set Hit

对照 Gold Set v1（见 `docs/prompt-lab/gold-set.md`）：

| 类型 | 命中 | 明细 |
|---|---|---|
| Concept | **5 / 5** | 平均斯坦、极端斯坦、游戏谬误、认知自大、未来盲性 全部命中 |
| Definition | **3 / 3** | 黑天鹅、叙述谬误、沉默的证据 全部命中 |
| Quote | **1 / 3** | 命中「不对称」；未命中「火鸡归纳法」「你就是黑天鹅」 |

Concept / Definition 命中率 100%，证明 Prompt 已稳定理解类型定义，非偶然。

---

## Duplicate Rate

68 条有效 Concept → **47 个不同名称**，重复率约 **31%**（跨片段重复，Asset 层按契约不去重）。

高频 Concept（一本书真正围绕的思想）：

| 次数 | Concept |
|---|---|
| 8 | 极端斯坦 |
| 6 | 叙述谬误 |
| 4 | 沉默的证据 |
| 3 | 游戏谬误 |
| 2 | 黑天鹅事件 / 黑天鹅现象 / 分形随机性 |

完整排名见本地 `sources/black-swan-cn/output/concept-ranking.txt`。

**归属**：重复不是 Prompt 问题，属于未来 Ranking / Merge / Deduplicate（M2.2+）职责。

---

## Noise Cases

1. **英文概念名**：`极端斯坦` 等本应中文，但出现 `Black Swan`×1、`Redundancy`×2、`系统2（System 2）`、`柏拉图化（Platonification）` 等英文/混排命名（模型偶发语言不一致）。
2. **同一思想的近义命名分裂**：`黑天鹅事件` / `黑天鹅现象` / `黑天鹅问题` / `正面黑天鹅` 等被视为不同 Concept，加剧表面重复。
3. **概念名是否作者原生术语存疑**：如 `认知斯坦` / `假想的理解` / `简化谬误` 等需人工判定是原生术语还是模型改写。

以上为如实呈现，是否算噪声由产品评审裁定。

---

## Miss Cases

- **Quote 漏检**：Gold 的「火鸡归纳法」「你就是黑天鹅」未落在任何有效 Quote。
- **两种可能未区分**：
  1. Knowledge 切分把经典句拆散 / 未落入同一片段；
  2. Quote V1.1 高门槛把它们判为不够格。
- **证据不足以归因 Prompt**。定位方法：抽查 73 条 knowledge 中「火鸡」相关片段是否存在——存在则属 Prompt 门槛，不存在则属 Knowledge 切分。
- 68 条 Quote 全文见本地 `sources/black-swan-cn/output/quote-list.txt`（供人工 Review）。

---

## Decision

- Concept V1.6 / Definition V1.1：命中率与格式均达标，**不再微调**。
- Quote V1.1：命中 1/3，但**暂不调 Prompt** —— Quote 受「Knowledge 切分 + Prompt」双变量影响，当前无证据指向 Prompt。
- 重复率：交由 M2.2 的去重/排序策略处理，非 Prompt 层。
- 下一阶段进入**数据分析 + 人工评审**，而非继续 Prompt 微调。

---

## Freeze

**Prompt Lab 第一阶段冻结。** 除非后续多本书验证暴露系统性问题，否则三个 Prompt 版本不再改动。

本次《黑天鹅》全量验证结果（`asset-full.json` 219 条）作为 Prompt 的**基准测试集**保留。

---

## Artifacts（本地，未入库 / gitignore）

| 文件 | 说明 |
|---|---|
| `sources/black-swan-cn/output/asset-full.json` | 219 条全量资产（基准测试集） |
| `sources/black-swan-cn/output/concept-ranking.txt` | Concept 完整排名 |
| `sources/black-swan-cn/output/quote-list.txt` | 68 条 Quote 全文（人工评审用） |
| `sources/black-swan-cn/output/definition-terms.txt` | 45 条 Definition 术语列表 |
