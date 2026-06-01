# 🚀 AdMob Model Context Protocol (MCP) Server

A powerful **Model Context Protocol (MCP)** server that exposes Google AdMob management, mediation waterfall operations, advanced revenue analysis, and A/B experiments directly to MCP-compatible AI clients (such as **Claude Code CLI**, **Claude Desktop**, **Cursor**, **Windsurf**, and **Cline**).

Features a local **Rules Engine** and **Safety Layer** ensuring that mutating operations are audited, verified, and run via dry-runs before touching your live AdMob account.

---

## 📂 Architecture Overview

```
MCP-admob/
├── admob_mcp/              ← MCP Server Layer (FastMCP)
│   ├── server.py           ← Server entry point, async context & lifespans
│   ├── resources.py        ← Exposed resources (ad-sources, format-support)
│   ├── prompts.py          ← Integrated workflow prompt templates
│   └── tools/              ← MCP Tool modules
│       ├── reporting.py    ← Read-only reports & network data
│       ├── management.py   ← Mediation Group CRUD
│       ├── experiments.py  ← A/B experiment lifecycles
│       └── diagnostics.py  ← Expert metrics analysis & geo recommendations
├── admob_core/             ← Business Logic & Library Layer
│   ├── client.py           ← Async Google AdMob REST API v1beta wrapper
│   ├── auth.py             ← OAuth 2.0 credential loading & browser flow
│   ├── db.py               ← Local SQLite metrics database (admob_metrics.db)
│   ├── analyzer.py         ← AdMonExpert core diagnostics & sync logic
│   ├── rules.py            ← Mediation policy validator (Rules Engine)
│   ├── safety.py           ← Write safeguard & audit logger
│   └── registry.py         ← 13+ Ad Source capabilities knowledge base
├── config.yaml             ← App categories & rule configuration thresholds
├── requirements.txt        ← Python package dependencies
├── .env.example            ← Template for required environment variables
├── .env                    ← Your secrets (not committed — copy from .env.example)
├── credentials.json        ← OAuth 2.0 Client credentials (not committed — you provide)
└── token.json              ← Authorized OAuth user token (not committed — auto-generated)
```

---

## 🛠️ Prerequisites & Setup

### 1. Enable the Google AdMob API
1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Select or create your project.
3. Search for **AdMob API** in the API Library and click **Enable**.

### 2. Download OAuth 2.0 Desktop Credentials
1. Navigate to **APIs & Services** → **Credentials**.
2. Click **Create Credentials** → **OAuth client ID**.
3. Select **Desktop app** as the Application Type.
4. Download the generated client JSON and save it in the root of this repo as `credentials.json`.

### 3. Create Virtual Environment & Install Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> **Python 3.10+ required.** `fastmcp` does not support Python 3.9 or older.

### 4. Configure Environment (`.env`)
```bash
cp .env.example .env
```
Then edit `.env`:
```env
PUBLISHER_ID=pub-XXXXXXXXXXXXXXXX      # Your AdMob Publisher ID (AdMob UI → Account)
CREDENTIALS_PATH=credentials.json       # Path to your OAuth credentials file
TOKEN_PATH=token.json                   # Where to cache the authorized token
AUDIT_LOG_PATH=audit.log               # Log file for mutating operations
SLACK_WEBHOOK_URL=                      # (Optional) Slack alert webhook
```

### 5. Run the One-time Authorization Flow
```bash
python admob_core/auth.py
```
A browser tab will open — authenticate with your Google AdMob account and grant permissions. This writes `token.json` which is cached and auto-refreshed on all subsequent runs.

---

## 💻 Integrating with AI Clients

> **Replace `/path/to/MCP-admob` with the absolute path to wherever you cloned this repo.**

### 🤖 Claude Code (CLI)

```bash
claude mcp add admob-mediation \
  --env PYTHONPATH="/path/to/MCP-admob" \
  --env PUBLISHER_ID="pub-XXXXXXXXXXXXXXXX" \
  --env CREDENTIALS_PATH="/path/to/MCP-admob/credentials.json" \
  --env TOKEN_PATH="/path/to/MCP-admob/token.json" \
  --env AUDIT_LOG_PATH="/path/to/MCP-admob/audit.log" \
  -- "/path/to/MCP-admob/.venv/bin/python" -m admob_mcp
```

Or via JSON:
```bash
claude mcp add-json admob-mediation '{
  "command": "/path/to/MCP-admob/.venv/bin/python",
  "args": ["-m", "admob_mcp"],
  "env": {
    "PYTHONPATH": "/path/to/MCP-admob",
    "PUBLISHER_ID": "pub-XXXXXXXXXXXXXXXX",
    "CREDENTIALS_PATH": "/path/to/MCP-admob/credentials.json",
    "TOKEN_PATH": "/path/to/MCP-admob/token.json",
    "AUDIT_LOG_PATH": "/path/to/MCP-admob/audit.log"
  }
}'
```

Verify with `claude mcp list`.

---

