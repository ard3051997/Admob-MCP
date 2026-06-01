# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Model Context Protocol (MCP) Server** for Google AdMob. It exposes 14 tools, 3 resources, and 2 prompts to AI clients (Claude Code, Claude Desktop, Cursor, Windsurf, Cline), enabling account management, monetization optimization, and A/B testing via the AdMob REST API v1beta.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python admob_core/auth.py  # one-time OAuth browser flow — generates token.json
```

Required files before first run:
- `credentials.json` — OAuth 2.0 desktop app credentials from Google Cloud Console (AdMob API enabled)
- `.env` — must contain `PUBLISHER_ID=pub-XXXXXXXXXXXXXXXX` (find in AdMob UI → Account)

## Running the Server

```bash
python -m admob_mcp          # stdio transport (default for AI client integration)
python -m admob_mcp.server   # equivalent explicit invocation
```

**Add to Claude Code:**
```bash
claude mcp add admob-mediation -- env PYTHONPATH=/path/to/MCP-admob python -m admob_mcp
```

## Architecture

The codebase has two distinct layers:

### `admob_mcp/` — MCP Server Layer
Thin wrappers that expose functionality to AI clients via FastMCP:
- **`server.py`** — Entry point; initializes all core component singletons (`client`, `db`, `expert`, `rules_engine`, `safety_layer`) in an async lifespan context manager
- **`tools/`** — 14 tools across 4 modules: `reporting.py` (list apps/ad units, generate reports), `management.py` (mediation group CRUD with rules + safety enforcement), `experiments.py` (A/B experiment lifecycle), `diagnostics.py` (expert sync/analyze, geo recommendations, placement map)
- **`resources.py`** — 3 static resources: `admob://ad-sources`, `admob://app-categories`, `admob://format-support`
- **`prompts.py`** — 2 guided workflow prompts: `optimize_app(app_id)`, `portfolio_health()`

### `admob_core/` — Business Logic Layer
- **`client.py`** — Async AdMob REST API wrapper; injects OAuth headers, integrates rate limiter and TTL cache
- **`auth.py`** — OAuth 2.0 flow; caches token in `token.json` with auto-refresh
- **`db.py`** — SQLite3 (`admob_metrics.db`); stores daily, geo, format, and per-source metrics for offline analysis
- **`analyzer.py`** — `AdMonExpert`: downloads 14-day mediation+geo history into DB, detects revenue anomalies (>15% drops), audits waterfall health, compares 30d trends
- **`rules.py`** — `RulesEngine`: validates mediation group configs before writes; 2 blocking rules (format_check, child_directed/COPPA) and 2 warning rules (min_bidding ≥3, admob_network_required)
- **`safety.py`** — `SafetyLayer`: structured JSON audit logging to `audit.log`; `dry_run_response()` previews mutations; `snapshot_before()` captures state before updates
- **`registry.py`** — Hard-coded knowledge base of 13+ ad networks (bidding/waterfall support, format matrix, geo Tier-1/Tier-2 recommendations)
- **`rate_limiter.py`** — Token bucket with separate limits: read (5/s), write (1/s), report (0.5/s); exponential backoff on 429s
- **`cache.py`** — In-memory TTL cache: apps/ad_units (1h), mediation_groups (5m), reports (15m)
- **`config.py`** — Loads `.env` and `config.yaml`; exposes `get_app_category()`, `is_child_directed()`
- **`models/`** — Pydantic v2 models: `apps.py`, `reports.py`, `mediation.py`, `experiments.py`

## Write Operation Flow

All mediation group creates/updates go through this sequence in `management.py`:
1. `rules_engine.validate_mediation_group()` — runs 4 policy checks; BLOCKs abort immediately
2. If `dry_run=True` → `safety_layer.dry_run_response()` returns preview without mutating
3. `safety_layer.snapshot_before()` — captures current state
4. `client.create_mediation_group()` / `client.update_mediation_group()` — API call
5. `safety_layer.log_operation()` — writes structured JSON to `audit.log`

## Configuration

**`.env`** (secrets, not committed):
```
PUBLISHER_ID=pub-XXXXXXXXXXXXXXXX
CREDENTIALS_PATH=./credentials.json
TOKEN_PATH=./token.json
AUDIT_LOG_PATH=./audit.log
SLACK_WEBHOOK_URL=https://...  # optional
```

**`config.yaml`** (app policy & rule thresholds):
- `app_categories` — per-app: `child_directed`, `primary_formats`, notes
- `rules` — `min_bidding_partners` (default 3), `stale_ecpm_threshold_days` (30), `stale_experiment_days` (14)

## Generated Runtime Files
- `token.json` — OAuth access token (auto-created after first auth)
- `admob_metrics.db` — SQLite metrics database (auto-created on first sync)
- `audit.log` — Structured JSON mutation audit trail (created on first write operation)
