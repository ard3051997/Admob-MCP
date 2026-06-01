"""
AdSourceRegistry - Network knowledge base.

Format support sourced from:
  - https://developers.google.com/admob/android/choose-networks
  - Per-network official mediation guides (Google Developers)
  - Network documentation (Pangle, Mintegral, Unity, Meta, Liftoff, etc.)

Last updated: 2026-05-07
"""
from typing import Dict, List, Optional

ALL_FORMATS = ["BANNER", "INTERSTITIAL", "REWARDED", "REWARDED_INTERSTITIAL", "NATIVE", "APP_OPEN"]

class AdSourceRegistry:
    """
    Registry of all AdMob-supported third-party ad networks.

    FORMAT_SUPPORT entries only needed when a network does NOT support all formats.
    If a source_id is absent, supports_format() returns True (unknown = assume OK).

    SOURCES marks bidding=True for any network where cpmMode="LIVE" is valid.
    """

    SOURCES = {
        # ─── Google ───────────────────────────────────────────────────────────
        "5450213213286189855": {"name": "AdMob Network",            "bidding": True,  "waterfall": True},
        "1215381445328257950": {"name": "AdMob Network (waterfall)","bidding": False, "waterfall": True},

        # ─── AppLovin ─────────────────────────────────────────────────────────
        # Bidding (SDK Bidding): banner note – bidding banner support limited in some configs
        "1328079684332308356": {"name": "AppLovin (bidding)",       "bidding": True,  "waterfall": False},
        "1063618907739174004": {"name": "AppLovin",                 "bidding": False, "waterfall": True},

        # ─── Liftoff Monetize (formerly Vungle) ───────────────────────────────
        # Supports all 6 formats. REW_ITT needs special dashboard setup.
        "4692500501762622185": {"name": "Liftoff Monetize (bidding)","bidding": True,  "waterfall": False},
        "1953547073528090325": {"name": "Liftoff Monetize",          "bidding": False, "waterfall": True},

        # ─── Mintegral ────────────────────────────────────────────────────────
        # Supports all 6 formats. Strong in APAC / Southeast Asia.
        "6250601289653372374": {"name": "Mintegral (bidding)",       "bidding": True,  "waterfall": False},
        "1357746574408896200": {"name": "Mintegral",                 "bidding": False, "waterfall": True},

        # ─── Meta Audience Network (formerly Facebook) ─────────────────────────
        # No App Open. No adaptive banners. REW_ITT bidding only.
        "11198165126854996598": {"name": "Meta Audience Network (bidding)","bidding": True,  "waterfall": False},
        "10568273599589928883": {"name": "Meta Audience Network",          "bidding": False, "waterfall": True},

        # ─── Unity Ads ────────────────────────────────────────────────────────
        # Waterfall deprecated Jan 31 2026. Bidding only going forward.
        # No REW_ITT, no APP_OPEN.
        "7069338991535737586": {"name": "Unity Ads (bidding)", "bidding": True,  "waterfall": False},
        "4970775877303683148": {"name": "Unity Ads",           "bidding": False, "waterfall": True},  # deprecated

        # ─── Pangle (TikTok for Business) ─────────────────────────────────────
        # Supports all 6 formats. Best demand in APAC + US/BR/MX.
        "3525379893916449117": {"name": "Pangle (bidding)", "bidding": True,  "waterfall": False},
        "4069896914521993236": {"name": "Pangle",           "bidding": False, "waterfall": True},

        # ─── ironSource Ads (IS) ───────────────────────────────────────────────
        # Supports REW_ITT. No APP_OPEN.
        "1643326773739866623": {"name": "ironSource Ads (bidding)", "bidding": True,  "waterfall": False},
        "6925240245545091930": {"name": "ironSource Ads",           "bidding": False, "waterfall": True},

        # ─── InMobi ───────────────────────────────────────────────────────────
        # No REW_ITT. No APP_OPEN.
        "6325663098072678541": {"name": "InMobi (bidding)", "bidding": True,  "waterfall": False},
        "7681903010231960328": {"name": "InMobi",           "bidding": False, "waterfall": True},

        # ─── DT Exchange (formerly Fyber) ─────────────────────────────────────
        # No REW_ITT, no APP_OPEN. Native in beta.
        "2179455223494392917": {"name": "DT Exchange", "bidding": True, "waterfall": True},

        # ─── Chartboost ───────────────────────────────────────────────────────
        # Waterfall only. No REW_ITT, no APP_OPEN.
        "2873236629771172317": {"name": "Chartboost", "bidding": False, "waterfall": True},

        # ─── Moloco ───────────────────────────────────────────────────────────
        # Bidding only. Some formats in beta.
        "7562261807874066446": {"name": "Moloco", "bidding": True, "waterfall": False},
    }

    # ─── Format Support Matrix ────────────────────────────────────────────────
    # Only entries where support is RESTRICTED from ALL_FORMATS.
    # Absence from this dict → assume full support.
    FORMAT_SUPPORT = {
        # AdMob Network: full support
        "5450213213286189855": ALL_FORMATS,
        "1215381445328257950": ["BANNER", "INTERSTITIAL", "REWARDED", "NATIVE"],

        # AppLovin: full support (all 6)
        "1328079684332308356": ALL_FORMATS,
        "1063618907739174004": ALL_FORMATS,

        # Liftoff Monetize: full support (all 6)
        "4692500501762622185": ALL_FORMATS,
        "1953547073528090325": ALL_FORMATS,

        # Mintegral: full support (all 6)
        "6250601289653372374": ALL_FORMATS,
        "1357746574408896200": ALL_FORMATS,

        # Meta Audience Network: NO APP_OPEN; REW_ITT bidding only
        "11198165126854996598": ["BANNER", "INTERSTITIAL", "REWARDED", "REWARDED_INTERSTITIAL", "NATIVE"],
        "10568273599589928883": ["BANNER", "INTERSTITIAL", "REWARDED", "NATIVE"],  # waterfall: no REW_ITT

        # Unity Ads: NO REW_ITT, NO APP_OPEN
        "7069338991535737586": ["BANNER", "INTERSTITIAL", "REWARDED", "NATIVE"],
        "4970775877303683148": ["BANNER", "INTERSTITIAL", "REWARDED", "NATIVE"],

        # Pangle: full support (all 6)
        "3525379893916449117": ALL_FORMATS,
        "4069896914521993236": ALL_FORMATS,

        # ironSource Ads: REW_ITT yes, APP_OPEN NO
        "1643326773739866623": ["BANNER", "INTERSTITIAL", "REWARDED", "REWARDED_INTERSTITIAL", "NATIVE"],
        "6925240245545091930": ["BANNER", "INTERSTITIAL", "REWARDED", "REWARDED_INTERSTITIAL", "NATIVE"],

        # InMobi: NO REW_ITT, NO APP_OPEN
        "6325663098072678541": ["BANNER", "INTERSTITIAL", "REWARDED", "NATIVE"],
        "7681903010231960328": ["BANNER", "INTERSTITIAL", "REWARDED", "NATIVE"],

        # DT Exchange: NO REW_ITT, NO APP_OPEN
        "2179455223494392917": ["BANNER", "INTERSTITIAL", "REWARDED", "NATIVE"],

        # Chartboost: NO REW_ITT, NO APP_OPEN
        "2873236629771172317": ["BANNER", "INTERSTITIAL", "REWARDED", "NATIVE"],
    }

    # ─── Regional Notes ───────────────────────────────────────────────────────
    # Pangle has best fill in these geos.
    PANGLE_REGIONS = ["JP", "CN", "KR", "TW", "TH", "ID", "VN", "MY", "SG", "US", "BR", "MX"]

    # ─── Geo Inventory Strength ───────────────────────────────────────────────
    # Tier system:
    #   T1 = Strong inventory, high fill, competitive eCPMs → MUST include
    #   T2 = Decent inventory, moderate fill → SHOULD include
    #   T3 = Weak/no inventory → SKIP (wastes ad requests, hurts latency)
    #
    # "GLOBAL" means the network is a safe default everywhere (e.g., AdMob, AppLovin).
    # Networks without a GLOBAL entry should only be added to groups targeting their T1/T2 geos.
    #
    # Geo codes use ISO 3166-1 alpha-2.
    # Region shortcuts used in T1/T2 lists:
    #   NA  = US, CA
    #   EU  = GB, DE, FR, IT, ES, NL, PL, SE, NO, DK, FI, AT, CH, BE, IE
    #   SEA = ID, TH, VN, MY, SG, PH
    #   MENA = AE, SA, EG, QA, KW, BH, OM, IQ, MA, TR
    #   LATAM = BR, MX, AR, CO, CL, PE
    #   CJK = CN, JP, KR, TW, HK

    _NA   = ["US", "CA"]
    _EU   = ["GB", "DE", "FR", "IT", "ES", "NL", "PL", "SE", "NO", "DK", "FI", "AT", "CH", "BE", "IE"]
    _SEA  = ["ID", "TH", "VN", "MY", "SG", "PH"]
    _MENA = ["AE", "SA", "EG", "QA", "KW", "BH", "OM", "IQ", "MA", "TR"]
    _LATAM = ["BR", "MX", "AR", "CO", "CL", "PE"]
    _CJK  = ["CN", "JP", "KR", "TW", "HK"]

    # Network name → { "t1": [...], "t2": [...], "global": bool }
    # Use network NAME (not source_id) so bidding + waterfall variants share the same profile.
    GEO_STRENGTH = {
        "AdMob Network": {
            "global": True,  # Strong everywhere — Google's own demand
            "notes": "Baseline demand source. Always include.",
        },
        "AppLovin": {
            "global": True,  # Strong global demand, especially gaming
            "t1": _NA + _EU + ["AU", "JP"],
            "t2": _LATAM + _SEA + ["IN"],
            "notes": "Strongest in T1 markets (US, EU). Weaker fill in IN/SEA compared to Meta.",
        },
        "Meta Audience Network": {
            "global": False,
            "t1": _NA + _EU + ["IN", "BR", "AU"] + _SEA,
            "t2": _MENA + _LATAM,
            "notes": "Strongest in India & SEA due to Facebook/Instagram penetration. Weak in CN/JP.",
        },
        "Unity Ads": {
            "global": False,
            "t1": _NA + _EU + ["AU", "JP", "KR"],
            "t2": _LATAM + _SEA + ["IN", "TR"],
            "notes": "Gaming-focused. Strong in T1 markets. Moderate in emerging markets.",
        },
        "Liftoff Monetize": {
            "global": True,  # Broad programmatic reach
            "t1": _NA + _EU + ["AU"],
            "t2": _LATAM + _SEA + ["IN", "JP"],
            "notes": "Good programmatic fill globally. Slightly weaker in APAC vs Mintegral.",
        },
        "Mintegral": {
            "global": False,
            "t1": _CJK + _SEA,
            "t2": _NA + _EU + ["IN", "BR"],
            "notes": "Dominant in China/SEA. Growing in US/EU. Best for gaming + short-drama apps.",
        },
        "Pangle": {
            "global": False,
            "t1": ["JP", "KR", "TW", "TH", "ID", "VN", "MY", "SG"],
            "t2": _MENA + ["US", "BR", "MX"],
            "notes": "TikTok demand. Best in APAC + MENA. Weak in EU (privacy regulations).",
        },
        "ironSource Ads": {
            "global": False,
            "t1": _NA + _EU + ["AU", "JP", "KR"],
            "t2": _LATAM + ["IN", "TR"] + _SEA,
            "notes": "Gaming-focused like Unity. Strong in T1. Part of Unity/IS ecosystem.",
        },
        "InMobi": {
            "global": False,
            "t1": ["IN"] + _SEA,
            "t2": _NA + _EU + _MENA,
            "notes": "Headquartered in India. Strongest in IN/SEA. Decent in T1 as secondary source.",
        },
        "DT Exchange": {
            "global": False,
            "t1": _EU + _NA,
            "t2": _LATAM,
            "notes": "European roots (Fyber). Best in EU/NA. Limited in APAC.",
        },
        "Chartboost": {
            "global": False,
            "t1": _NA,
            "t2": _EU + _LATAM,
            "notes": "US-focused gaming network. Waterfall only. Limited global reach.",
        },
    }

    # ─── Required Mapping Params per Network ──────────────────────────────────
    MAPPING_PARAMS = {
        "1063618907739174004": ["sdkKey", "zone_id"],                       # AppLovin
        "1328079684332308356": ["sdkKey", "zone_id"],                       # AppLovin bidding
        "1953547073528090325": ["app_id", "placement_id"],                  # Liftoff
        "4692500501762622185": ["app_id", "placement_id"],                  # Liftoff bidding
        "1357746574408896200": ["appKey", "appId", "placementId", "adUnitId"],# Mintegral
        "6250601289653372374": ["appKey", "appId", "placementId", "adUnitId"],# Mintegral bidding
        "4970775877303683148": ["gameId", "placementId"],                    # Unity Ads
        "7069338991535737586": ["gameId", "placementId"],                    # Unity Ads bidding
        "4069896914521993236": ["appId", "slotId"],                          # Pangle
        "3525379893916449117": ["appId", "slotId"],                          # Pangle bidding
        "6925240245545091930": ["appKey", "instanceId"],                     # ironSource
        "1643326773739866623": ["appKey", "instanceId"],                     # ironSource bidding
        "7681903010231960328": ["accountId", "placementId"],                 # InMobi
        "6325663098072678541": ["accountId", "placementId"],                 # InMobi bidding
        "2873236629771172317": ["appId", "appSignature", "adLocation"],      # Chartboost
        "2179455223494392917": ["applicationId", "spotId"],                  # DT Exchange
    }

    # ─── Methods ──────────────────────────────────────────────────────────────
    @classmethod
    def get_mapping_params(cls, source_id: str) -> List[str]:
        return cls.MAPPING_PARAMS.get(source_id, [])

    @classmethod
    def get_source_name(cls, source_id: str) -> str:
        return cls.SOURCES.get(source_id, {}).get("name", f"Unknown ({source_id})")

    @classmethod
    def is_bidding_supported(cls, source_id: str) -> bool:
        return cls.SOURCES.get(source_id, {}).get("bidding", False)

    @classmethod
    def supports_format(cls, source_id: str, ad_format: str) -> bool:
        """
        Returns True if the network supports the given ad format.
        If the source is unknown to us, conservatively returns True (no false positives).
        """
        supported = cls.FORMAT_SUPPORT.get(source_id)
        if supported is None:
            return True  # Unknown network — don't flag
        return ad_format in supported

    @classmethod
    def is_pangle_supported_geo(cls, geo: str) -> bool:
        return geo in cls.PANGLE_REGIONS

    @classmethod
    def get_all_bidding_source_ids(cls) -> List[str]:
        return [sid for sid, meta in cls.SOURCES.items() if meta.get("bidding")]

    @classmethod
    def get_network_notes(cls, source_id: str) -> str:
        notes = {
            "4970775877303683148": "Unity Ads waterfall deprecated Jan 2026. Migrate to bidding.",
            "7069338991535737586": "Unity Ads bidding only — preferred integration method.",
            "11198165126854996598": "Meta: no App Open. No adaptive banners. REW_ITT bidding only.",
            "10568273599589928883": "Meta waterfall: no App Open, no REW_ITT.",
            "2873236629771172317": "Chartboost: waterfall only. No bidding support.",
            "3525379893916449117": "Pangle: best fill in APAC + US/BR/MX only.",
            "4069896914521993236": "Pangle: best fill in APAC + US/BR/MX only.",
        }
        return notes.get(source_id, "")

    # ─── Geo-Aware Methods ────────────────────────────────────────────────────
    @classmethod
    def _get_network_base_name(cls, source_id: str) -> str:
        """Strip '(bidding)' / '(waterfall)' suffix to find the GEO_STRENGTH key."""
        name = cls.get_source_name(source_id)
        # Normalize: "AppLovin (bidding)" → "AppLovin"
        for suffix in [" (bidding)", " (waterfall)"]:
            name = name.replace(suffix, "")
        return name

    @classmethod
    def get_geo_tier(cls, source_id: str, country_code: str) -> str:
        """
        Returns the tier of a network for a given country.
        Returns: "T1", "T2", "T3", or "GLOBAL" (always strong).
        """
        base_name = cls._get_network_base_name(source_id)
        profile = cls.GEO_STRENGTH.get(base_name)
        if not profile:
            return "T3"  # Unknown network — treat as weak

        if profile.get("global"):
            # Global networks are T1 in their strong regions, T2 everywhere else
            t1_geos = profile.get("t1", [])
            if t1_geos and country_code in t1_geos:
                return "T1"
            return "T2"  # Global networks are at least T2 everywhere

        t1_geos = profile.get("t1", [])
        t2_geos = profile.get("t2", [])
        if country_code in t1_geos:
            return "T1"
        elif country_code in t2_geos:
            return "T2"
        return "T3"

    @classmethod
    def recommend_networks_for_geo(cls, country_code: str, ad_format: str,
                                    bidding_only: bool = True) -> Dict[str, List[dict]]:
        """
        Given a target country + ad format, return recommended networks grouped by tier.
        
        Returns:
            {"T1": [{"source_id": ..., "name": ..., "bidding": ...}, ...],
             "T2": [...],
             "skip": [...]}
        """
        result = {"T1": [], "T2": [], "skip": []}

        for source_id, meta in cls.SOURCES.items():
            # Filter: bidding only if requested
            if bidding_only and not meta.get("bidding"):
                continue
            # Filter: must support the ad format
            if not cls.supports_format(source_id, ad_format):
                continue

            tier = cls.get_geo_tier(source_id, country_code)
            entry = {
                "source_id": source_id,
                "name": meta["name"],
                "bidding": meta.get("bidding", False),
                "notes": cls.GEO_STRENGTH.get(cls._get_network_base_name(source_id), {}).get("notes", ""),
            }

            if tier in ("T1", "T2"):
                result[tier].append(entry)
            else:
                result["skip"].append(entry)

        return result

    @classmethod
    def get_geo_notes(cls, source_id: str) -> str:
        """Get regional intelligence notes for a network."""
        base_name = cls._get_network_base_name(source_id)
        profile = cls.GEO_STRENGTH.get(base_name, {})
        return profile.get("notes", "")
