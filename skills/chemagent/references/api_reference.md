# ChemAgent API 参考

默认地址 `http://localhost:8000`，可用 `--api-base` / `CHEMAGENT_API_BASE` 覆盖。
技能版默认**本地免登录**（后端以 `CHEM_AUTH_BYPASS=true` 启动），无需 `Authorization` 头。
若后端未开启免登录，则除「公开」端点外均需 `Authorization: Bearer <JWT>`。

## 公开端点

| 端点 | 方法 | 说明 |
|---|---|---|
| `/health` | GET | 服务状态与知识图谱/LLM 配置概览 |
| `/api/auth/login` | POST | （认证模式下）登录，body `{"username","password"}`，返回 `access_token` |
| `/api/compliance/domains` | GET | 支持的法规领域列表 |
| `/api/compliance/standards` | GET | 国标/行标登记索引（GB/GB-T、QB/T 等） |

## 配方

| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/formulas?keyword=&category=&materials=&limit=` | GET | 多维检索配方（返回相似度排序） |
| `/api/formulas/{code}` | GET | 配方详情（组分、工艺、性能） |
| `/api/formulas/{code}/similar?top_k=` | GET | 基于共同原料的相似配方 |
| `/api/formulas/analyze` | POST | AI 五维度分析配方 |
| `/api/formulas/recommend` | POST | 需求+目标性能 → 推荐方案 |
| `/api/formulas/import` | POST | Excel(4-Sheet)/JSON 批量导入 |
| `/api/formulas/export?条件` | GET | 按条件导出 |
| `/api/formula-versions/{code}` | GET | 配方版本历史 |
| `/api/formula-versions/{code}/diff?v1=&v2=` | GET | 版本差异对比 |

## 原料

| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/materials?keyword=&function=&limit=` | GET | 原料检索（CAS、供应商） |
| `/api/materials/{name}/detail` | GET | 原料详情与关联配方 |
| `/api/materials/{name}/stats` | GET | 使用统计（哪些配方、平均用量） |
| `/api/materials/substitute` | POST | AI 替代建议（性能影响+成本） |

## 知识库 / 问答 / 预测

| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/kb/search?query=` | GET | 语义检索知识库文档 |
| `/api/chat` | POST | body `{"message","use_agent":bool,"history"}`，agent 模式走 ReAct |
| `/api/predict` | POST | 性能预测（硬度/光泽度等），附带置信度 |
| `/api/predict/train` | POST | 用历史配方训练专属模型 |
| `/api/graph/stats` | GET | 知识图谱统计（配方/原料/关系数） |

## 合规

| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/compliance/check` | POST | body `{"formula":{...},"domains":["cosmetics",...]}`，返回违规清单 |

客户端子命令：`python scripts/chemagent_client.py compliance-check --file f.json --domains construction,cosmetics`；
不带参数时使用内置示例配方（水性内墙涂料）快速演示。

领域代码：`food_contact` / `toys` / `automotive` / `construction` / `electronics` / `medical` / `cosmetics` / `textile`。

> 合规结果基于内置规则库（EU/EN/ISO + GB/GB-T + 化妆品安全技术规范 2015），
> 限值以质量占比近似换算，属于研发阶段初筛，非官方合规判定。


## 知识库（KB）

后端基于 ChromaDB 的本地向量库；**入库与检索都需要配置 embedding**（未配置时入库会失败，检索空库返回空数组）。

| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/kb/upload` | POST(multipart) | 上传文档：PDF / DOCX / TXT / XLSX，自动分块向量化 |
| `/api/kb/search` | POST | body `{"query","top_k"}`，语义检索 |
| `/api/kb/documents` | GET | 文档列表 |
| `/api/kb/documents/{doc_id}` | DELETE | 删除文档 |
| `/api/kb/documents/{doc_id}/summary` | POST | AI 摘要（需 LLM） |
| `/api/kb/stats` | GET | 文档/片段统计 |
| `/api/kb/url` | POST | 从 URL 抓取入库（由 AI 助理按需执行） |

## 客户端命令清单

`python scripts/chemagent_client.py <命令> [参数]`，完整列表见 `--help`：

- 数据：`health` `graph-stats` `search-formulas` `formula` `similar` `search-materials` `materials-detail` `materials-stats`
- 合规/标准：`standards` `compliance-domains` `compliance-check`
- 知识库：`kb-stats` `kb-documents` `kb-search` `kb-upload`
- 登记/导入：`import-formula`
- 后端 LLM 端点（未配 LLM 时不可用）：`chat`