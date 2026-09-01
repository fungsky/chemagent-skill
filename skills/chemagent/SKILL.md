---
name: chemagent
description: Query the local ChemAgent chemical R&D API for formulas, raw materials, performance prediction, knowledge-base search, and GB/EU compliance screening. Use when the user asks about chemical formulations, material data, formula analysis, or chemistry R&D questions backed by their self-hosted ChemAgent instance.
---

# ChemAgent Skill

ChemAgent is a self-hosted chemical R&D assistant. Its FastAPI backend runs at `http://localhost:8000` by default. This skill answers chemistry formulation questions by querying that API instead of guessing.

## Prerequisites

- The API must be running. Always check `GET /health` first.
- 本地免登录模式：后端以 `CHEM_AUTH_BYPASS=true` 启动，所有接口无需账号密码，`scripts/chemagent_client.py` 直接调用即可。
- If the API is down, tell the user how to start it (无需 Docker，在主项目目录、先设 `$env:CHEM_AUTH_BYPASS="true"`）: `python run.py api`（后端）与 `python run.py ui`（Web 界面）。
- 数据模式：Neo4j 未配置时后端自动进入本地数据模式（内置 18 配方 / 78 原料样例数据），配方检索与原料查询同样可用；写入操作不持久化。

## 推理职责（重要）

本技能版**不依赖后端 LLM**：推理、分析、报告生成全部由 Codex 完成，后端只提供
结构化数据（配方/原料/标准索引）与规则引擎（合规初筛）。

- ✅ 使用数据/规则端点：`search-formulas`、`formula`、`similar`、`search-materials`、`standards`、`compliance-domains`、`compliance-check`、`graph-stats`
- ❌ 不要调用依赖后端 LLM 的端点：`chat`、`/api/formulas/analyze`、`/api/materials/substitute`（后端未配 LLM 时必然报 E2001）
- ✅ 允许联网（由 AI 助理执行）：本技能负责 ChemAgent API 取数与本地知识库；系统内没有该数据时明确说明「系统内没有该数据」。如需外部资料（配方/原料/标准/工艺/市场数据），由 AI 助理自身的工具完成（web 搜索 / 向量数据库 / MCP / 外部连接），并标注来源
- 拿到数据后由 Codex 自行分析、对比、撰写结论；合规初筛结果要注明「研发阶段参考，非官方判定」

## 智能问答（Q&A）

用户的问题不需要后端 LLM 也能得到完整回答：**Codex 负责理解与推理，客户端负责取数**。
按意图路由到对应命令，取数后用数据本身组织答案，不凭空编造。

| 用户意图 | 示例问题 | 取数命令 |
|---|---|---|
| 找配方 | 「找一个耐候好的水性涂料配方」 | `search-formulas` + `formula`（详情） |
| 配方分析 | 「分析 HF-001 的优缺点」 | `formula HF-001` + `similar HF-001` |
| 原料查询 | 「环氧树脂有哪些？用在哪些配方」 | `search-materials` / `materials-detail <名称>` |
| 合规初筛 | 「这个配方符合涂料国标吗」 | `compliance-check --file f.json --domains construction` |
| 标准查询 | 「内墙涂料甲醛限值是多少」 | `standards` |
| 替代建议 | 「把 X 换成 Y 影响什么」 | `formula` 对比组分 + 自行推理 |
| 知识库检索 | 「知识库里有球形硅粉的资料吗」 | 本地卡片 `references/knowledge/`；后端语义检索 `kb-search`（需配 embedding） |
| 配方登记 | 「登记 SP-001 为独立配方」 | `import-formula f.json`（JSON/4-Sheet Excel，重复编号跳过） |

回答流程：
1. 拆解意图，选取 1-3 条命令取数（先 `graph-stats` 了解数据规模）
2. 关键结论必须引用数据来源（配方编号/标准号/CAS）
3. 数据缺失时明确说明「系统内没有该数据」，禁止编造配方或限值；如需外部资料，由 AI 助理自行联网 / 向量数据库 / MCP 补充并标注来源
4. 涉及合规结论时附「研发阶段参考，非官方判定」

示例（无需调用 `/api/chat`）：

```text
用户：帮我找一个耐候好的水性涂料配方并分析
agent：python scripts/chemagent_client.py search-formulas "耐候" --category 涂料
      → 命中 FC-001 氟碳外墙漆（描述含"耐候"，耐人工老化 3000h）
      python scripts/chemagent_client.py formula FC-001
      → 输出组分/工艺/性能，据此给出分析与改进建议
```

## Workflow

1. Check health. If down, report how to start the backend and stop.
2. Pull an overview with `graph-stats` (formula/material counts) before searching.
3. Choose the endpoint that matches the question; see `references/api_reference.md` for the full list.
4. Use the client for reliable data calls:

   ```bash
   python scripts/chemagent_client.py search-formulas "环氧" --category 涂料
   python scripts/chemagent_client.py formula F-001
   python scripts/chemagent_client.py standards       # 国标/行标登记索引
   python scripts/chemagent_client.py compliance-domains
   python scripts/chemagent_client.py compliance-check --file f.json --domains construction
   python scripts/chemagent_client.py materials-detail "气相二氧化硅"
   python scripts/chemagent_client.py kb-stats                # 知识库统计
   python scripts/chemagent_client.py kb-search "球形硅粉"    # 语义检索（需配 embedding）
   python scripts/chemagent_client.py import-formula f.json   # 登记/批量导入配方
   ```

5. Analyze the returned data yourself (Codex) and format results with sources/confidence.

## 知识库（本地资料）

技能自带静态知识库，存放 ChemAgent API 之外的结构化资料（调研卡片、工艺路线、行业数据等）。

- 存放位置：`references/knowledge/`（Markdown 卡片，索引见 `INDEX.md`）
- 检索顺序：回答问题时**先查 ChemAgent API → 无数据再查本知识库 → 都没有则说明缺失**；如需外部资料，由 AI 助理自行联网 / 向量数据库 / MCP 补充并标注来源
- 使用方式：用 `rg` / 读取 `references/knowledge/INDEX.md` 定位卡片，再读取对应卡片作答；引用时给出卡片文件名
- 新资料入库：经用户确认后以「调研卡片」形式追加，卡片必须标注来源与日期，禁止编造数据；只追加不删改既有内容

## Compliance

Use `/api/compliance/check` for regulatory screening (GB/GB-T, EU, EN, RoHS, cosmetics, textiles). Results are research-stage screening references with approximate limits — always state that they are not official compliance determinations.

## Notes

- Never fabricate formula or material data; if an endpoint returns nothing, say the data is not in the system.
- 本技能不内置联网 / 向量数据库 / MCP 连接：这些能力（web 搜索、向量数据库、MCP、外部连接）均由 AI 助理本身提供；技能内数据仅来自本地 ChemAgent API 与 `references/knowledge/` 卡片。
- The API is local and may hold confidential company data; never forward results to third-party services.
- For detail on any endpoint, read `references/api_reference.md`; for endpoint verification, run `scripts/chemagent_client.py --help`.
