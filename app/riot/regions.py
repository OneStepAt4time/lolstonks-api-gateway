"""
Region routing configuration for Riot API.

This module defines the data structures and functions for routing requests to the correct
Riot API endpoints. It includes a Pydantic model for representing regions and a dictionary
that maps region names to their corresponding data.

The main components are:
- Region: A Pydantic model that defines the data structure for a single region, including
          its platform, hostname, and regional routing value.
- REGIONS: A dictionary that maps region names (e.g., "euw1", "na1") to instances of the
           Region model.
- get_regional_url: A function that returns the regional base URL for a given region.
- get_platform_url: A function that returns the platform base URL for a given region.
- get_base_url: A function that returns the appropriate base URL for a given region and
                endpoint type.
"""

from pydantic import BaseModel


class Region(BaseModel):
    """Pydantic model for a Riot API region."""

    platform: str
    hostname: str
    regional_routing: str


REGIONS = {
    "br1": Region(
        platform="americas",
        hostname="br1.api.riotgames.com",
        regional_routing="americas.api.riotgames.com",
    ),
    "eun1": Region(
        platform="europe",
        hostname="eun1.api.riotgames.com",
        regional_routing="europe.api.riotgames.com",
    ),
    "euw1": Region(
        platform="europe",
        hostname="euw1.api.riotgames.com",
        regional_routing="europe.api.riotgames.com",
    ),
    "jp1": Region(
        platform="asia", hostname="jp1.api.riotgames.com", regional_routing="asia.api.riotgames.com"
    ),
    "kr": Region(
        platform="asia", hostname="kr.api.riotgames.com", regional_routing="asia.api.riotgames.com"
    ),
    "la1": Region(
        platform="americas",
        hostname="la1.api.riotgames.com",
        regional_routing="americas.api.riotgames.com",
    ),
    "la2": Region(
        platform="americas",
        hostname="la2.api.riotgames.com",
        regional_routing="americas.api.riotgames.com",
    ),
    "na1": Region(
        platform="americas",
        hostname="na1.api.riotgames.com",
        regional_routing="americas.api.riotgames.com",
    ),
    "oc1": Region(
        platform="sea", hostname="oc1.api.riotgames.com", regional_routing="sea.api.riotgames.com"
    ),
    "tr1": Region(
        platform="europe",
        hostname="tr1.api.riotgames.com",
        regional_routing="europe.api.riotgames.com",
    ),
    "ru": Region(
        platform="europe",
        hostname="ru.api.riotgames.com",
        regional_routing="europe.api.riotgames.com",
    ),
    "ph2": Region(
        platform="sea", hostname="ph2.api.riotgames.com", regional_routing="sea.api.riotgames.com"
    ),
    "sg2": Region(
        platform="sea", hostname="sg2.api.riotgames.com", regional_routing="sea.api.riotgames.com"
    ),
    "th2": Region(
        platform="sea", hostname="th2.api.riotgames.com", regional_routing="sea.api.riotgames.com"
    ),
    "tw2": Region(
        platform="sea", hostname="tw2.api.riotgames.com", regional_routing="sea.api.riotgames.com"
    ),
    "vn2": Region(
        platform="sea", hostname="vn2.api.riotgames.com", regional_routing="sea.api.riotgames.com"
    ),
}

# All supported regions
SUPPORTED_REGIONS = list(REGIONS.keys())


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

    return f"https://{REGIONS[region].hostname}"


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

    return f"https://{REGIONS[region].regional_routing}"


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
