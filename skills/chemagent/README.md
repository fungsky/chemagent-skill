# ChemAgent Skill · 化学研发助理

面向 ChemAgent（自托管化学研发系统）的 Codex/Claude Agent 技能包。技能负责理解与推理，后端只提供结构化数据（配方 / 原料 / 标准索引）与规则引擎（合规初筛），**不依赖后端 LLM**。

## 特性

- 本地免登录调用 ChemAgent API（`CHEM_AUTH_BYPASS=true`）
- 配方检索 / 详情 / 相似、原料查询与详情、国标/行标索引、GB/EU 合规初筛
- 本地静态知识库卡片（`references/knowledge/`），可脱离 embedding 使用
- 可选后端语义知识库（ChromaDB，需配置 embedding）
- 数据缺失时明确说明；联网 / 向量数据库 / MCP 等外部能力由 AI 助理自身提供
- 客户端仅用 Python 标准库，自动 UTF-8 输出，Windows PowerShell 直接可用

## 目录结构

```
chemagent/
├── SKILL.md                     # 技能指令（入口）
├── README.md
├── references/
│   ├── api_reference.md         # API 端点与客户端命令清单
│   └── knowledge/               # 本地知识库卡片（只追加不删改）
│       ├── INDEX.md
│       ├── 球形硅粉.md
│       ├── 溶胶-凝胶法球形二氧化硅微球.md
│       └── 球形硅粉中试工艺.md
└── scripts/
    └── chemagent_client.py      # API 客户端（仅标准库）
```

## 快速开始

1. 启动后端（ChemAgent 主项目目录）：

   ```powershell
   $env:CHEM_AUTH_BYPASS="true"
   python run.py api        # 后端 http://localhost:8000
   python run.py ui         # （可选）Web 界面
   ```

2. 将本目录放入 Agent 技能目录（如 `~/.codex/skills/chemagent`）即可被自动加载。

3. 客户端验证：

   ```bash
   python scripts/chemagent_client.py health
   python scripts/chemagent_client.py graph-stats
   ```

## 客户端用法

```bash
python scripts/chemagent_client.py search-formulas "耐候" --category 涂料
python scripts/chemagent_client.py formula FC-001
python scripts/chemagent_client.py similar FC-001 --top-k 5
python scripts/chemagent_client.py search-materials "硅" --function 填料
python scripts/chemagent_client.py materials-detail "气相二氧化硅"
python scripts/chemagent_client.py standards
python scripts/chemagent_client.py compliance-check --file f.json --domains construction
python scripts/chemagent_client.py kb-stats                     # 知识库统计
python scripts/chemagent_client.py kb-search "球形硅粉 应用"    # 语义检索（需配置 embedding）
python scripts/chemagent_client.py kb-upload doc.md             # 上传文档（需配置 embedding）
python scripts/chemagent_client.py import-formula f.json        # 登记/批量导入配方
```

- 完整命令：`python scripts/chemagent_client.py --help`
- 自定义地址：`--api-base http://host:port` 或环境变量 `CHEMAGENT_API_BASE`

## 数据模式

- 后端未配置 Neo4j 时进入本地数据模式（内置样例配方/原料），配方检索与原料查询可用；写入（登记配方、上传文档）的持久性取决于后端存储配置，重启后可能回退，请以实际部署为准。
- 合规初筛基于内置规则库（GB/GB-T、EU/EN、RoHS 等），限值为近似换算，属于**研发阶段参考，非官方合规判定**。

## 知识库

- **本地卡片**（默认）：`references/knowledge/` 下的 Markdown 调研卡片，由技能直接读取，无需 embedding。
- **后端语义库**（可选）：配置 embedding 后，可用 `kb-upload` 上传 PDF/DOCX/TXT/XLSX，用 `kb-search` 语义检索。
- 检索顺序：先 ChemAgent API → 本地卡片 → 缺失时由 AI 助理联网/向量库/MCP 补充并标注来源。

## License

MIT © 2026 ChemAgent Contributors（仓库根目录 `LICENSE`）。