# Migration Policy

> 团队开发规范（CEO 裁定，2026-07-27）。

## 原则

任何数据库 Schema 修改，必须按以下顺序执行，不可跳过、不可合并：

```
Backup
   ↓
Migration
   ↓
Validation
   ↓
Cleanup
```

1. **Backup** — 迁移前先备份受影响数据（例如：删除 Notion 属性前，先导出该属性下全部内容并留档）。
2. **Migration** — 执行 Schema 修改。
3. **Validation** — 验证迁移结果：数据完整、无丢失、结构与预期一致。
4. **Cleanup** — 确认无误后清理临时产物，并在 PRODUCTION_LOG 记录迁移。

## 背景

2026-07-27 删除 Notion Content 属性时，两篇历史文章正文随字段删除永久丢失（无备份）。
本规范为防止同类事件而设；适用于所有 Schema 修改，删除字段时尤其必须执行 Backup。
