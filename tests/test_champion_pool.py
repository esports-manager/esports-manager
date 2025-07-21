import pytest
from datetime import date
from sqlmodel import Session
from esm.models.moba_player import (
    MobaPlayer,
    PlayerRole,
)
from esm.models.champion import Champion
from esm.models.champion_mastery import ChampionMastery


@pytest.fixture
def player_with_champions(session_fixture: Session):
    """
    Create a player with champion masteries for testing the champion pool methods.

    Sets up:
    - 1 player (Faker)
    - 6 champions across different roles with varying mastery levels
    - Champion masteries connecting the player to champions

    Returns:
        Tuple containing:
        - player: MobaPlayer instance
        - champions: Dict mapping role to list of Champions
        - masteries: List of all ChampionMastery objects
    """
    # Create a player
    player = MobaPlayer(
        name="Faker",
        full_name="Lee Sang-hyeok",
        nationality="South Korea",
        date_of_birth=date(1996, 5, 7),
        role=PlayerRole.MID,
        mechanics=95,
        game_knowledge=98,
        team_fighting=94,
        champion_pool_size=90,  # Static attribute
        laning=92,
    )
    session_fixture.add(player)
    session_fixture.commit()

    # Create champions for different roles
    champions = {
        PlayerRole.MID: [
            Champion(
                name="Zed",
                title="The Master of Shadows",
                primary_role=PlayerRole.MID,
                difficulty=8,
                release_date=date(2012, 11, 13),
            ),
            Champion(
                name="Ahri",
                title="The Nine-Tailed Fox",
                primary_role=PlayerRole.MID,
                difficulty=6,
                release_date=date(2011, 12, 14),
            ),
            Champion(
                name="Syndra",
                title="The Dark Sovereign",
                primary_role=PlayerRole.MID,
                difficulty=7,
                release_date=date(2012, 9, 13),
            ),
        ],
        PlayerRole.TOP: [
            Champion(
                name="Darius",
                title="The Hand of Noxus",
                primary_role=PlayerRole.TOP,
                difficulty=5,
                release_date=date(2012, 5, 23),
            )
        ],
        PlayerRole.JUNGLE: [
            Champion(
                name="Lee Sin",
                title="The Blind Monk",
                primary_role=PlayerRole.JUNGLE,
                difficulty=9,
                release_date=date(2011, 4, 1),
            )
        ],
        PlayerRole.ADC: [
            Champion(
                name="Ezreal",
                title="The Prodigal Explorer",
                primary_role=PlayerRole.ADC,
                difficulty=7,
                release_date=date(2010, 3, 16),
            )
        ],
    }

    # Add champions to database
    for _, champs in champions.items():
        for champ in champs:
            session_fixture.add(champ)

    session_fixture.commit()

    # Create champion masteries with different levels
    masteries = [
        # High mastery champions (should be in effective pool)
        ChampionMastery(
            player_id=player.id,
            champion_id=champions[PlayerRole.MID][0].id,  # Zed
            mastery_level=95,
            games_played=150,
            wins=95,
            losses=55,
            kda_ratio=3.5,
            is_comfort_pick=True,
        ),
        ChampionMastery(
            player_id=player.id,
            champion_id=champions[PlayerRole.MID][1].id,  # Ahri
            mastery_level=85,
            games_played=120,
            wins=70,
            losses=50,
            kda_ratio=3.2,
            is_comfort_pick=True,
        ),
        # Medium mastery (slightly above threshold)
        ChampionMastery(
            player_id=player.id,
            champion_id=champions[PlayerRole.JUNGLE][0].id,  # Lee Sin
            mastery_level=75,
            games_played=50,
            wins=28,
            losses=22,
            kda_ratio=2.7,
            is_comfort_pick=False,
        ),
        # At threshold
        ChampionMastery(
            player_id=player.id,
            champion_id=champions[PlayerRole.TOP][0].id,  # Darius
            mastery_level=70,
            games_played=30,
            wins=15,
            losses=15,
            kda_ratio=2.1,
            is_comfort_pick=False,
        ),
        # Below threshold champions (shouldn't be in effective pool)
        ChampionMastery(
            player_id=player.id,
            champion_id=champions[PlayerRole.MID][2].id,  # Syndra
            mastery_level=65,
            games_played=20,
            wins=10,
            losses=10,
            kda_ratio=2.5,
            is_comfort_pick=False,
        ),
        ChampionMastery(
            player_id=player.id,
            champion_id=champions[PlayerRole.ADC][0].id,  # Ezreal
            mastery_level=50,
            games_played=15,
            wins=6,
            losses=9,
            kda_ratio=1.8,
            is_comfort_pick=False,
        ),
    ]

    # Add masteries to database
    for mastery in masteries:
        session_fixture.add(mastery)

    session_fixture.commit()
    session_fixture.refresh(player)

    # Return everything needed for testing
    return player, champions, masteries


