# ChemAgent Skill · 化学研发助理技能包

🌐 [English](README.en.md) | **中文**

> 面向自托管 ChemAgent 化学研发系统的 Agent 技能包 —— **Agent 负责理解与推理，后端负责数据与规则**，不依赖后端 LLM，可离线、免登录、开箱即用。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Client](https://img.shields.io/badge/Client-stdlib-green)

## 这是什么

ChemAgent Skill 把"化学研发问答"沉淀为一个可复用的 Agent 技能：配方检索、原料查询、国标/行标索引、GB/EU 合规初筛、本地知识库、配方登记导入，全部通过一个仅用 Python 标准库的客户端脚本完成。

设计原则：

- **推理在 Agent**：分析、对比、报告撰写由 Codex / Claude 等 AI 助理完成，后端只返回结构化数据。
- **数据在本地**：数据来自本地 ChemAgent API 与 `references/knowledge/` 静态知识库卡片，不依赖外部服务。
- **能力可扩展**：联网搜索、向量数据库、MCP 等外部能力由 AI 助理自身提供，技能只负责化学数据部分。
- **数据缺失即明说**：系统内没有的数据明确告知，绝不编造配方、原料或限值。

## 功能特性

- 配方检索 / 详情 / 相似配方对比
- 原料检索与详情（CAS、功能、供应商等）
- 国标 / 行标登记索引查询
- GB / EU / RoHS 等合规初筛（规则引擎，研发阶段参考）
- 本地静态知识库（Markdown 调研卡片，无需 embedding）
- 可选后端语义知识库（ChromaDB，需配置 embedding）
- 配方登记与批量导入（JSON / 4-Sheet Excel，重复编号自动跳过）
- Windows 中文兼容（客户端内置 UTF-8 输出，PowerShell 直接可用）

## 目录结构

```
chemagent-skill/
├── .codex-plugin/                # Codex 插件清单
├── skills/
│   └── chemagent/                # 技能本体（放入 ~/.codex/skills/ 即可加载）
│       ├── SKILL.md              # 技能指令（入口）
│       ├── README.md             # 技能安装与使用说明
│       ├── references/
│       │   ├── api_reference.md  # API 端点与客户端命令清单
│       │   └── knowledge/        # 本地知识库卡片
│       │       ├── INDEX.md
│       │       ├── 球形硅粉.md
│       │       ├── 溶胶-凝胶法球形二氧化硅微球.md
│       │       └── 球形硅粉中试工艺.md
│       └── scripts/
│           └── chemagent_client.py  # API 客户端（仅标准库）
├── LICENSE                      # MIT
└── README.md                    # 本文件
```

## 快速开始

### 1. 启动后端

```powershell
cd ChemAgent          # ChemAgent 主项目目录
$env:CHEM_AUTH_BYPASS="true"
python run.py api     # 后端 http://localhost:8000
python run.py ui      # （可选）Web 界面
```

无需 Docker；未配置 Neo4j 时自动进入本地数据模式（内置样例配方 / 原料），检索类功能开箱可用。

### 2. 安装技能

将 `skills/chemagent/` 复制到 Agent 技能目录：

```powershell
Copy-Item -Recurse skills/chemagent $HOME.codexskillschemagent
```

### 3. 验证

```bash
python skills/chemagent/scripts/chemagent_client.py health
python skills/chemagent/scripts/chemagent_client.py graph-stats
```

## 客户端命令一览

```bash
# 配方
python scripts/chemagent_client.py search-formulas "耐候" --category 涂料
python scripts/chemagent_client.py formula FC-001
python scripts/chemagent_client.py similar FC-001 --top-k 5

# 原料
python scripts/chemagent_client.py search-materials "硅" --function 填料
python scripts/chemagent_client.py materials-detail "气相二氧化硅A200"

# 标准与合规
python scripts/chemagent_client.py standards
python scripts/chemagent_client.py compliance-check --file f.json --domains construction

# 知识库与导入
python scripts/chemagent_client.py kb-stats
python scripts/chemagent_client.py kb-search "球形硅粉 应用"   # 需配置 embedding
python scripts/chemagent_client.py kb-upload doc.md            # 需配置 embedding
python scripts/chemagent_client.py import-formula f.json       # 登记/批量导入配方
```

完整命令：`python scripts/chemagent_client.py --help`；自定义地址：`--api-base` 或环境变量 `CHEMAGENT_API_BASE`。

## 知识库设计

- **本地卡片（默认）**：`references/knowledge/` 下的 Markdown 调研卡片，技能直接读取，无需 embedding，离线可用。
- **后端语义库（可选）**：配置 embedding 后可用 `kb-upload` / `kb-search` 做语义检索。
- **检索顺序**：ChemAgent API → 本地卡片 → 缺失时由 AI 助理联网 / 向量库 / MCP 补充并标注来源。

## 数据与合规说明

- 未配置 Neo4j 时为本地数据模式，写入操作（登记配方、上传文档）的持久性取决于后端存储配置，重启后可能回退。
- 合规初筛基于内置规则库（GB/GB-T、EU/EN、RoHS 等），限值为近似换算，**属研发阶段参考，非官方合规判定**。
- 本地 API 可能包含公司机密数据，请勿将结果转发给第三方服务。

## License

[MIT](LICENSE) © 2026 ChemAgent Contributors
