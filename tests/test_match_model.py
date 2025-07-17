import pytest
from datetime import date, datetime
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

# Import the models we'll be testing
from esm.models.moba_team import MobaTeam, TeamRegion
from esm.models.match import (
    Match,
    MatchResult,
    MatchStatus,
    MatchType,
    MatchFormat,
)


@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    """Create a new database session for a test."""
    with Session(in_memory_db) as session:
        yield session


@pytest.fixture
def create_teams(session):
    """Create sample teams for testing match relationships."""
    team1 = MobaTeam(
        name="T1",
        tag="T1",
        region=TeamRegion.KR,
        founded_date=date(2019, 2, 25),
    )
    team2 = MobaTeam(
        name="Cloud9",
        tag="C9",
        region=TeamRegion.NA,
        founded_date=date(2013, 1, 1),
    )

    session.add(team1)
    session.add(team2)
    session.commit()
    session.refresh(team1)
    session.refresh(team2)

    return team1, team2


@pytest.fixture
def create_match(session, create_teams):
    """Create a sample match for testing."""
    team1, team2 = create_teams

    match = Match(
        home_team_id=team1.id,
        away_team_id=team2.id,
        scheduled_date=datetime(2025, 7, 20, 18, 0, 0),
        match_type=MatchType.REGULAR_SEASON,
        match_format=MatchFormat.BO3,
        venue="LoL Park, Seoul",
        status=MatchStatus.SCHEDULED,
    )

    session.add(match)
    session.commit()
    session.refresh(match)

    return match


def test_match_creation(create_match):
    """Test creating a Match instance."""
    match = create_match

    # Basic match attributes
    assert match.scheduled_date == datetime(2025, 7, 20, 18, 0, 0)
    assert match.match_type == MatchType.REGULAR_SEASON
    assert match.match_format == MatchFormat.BO3
    assert match.venue == "LoL Park, Seoul"
    assert match.status == MatchStatus.SCHEDULED

    # Default values
    assert match.home_team_score == 0
    assert match.away_team_score == 0
    assert match.completed_date is None
    assert match.match_data is None


def test_match_team_relationships(session, create_match):
    """Test the relationships between Match and MobaTeam."""
    match = create_match

    # Check relationships
    assert match.home_team is not None
    assert match.away_team is not None
    assert match.home_team.name == "T1"
    assert match.away_team.name == "Cloud9"


def test_match_update_status(session, create_match):
    """Test updating match status."""
    match = create_match

    # Start the match
    match.status = MatchStatus.IN_PROGRESS
    session.add(match)
    session.commit()
    session.refresh(match)
    assert match.status == MatchStatus.IN_PROGRESS

    # Complete the match
    match.status = MatchStatus.COMPLETED
    match.home_team_score = 2
    match.away_team_score = 1
    match.completed_date = datetime(2025, 7, 20, 20, 30, 0)
    session.add(match)
    session.commit()
    session.refresh(match)

    assert match.status == MatchStatus.COMPLETED
    assert match.home_team_score == 2
    assert match.away_team_score == 1
    assert match.completed_date == datetime(2025, 7, 20, 20, 30, 0)


def test_match_result(create_match):
    """Test the match_result property."""
    match = create_match

    # Initial state (scheduled)
    assert match.match_result is None

    # Update scores
    match.home_team_score = 2
    match.away_team_score = 1
    match.status = MatchStatus.COMPLETED

    # Check result
    assert match.match_result == MatchResult.HOME_WIN

    # Test away win
    match.home_team_score = 0
    match.away_team_score = 2
    assert match.match_result == MatchResult.AWAY_WIN

    # Test draw (although rare in esports)
    match.home_team_score = 1
    match.away_team_score = 1
    assert match.match_result == MatchResult.DRAW

    # Test incomplete match
    match.status = MatchStatus.IN_PROGRESS
    assert match.match_result is None

    match.status = MatchStatus.SCHEDULED
    assert match.match_result is None


def test_match_data_json_handling(session, create_match):
    """Test JSON handling for match_data."""
    match = create_match

    # Set match data
    match_data = {
        "maps": [
            {
                "map_name": "Summoner's Rift",
                "duration": 1850,  # in seconds
                "winner": "T1",
                "team1_kills": 15,
                "team2_kills": 8,
                "team1_gold": 65000,
                "team2_gold": 57000,
                "team1_towers": 11,
                "team2_towers": 4,
                "team1_barons": 1,
                "team2_barons": 0,
                "team1_dragons": 3,
                "team2_dragons": 1,
                "mvp_player_id": 1,
            },
            {
                "map_name": "Summoner's Rift",
                "duration": 2100,  # in seconds
                "winner": "Cloud9",
                "team1_kills": 12,
                "team2_kills": 18,
                "team1_gold": 62000,
                "team2_gold": 68000,
                "team1_towers": 5,
                "team2_towers": 10,
                "team1_barons": 0,
                "team2_barons": 2,
                "team1_dragons": 2,
                "team2_dragons": 4,
                "mvp_player_id": 6,
            },
            {
                "map_name": "Summoner's Rift",
                "duration": 1950,  # in seconds
                "winner": "T1",
                "team1_kills": 20,
                "team2_kills": 10,
                "team1_gold": 72000,
                "team2_gold": 58000,
                "team1_towers": 11,
                "team2_towers": 3,
                "team1_barons": 2,
                "team2_barons": 0,
                "team1_dragons": 4,
                "team2_dragons": 1,
                "mvp_player_id": 3,
            },
        ],
        "overall_stats": {
            "total_kills": 83,
            "total_deaths": 83,
            "total_duration": 5900,
            "highest_kda_player_id": 3,
        },
    }

    # Set the match data
    match.set_match_data(match_data)
    session.add(match)
    session.commit()

    # Fetch from database to verify persistence
    stored_match = session.get(Match, match.id)
    assert stored_match.get_match_data() == match_data

    # Test updating specific parts of the match data
    updated_overall_stats = {
        "total_kills": 85,  # Updated
        "total_deaths": 85,  # Updated
        "total_duration": 5900,
        "highest_kda_player_id": 3,
    }

    current_data = stored_match.get_match_data()
    current_data["overall_stats"] = updated_overall_stats
    stored_match.set_match_data(current_data)
    session.add(stored_match)
    session.commit()

    # Verify the update
    refreshed_match = session.get(Match, match.id)
    assert refreshed_match.get_match_data()["overall_stats"]["total_kills"] == 85


def test_str_representation(create_match):
    """Test string representation of Match."""
    match = create_match

    # Scheduled match
    expected = "Match: T1 vs Cloud9 (Scheduled for 2025-07-20 18:00:00)"
    assert str(match) == expected

    # In progress
    match.status = MatchStatus.IN_PROGRESS
    expected = "Match: T1 vs Cloud9 (In Progress)"
    assert str(match) == expected

    # Completed
    match.status = MatchStatus.COMPLETED
    match.home_team_score = 2
    match.away_team_score = 1
    expected = "Match: T1 2-1 Cloud9 (Completed)"
    assert str(match) == expected
