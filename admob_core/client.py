import os
import httpx
import asyncio
from typing import List, Optional, Dict, Any, Union
from .auth import get_credentials
from .rate_limiter import AdMobRateLimiter
from .cache import TTLCache
from .models.apps import App, AdUnit
from .models.reports import ReportSpec, ReportResponse, ReportRow

class AdMobClient:
    BASE_URL = "https://admob.googleapis.com/v1beta"

    def __init__(self, publisher_id: Optional[str] = None):
        self.publisher_id = publisher_id or os.getenv("PUBLISHER_ID")
        if not self.publisher_id:
            raise ValueError("PUBLISHER_ID must be provided or set in environment.")
        
        self.credentials = None
        self.limiter = AdMobRateLimiter()
        self.cache = TTLCache()
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def _get_headers(self) -> Dict[str, str]:
        if not self.credentials or not self.credentials.valid:
            self.credentials = await asyncio.to_thread(get_credentials)
        
        return {
            "Authorization": f"Bearer {self.credentials.token}",
            "Content-Type": "application/json"
        }

    async def _request(self, method: str, path: str, _retry_count: int = 0, **kwargs) -> Dict[str, Any]:
        MAX_RETRIES = 5
        url = f"{self.BASE_URL}/{path}"
        headers = await self._get_headers()
        
        # Determine which rate limiter to use
        if "Report" in path:
            await self.limiter.acquire_report()
        elif method in ["POST", "PATCH", "DELETE"]:
            await self.limiter.acquire_write()
        else:
            await self.limiter.acquire_read()

        response = await self.http_client.request(method, url, headers=headers, **kwargs)
        
        if response.status_code == 429:
            if _retry_count >= MAX_RETRIES:
                response.raise_for_status()  # Give up after max retries
            backoff = min(2 ** _retry_count, 32)  # Exponential backoff, max 32s
            await asyncio.sleep(backoff)
            return await self._request(method, path, _retry_count=_retry_count + 1, **kwargs)
        
        if response.status_code == 400:
            print(f"API Error Response: {response.text}")
        response.raise_for_status()
        return response.json()

    async def list_accounts(self) -> List[Dict[str, Any]]:
        data = await self._request("GET", "accounts")
        return data.get("account", [])

    async def list_apps(self) -> List[App]:
        cache_key = "apps"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        apps = []
        next_page_token = None
        
        while True:
            params = {"pageSize": 1000}
            if next_page_token:
                params["pageToken"] = next_page_token
            
            data = await self._request("GET", f"accounts/{self.publisher_id}/apps", params=params)
            apps.extend([App(**app) for app in data.get("apps", [])])
            
            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break
        
        self.cache.set(cache_key, apps)
        return apps

    async def list_ad_units(self, app_id: Optional[str] = None) -> List[AdUnit]:
        cache_key = f"ad_units:{app_id or 'all'}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        ad_units = []
        next_page_token = None
        
        while True:
            params = {"pageSize": 1000}
            if next_page_token:
                params["pageToken"] = next_page_token
            
            data = await self._request("GET", f"accounts/{self.publisher_id}/adUnits", params=params)
            units = [AdUnit(**unit) for unit in data.get("adUnits", [])]
            
            if app_id:
                units = [u for u in units if u.app_id == app_id]
            
            ad_units.extend(units)
            
            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break
        
        self.cache.set(cache_key, ad_units)
        return ad_units

    async def generate_network_report(self, spec: ReportSpec) -> ReportResponse:
        cache_key = f"report:network:{hash(spec.model_dump_json())}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        payload = {"reportSpec": spec.model_dump(exclude_none=True, by_alias=True)}
        data = await self._request("POST", f"accounts/{self.publisher_id}/networkReport:generate", json=payload)
        
        # AdMob reporting API returns a list of objects, where each object is either a header, row, or footer.
        # We need to parse this into a cleaner ReportResponse.
        rows = []
        for item in data:
            if "row" in item:
                rows.append(ReportRow(
                    dimension_values=item["row"].get("dimensionValues", {}),
                    metric_values=item["row"].get("metricValues", {})
                ))
        
        response = ReportResponse(rows=rows, metadata={}) # Simplified metadata for now
        self.cache.set(cache_key, response)
        return response

    async def generate_mediation_report(self, spec: ReportSpec) -> ReportResponse:
        cache_key = f"report:mediation:{hash(spec.model_dump_json())}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        payload = {"reportSpec": spec.model_dump(exclude_none=True, by_alias=True)}
        data = await self._request("POST", f"accounts/{self.publisher_id}/mediationReport:generate", json=payload)
        
        rows = []
        for item in data:
            if "row" in item:
                rows.append(ReportRow(
                    dimension_values=item["row"].get("dimensionValues", {}),
                    metric_values=item["row"].get("metricValues", {})
                ))
        
        response = ReportResponse(rows=rows, metadata={})
        self.cache.set(cache_key, response)
        return response

    async def list_ad_sources(self) -> List[Dict[str, Any]]:
        cache_key = "ad_sources"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        data = await self._request("GET", f"accounts/{self.publisher_id}/adSources")
        sources = data.get("adSources", [])
        self.cache.set(cache_key, sources)
        return sources

    async def list_mediation_groups(self) -> List[Dict[str, Any]]:
        cache_key = "mediation_groups:all"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        groups = []
        next_page_token = None
        
        while True:
            params = {"pageSize": 1000}
            if next_page_token:
                params["pageToken"] = next_page_token
            
            data = await self._request("GET", f"accounts/{self.publisher_id}/mediationGroups", params=params)
            groups.extend(data.get("mediationGroups", []))
            
            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break
        
        self.cache.set(cache_key, groups)
        return groups

    async def create_mediation_group(self, group: Dict[str, Any]) -> Dict[str, Any]:
        data = await self._request("POST", f"accounts/{self.publisher_id}/mediationGroups", json=group)
        self.cache.invalidate("mediation_groups:.*")
        return data

    async def update_mediation_group(self, group_id: str, group: Dict[str, Any], update_mask: str) -> Dict[str, Any]:
        params = {"updateMask": update_mask}
        data = await self._request("PATCH", f"accounts/{self.publisher_id}/mediationGroups/{group_id}", json=group, params=params)
        self.cache.invalidate("mediation_groups:.*")
        return data

    async def create_ad_unit_mapping(self, ad_unit_id: str, mapping: Dict[str, Any]) -> Dict[str, Any]:
        data = await self._request("POST", f"accounts/{self.publisher_id}/adUnits/{ad_unit_id}/adUnitMappings", json=mapping)
        self.cache.invalidate(f"ad_units:.*")
        return data

    async def create_ad_unit(self, ad_unit: Dict[str, Any]) -> Dict[str, Any]:
        data = await self._request("POST", f"accounts/{self.publisher_id}/adUnits", json=ad_unit)
        self.cache.invalidate("ad_units:.*")
        return data

    async def update_ad_unit(self, ad_unit_id: str, ad_unit: Dict[str, Any], update_mask: str) -> Dict[str, Any]:
        params = {"updateMask": update_mask}
        # ad_unit_id is usually ca-app-pub-XXX/YYY, but the API uses accounts/pub-XXX/adUnits/YYY
        # The path should be accounts/{publisher_id}/adUnits/{unit_id}
        unit_id_only = ad_unit_id.split("/")[-1]
        data = await self._request("PATCH", f"accounts/{self.publisher_id}/adUnits/{unit_id_only}", json=ad_unit, params=params)
        self.cache.invalidate("ad_units:.*")
        return data

    async def create_ab_experiment(self, group_id: str, experiment: Dict[str, Any]) -> Dict[str, Any]:
        data = await self._request("POST", f"accounts/{self.publisher_id}/mediationGroups/{group_id}/mediationAbExperiments", json=experiment)
        self.cache.invalidate("mediation_groups:.*")
        return data

    async def stop_ab_experiment(self, group_id: str, experiment_id: str, winner: str) -> Dict[str, Any]:
        payload = {"variantChoice": winner}
        data = await self._request("POST", f"accounts/{self.publisher_id}/mediationGroups/{group_id}/mediationAbExperiments/{experiment_id}:stop", json=payload)
        self.cache.invalidate("mediation_groups:.*")
        return data

    async def close(self):
        await self.http_client.aclose()
