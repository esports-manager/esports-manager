"""
Unit tests for Champion model.

This module contains tests for the Champion model validation and database operations.
"""

import pytest
from datetime import date, timedelta
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from esm.models.champion import Champion, ROLE_TOP, ROLE_JUNGLE, ROLE_MID, VALID_ROLES


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
def create_champion():
    """Create a sample Champion object for testing."""
    champion = Champion(
        name="Ahri",
        title="The Nine-Tailed Fox",
        primary_role=ROLE_MID,
        secondary_role=None,
        difficulty=5,
        release_date=date(2011, 12, 14),
    )
    return champion


def test_champion_creation(create_champion):
    """Test creating a basic Champion instance."""
    champion = create_champion

    assert champion.name == "Ahri"
    assert champion.title == "The Nine-Tailed Fox"
    assert champion.primary_role == ROLE_MID
    assert champion.secondary_role is None
    assert champion.difficulty == 5
    assert champion.release_date == date(2011, 12, 14)
    assert champion.abilities is None
    assert champion.stats is None
    assert champion.description is None
    assert champion.image_url is None


def test_champion_roles():
    """Test champion role assignments and validation."""
    # Test all valid roles as primary role
    for role in VALID_ROLES:
        champion = Champion(
            name=f"Test Champion {role}",
            title="Test Champion",
            primary_role=role,
            difficulty=3,
            release_date=date.today(),
        )
        assert champion.primary_role == role

    # Test secondary role
    champion = Champion(
        name="Flex Champion",
        title="The Flexible One",
        primary_role=ROLE_TOP,
        secondary_role=ROLE_MID,
        difficulty=7,
        release_date=date.today(),
    )
    assert champion.primary_role == ROLE_TOP
    assert champion.secondary_role == ROLE_MID


def test_champion_abilities(create_champion):
    """Test the abilities JSON functionality."""
    champion = create_champion

    # Test empty abilities
    assert champion.get_abilities() == {}

    # Set abilities
    abilities = {
        "passive": {
            "name": "Essence Theft",
            "description": "After hitting 9 spells, heal for some amount",
        },
        "q": {
            "name": "Orb of Deception",
            "description": "Send orb that deals magic damage and returns",
        },
        "w": {
            "name": "Fox-Fire",
            "description": "Release fox-fires that target nearby enemies",
        },
        "e": {"name": "Charm", "description": "Blow kiss that deals damage and charms"},
        "r": {
            "name": "Spirit Rush",
            "description": "Dash and fire essence bolts at nearby enemies",
        },
    }

    champion.set_abilities(abilities)

    # Verify abilities were set
    stored_abilities = champion.get_abilities()
    assert stored_abilities["passive"]["name"] == "Essence Theft"
    assert stored_abilities["q"]["name"] == "Orb of Deception"
    assert len(stored_abilities) == 5


def test_champion_stats(create_champion):
    """Test the stats JSON functionality."""
    champion = create_champion

    # Test empty stats
    assert champion.get_stats() == {}

    # Set stats
    stats = {
        "health": 526,
        "health_regen": 5.5,
        "mana": 418,
        "mana_regen": 8.0,
        "attack_damage": 53,
        "attack_speed": 0.668,
        "armor": 21,
        "magic_resist": 30,
        "move_speed": 330,
        "scaling": {
            "health_per_level": 92,
            "attack_damage_per_level": 3,
            "armor_per_level": 3.5,
        },
    }

    champion.set_stats(stats)

    # Verify stats were set
    stored_stats = champion.get_stats()
    assert stored_stats["health"] == 526
    assert stored_stats["attack_damage"] == 53
    assert stored_stats["scaling"]["health_per_level"] == 92


def test_champion_database_operations(session):
    """Test CRUD operations with Champion model."""
    # Create champion
    champion = Champion(
        name="Lee Sin",
        title="The Blind Monk",
        primary_role=ROLE_JUNGLE,
        secondary_role=ROLE_TOP,
        difficulty=8,
        release_date=date(2011, 4, 1),
        description="A martial arts expert who channels spirit energy",
    )
    session.add(champion)
    session.commit()

    # Verify ID was assigned
    assert champion.id is not None

    # Query from database
    retrieved_champion = session.get(Champion, champion.id)
    assert retrieved_champion.name == "Lee Sin"
    assert retrieved_champion.primary_role == ROLE_JUNGLE
    assert retrieved_champion.secondary_role == ROLE_TOP

    # Update champion
    retrieved_champion.difficulty = 9
    retrieved_champion.description = (
        "A masterful blind monk who unleashes devastating kicks"
    )
    session.add(retrieved_champion)
    session.commit()

    # Verify update
    updated_champion = session.get(Champion, champion.id)
    assert updated_champion.difficulty == 9
    assert (
        updated_champion.description
        == "A masterful blind monk who unleashes devastating kicks"
    )

    # Delete champion
    session.delete(updated_champion)
    session.commit()

    # Verify deletion
    assert session.get(Champion, champion.id) is None


def test_years_since_release():
    """Test the years_since_release calculation."""
    today = date.today()

    # Champion released exactly 5 years ago
    release_date = date(today.year - 5, today.month, today.day)
    champion = Champion(
        name="Test Champion",
        title="The Test",
        primary_role=ROLE_MID,
        difficulty=1,
        release_date=release_date,
    )
    assert champion.years_since_release() == 5

    # Champion released 5 years and 1 day ago
    release_date = date(today.year - 5, today.month, today.day) - timedelta(days=1)
    champion.release_date = release_date
    assert champion.years_since_release() == 5

    # Champion released 5 years less 1 day ago
    release_date = date(today.year - 5, today.month, today.day) + timedelta(days=1)
    champion.release_date = release_date
    assert champion.years_since_release() == 4


def test_repr_method(create_champion):
    """Test the __repr__ method of Champion."""
    champion = create_champion

    expected_repr = "<Champion: Ahri (The Nine-Tailed Fox, mid)>"
    assert repr(champion) == expected_repr
