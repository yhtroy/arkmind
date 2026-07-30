# Benchmarks

Prompt / Knowledge / LLM 的**质量基准（QA）**。不是产品，不是 Topic Builder。
目的只有一个：

> 每改一次 Prompt，跑同一套固定输入，量化它到底是**变好**还是只是**碰巧通过**。

---

## 版权边界（硬规则）

书正文与原文摘录**永不提交进 Git**。

- 提交进仓库的：`manifest.json`（规格 + 期望指标 + 输入文件 sha256）、`report.md`/`gold-set.md` 引用（正文在 `docs/prompt-lab/`）。
- **不提交**：`knowledge.json`（书正文）、`asset*.json`（含原文 Quote 与概念描述）。这两类文件放**私有存储**。
- `.gitignore` 已加护栏：即使把这些文件放进 `benchmarks/` 本地目录，也不会被误提交。

`manifest.json` 用 sha256 锁定私有数据文件的指纹——跑基准时可校验用的是不是同一份输入，从而保证可复现。

---

## 目录结构

```
benchmarks/
  prompt-lab/
    black-swan/
      manifest.json        # 可复现规格 + 期望指标 + 私有数据 sha256（committed）
      # knowledge.json      → 私有存储，不入库
      # asset-full.json     → 私有存储，不入库
```

判定 oracle 与人类报告是单一真源，位于：
- Gold Set：`docs/prompt-lab/gold-set.md`
- 评审报告：`docs/prompt-lab/PromptLab_Report_V1.md`

---

## 如何复现一次基准

1. 从私有存储取回 `knowledge.json`，校验 sha256 与 `manifest.json` 一致。
2. 用 `manifest.json` 记录的 provider / model / 冻结 Prompt 版本跑 Asset Factory。
3. 与 `expected_metrics` 对比：Asset 数、None 分布、Output Contract 违规、Gold Set 命中、重复率。
4. 指标偏离即说明 Prompt / 模型 / 输入其一发生了变化。

---

## 跨书结果表

| Book | Concept | Definition | Quote | 违规 | 备注 |
| ---- | ------- | ---------- | ----- | ---- | ---- |
| 黑天鹅 | 5/5 | 3/3 | 1/3 | 0/219 | Prompt Lab Phase 1 基准（冻结 Concept V1.6 / Definition V1.1 / Quote V1.1） |

后续每验证一本书，新增一行。
