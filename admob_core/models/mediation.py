from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class GeoTargeting(BaseModel):
    included_countries: List[str] = Field(default_factory=list, description="List of ISO 3166-1 alpha-2 country codes.")
    excluded_countries: List[str] = Field(default_factory=list, description="List of ISO 3166-1 alpha-2 country codes to exclude.")

class MediationGroupLine(BaseModel):
    id: Optional[str] = None
    ad_source_id: str
    ad_unit_mapping_id: Optional[str] = None
    cpm_mode: str = Field(..., description="LIVE, MANUAL, or ANO.")
    cpm_value: Optional[float] = None
    state: str = "ENABLED"
    display_name: Optional[str] = None

class MediationGroup(BaseModel):
    name: Optional[str] = None
    mediation_group_id: Optional[str] = None
    display_name: str
    platform: str
    ad_format: str
    targeting: Dict[str, Any] = Field(default_factory=dict)
    mediation_group_lines: List[MediationGroupLine] = Field(default_factory=list)
    state: str = "ENABLED"
    mediation_ab_experiment_state: str = "NO_AB_TEST"

class AdUnitMapping(BaseModel):
    name: Optional[str] = None
    ad_unit_mapping_id: Optional[str] = None
    ad_source_id: str
    adapter_id: str
    ad_unit_mapping_params: Dict[str, str] = Field(default_factory=dict)
    display_name: Optional[str] = None
    state: str = "ENABLED"
