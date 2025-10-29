"""Tests for data models."""

import pytest
from pydantic import ValidationError


def test_model_imports():
    """Test that model modules can be imported."""
    from app import models

    assert models is not None


def test_game_region_enum():
    """Test GameRegion enum."""
    from app.models import GameRegion

    # Test valid regions
    assert GameRegion.EUW1 == "euw1"
    assert GameRegion.NA1 == "na1"
    assert GameRegion.KR == "kr"

    # Test that we can access all regions
    regions = list(GameRegion)
    assert len(regions) > 0
    assert "euw1" in [r.value for r in regions]


def test_platform_region_enum():
    """Test PlatformRegion enum."""
    from app.models import PlatformRegion

    # Test valid platform regions
    assert PlatformRegion.EUROPE == "europe"
    assert PlatformRegion.AMERICAS == "americas"
    assert PlatformRegion.ASIA == "asia"

    # Test that we can access all platform regions
    regions = list(PlatformRegion)
    assert len(regions) > 0


def test_queue_type_enum():
    """Test QueueType enum."""
    from app.models import QueueType

    # Test common queue types
    assert QueueType.RANKED_SOLO_5x5 == "RANKED_SOLO_5x5"
    assert QueueType.RANKED_FLEX_SR == "RANKED_FLEX_SR"

    # Test that we can access all queue types
    queues = list(QueueType)
    assert len(queues) > 0


def test_tier_enum():
    """Test Tier enum."""
    from app.models import Tier

    # Test all tiers
    assert Tier.IRON == "IRON"
    assert Tier.BRONZE == "BRONZE"
    assert Tier.SILVER == "SILVER"
    assert Tier.GOLD == "GOLD"
    assert Tier.PLATINUM == "PLATINUM"
    assert Tier.EMERALD == "EMERALD"
    assert Tier.DIAMOND == "DIAMOND"
    assert Tier.MASTER == "MASTER"
    assert Tier.GRANDMASTER == "GRANDMASTER"
    assert Tier.CHALLENGER == "CHALLENGER"

    # Test ordering
    tiers = list(Tier)
    assert len(tiers) >= 10  # At least 10 tiers (may include UNRANKED)


def test_division_enum():
    """Test Division enum."""
    from app.models import Division

    # Test all divisions
    assert Division.I == "I"
    assert Division.II == "II"
    assert Division.III == "III"
    assert Division.IV == "IV"

    # Test that we have all 4 divisions
    divisions = list(Division)
    assert len(divisions) == 4


def test_enum_validation():
    """Test that enums validate correctly."""
    from app.models import GameRegion

    # Valid region
    region = GameRegion("euw1")
    assert region == GameRegion.EUW1

    # Invalid region should raise ValueError
    with pytest.raises(ValueError):
        GameRegion("invalid_region")


def test_enum_usage_in_models():
    """Test that enums can be used in Pydantic models."""
    from pydantic import BaseModel
    from app.models import GameRegion, QueueType

    class TestModel(BaseModel):
        region: GameRegion
        queue: QueueType

    # Valid data
    model = TestModel(region="euw1", queue="RANKED_SOLO_5x5")
    assert model.region == GameRegion.EUW1
    assert model.queue == QueueType.RANKED_SOLO_5x5

    # Invalid data should raise validation error
    with pytest.raises(ValidationError):
        TestModel(region="invalid", queue="RANKED_SOLO_5x5")
