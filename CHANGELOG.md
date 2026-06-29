# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2026-06-29

### Added
- **Browser Automation Suite**:
  - Implemented Playwright session manager `BrowserControl` in `admob_core/browser_control.py`.
  - Added headful login automation script `admob_mcp/login.py` to create and save persistent Chrome profiles under `.admob_session/`, bypassing bot protection.
  - Added new tool `admob_policy_violations` to automatically scrape the AdMob Policy Center and report active account or app-level policy issues.
  - Added stub for `admob_realtime_metrics` to support dashboard scraping in future iterations.
  - Added `requirements-browser.txt` for browser automation library requirements.
- **Advanced Mediation Management**:
  - Added `MediationGroupBuilder` in `admob_core/builder.py` to enable structured, programmatic generation of mediation group payloads.
  - Added new tools:
    - `admob_create_ad_unit_mapping`: Link third-party network credentials to an ad unit (e.g. for InMobi, AppLovin).
    - `admob_list_ad_unit_mappings`: List existing ad unit mapping credentials.
    - `admob_set_floor`: Set or update the eCPM floor price (in dollars) for a specific waterfall mediation line item.
    - `admob_add_mediation_line`: Dynamically add a new bidding or waterfall line to an existing group, complete with rules validation.
    - `admob_build_mediation_group`: Guided creation of a mediation group using `MediationGroupBuilder`.

### Changed
- Expanded `admob_core/client.py` API wrapper to support ad unit mapping creation and listings.
- Enhanced rules validation during line insertion and mediation group updates to prevent invalid waterfall modifications.

---

## [1.0.0] - 2026-06-29

### Added
- **Core MCP Server Layer**:
  - Implemented FastMCP server inside `admob_mcp/server.py`.
  - Exposed key AdMob resources (`admob://ad-sources`, `admob://app-categories`, `admob://format-support`).
  - Added native prompts: `optimize_app` and `portfolio_health`.
- **AdMob API Integration**:
  - Async Google AdMob REST API v1beta client wrapper.
  - Automated OAuth 2.0 authorization with credentials loading and local token cache refreshing.
- **Diagnostics & Local Database**:
  - SQLite metrics cache (`admob_metrics.db`) with 14-day history sync tool `admob_expert_sync`.
  - Root-cause analyzer rules for match rate drops, fill rate anomalies, and revenue fluctuations (`admob_expert_analyze`).
  - Automated geographical network recommendations tool.
- **Safety & Policy Rules Engine**:
  - Rules validator (`rules.py`) supporting format checks, COPPA child-directed network blocks, and partner density warnings.
  - Pre-change snapshot tracking and JSON audit logging for mutation operations (`safety.py`).
  - Support for dry-runs across write endpoints.
- **Mediation & Experimentation Tools**:
  - CRUD operations for Mediation Groups.
  - Experiment management tools: `admob_create_ab_experiment` and `admob_stop_ab_experiment`.
