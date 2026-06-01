import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from admob_core.client import AdMobClient
from admob_core.db import AdMobDB
from admob_core.registry import AdSourceRegistry
from admob_core.models.reports import ReportSpec, DateRange, Date, ReportRow

class AdMonExpert:
    def __init__(self, client: AdMobClient, db: AdMobDB):
        self.client = client
        self.db = db

    async def sync_app_data(self, app_name_query: str, days: int = 14):
        """Sync historical data for an app into the local DB."""
        # 1. Resolve app_id
        app_id = self.db.get_app_id_by_name(app_name_query)
        if not app_id:
            # Try to fetch from API and save to DB
            accounts = await self.client.list_accounts()
            if not accounts:
                raise Exception("No AdMob accounts found")
            
            publisher_id = accounts[0]["name"].split("/")[-1]
            apps = await self.client.list_apps()
            
            # Save apps to DB
            app_list = []
            for app in apps:
                app_list.append({
                    "app_id": app.app_id,
                    "app_name": app.display_name or "Unknown",
                    "platform": app.platform
                })
            self.db.save_apps(app_list)
            
            app_id = self.db.get_app_id_by_name(app_name_query)
            if not app_id:
                raise Exception(f"App '{app_name_query}' not found in AdMob account")

        # 2. Fetch reports for last N days
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=days)
        
        publisher_id = app_id.split("~")[0]
        
        # 2. Mediation Report (The "Everything" Report)
        med_metrics = ["ESTIMATED_EARNINGS", "AD_REQUESTS", "MATCHED_REQUESTS", "IMPRESSIONS"]
        med_dims = ["DATE", "APP", "AD_SOURCE", "FORMAT"]
        
        med_spec = ReportSpec(**self._build_spec(start_dt, end_dt, med_dims, med_metrics, app_id))
        med_res = await self.client.generate_mediation_report(med_spec)
        self._save_mediation_rows(app_id, med_res.rows)

        # 2.1 Geo Report (using mediation report to ensure consistency with partners)
        geo_spec = ReportSpec(**self._build_spec(start_dt, end_dt, ["APP", "COUNTRY"], ["ESTIMATED_EARNINGS", "IMPRESSIONS"], app_id))
        geo_res = await self.client.generate_mediation_report(geo_spec)
        self._save_geo_rows(app_id, geo_res.rows)

        return app_id

    async def sync_app_data_by_id(self, app_id: str, days: int = 14):
        """Sync historical data for an app into the local DB using app_id."""
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=days)
        
        # 2. Mediation Report (The "Everything" Report)
        med_metrics = ["ESTIMATED_EARNINGS", "AD_REQUESTS", "MATCHED_REQUESTS", "IMPRESSIONS"]
        med_dims = ["DATE", "APP", "AD_SOURCE", "FORMAT"]
        
        med_spec = ReportSpec(**self._build_spec(start_dt, end_dt, med_dims, med_metrics, app_id))
        med_res = await self.client.generate_mediation_report(med_spec)
        self._save_mediation_rows(app_id, med_res.rows)

        # 2.1 Geo Report
        geo_spec = ReportSpec(**self._build_spec(start_dt, end_dt, ["APP", "COUNTRY"], ["ESTIMATED_EARNINGS", "IMPRESSIONS"], app_id))
        geo_res = await self.client.generate_mediation_report(geo_spec)
        self._save_geo_rows(app_id, geo_res.rows)

        return app_id

    def _build_spec(self, start: datetime, end: datetime, dimensions: List[str], metrics: List[str], app_id: str) -> Dict[str, Any]:
        return {
            "dateRange": {
                "startDate": {"year": start.year, "month": start.month, "day": start.day},
                "endDate": {"year": end.year, "month": end.month, "day": end.day}
            },
            "dimensions": dimensions,
            "metrics": metrics,
            "dimensionFilters": [
                {"dimension": "APP", "matchesAny": {"values": [app_id]}}
            ]
        }

    def _save_daily_rows(self, app_id: str, rows: List[ReportRow]):
        db_rows = []
        for row in rows:
            dv = row.dimension_values
            mv = row.metric_values
            
            # Parse date: "20240507"
            raw_date = dv.get("DATE", {}).get("value", "")
            if len(raw_date) == 8:
                date_str = f"{raw_date[0:4]}-{raw_date[4:6]}-{raw_date[6:8]}"
            else:
                continue

            ad_requests = int(mv.get("AD_REQUESTS", {}).get("integerValue", 0))
            matched_requests = int(mv.get("MATCHED_REQUESTS", {}).get("integerValue", 0))
            fill_rate = (matched_requests / ad_requests) if ad_requests > 0 else 0.0

            db_rows.append({
                "date": date_str,
                "app_id": app_id,
                "revenue": float(mv.get("ESTIMATED_EARNINGS", {}).get("microsValue", 0)) / 1_000_000,
                "impressions": int(mv.get("IMPRESSIONS", {}).get("integerValue", 0)),
                "arpdau": 0.0,
                "arpav": 0.0,
                "ad_requests": ad_requests,
                "matched_requests": matched_requests,
                "fill_rate": fill_rate,
                "match_rate": float(mv.get("MATCH_RATE", {}).get("doubleValue", 0)),
                "show_rate": float(mv.get("SHOW_RATE", {}).get("doubleValue", 0))
            })
        self.db.save_daily_metrics(db_rows)

    def _save_geo_rows(self, app_id: str, rows: List[ReportRow]):
        db_rows = []
        for row in rows:
            dv = row.dimension_values
            mv = row.metric_values
            
            # If no date in geo report, we might need to add it or handle it as aggregate
            # For now, assume we use a fixed date range or the report has DATE dimension
            # If DATE is missing, we use today's date for aggregate storage (not ideal but works for now)
            date_str = datetime.now().strftime("%Y-%m-%d")
            
            db_rows.append({
                "date": date_str,
                "app_id": app_id,
                "country_code": dv.get("COUNTRY", {}).get("value", "Unknown"),
                "revenue": float(mv.get("ESTIMATED_EARNINGS", {}).get("microsValue", 0)) / 1_000_000,
                "impressions": int(mv.get("IMPRESSIONS", {}).get("integerValue", 0)),
                "ecpm": 0.0 # Calculate later if needed
            })
        self.db.save_geo_metrics(db_rows)

    def _save_format_rows(self, app_id: str, rows: List[ReportRow]):
        db_rows = []
        for row in rows:
            dv = row.dimension_values
            mv = row.metric_values
            date_str = datetime.now().strftime("%Y-%m-%d")
            
            db_rows.append({
                "date": date_str,
                "app_id": app_id,
                "ad_format": dv.get("FORMAT", {}).get("value", "Unknown"),
                "revenue": float(mv.get("ESTIMATED_EARNINGS", {}).get("microsValue", 0)) / 1_000_000,
                "impressions": int(mv.get("IMPRESSIONS", {}).get("integerValue", 0)),
                "ecpm": 0.0
            })
        self.db.save_format_metrics(db_rows)

    async def analyze_app(self, app_id: str):
        """Perform full diagnostic on an app."""
        # 1. Baseline Snapshot
        end_date = datetime.now().strftime("%Y-%m-%d")
        metrics = self.db.get_metrics_for_period(app_id, (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"), end_date)
        
        if not metrics:
            return "No historical data found in DB. Run sync first."

        # Average eCPM
        total_rev = sum(m["revenue"] for m in metrics)
        total_imp = sum(m["impressions"] for m in metrics)
        avg_ecpm = (total_rev / (total_imp / 1000)) if total_imp > 0 else 0
        
        # Check for revenue drops
        latest_rev = metrics[0]["revenue"]
        avg_rev = sum(m["revenue"] for m in metrics[1:]) / len(metrics[1:]) if len(metrics) > 1 else latest_rev
        
        drop_pct = (avg_rev - latest_rev) / avg_rev if avg_rev > 0 else 0
        
        report = f"# Diagnostic Report for {app_id}\n"
        report += f"- **Current Rev:** ${latest_rev:.2f}\n"
        report += f"- **7-Day Avg:** ${avg_rev:.2f}\n"
        
        if drop_pct > 0.15:
            report += f"⚠️ **ALERT: Revenue Drop Detected ({drop_pct:.1%})**\n"
            # Perform deeper analysis
            report += self._investigate_drop(metrics)
        else:
            report += "✅ Revenue is stable within 15% threshold.\n"
            
        return report

    async def analyze_monthly_trend(self, app_id: str):
        """Compare last 30 days vs previous 30 days."""
        now = datetime.now()
        this_month_start = (now - timedelta(days=30)).strftime("%Y-%m-%d")
        prev_month_start = (now - timedelta(days=60)).strftime("%Y-%m-%d")
        prev_month_end = this_month_start
        
        this_metrics = self.db.get_metrics_for_period(app_id, this_month_start, now.strftime("%Y-%m-%d"))
        prev_metrics = self.db.get_metrics_for_period(app_id, prev_month_start, prev_month_end)
        
        if not this_metrics or not prev_metrics:
            return "Insufficient data for monthly comparison."
            
        this_stats = self._calc_stats(this_metrics)
        prev_stats = self._calc_stats(prev_metrics)
        
        report = "# Monthly Trend Analysis (Last 30d vs Prev 30d)\n"
        report += f"| Metric | Prev 30d | Last 30d | Delta |\n"
        report += f"| :--- | :--- | :--- | :--- |\n"
        report += f"| Revenue | ${prev_stats['rev']:.2f} | ${this_stats['rev']:.2f} | {self._delta(prev_stats['rev'], this_stats['rev'])} |\n"
        report += f"| Impressions | {prev_stats['imp']:,} | {this_stats['imp']:,} | {self._delta(prev_stats['imp'], this_stats['imp'])} |\n"
        report += f"| eCPM | ${prev_stats['ecpm']:.2f} | ${this_stats['ecpm']:.2f} | {self._delta(prev_stats['ecpm'], this_stats['ecpm'])} |\n"
        report += f"| Fill Rate | {prev_stats['fill']:.1%} | {this_stats['fill']:.1%} | {self._delta(prev_stats['fill'], this_stats['fill'])} |\n"
        
        return report

    def _calc_stats(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        rev = sum(m["revenue"] for m in metrics)
        imp = sum(m["impressions"] for m in metrics)
        req = sum(m["ad_requests"] for m in metrics)
        matched = sum(m["matched_requests"] for m in metrics)
        return {
            "rev": rev,
            "imp": imp,
            "ecpm": (rev / (imp / 1000)) if imp > 0 else 0,
            "fill": (matched / req) if req > 0 else 0
        }

    def _delta(self, prev, current):
        if prev == 0: return "+∞"
        diff = (current - prev) / prev
        emoji = "📈" if diff > 0 else "📉"
        return f"{emoji} {diff:+.1%}"

    async def audit_waterfall_health(self, app_id: str):
        """Check mediation groups for missing Tier 1 partners."""
        groups = await self.client.list_mediation_groups()
        
        # Filter groups targeting this app (simplified: check if group name contains app name/ID context)
        # In real API, we check mediationGroup.targeting.adUnitIds
        app_groups = groups # For now assume all for simplicity in this sandbox
        
        audit = "## Waterfall Health Audit\n"
        
        # Check India Interstitial specifically
        partners = []
        for g in app_groups:
            for source in g.get("mediationAbvLineItems", []):
                partners.append(source.get("adSourceName", "").lower())
        
        missing_in_in = []
        in_t1 = ["inmobi", "applovin", "liftoff monetize"] # Removed Meta due to corruption
        for p in in_t1:
            if p not in partners:
                missing_in_in.append(p)
                
        if missing_in_in:
            audit += f"⚠️ **MISSING PARTNERS (India)**: {', '.join(missing_in_in)}. Adding these could increase India yield by 15-25%.\n"
        else:
            audit += "✅ India waterfall contains key Tier 1 partners.\n"
        
        if "meta audience network" in partners:
            audit += "🛑 **WARNING**: Meta Audience Network detected. User reported data corruption issues for EMI app. Consider removing if performance is erratic.\n"
            
        return audit

    def _save_mediation_rows(self, app_id: str, rows: List[ReportRow]):
        source_data = []
        daily_agg = {} # date -> metrics
        format_agg = {} # (date, format) -> metrics
        
        for row in rows:
            dv = row.dimension_values
            mv = row.metric_values
            
            raw_date = dv.get("DATE", {}).get("value", "")
            if len(raw_date) != 8: continue
            date_str = f"{raw_date[0:4]}-{raw_date[4:6]}-{raw_date[6:8]}"
            
            source_name = dv.get("AD_SOURCE", {}).get("displayLabel", "Unknown")
            ad_format = dv.get("FORMAT", {}).get("value", "Unknown")
            
            rev = float(mv.get("ESTIMATED_EARNINGS", {}).get("microsValue", 0)) / 1_000_000
            imp = int(mv.get("IMPRESSIONS", {}).get("integerValue", 0))
            req = int(mv.get("AD_REQUESTS", {}).get("integerValue", 0))
            matched = int(mv.get("MATCHED_REQUESTS", {}).get("integerValue", 0))
            
            source_data.append({
                "date": date_str,
                "app_id": app_id,
                "ad_source_name": source_name,
                "ad_format": ad_format,
                "revenue": rev,
                "impressions": imp,
                "ad_requests": req,
                "matched_requests": matched
            })
            
            # Aggregate for Daily
            if date_str not in daily_agg:
                daily_agg[date_str] = {"revenue": 0, "impressions": 0, "ad_requests": 0, "matched_requests": 0}
            daily_agg[date_str]["revenue"] += rev
            daily_agg[date_str]["impressions"] += imp
            daily_agg[date_str]["ad_requests"] += req
            daily_agg[date_str]["matched_requests"] += matched
            
            # Aggregate for Format
            key = (date_str, ad_format)
            if key not in format_agg:
                format_agg[key] = {"revenue": 0, "impressions": 0}
            format_agg[key]["revenue"] += rev
            format_agg[key]["impressions"] += imp

        self.db.save_source_metrics(source_data)
        
        # Save aggregated daily
        daily_rows = []
        for d, m in daily_agg.items():
            daily_rows.append({
                "date": d,
                "app_id": app_id,
                "revenue": m["revenue"],
                "impressions": m["impressions"],
                "arpdau": 0.0, "arpav": 0.0,
                "ad_requests": m["ad_requests"],
                "matched_requests": m["matched_requests"],
                "fill_rate": m["matched_requests"]/m["ad_requests"] if m["ad_requests"] > 0 else 0,
                "match_rate": 0, "show_rate": 0
            })
        self.db.save_daily_metrics(daily_rows)
        
        # Save aggregated format
        format_rows = []
        for (d, f), m in format_agg.items():
            format_rows.append({
                "date": d,
                "app_id": app_id,
                "ad_format": f,
                "revenue": m["revenue"],
                "impressions": m["impressions"],
                "ecpm": (m["revenue"]/(m["impressions"]/1000)) if m["impressions"] > 0 else 0
            })
        self.db.save_format_metrics(format_rows)

    def _investigate_drop(self, metrics: List[Dict[str, Any]]) -> str:
        latest = metrics[0]
        prev_avg = {
            "impressions": sum(m["impressions"] for m in metrics[1:]) / len(metrics[1:]),
            "fill_rate": sum(m["fill_rate"] for m in metrics[1:]) / len(metrics[1:]),
            "show_rate": sum(m["show_rate"] for m in metrics[1:]) / len(metrics[1:]),
            "match_rate": sum(m["match_rate"] for m in metrics[1:]) / len(metrics[1:]),
        }
        
        analysis = "## Root Cause Analysis\n"
        
        imp_drop = (prev_avg["impressions"] - latest["impressions"]) / prev_avg["impressions"] if prev_avg["impressions"] > 0 else 0
        
        if imp_drop > 0.15:
            analysis += f"- **Impression Volume Issue:** Drop of {imp_drop:.1%}.\n"
            # Check fill rate
            fill_drop = prev_avg["fill_rate"] - latest["fill_rate"]
            if fill_drop > 0.1:
                analysis += f"  - Fill Rate drop identified: {latest['fill_rate']:.1%} vs avg {prev_avg['fill_rate']:.1%}.\n"

            match_drop = prev_avg["match_rate"] - latest["match_rate"]
            if match_drop > 0.1:
                analysis += f"  - Match Rate drop identified: {latest['match_rate']:.1%} vs avg {prev_avg['match_rate']:.1%}.\n"
            
            show_drop = prev_avg["show_rate"] - latest["show_rate"]
            if show_drop > 0.1:
                analysis += f"  - Show Rate drop identified: {latest['show_rate']:.1%} vs avg {prev_avg['show_rate']:.1%}.\n"
        else:
            analysis += "- **eCPM/Yield Issue:** Impressions stable, but revenue down. Investigating demand side...\n"
            
        return analysis
