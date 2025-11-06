"""Community Dragon API input models.

Models for validating path and query parameters for Community Dragon endpoints.
"""

from typing import Annotated

from pydantic import BaseModel, Field


class ChampionIdParams(BaseModel):
    """Path parameters for GET /cdragon/champions/{champion_id}."""

    champion_id: Annotated[
        int,
        Field(
            gt=0,
            le=1000,
            description="Numeric champion ID (e.g., 103 for Ahri, 64 for Lee Sin)",
            examples=[103, 64, 11],
        ),
    ]


class SkinIdParams(BaseModel):
    """Path parameters for GET /cdragon/skins/{skin_id}."""

    skin_id: Annotated[int, Field(gt=0, description="Numeric skin ID", examples=[103001, 103002])]
