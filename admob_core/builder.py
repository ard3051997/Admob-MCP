from typing import Dict, Any, List, Optional
from .registry import AdSourceRegistry

class MediationGroupBuilder:
    """Helper to construct valid AdMob API payloads for mediation groups."""
    
    def __init__(self, display_name: str, platform: str, ad_format: str, 
                 geo_targeting: Optional[List[str]] = None, 
                 excluded_countries: Optional[List[str]] = None):
        self.display_name = display_name
        self.platform = platform
        self.ad_format = ad_format
        self.included_countries = geo_targeting or []
        self.excluded_countries = excluded_countries or []
        
        self.lines: Dict[str, Dict[str, Any]] = {}
        self._next_id = -1
        
    def add_bidding_line(self, ad_source_id: str, ad_unit_mapping_id: Optional[str] = None) -> str:
        """Adds a LIVE (bidding) line item. Returns the assigned negative ID string."""
        if not AdSourceRegistry.is_bidding_supported(ad_source_id):
            raise ValueError(f"Ad source {ad_source_id} does not support bidding.")
            
        if not AdSourceRegistry.supports_format(ad_source_id, self.ad_format):
             raise ValueError(f"Ad source {ad_source_id} does not support {self.ad_format}.")

        line_id = str(self._next_id)
        self._next_id -= 1
        
        line: Dict[str, Any] = {
            "adSourceId": ad_source_id,
            "cpmMode": "LIVE",
            "state": "ENABLED"
        }
        if ad_unit_mapping_id:
            line["adUnitMappingId"] = ad_unit_mapping_id
            
        self.lines[line_id] = line
        return line_id
        
    def add_waterfall_line(self, ad_source_id: str, floor_cpm: float, ad_unit_mapping_id: Optional[str] = None) -> str:
        """Adds a MANUAL (waterfall) line item with a floor price. Returns the assigned negative ID string."""
        if not AdSourceRegistry.supports_format(ad_source_id, self.ad_format):
             raise ValueError(f"Ad source {ad_source_id} does not support {self.ad_format}.")
             
        line_id = str(self._next_id)
        self._next_id -= 1
        
        # Convert dollar CPM to micros (e.g. 2.50 -> "2500000")
        # Must be passed as a string/int in API, let's use string to be safe.
        cpm_micros = str(int(round(floor_cpm * 1_000_000)))
        
        line: Dict[str, Any] = {
            "adSourceId": ad_source_id,
            "cpmMode": "MANUAL",
            "cpmMicros": cpm_micros,
            "state": "ENABLED"
        }
        if ad_unit_mapping_id:
            line["adUnitMappingId"] = ad_unit_mapping_id
            
        self.lines[line_id] = line
        return line_id

    def build(self) -> Dict[str, Any]:
        """Returns the final dictionary ready to be sent to the API."""
        group: Dict[str, Any] = {
            "displayName": self.display_name,
            "state": "ENABLED",
            "targeting": {
                "format": self.ad_format,
                "platform": self.platform
            }
        }
        
        geo = {}
        if self.included_countries:
            geo["includedCountries"] = self.included_countries
        if self.excluded_countries:
            geo["excludedCountries"] = self.excluded_countries
            
        if geo:
            group["targeting"]["geoTargeting"] = geo
            
        if self.lines:
            group["mediationGroupLines"] = self.lines
            
        return group
