from enum import Enum
from typing import List, Dict, Any, Optional
from .registry import AdSourceRegistry
from .config import Config

class Severity(Enum):
    BLOCK = "BLOCK"
    WARN = "WARN"
    INFO = "INFO"

class RuleResult:
    def __init__(self, rule_name: str, description: str, severity: Severity, fix_suggestion: str = ""):
        self.rule_name = rule_name
        self.description = description
        self.severity = severity
        self.fix_suggestion = fix_suggestion

    def to_dict(self):
        return {
            "rule_name": self.rule_name,
            "description": self.description,
            "severity": self.severity.value,
            "fix_suggestion": self.fix_suggestion
        }

class RulesEngine:
    def __init__(self, config: Config):
        self.config = config

    def validate_mediation_group(self, group: Dict[str, Any]) -> List[RuleResult]:
        results = []
        targeting = group.get("targeting", {})
        ad_format = targeting.get("format")
        lines_data = group.get("mediationGroupLines", {})
        
        # Convert dict to list if necessary
        if isinstance(lines_data, dict):
            lines = list(lines_data.values())
        else:
            lines = lines_data

        app_ids = targeting.get("adUnitIds", [])
        
        # Rule 1: format_check (BLOCK)
        for line in lines:
            source_id = line.get("adSourceId")
            if not AdSourceRegistry.supports_format(source_id, ad_format):
                results.append(RuleResult(
                    "format_check",
                    f"Ad source {AdSourceRegistry.get_source_name(source_id)} does not support format {ad_format}",
                    Severity.BLOCK,
                    "Remove this ad source from the mediation group."
                ))

        # Rule 2: child_directed (BLOCK)
        for app_id in app_ids:
            if self.config.is_child_directed(app_id):
                for line in lines:
                    source_id = line.get("adSourceId")
                    if AdSourceRegistry.is_bidding_supported(source_id):
                        results.append(RuleResult(
                            "child_directed",
                            f"Bidding source {AdSourceRegistry.get_source_name(source_id)} is not allowed for child-directed app {app_id}",
                            Severity.BLOCK,
                            "Use only waterfall (MANUAL/ANO) sources for COPPA-tagged apps."
                        ))

        # Rule 3: min_bidding (WARN)
        bidding_count = sum(1 for line in lines if AdSourceRegistry.is_bidding_supported(line.get("adSourceId")))
        if bidding_count < self.config.rules_config.get("min_bidding_partners", 3):
            results.append(RuleResult(
                "min_bidding",
                f"Mediation group has only {bidding_count} bidding partners. Recommended minimum is 3.",
                Severity.WARN,
                "Add more bidding partners (e.g., AppLovin, Meta, Mintegral) to increase auction pressure."
            ))

        # Rule 4: admob_network_required (WARN)
        has_admob = any(line.get("adSourceId") == "5450213213286189855" for line in lines)
        if not has_admob:
            results.append(RuleResult(
                "admob_network_required",
                "AdMob Network is missing from the mediation group.",
                Severity.WARN,
                "Always include AdMob Network (LIVE mode) as a baseline."
            ))

        # Rule 7: regional_check (BLOCK)
        geo = targeting.get("geoTargeting", {})
        included_countries = geo.get("includedCountries", [])
        for line in lines:
            source_id = line.get("adSourceId")
            if "Pangle" in AdSourceRegistry.get_source_name(source_id):
                if included_countries and not any(AdSourceRegistry.is_pangle_supported_geo(c) for c in included_countries):
                    results.append(RuleResult(
                        "pangle_region",
                        "Pangle is added for regions where it has no coverage.",
                        Severity.WARN,
                        "Only add Pangle for APAC, US, BR, MX geos."
                    ))

        return results
