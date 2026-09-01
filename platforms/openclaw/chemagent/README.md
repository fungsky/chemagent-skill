# ChemAgent Skill（OpenClaw / ClawHub 版）

面向自托管 ChemAgent 化学研发系统的 Agent 技能。**AI 助理负责理解与推理，后端提供数据与规则**，不依赖后端 LLM。

## 安装

将本目录 `platforms/openclaw/chemagent/` 放入 OpenClaw 技能目录（通常为 `~/.openclaw/skills/chemagent/` 或项目内 `skills/chemagent/`）：

```bash
cp -r platforms/openclaw/chemagent ~/.openclaw/skills/chemagent
```

也可以打包上传 [ClawHub](https://clawhub.ai) 分发（包内已含 `skill.json` 元数据）。

## 前置条件

1. ChemAgent 后端已启动（主项目目录下，本地免登录）：

   ```powershell
   $env:CHEM_AUTH_BYPASS="true"
   python run.py api
   ```

2. 客户端仅依赖 Python 标准库，无第三方包。

## 使用

直接以自然语言提问，例如：

- "找一个耐候好的水性涂料配方"
- "球形硅粉和气象二氧化硅有什么区别？"
- "这个配方符合 RoHS 吗？"

技能调用 `scripts/chemagent_client.py` 完成取数；系统内没有的数据会明确说明，由 AI 助理自行联网/向量库/MCP 补充并标注来源。
