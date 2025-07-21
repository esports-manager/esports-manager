import pytest
from datetime import date, datetime
from sqlmodel import Session, select

# Import the models we'll be testing
from esm.models.moba_team import MobaTeam, TeamRegion
from esm.models.tournament import (
    Tournament,
    Season,
    TournamentStage,
    TournamentType,
    TournamentFormat,
    StageType,
)
from esm.models.match import (
    Match,
    MatchStatus,
    MatchType,
    MatchFormat,
)


@pytest.fixture
def create_teams(session_fixture: Session) -> list[MobaTeam]:
    """Create sample teams for testing tournament relationships."""
    teams = []
    team_data = [
        ("T1", "T1", TeamRegion.KR, date(2019, 2, 25)),
        ("Cloud9", "C9", TeamRegion.NA, date(2013, 1, 1)),
        ("Gen.G", "GEN", TeamRegion.KR, date(2017, 5, 5)),
        ("Team Liquid", "TL", TeamRegion.NA, date(2015, 1, 15)),
    ]

    for name, tag, region, founded_date in team_data:
        team = MobaTeam(
            name=name,
            tag=tag,
            region=region,
            founded_date=founded_date,
        )
        session_fixture.add(team)
        teams.append(team)

    session_fixture.commit()
    for team in teams:
        session_fixture.refresh(team)

    return teams


@pytest.fixture
def create_season(session_fixture: Session) -> Season:
    """Create a sample season for testing."""
    season = Season(
        name="2025 Season",
        start_date=date(2025, 1, 15),
        end_date=date(2025, 11, 15),
        description="The 2025 professional esports season",
    )
    session_fixture.add(season)
    session_fixture.commit()
    session_fixture.refresh(season)
    return season


@pytest.fixture
def create_tournament(
    session_fixture: Session, create_teams, create_season
) -> Tournament:
    """Create a sample tournament for testing."""
    teams = create_teams
    season = create_season

    tournament = Tournament(
        name="LCK Summer 2025",
        tournament_type=TournamentType.LEAGUE,
        tournament_format=TournamentFormat.ROUND_ROBIN,
        start_date=date(2025, 6, 1),
        end_date=date(2025, 8, 15),
        region=TeamRegion.KR,
        prize_pool=500000.00,
        description="LCK Summer Split 2025",
        logo_path="assets/images/tournaments/lck_logo.png",
        season_id=season.id,
    )
    session_fixture.add(tournament)
    session_fixture.commit()
    session_fixture.refresh(tournament)

    # Add teams to the tournament
    for team in teams[:2]:  # Just add first two teams
        tournament.teams.append(team)

    session_fixture.add(tournament)
    session_fixture.commit()
    session_fixture.refresh(tournament)

    # Create tournament stages
    regular_season = TournamentStage(
        name="Regular Season",
        stage_type=StageType.GROUPS,
        start_date=date(2025, 6, 1),
        end_date=date(2025, 7, 30),
        tournament_id=tournament.id,
    )

    playoffs = TournamentStage(
        name="Playoffs",
        stage_type=StageType.PLAYOFFS,
        start_date=date(2025, 8, 1),
        end_date=date(2025, 8, 15),
        tournament_id=tournament.id,
    )

    session_fixture.add(regular_season)
    session_fixture.add(playoffs)
    session_fixture.commit()

    # Create a match in the tournament
    match = Match(
        home_team_id=teams[0].id,
        away_team_id=teams[1].id,
        scheduled_date=datetime(2025, 6, 10, 18, 0, 0),
        match_type=MatchType.REGULAR_SEASON,
        match_format=MatchFormat.BO3,
        venue="LoL Park, Seoul",
        status=MatchStatus.SCHEDULED,
        tournament_id=tournament.id,
        tournament_stage_id=regular_season.id,
    )

    session_fixture.add(match)
    session_fixture.commit()

    return tournament


def test_tournament_creation(create_tournament: Tournament):
    """Test creating a Tournament instance."""
    tournament = create_tournament

    # Basic tournament attributes
    assert tournament.name == "LCK Summer 2025"
    assert tournament.tournament_type == TournamentType.LEAGUE
    assert tournament.tournament_format == TournamentFormat.ROUND_ROBIN
    assert tournament.start_date == date(2025, 6, 1)
    assert tournament.end_date == date(2025, 8, 15)
    assert tournament.region == TeamRegion.KR
    assert tournament.prize_pool == 500000.00
    assert tournament.description == "LCK Summer Split 2025"
    assert tournament.logo_path == "assets/images/tournaments/lck_logo.png"

    # Relationships
    assert len(tournament.teams) == 2
    assert tournament.teams[0].name in ["T1", "Cloud9"]
    assert tournament.teams[1].name in ["T1", "Cloud9"]
    assert len(tournament.stages) == 2
    assert tournament.season is not None
    assert tournament.season.name == "2025 Season"


