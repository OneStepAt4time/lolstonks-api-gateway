"""
Region routing configuration for Riot API.

Maps regions to their appropriate API base URLs.
Different endpoints use different routing:
- Regional endpoints (Summoner, League, Mastery): region-specific
- Platform endpoints (Match): platform-specific (europe, americas, asia, sea)
"""

# Mapping of regions to platform routing endpoints
PLATFORM_REGIONS = {
    "br1": "americas",
    "eun1": "europe",
    "euw1": "europe",
    "jp1": "asia",
    "kr": "asia",
    "la1": "americas",
    "la2": "americas",
    "na1": "americas",
    "oc1": "sea",
    "ph2": "sea",
    "ru": "europe",
    "sg2": "sea",
    "th2": "sea",
    "tr1": "europe",
    "tw2": "sea",
    "vn2": "sea",
}

# All supported regions
SUPPORTED_REGIONS = list(PLATFORM_REGIONS.keys())


def get_regional_url(region: str) -> str:
    """
    Get regional base URL for endpoints like Summoner, League, Mastery.

    Args:
        region: Region code (e.g., 'euw1', 'kr', 'na1')

    Returns:
        Base URL for regional endpoints

    Examples:
        >>> get_regional_url("euw1")
        'https://euw1.api.riotgames.com'
        >>> get_regional_url("kr")
        'https://kr.api.riotgames.com'
    """
    if region not in SUPPORTED_REGIONS:
        raise ValueError(f"Unsupported region: {region}. Supported: {SUPPORTED_REGIONS}")

    return f"https://{region}.api.riotgames.com"


def get_platform_url(region: str) -> str:
    """
    Get platform base URL for Match API and Account API endpoints.

    Args:
        region: Region code (e.g., 'euw1', 'kr', 'na1') OR platform region (e.g., 'americas', 'europe', 'asia', 'sea')

    Returns:
        Base URL for platform endpoints

    Examples:
        >>> get_platform_url("euw1")
        'https://europe.api.riotgames.com'
        >>> get_platform_url("kr")
        'https://asia.api.riotgames.com'
        >>> get_platform_url("americas")
        'https://americas.api.riotgames.com'
    """
    # If it's already a platform region, use it directly
    platform_regions_list = ["americas", "europe", "asia", "sea"]
    if region in platform_regions_list:
        return f"https://{region}.api.riotgames.com"

    # Otherwise, it's a game region code, map it to platform
    if region not in SUPPORTED_REGIONS:
        raise ValueError(
            f"Unsupported region: {region}. Supported: {SUPPORTED_REGIONS + platform_regions_list}"
        )

    platform = PLATFORM_REGIONS[region]
    return f"https://{platform}.api.riotgames.com"


def get_base_url(region: str, is_platform_endpoint: bool = False) -> str:
    """
    Get the appropriate base URL based on endpoint type.

    Args:
        region: Region code (e.g., 'euw1', 'kr', 'na1')
        is_platform_endpoint: True for Match API, False for Summoner/League/Mastery

    Returns:
        Appropriate base URL for the endpoint type

    Examples:
        >>> get_base_url("euw1", is_platform_endpoint=False)
        'https://euw1.api.riotgames.com'
        >>> get_base_url("euw1", is_platform_endpoint=True)
        'https://europe.api.riotgames.com'
    """
    if is_platform_endpoint:
        return get_platform_url(region)
    else:
        return get_regional_url(region)
