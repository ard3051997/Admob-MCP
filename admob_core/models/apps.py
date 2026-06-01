from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, model_validator, ConfigDict

class App(BaseModel):
    name: str
    app_id: str = Field(..., alias="appId")
    platform: str
    display_name: str = Field("", description="Extracted display name")
    app_store_id: Optional[str] = Field(None, alias="appStoreId")
    app_approval_state: Optional[str] = Field(None, alias="appApprovalState")

    @model_validator(mode='before')
    @classmethod
    def extract_info(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Extract display name from nested info
            manual = data.get("manualAppInfo", {})
            linked = data.get("linkedAppInfo", {})
            data["display_name"] = linked.get("displayName") or manual.get("displayName") or ""
            
            # Extract app store ID
            if "appStoreId" not in data:
                data["appStoreId"] = linked.get("appStoreId")
        return data

class AdUnit(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str
    ad_unit_id: str = Field(..., alias="adUnitId")
    display_name: str = Field(..., alias="displayName")
    ad_format: str = Field(..., alias="adFormat")
    app_id: Optional[str] = Field(None, alias="appId")

    @model_validator(mode='before')
    @classmethod
    def extract_app_id(cls, data: Any) -> Any:
        if isinstance(data, dict) and "name" in data:
            # name is accounts/pub-.../adUnits/... 
            # We can't directly get app_id from name here without more context,
            # but usually it's passed during creation.
            pass
        return data
