"""CLASH-V1 API input models.

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#clash-v1
"""

from app.models.common import HasPuuid, HasTeamId, HasTournamentId, RegionQuery


class ClashPlayerParams(HasPuuid):
    """Path parameters for GET /lol/clash/v1/players/by-puuid/{puuid}."""

    pass


class ClashPlayerQuery(RegionQuery):
    """Query parameters for GET /lol/clash/v1/players/by-puuid/{puuid}."""

    pass


class ClashTeamParams(HasTeamId):
    """Path parameters for GET /lol/clash/v1/teams/{teamId}."""

    pass


class ClashTeamQuery(RegionQuery):
    """Query parameters for GET /lol/clash/v1/teams/{teamId}."""

    pass


class ClashTournamentsQuery(RegionQuery):
    """Query parameters for GET /lol/clash/v1/tournaments."""

    pass


class ClashTournamentParams(HasTournamentId):
    """Path parameters for GET /lol/clash/v1/tournaments/{tournamentId}."""

    pass


class ClashTournamentQuery(RegionQuery):
    """Query parameters for GET /lol/clash/v1/tournaments/{tournamentId}."""

    pass


class ClashTournamentByTeamParams(HasTeamId):
    """Path parameters for GET /lol/clash/v1/tournaments/by-team/{teamId}."""

    pass


class ClashTournamentByTeamQuery(RegionQuery):
    """Query parameters for GET /lol/clash/v1/tournaments/by-team/{teamId}."""

    pass
