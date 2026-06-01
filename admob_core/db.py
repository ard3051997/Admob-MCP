import sqlite3
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class AdMobDB:
    def __init__(self, db_path: str = "admob_metrics.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Daily metrics by app
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_metrics (
                    date TEXT,
                    app_id TEXT,
                    revenue REAL,
                    impressions INTEGER,
                    arpdau REAL,
                    arpav REAL,
                    ad_requests INTEGER,
                    matched_requests INTEGER,
                    fill_rate REAL,
                    match_rate REAL,
                    show_rate REAL,
                    PRIMARY KEY (date, app_id)
                )
            """)
            
            # Metrics by Geo
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS geo_metrics (
                    date TEXT,
                    app_id TEXT,
                    country_code TEXT,
                    revenue REAL,
                    impressions INTEGER,
                    ecpm REAL,
                    PRIMARY KEY (date, app_id, country_code)
                )
            """)
            
            # Metrics by Format
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS format_metrics (
                    date TEXT,
                    app_id TEXT,
                    ad_format TEXT,
                    revenue REAL,
                    impressions INTEGER,
                    ecpm REAL,
                    PRIMARY KEY (date, app_id, ad_format)
                )
            """)

            # Metrics by Source (Mediation Partners)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS source_metrics (
                    date TEXT,
                    app_id TEXT,
                    ad_source_name TEXT,
                    ad_format TEXT,
                    revenue REAL,
                    impressions INTEGER,
                    ad_requests INTEGER,
                    matched_requests INTEGER,
                    PRIMARY KEY (date, app_id, ad_source_name, ad_format)
                )
            """)
            
            # App metadata
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS apps (
                    app_id TEXT PRIMARY KEY,
                    app_name TEXT,
                    platform TEXT
                )
            """)
            conn.commit()

    def save_apps(self, apps: List[Dict[str, Any]]):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for app in apps:
                cursor.execute("""
                    INSERT OR REPLACE INTO apps (app_id, app_name, platform)
                    VALUES (?, ?, ?)
                """, (app["app_id"], app["app_name"], app["platform"]))
            conn.commit()

    def get_app_id_by_name(self, name_query: str) -> Optional[str]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT app_id FROM apps WHERE app_name LIKE ?", (f"%{name_query}%",))
            row = cursor.fetchone()
            return row[0] if row else None

    def save_daily_metrics(self, data: List[Dict[str, Any]]):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for row in data:
                cursor.execute("""
                    INSERT OR REPLACE INTO daily_metrics 
                    (date, app_id, revenue, impressions, arpdau, arpav, ad_requests, matched_requests, fill_rate, match_rate, show_rate)
                    VALUES (:date, :app_id, :revenue, :impressions, :arpdau, :arpav, :ad_requests, :matched_requests, :fill_rate, :match_rate, :show_rate)
                """, row)
            conn.commit()

    def save_geo_metrics(self, data: List[Dict[str, Any]]):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for row in data:
                cursor.execute("""
                    INSERT OR REPLACE INTO geo_metrics 
                    (date, app_id, country_code, revenue, impressions, ecpm)
                    VALUES (:date, :app_id, :country_code, :revenue, :impressions, :ecpm)
                """, row)
            conn.commit()

    def save_format_metrics(self, data: List[Dict[str, Any]]):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for row in data:
                cursor.execute("""
                    INSERT OR REPLACE INTO format_metrics 
                    (date, app_id, ad_format, revenue, impressions, ecpm)
                    VALUES (:date, :app_id, :ad_format, :revenue, :impressions, :ecpm)
                """, row)
            conn.commit()

    def save_source_metrics(self, data: List[Dict[str, Any]]):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for row in data:
                cursor.execute("""
                    INSERT OR REPLACE INTO source_metrics 
                    (date, app_id, ad_source_name, ad_format, revenue, impressions, ad_requests, matched_requests)
                    VALUES (:date, :app_id, :ad_source_name, :ad_format, :revenue, :impressions, :ad_requests, :matched_requests)
                """, row)
            conn.commit()

    def get_trailing_avg(self, app_id: str, metric: str, end_date: str, days: int = 7) -> float:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Calculate start date
            dt = datetime.strptime(end_date, "%Y-%m-%d")
            start_date = (dt - timedelta(days=days)).strftime("%Y-%m-%d")
            
            cursor.execute(f"SELECT AVG({metric}) FROM daily_metrics WHERE app_id = ? AND date >= ? AND date < ?", 
                          (app_id, start_date, end_date))
            row = cursor.fetchone()
            return row[0] if row and row[0] is not None else 0.0

    def get_metrics_for_period(self, app_id: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM daily_metrics WHERE app_id = ? AND date >= ? AND date <= ? ORDER BY date DESC",
                          (app_id, start_date, end_date))
            return [dict(row) for row in cursor.fetchall()]

    def get_last_data_date(self, app_id: str) -> Optional[str]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(date) FROM daily_metrics WHERE app_id = ?", (app_id,))
            row = cursor.fetchone()
            return row[0] if row else None
