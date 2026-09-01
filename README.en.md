# ChemAgent Skill · Chemical R&D Assistant for AI Agents

🌐 **English** | [中文](README.md)

> An agent skill package for the self-hosted ChemAgent chemical R&D system — **the agent handles understanding & reasoning, the backend handles data & rules**. No backend LLM required; offline, login-free, and ready to use.

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Client](https://img.shields.io/badge/Client-stdlib-green)

## What Is This

ChemAgent Skill turns "chemical R&D Q&A" into a reusable agent skill: formula search, raw-material lookup, Chinese GB/GB-T standard index, GB/EU compliance screening, a local knowledge base, and formula import — all through a single client script built with only the Python standard library.

Design principles:

- **Reasoning lives in the agent**: analysis, comparison, and report writing are done by the AI assistant (Codex / Claude, etc.); the backend only returns structured data.
- **Data stays local**: data comes from the local ChemAgent API and the static knowledge cards in `references/knowledge/` — no external services required.
- **Extensible by design**: web search, vector databases, MCP, and other external capabilities are provided by the AI assistant itself; the skill only handles the chemistry data layer.
- **Never fabricate**: when data is missing from the system, say so explicitly. The skill never invents formulas, materials, or limit values.

## Features

- Formula search / details / similar-formula comparison
- Raw-material search and details (CAS, function, suppliers, etc.)
- Chinese national & industry standard index queries
- GB / EU / RoHS compliance screening (rule engine, research-stage reference)
- Local static knowledge base (Markdown research cards, no embedding required)
- Optional backend semantic knowledge base (ChromaDB, requires embedding config)
- Formula registration & batch import (JSON / 4-sheet Excel, duplicate IDs skipped)
- Windows-ready (client outputs UTF-8 natively, works directly in PowerShell)

## Directory Structure

```
chemagent-skill/
├── skills/
│   └── chemagent/                # The skill itself (copy to ~/.codex/skills/ to load)
│       ├── SKILL.md              # Skill instructions (entry point)
│       ├── README.md             # Skill install & usage docs
│       ├── references/
│       │   ├── api_reference.md  # API endpoints & client command list
│       │   └── knowledge/        # Local knowledge base cards
│       │       ├── INDEX.md
│       │       ├── 球形硅粉.md
│       │       ├── 溶胶-凝胶法球形二氧化硅微球.md
│       │       └── 球形硅粉中试工艺.md
│       └── scripts/
│           └── chemagent_client.py  # API client (stdlib only)
├── LICENSE                      # Apache-2.0
└── README.md                    # This file
```

## Quick Start

### 1. Start the Backend

```powershell
cd ChemAgent          # ChemAgent main project directory
$env:CHEM_AUTH_BYPASS="true"
python run.py api     # backend at http://localhost:8000
python run.py ui      # (optional) Web UI
```

No Docker required. When Neo4j is not configured, the backend automatically falls back to local data mode (bundled sample formulas / materials), so all read-only features work out of the box.

### 2. Install the Skill (pick your platform)

**Codex (as a skill)**:

```powershell
Copy-Item -Recurse skills/chemagent $HOME\.codex\skills\chemagent
```

**Codex (as a plugin)**: clone this repo — `.codex-plugin/plugin.json` declares `skills/` as the skill directory.

**Hermes**:

```powershell
Copy-Item -Recurse platforms/hermes/chemagent $env:LOCALAPPDATA\hermes\skills\chemagent
```

**OpenClaw / ClawHub**:

```bash
cp -r platforms/openclaw/chemagent ~/.openclaw/skills/chemagent
```

### 3. Verify

```bash
python skills/chemagent/scripts/chemagent_client.py health
python skills/chemagent/scripts/chemagent_client.py graph-stats
```

## Client Commands

```bash
# Formulas
python scripts/chemagent_client.py search-formulas "weather-resistant" --category coatings
python scripts/chemagent_client.py formula FC-001
python scripts/chemagent_client.py similar FC-001 --top-k 5

# Materials
python scripts/chemagent_client.py search-materials "silica" --function filler
python scripts/chemagent_client.py materials-detail "气相二氧化硅"

# Standards & compliance
python scripts/chemagent_client.py standards
python scripts/chemagent_client.py compliance-check --file f.json --domains construction

# Knowledge base & import
python scripts/chemagent_client.py kb-stats
python scripts/chemagent_client.py kb-search "spherical silica applications"  # requires embedding
python scripts/chemagent_client.py kb-upload doc.md                          # requires embedding
python scripts/chemagent_client.py import-formula f.json                     # register/batch import
```

Full command list: `python scripts/chemagent_client.py --help`. Custom endpoint: `--api-base` or the `CHEMAGENT_API_BASE` environment variable.

## Knowledge Base Design

- **Local cards (default)**: Markdown research cards in `references/knowledge/`, read directly by the skill — no embedding, works offline.
- **Backend semantic KB (optional)**: once embedding is configured, use `kb-upload` / `kb-search` for semantic retrieval.
- **Lookup order**: ChemAgent API → local cards → if still missing, the AI assistant supplements from web / vector DB / MCP and cites sources.

## Data & Compliance Notes

- Without Neo4j, the backend runs in local data mode; writes (formula registration, document upload) depend on backend storage config and may be lost on restart.
- Compliance screening uses the built-in rule base (GB/GB-T, EU/EN, RoHS, etc.); limits are approximate conversions and are **research-stage references, not official compliance determinations**.
- The local API may hold confidential company data — never forward results to third-party services.

## License

[Apache-2.0](LICENSE) © 2026 ChemAgent Contributors