def test_tournament_stages(create_tournament: Tournament):
    """Test tournament stages."""
    tournament = create_tournament

    # Check that tournament has stages
    assert len(tournament.stages) == 2

    # Check stage attributes
    stage_names = [stage.name for stage in tournament.stages]
    assert "Regular Season" in stage_names
    assert "Playoffs" in stage_names

    # Get specific stages
    regular_season = None
    playoffs = None
    for stage in tournament.stages:
        if stage.name == "Regular Season":
            regular_season = stage
        elif stage.name == "Playoffs":
            playoffs = stage

    assert regular_season is not None
    assert playoffs is not None

    # Check stage details
    assert regular_season.stage_type == StageType.GROUPS
    assert regular_season.start_date == date(2025, 6, 1)
    assert regular_season.end_date == date(2025, 7, 30)

    assert playoffs.stage_type == StageType.PLAYOFFS
    assert playoffs.start_date == date(2025, 8, 1)
    assert playoffs.end_date == date(2025, 8, 15)


def test_tournament_matches(create_tournament: Tournament, session_fixture: Session):
    """Test matches in a tournament."""
    tournament = create_tournament

    # Query for matches in this tournament
    statement = select(Match).where(Match.tournament_id == tournament.id)
    matches = session_fixture.exec(statement).all()

    # Check match details
    assert len(matches) == 1
    match = matches[0]
    assert match.home_team.name in ["T1", "Cloud9"]
    assert match.away_team.name in ["T1", "Cloud9"]
    assert match.home_team.name != match.away_team.name
    assert match.scheduled_date == datetime(2025, 6, 10, 18, 0, 0)

    # Check match is associated with tournament stage
    for stage in tournament.stages:
        if stage.name == "Regular Season":
            assert match.tournament_stage_id == stage.id


def test_season(create_season: Season, create_tournament: Tournament):
    """Test the Season model and its relationship with tournaments."""
    season = create_season
    tournament = create_tournament

    # Check season attributes
    assert season.name == "2025 Season"
    assert season.start_date == date(2025, 1, 15)
    assert season.end_date == date(2025, 11, 15)
    assert season.description == "The 2025 professional esports season"

    # Check relationship with tournaments
    assert len(season.tournaments) == 1
    assert season.tournaments[0].id == tournament.id
    assert season.tournaments[0].name == "LCK Summer 2025"


def test_tournament_standings(session_fixture: Session, create_tournament: Tournament):
    """Test generating tournament standings."""
    tournament = create_tournament

    # Create some matches with results to generate standings
    teams = tournament.teams

    # Create more matches between teams
    match1 = Match(
        home_team_id=teams[0].id,
        away_team_id=teams[1].id,
        scheduled_date=datetime(2025, 6, 15, 18, 0, 0),
        match_type=MatchType.REGULAR_SEASON,
        match_format=MatchFormat.BO3,
        status=MatchStatus.COMPLETED,
        home_team_score=2,
        away_team_score=1,
        completed_date=datetime(2025, 6, 15, 21, 0, 0),
        tournament_id=tournament.id,
    )

    match2 = Match(
        home_team_id=teams[1].id,
        away_team_id=teams[0].id,
        scheduled_date=datetime(2025, 7, 5, 18, 0, 0),
        match_type=MatchType.REGULAR_SEASON,
        match_format=MatchFormat.BO3,
        status=MatchStatus.COMPLETED,
        home_team_score=2,
        away_team_score=0,
        completed_date=datetime(2025, 7, 5, 20, 30, 0),
        tournament_id=tournament.id,
    )

    session_fixture.add(match1)
    session_fixture.add(match2)
    session_fixture.commit()

    # Generate standings
    standings = tournament.generate_standings()

    # Check standings structure
    assert len(standings) == 2

    # Both teams should have played 2 matches
    for team_standing in standings:
        assert team_standing["matches_played"] == 2

    # Check team records
    for team_standing in standings:
        if team_standing["team_id"] == teams[0].id:
            assert team_standing["wins"] == 1
            assert team_standing["losses"] == 1
            assert team_standing["maps_won"] == 2
            assert team_standing["maps_lost"] == 3
        elif team_standing["team_id"] == teams[1].id:
            assert team_standing["wins"] == 1
            assert team_standing["losses"] == 1
            assert team_standing["maps_won"] == 3
            assert team_standing["maps_lost"] == 2


def test_str_representation(create_tournament: Tournament, create_season: Season):
    """Test string representation of Tournament and Season."""
    tournament = create_tournament
    season = create_season

    # Tournament representation
    expected = (
        f"Tournament: LCK Summer 2025 ({TeamRegion.KR.value}, 2025-06-01 to 2025-08-15)"
    )
    assert str(tournament) == expected

    # Season representation
    expected = "Season: 2025 Season (2025-01-15 to 2025-11-15)"
    assert str(season) == expected
