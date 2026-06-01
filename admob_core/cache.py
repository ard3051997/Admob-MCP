import time
import re
from typing import Dict, Any, Optional, Union

class CacheEntry:
    def __init__(self, value: Any, ttl: float):
        self.value = value
        self.expiry = time.time() + ttl

    def is_expired(self) -> bool:
        return time.time() > self.expiry

class TTLCache:
    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
        # Default TTLs in seconds
        self.ttls = {
            r"^apps$": 3600,             # 1 hour
            r"^ad_units:.*": 3600,       # 1 hour
            r"^ad_sources$": 86400,      # 24 hours
            r"^mediation_groups:.*": 300, # 5 minutes
            r"^report:.*": 900,          # 15 minutes
        }

    def _get_ttl(self, key: str) -> float:
        for pattern, ttl in self.ttls.items():
            if re.match(pattern, key):
                return ttl
        return 300  # Default 5 minutes

    def get(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if entry:
            if entry.is_expired():
                del self._cache[key]
                return None
            return entry.value
        return None

    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        if ttl is None:
            ttl = self._get_ttl(key)
        self._cache[key] = CacheEntry(value, ttl)

    def invalidate(self, pattern: str):
        regex = re.compile(pattern)
        keys_to_delete = [k for k in self._cache.keys() if regex.match(k)]
        for k in keys_to_delete:
            del self._cache[k]

    def clear(self):
        self._cache.clear()
