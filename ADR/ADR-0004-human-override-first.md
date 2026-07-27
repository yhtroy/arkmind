# ADR-0004：Human Override First

- 状态：Accepted
- 日期：2026-07-27

## 决策

任何时候，AI 都不能直接写入或修改 Knowledge。进入 Knowledge 的每一条数据，必须经过 Human Approve。

```
OCR / 解析 / 提取
        ↓
Knowledge Candidate（候选，status = candidate）
        ↓
Human Approve
        ↓
Knowledge（资产，status = approved）
```

以后 Reasoning 层的产出走向发布，同样适用：AI → Draft → 作者 Approve → 发布。

## 背景

这是作者的第二大脑，不是 GPT 的大脑。真正形成 IP 的不是 AI，而是作者的判断、价值观和取舍——这个环节自动化的那一天，系统就退化成了内容生成器。

## 后果

- AI（含任何 Pipeline）对 knowledge 表只有"提交候选"的权限，没有"转正"的权限。
- `candidate → approved` 的状态迁移只能由人触发，代码上不允许出现任何自动转正路径。
- Approve 界面/命令必须展示出处（原文 fragment），让人基于原文做判断。
- 此规则不设开关、不设"批量自动通过"选项。效率不足时优化候选质量，不降低门槛。

## 违规判定

任何绕过 Human Approve 写入 approved 状态的代码路径，直接打回。
