"""
Unit tests for ChampionMastery model.

This module contains tests for the ChampionMastery model and its
relationships with MobaPlayer and Champion.
"""

import pytest
from datetime import date
from sqlmodel import SQLModel, Session, create_engine, select
from sqlmodel.pool import StaticPool

from esm.models.moba_player import MobaPlayer, PlayerRole
from esm.models.champion import Champion
from esm.models.champion_mastery import ChampionMastery


@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    """Create a new database session for a test."""
    with Session(in_memory_db) as session:
        yield session


@pytest.fixture
def setup_player_and_champions(session):
    """Set up player and champions for testing champion mastery."""
    # Create a player
    player = MobaPlayer(
        name="Faker",
        nationality="South Korea",
        date_of_birth=date(1996, 5, 7),
        role=PlayerRole.MID,
        mechanics=95,
        game_knowledge=98,
        team_fighting=94,
        champion_pool_size=90,
        laning=92,
    )
    session.add(player)

    # Create champions
    champions = [
        Champion(
            name="Zed",
            title="The Master of Shadows",
            primary_role=PlayerRole.MID,
            difficulty=8,
            release_date=date(2012, 11, 13),
        ),
        Champion(
            name="Ryze",
            title="The Rune Mage",
            primary_role=PlayerRole.MID,
            difficulty=7,
            release_date=date(2009, 2, 21),
        ),
        Champion(
            name="LeBlanc",
            title="The Deceiver",
            primary_role=PlayerRole.MID,
            difficulty=9,
            release_date=date(2010, 11, 2),
        ),
    ]

    for champion in champions:
        session.add(champion)

    session.commit()

    return player, champions


def test_champion_mastery_creation(session, setup_player_and_champions):
    """Test creating champion mastery entries."""
    player, champions = setup_player_and_champions

    # Create champion mastery entries
    masteries = [
        ChampionMastery(
            player_id=player.id,
            champion_id=champions[0].id,  # Zed
            mastery_level=95,
            games_played=50,
            wins=35,
            losses=15,
            kda_ratio=3.2,
            is_comfort_pick=True,
        ),
        ChampionMastery(
            player_id=player.id,
            champion_id=champions[1].id,  # Ryze
            mastery_level=85,
            games_played=30,
            wins=18,
            losses=12,
            kda_ratio=2.8,
            is_comfort_pick=False,
        ),
    ]

    for mastery in masteries:
        session.add(mastery)
    session.commit()

    # Verify mastery entries were created
    db_masteries = session.exec(
        select(ChampionMastery).where(ChampionMastery.player_id == player.id)
    ).all()

    assert len(db_masteries) == 2
    assert db_masteries[0].mastery_level == 95
    assert db_masteries[1].mastery_level == 85


def test_champion_mastery_relationships(session, setup_player_and_champions):
    """Test relationships between Player, Champion, and ChampionMastery."""
    player, champions = setup_player_and_champions

    # Create champion mastery entries
    zed_mastery = ChampionMastery(
        player_id=player.id,
        champion_id=champions[0].id,  # Zed
        mastery_level=95,
        games_played=50,
        wins=35,
        losses=15,
        kda_ratio=3.2,
        is_comfort_pick=True,
    )
    session.add(zed_mastery)
    session.commit()

    # Refresh objects to load relationships
    session.refresh(player)
    session.refresh(champions[0])

    # Test player -> mastery -> champion relationship
    assert len(player.champion_masteries) == 1
    assert player.champion_masteries[0].mastery_level == 95
    assert player.champion_masteries[0].champion_id == champions[0].id

    # Test champion -> mastery -> player relationship
    assert len(champions[0].player_masteries) == 1
    assert champions[0].player_masteries[0].mastery_level == 95
    assert champions[0].player_masteries[0].player_id == player.id


def test_win_rate_calculation(session):
    """Test win rate calculation property."""
    # Create a ChampionMastery instance with known win/loss values
    mastery = ChampionMastery(
        player_id=1,  # Dummy ID
        champion_id=1,  # Dummy ID
        games_played=100,
        wins=60,
        losses=40,
    )

    # Test win rate calculation
    assert mastery.win_rate == 60.0

    # Test win rate with no games played
    mastery.games_played = 0
    assert mastery.win_rate == 0.0


def test_legacy_mastery_compatibility(session, setup_player_and_champions):
    """Test backward compatibility with the legacy JSON-based champion mastery."""
    player, champions = setup_player_and_champions

    # Use the legacy JSON-based mastery system
    legacy_mastery = {"Zed": 95, "Ryze": 85, "LeBlanc": 90}
    player.set_champion_mastery(legacy_mastery)
    session.add(player)
    session.commit()

    # Test retrieving the legacy mastery
    retrieved_mastery = player.get_champion_mastery()
    assert retrieved_mastery["Zed"] == 95
    assert retrieved_mastery["Ryze"] == 85
    assert retrieved_mastery["LeBlanc"] == 90

    # Also add data through the new relationship system
    zed_mastery = ChampionMastery(
        player_id=player.id,
        champion_id=champions[0].id,  # Zed
        mastery_level=92,  # Different from legacy to distinguish
        games_played=50,
        wins=35,
        losses=15,
    )
    session.add(zed_mastery)
    session.commit()
    session.refresh(player)

    # Verify both systems work in parallel
    assert player.get_champion_mastery()["Zed"] == 95  # Legacy system
    assert player.champion_masteries[0].mastery_level == 92  # New relationship system
