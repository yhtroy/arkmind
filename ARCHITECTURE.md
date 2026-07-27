# ARCHITECTURE

系统只有五层。不讨论代码，不讨论框架。

```
Source      →  原始输入（今天：得到 PDF）
Knowledge   →  结构化的原始事实（系统的资产，唯一不可丢的东西）
Reasoning   →  在 Knowledge 之上做推理（可以随时换模型、换方法重跑）
Content     →  输出（今天：文章草稿；经作者 Approve 后发布）
Feedback    →  作者与读者的反馈，回流修正 Knowledge 与 Reasoning
```

## 各层职责与边界

### 1. Source

- 职责：接收原始输入，保留原件，解析出可用文本。
- 边界：只做「拿进来、拆开」，不做任何理解和总结。
- 今天的实现范围：PDF（PyMuPDF + pdfplumber，必要时 PaddleOCR）。

### 2. Knowledge

- 职责：保存**原始事实**及其出处（详见 [DATA_MODEL.md](DATA_MODEL.md)）。
- 边界：**只存事实，不存 AI 结论。** AI 的总结、观点属于 Reasoning 层的产物，永不进入本层。
- **铁律：Knowledge 层禁止调用 LLM。** 本层只允许三种操作：Extraction（提取）、Normalization（规范化）、Validation（校验）。不推理、不总结、不扩写、不生成。一旦违反，Knowledge 被污染，模型升级时全部作废。
- 任何数据写入本层前必须经作者 Approve（见 ADR-0004）。
- 这是整个系统唯一需要长期守护的层。

### 3. Reasoning

- 职责：基于 Knowledge 做推理、总结、生成观点。**所有 AI 理解都住在这一层**，它们是派生数据：可整体删除、可用新模型重建（建模在 M2 进行，不进 DATA_MODEL.md）。
- 边界：所有产物必须标注「由哪些 Knowledge、哪个模型、什么时候推理出来的」，并且**可以随时重新推理**。
- 模型接入统一走 LLM Adapter（LiteLLM）。模型是插件，不是核心（见 ADR-0001）。

### 4. Content

- 职责：把 Reasoning 的产物组织成面向渠道的内容（知乎、小红书……）。
- 边界：任何内容进入「已发布 / 已入库」状态前，必须经过作者 Approve。

### 5. Feedback

- 职责：收集作者修改意见与外部反馈，作为下一轮 Reasoning 的输入。
- M3 之前只留接口位置，不实现（YAGNI，见 ADR-0002）。

## 依赖方向

只允许自上而下单向依赖：

```
Source → Knowledge → Reasoning → Content → Feedback
```

Feedback 回流是数据回流，不是代码依赖。任何反向的代码依赖都是架构腐化信号。
