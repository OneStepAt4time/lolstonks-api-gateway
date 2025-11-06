"""Data Dragon API input models.

Models for validating path and query parameters for Data Dragon endpoints.
"""

from typing import Annotated

from pydantic import BaseModel, Field


class ChampionIdParams(BaseModel):
    """Path parameters for GET /ddragon/champions/{champion_id}."""

    champion_id: Annotated[
        str,
        Field(
            min_length=1,
            max_length=50,
            pattern=r"^[A-Za-z]+$",
            description="Champion ID (e.g., 'Ahri', 'LeeSin', 'MasterYi')",
            examples=["Ahri", "LeeSin", "MasterYi"],
        ),
    ]


class RealmRegionParams(BaseModel):
    """Path parameters for GET /ddragon/realms/{region}."""

    region: Annotated[
        str,
        Field(
            min_length=2,
            max_length=10,
            pattern=r"^[a-z0-9]+$",
            description="Region code (e.g., 'na', 'euw', 'kr')",
            examples=["na", "euw", "kr", "eune"],
        ),
    ]
