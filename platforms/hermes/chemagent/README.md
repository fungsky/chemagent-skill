# ChemAgent Skill（Hermes 版）

面向自托管 ChemAgent 化学研发系统的 Agent 技能。**AI 助理负责理解与推理，后端提供数据与规则**，不依赖后端 LLM。

## 安装

将本目录 `platforms/hermes/chemagent/` 复制到 Hermes 技能目录：

```powershell
# Windows
Copy-Item -Recurse platforms/hermes/chemagent $env:LOCALAPPDATA\hermes\skills\chemagent
```

```bash
# Linux / macOS
cp -r platforms/hermes/chemagent ~/.hermes/skills/chemagent
```

## 前置条件

1. ChemAgent 后端已启动（主项目目录下）：

   ```powershell
   $env:CHEM_AUTH_BYPASS="true"
   python run.py api
   ```

2. 无需 Docker；未配置 Neo4j 时自动进入本地数据模式，检索类功能开箱可用。

## 使用

直接以自然语言提问即可，例如：

- "找一个耐候好的水性涂料配方"
- "分析 HF-001 的优缺点"
- "气相二氧化硅用在哪几个配方里？"
- "这个配方符合涂料国标吗？"

技能会通过 `scripts/chemagent_client.py` 调用本地 ChemAgent API；数据缺失时会明确说明，不编造配方或限值。
