import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Resolve project root relative to this file (admob_core/ -> project root)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env from project root so it works regardless of cwd
load_dotenv(_PROJECT_ROOT / ".env")

class Config:
    def __init__(self, config_path: str = "config.yaml"):
        # Resolve config_path relative to project root if not absolute
        config_p = Path(config_path)
        if not config_p.is_absolute():
            config_p = _PROJECT_ROOT / config_p
        self.config_path = str(config_p)
        self.publisher_id = os.getenv("PUBLISHER_ID")
        self.slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        self.audit_log_path = os.getenv("AUDIT_LOG_PATH", "audit.log")
        self.data = self._load_yaml()

    def _load_yaml(self):
        if not os.path.exists(self.config_path):
            return {}
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)

    @property
    def app_categories(self):
        return self.data.get("app_categories", {})

    @property
    def rules_config(self):
        return self.data.get("rules", {})

    def get_app_category(self, app_id: str) -> Optional[str]:
        for category, details in self.app_categories.items():
            if app_id in details.get("app_ids", []):
                return category
        return None

    def is_child_directed(self, app_id: str) -> bool:
        category = self.get_app_category(app_id)
        if category:
            return self.app_categories[category].get("child_directed", False)
        return False