def test_effective_champion_pool(session_fixture: Session, player_with_champions):
    """Test getting a player's effective champion pool based on mastery level."""
    player, champions, _ = player_with_champions

    # Default threshold (70)
    effective_pool = player.get_effective_champion_pool()
    assert len(effective_pool) == 4

    # Get champion names for easier assertions
    champion_names = [
        session_fixture.get(Champion, mastery.champion_id).name
        for mastery in effective_pool
    ]

    # Verify specific champions
    assert "Zed" in champion_names
    assert "Ahri" in champion_names
    assert "Lee Sin" in champion_names
    assert "Darius" in champion_names
    assert "Syndra" not in champion_names  # Below threshold (65)
    assert "Ezreal" not in champion_names  # Below threshold (50)

    # Test with different thresholds
    # Higher threshold - only include top champions
    high_threshold_pool = player.get_effective_champion_pool(min_mastery_level=90)
    assert len(high_threshold_pool) == 1
    assert (
        session_fixture.get(Champion, high_threshold_pool[0].champion_id).name == "Zed"
    )

    # Lower threshold - include more champions
    low_threshold_pool = player.get_effective_champion_pool(min_mastery_level=60)
    assert len(low_threshold_pool) == 5  # Now includes Syndra


def test_champion_pool_size(player_with_champions):
    """Test getting the size of a player's champion pool."""
    player, _, _ = player_with_champions

    # Default threshold (70)
    assert player.get_champion_pool_size() == 4

    # Different thresholds
    assert player.get_champion_pool_size(min_mastery_level=90) == 1
    assert player.get_champion_pool_size(min_mastery_level=80) == 2
    assert player.get_champion_pool_size(min_mastery_level=60) == 5
    assert player.get_champion_pool_size(min_mastery_level=0) == 6  # All champions


def test_role_champion_pool(player_with_champions):
    """Test getting a player's champion pool for a specific role."""
    player, _, _ = player_with_champions

    # Test for different roles
    mid_pool = player.get_role_champion_pool(PlayerRole.MID)
    top_pool = player.get_role_champion_pool(PlayerRole.TOP)
    jungle_pool = player.get_role_champion_pool(PlayerRole.JUNGLE)
    adc_pool = player.get_role_champion_pool(PlayerRole.ADC)
    support_pool = player.get_role_champion_pool(PlayerRole.SUPPORT)

    # Verify counts
    assert len(mid_pool) == 2  # Zed and Ahri (Syndra below threshold)
    assert len(top_pool) == 1  # Darius
    assert len(jungle_pool) == 1  # Lee Sin
    assert len(adc_pool) == 0  # Ezreal below threshold
    assert len(support_pool) == 0  # No support champions

    # Test with different threshold
    mid_pool_low = player.get_role_champion_pool(PlayerRole.MID, min_mastery_level=60)
    assert len(mid_pool_low) == 3  # Now includes Syndra


def test_static_vs_dynamic_champion_pool(
    session_fixture: Session, player_with_champions
):
    """
    Test the relationship between static champion_pool_size attribute and
    dynamic champion pool methods.
    """
    player, _, __ = player_with_champions

    # Static value is set in fixture
    assert player.champion_pool_size == 90

    # Dynamic count from relationships
    assert player.get_champion_pool_size() == 4

    # Add more masteries to increase dynamic pool size
    new_champions = [
        Champion(
            name="Orianna",
            title="The Lady of Clockwork",
            primary_role=PlayerRole.MID,
            difficulty=7,
            release_date=date(2011, 6, 1),
        ),
        Champion(
            name="Fizz",
            title="The Tidal Trickster",
            primary_role=PlayerRole.MID,
            difficulty=6,
            release_date=date(2011, 11, 15),
        ),
    ]

    for champ in new_champions:
        session_fixture.add(champ)
    session_fixture.commit()

    # Add masteries for new champions
    for champ in new_champions:
        mastery = ChampionMastery(
            player_id=player.id,
            champion_id=champ.id,
            mastery_level=80,
            games_played=60,
            wins=40,
            losses=20,
            kda_ratio=3.0,
            is_comfort_pick=True,
        )
        session_fixture.add(mastery)

    session_fixture.commit()
    session_fixture.refresh(player)

    # Dynamic count should now be increased
    assert player.get_champion_pool_size() == 6

    # Static value remains unchanged
    assert player.champion_pool_size == 90


def test_empty_champion_pool(session_fixture: Session):
    """Test champion pool methods on a player with no masteries."""
    # Create a player without any champion masteries
    player = MobaPlayer(
        name="Rookie",
        nationality="China",
        date_of_birth=date(2000, 1, 1),
        role=PlayerRole.MID,
    )
    session_fixture.add(player)
    session_fixture.commit()

    # Test the methods with empty data
    assert player.get_effective_champion_pool() == []
    assert player.get_champion_pool_size() == 0
    assert player.get_role_champion_pool(PlayerRole.MID) == []