### 🖥️ Claude Desktop App
Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "admob-mediation": {
      "command": "/path/to/MCP-admob/.venv/bin/python",
      "args": ["-m", "admob_mcp"],
      "cwd": "/path/to/MCP-admob",
      "env": {
        "PYTHONPATH": "/path/to/MCP-admob",
        "PUBLISHER_ID": "pub-XXXXXXXXXXXXXXXX",
        "CREDENTIALS_PATH": "/path/to/MCP-admob/credentials.json",
        "TOKEN_PATH": "/path/to/MCP-admob/token.json",
        "AUDIT_LOG_PATH": "/path/to/MCP-admob/audit.log"
      }
    }
  }
}
```
Restart Claude Desktop to reload.

---

### 🔍 Cursor IDE
1. **Settings** → **Features** → **MCP** → **+ Add New MCP Server**
2. **Name**: `admob-mediation` | **Type**: `command`
3. **Command**: `/path/to/MCP-admob/.venv/bin/python -m admob_mcp`
4. Ensure your `.env` is populated in the project root.

---

### 🌊 Windsurf / Cline / Roo Code
```json
"admob-mediation": {
  "command": "/path/to/MCP-admob/.venv/bin/python",
  "args": ["-m", "admob_mcp"],
  "env": {
    "PYTHONPATH": "/path/to/MCP-admob",
    "PUBLISHER_ID": "pub-XXXXXXXXXXXXXXXX",
    "CREDENTIALS_PATH": "/path/to/MCP-admob/credentials.json",
    "TOKEN_PATH": "/path/to/MCP-admob/token.json",
    "AUDIT_LOG_PATH": "/path/to/MCP-admob/audit.log"
  }
}
```

---

## 🧩 MCP Primitives Reference

### 🛠️ Tools (14 total)

#### Reporting — Read-Only
| Tool | Description |
|------|-------------|
| `admob_list_apps` | Lists all active apps in the publisher account |
| `admob_list_ad_units` | Lists ad units, optionally filtered by `app_id` |
| `admob_network_report` | Network revenue report across dates, apps, formats, countries |
| `admob_mediation_report` | Mediation revenue report broken down by network, bidding vs waterfall |

#### Mediation Management — Write Operations
| Tool | Description |
|------|-------------|
| `admob_list_mediation_groups` | Lists all mediation groups with targeting and line items |
| `admob_list_ad_sources` | Lists available ad network sources supported by AdMob |
| `admob_create_mediation_group` | Creates a mediation group (runs Rules Engine validation first) |
| `admob_update_mediation_group` | Updates targeting, status, or line items of a mediation group |

#### Experiments — A/B Testing
| Tool | Description |
|------|-------------|
| `admob_create_ab_experiment` | Creates a mediation A/B experiment |
| `admob_stop_ab_experiment` | Stops an A/B experiment and selects the winner variant |

#### Diagnostics & Optimization
| Tool | Description |
|------|-------------|
| `admob_expert_sync` | Syncs 14 days of mediation metrics into the local SQLite DB |
| `admob_expert_analyze` | Root-cause analysis: fill rate anomalies, match rate drops, revenue alerts |
| `admob_recommend_networks_geo` | Tier-1/Tier-2 network recommendations for a country + ad format |
| `admob_request_placement_map` | Returns a placement mapping template for UX/monetization planning |

---

### 📦 Resources (3)
| URI | Description |
|-----|-------------|
| `admob://ad-sources` | Full ad network registry with bidding/waterfall support and source IDs |
| `admob://app-categories` | App category definitions and child-directed settings from `config.yaml` |
| `admob://format-support` | Format support matrix per ad source (banner, interstitial, rewarded, etc.) |

---

### 💡 Prompts (2)
| Prompt | Description |
|--------|-------------|
| `optimize_app(app_id)` | Step-by-step audit: sync data → analyze → inspect groups → recommend changes |
| `portfolio_health` | Portfolio-wide audit: flags stale A/B tests, revenue drops, missing partners |

---

## 🔒 Safety, Auditing & Rules Engine

All write operations go through a two-stage safety pipeline before touching the live API:

### Stage 1 — Rules Engine (`rules.py`)
| Rule | Severity | Description |
|------|----------|-------------|
| `format_check` | 🔴 BLOCK | Prevents adding a network that doesn't support the group's ad format |
| `child_directed` | 🔴 BLOCK | Blocks bidding networks on COPPA-tagged apps |
| `min_bidding` | 🟡 WARN | Alerts when fewer than 3 bidding partners are configured |
| `admob_network_required` | 🟡 WARN | Warns if AdMob Network is absent from the waterfall |
| `pangle_region` | 🟡 WARN | Warns if Pangle is added outside its strong geos (APAC, US, BR, MX) |

### Stage 2 — Snapshot + Audit Log (`safety.py`)
- **`dry_run=True`** on any write tool previews the change without hitting the API
- Every real mutation captures a **pre-change snapshot** and appends a structured JSON entry to `audit.log`

---

## ⚙️ Configuration (`config.yaml`)

Customize app categories and rule thresholds:

```yaml
app_categories:
  gaming:
    app_ids: ["ca-app-pub-XXXX~YYYY"]   # AdMob app IDs to tag
    child_directed: false
    primary_formats: ["REWARDED_VIDEO", "INTERSTITIAL", "BANNER"]

rules:
  min_bidding_partners: 3
  stale_ecpm_threshold_days: 30
  stale_experiment_days: 14
```

---

## ❌ Troubleshooting

| Error | Fix |
|-------|-----|
| `ValueError: PUBLISHER_ID must be provided` | Check `.env` contains `PUBLISHER_ID=pub-...` and that the server's `cwd` points to the repo root |
| `FileNotFoundError: credentials.json not found` | Place `credentials.json` in the repo root or set `CREDENTIALS_PATH` to its absolute path |
| `403 Forbidden / AdMob API not enabled` | Enable the AdMob API in Google Cloud Console for your project |
| `401 Unauthorized / Token Expired` | Delete `token.json` and re-run `python admob_core/auth.py` |
| `fastmcp not found` / install errors | Ensure you're using Python 3.10+ (`python --version`) |

---

## 📋 Requirements

- Python 3.10+
- Google Cloud project with AdMob API enabled
- OAuth 2.0 Desktop App credentials (`credentials.json`)
- An active AdMob publisher account

---

## 📄 License

MIT — see [LICENSE](LICENSE).
