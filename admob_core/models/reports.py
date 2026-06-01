from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator

class Date(BaseModel):
    year: int
    month: int
    day: int

    @model_validator(mode='before')
    @classmethod
    def parse_string(cls, value: Any) -> Any:
        if isinstance(value, str):
            if "-" in value:
                parts = value.split("-")
                return {"year": int(parts[0]), "month": int(parts[1]), "day": int(parts[2])}
            elif len(value) == 8 and value.isdigit():
                return {"year": int(value[0:4]), "month": int(value[4:6]), "day": int(value[6:8])}
        return value

class DateRange(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    start_date: Date = Field(..., alias="startDate")
    end_date: Date = Field(..., alias="endDate")

class ReportSpec(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    date_range: DateRange = Field(..., alias="dateRange")
    dimensions: List[str] = Field(default_factory=list)
    metrics: List[str] = Field(default_factory=list)
    dimension_filters: Optional[List[Dict[str, Any]]] = Field(None, alias="dimensionFilters")
    sort_conditions: Optional[List[Dict[str, Any]]] = Field(None, alias="sortConditions")
    localization_settings: Optional[Dict[str, Any]] = Field(None, alias="localizationSettings")
    max_report_rows: Optional[int] = Field(None, alias="maxReportRows")
    time_zone: Optional[str] = Field(None, alias="timeZone")

class ReportRow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    dimension_values: Dict[str, Any] = Field(default_factory=dict, alias="dimensionValues")
    metric_values: Dict[str, Any] = Field(default_factory=dict, alias="metricValues")

class ReportResponse(BaseModel):
    rows: List[ReportRow] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
