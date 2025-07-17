import pytest
from datetime import date, datetime
from sqlmodel import SQLModel, Session, create_engine, select
from sqlmodel.pool import StaticPool
import random

# Import the models we'll be testing
from esm.models.moba_team import MobaTeam, TeamRegion
from esm.models.moba_player import (
    MobaPlayer,
    PlayerRole,
)
from esm.models.champion import Champion
from esm.models.match import Match, MatchType, MatchFormat, MatchStatus
from esm.models.match_performance import (
    MatchPerformance,
    MatchPlayerStats,
    MapResult,
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
    """Create sample teams for testing."""
    teams = []
    team_data = [
        ("T1", "T1", TeamRegion.KR, date(2019, 2, 25)),
        ("Cloud9", "C9", TeamRegion.NA, date(2013, 1, 1)),
    ]

    for name, tag, region, founded_date in team_data:
        team = MobaTeam(
            name=name,
            tag=tag,
            region=region,
            founded_date=founded_date,
        )
        session.add(team)
        teams.append(team)

    session.commit()
    for team in teams:
        session.refresh(team)

    return teams


@pytest.fixture
def create_players(session, create_teams):
    """Create sample players for testing."""
    teams = create_teams
    players = []

    # Create players for T1
    t1_players = [
        ("Lee", "Faker", "Kim", PlayerRole.MID, teams[0].id),
        ("Mun", "Oner", "Hyeon-jun", PlayerRole.JUNGLE, teams[0].id),
        ("Choi", "Zeus", "Woo-je", PlayerRole.TOP, teams[0].id),
        ("Lee", "Gumayusi", "Min-hyeong", PlayerRole.ADC, teams[0].id),
        ("Ryu", "Keria", "Min-seok", PlayerRole.SUPPORT, teams[0].id),
    ]

    # Create players for C9
    c9_players = [
        ("Nicolaj", "Jensen", "Jensen", PlayerRole.MID, teams[1].id),
        ("Robert", "Blaber", "Huang", PlayerRole.JUNGLE, teams[1].id),
        ("Ibrahim", "Fudge", "Allami", PlayerRole.TOP, teams[1].id),
        ("Kim", "Berserker", "Min-cheol", PlayerRole.ADC, teams[1].id),
        ("Jesper", "Zven", "Svenningsen", PlayerRole.SUPPORT, teams[1].id),
    ]

    for first_name, nickname, last_name, role, team_id in t1_players + c9_players:
        # Generate a random birth date between 2000 and 2005 for players
        birth_year = random.randint(2000, 2005)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(
            1, 28
        )  # Using 28 to avoid month/day validation issues

        player = MobaPlayer(
            # Required Person fields
            name=nickname,  # Use nickname as the required name field
            nationality="Korea"
            if "Kim" in (first_name, last_name)
            or "Ryu" in (first_name, last_name)
            or "Choi" in (first_name, last_name)
            or "Mun" in (first_name, last_name)
            else "USA",
            date_of_birth=date(birth_year, birth_month, birth_day),
            # MobaPlayer specific fields
            first_name=first_name,
            nickname=nickname,
            last_name=last_name,
            role=role,
            team_id=team_id,
            mechanics=85,
            game_knowledge=85,
            team_fighting=85,
            champion_pool_size=85,
            laning=85,
        )
        session.add(player)
        players.append(player)

    session.commit()
    for player in players:
        session.refresh(player)

    return players


@pytest.fixture
def create_champions(session):
    """Create sample champions for testing."""
    # Define some placeholder release dates
    champions = [
        Champion(
            name="Ahri",
            title="The Nine-Tailed Fox",
            primary_role=PlayerRole.MID,
            difficulty=6,
            release_date=date(2011, 12, 14),
        ),
        Champion(
            name="Lee Sin",
            title="The Blind Monk",
            primary_role=PlayerRole.JUNGLE,
            difficulty=8,
            release_date=date(2011, 4, 1),
        ),
        Champion(
            name="Darius",
            title="The Hand of Noxus",
            primary_role=PlayerRole.TOP,
            difficulty=5,
            release_date=date(2012, 5, 23),
        ),
        Champion(
            name="Jinx",
            title="The Loose Cannon",
            primary_role=PlayerRole.ADC,
            difficulty=7,
            release_date=date(2013, 10, 10),
        ),
        Champion(
            name="Thresh",
            title="The Chain Warden",
            primary_role=PlayerRole.SUPPORT,
            difficulty=7,
            release_date=date(2013, 1, 23),
        ),
    ]

    for champion in champions:
        session.add(champion)

    session.commit()
    for champion in champions:
        session.refresh(champion)

    return champions


@pytest.fixture
def create_match(session, create_teams):
    """Create a completed match for testing."""
    teams = create_teams

    match = Match(
        home_team_id=teams[0].id,
        away_team_id=teams[1].id,
        scheduled_date=datetime(2025, 6, 15, 18, 0, 0),
        completed_date=datetime(2025, 6, 15, 21, 0, 0),
        match_type=MatchType.REGULAR_SEASON,
        match_format=MatchFormat.BO3,
        venue="LoL Park, Seoul",
        status=MatchStatus.COMPLETED,
        home_team_score=2,
        away_team_score=1,
    )

    session.add(match)
    session.commit()
    session.refresh(match)

    return match


@pytest.fixture
def create_match_performance(session, create_match, create_players, create_champions):
    """Create match performance entries for a match."""
    match = create_match
    players = create_players
    champions = create_champions

    # Create map results
    map_results = [
        MapResult(
            match_id=match.id,
            map_number=1,
            winner_team_id=match.home_team_id,
            duration_minutes=35,
            blue_side_team_id=match.home_team_id,
            red_side_team_id=match.away_team_id,
            blue_side_gold=65000,
            red_side_gold=58000,
            blue_side_kills=15,
            red_side_kills=10,
            blue_side_towers=9,
            red_side_towers=4,
            blue_side_dragons=3,
            red_side_dragons=1,
            blue_side_barons=1,
            red_side_barons=0,
        ),
        MapResult(
            match_id=match.id,
            map_number=2,
            winner_team_id=match.away_team_id,
            duration_minutes=42,
            blue_side_team_id=match.away_team_id,
            red_side_team_id=match.home_team_id,
            blue_side_gold=72000,
            red_side_gold=68000,
            blue_side_kills=18,
            red_side_kills=14,
            blue_side_towers=10,
            red_side_towers=5,
            blue_side_dragons=4,
            red_side_dragons=1,
            blue_side_barons=2,
            red_side_barons=0,
        ),
        MapResult(
            match_id=match.id,
            map_number=3,
            winner_team_id=match.home_team_id,
            duration_minutes=28,
            blue_side_team_id=match.home_team_id,
            red_side_team_id=match.away_team_id,
            blue_side_gold=55000,
            red_side_gold=45000,
            blue_side_kills=20,
            red_side_kills=8,
            blue_side_towers=11,
            red_side_towers=2,
            blue_side_dragons=3,
            red_side_dragons=0,
            blue_side_barons=1,
            red_side_barons=0,
        ),
    ]

    for map_result in map_results:
        session.add(map_result)

    session.commit()

    # Create player performance entries
    performances = []

    # Create performance for T1 players (first 5 players)
    for i, player in enumerate(players[:5]):
        for map_num in range(1, 4):
            # Skip map 2 for player 0 (simulating substitution)
            if i == 0 and map_num == 2:
                continue

            # Select champion based on role
            champion_id = champions[min(i, len(champions) - 1)].id

            # Stats for winners are better than losers
            is_winner = map_num != 2

            kills = 5 if is_winner else 2
            deaths = 2 if is_winner else 5
            assists = 10 if is_winner else 7

            stats = MatchPlayerStats(
                player_id=player.id,
                match_id=match.id,
                map_number=map_num,
                team_id=match.home_team_id,
                champion_id=champion_id,
                kills=kills,
                deaths=deaths,
                assists=assists,
                cs=220 + i * 10,
                vision_score=25 + i * 5,
                gold_earned=12000 + i * 500,
                damage_dealt=25000 + i * 1000,
                healing=2000 if i == 4 else 500,  # Support has more healing
                damage_taken=15000 if i == 2 else 10000,  # Top laner takes more damage
                objectives_stolen=1 if i == 1 else 0,  # Jungler steals objectives
                skill_shots_hit=45,
                skill_shots_missed=15,
                crowd_control_score=100 + i * 20,
            )
            session.add(stats)
            performances.append(stats)

    # Create performance for C9 players (next 5 players)
    for i, player in enumerate(players[5:10]):
        for map_num in range(1, 4):
            # Skip map 3 for player 0 (simulating substitution)
            if i == 0 and map_num == 3:
                continue

            # Select champion based on role
            champion_id = champions[min(i, len(champions) - 1)].id

            # Stats for winners are better than losers
            is_winner = map_num == 2

            kills = 5 if is_winner else 2
            deaths = 2 if is_winner else 5
            assists = 10 if is_winner else 7

            stats = MatchPlayerStats(
                player_id=player.id,
                match_id=match.id,
                map_number=map_num,
                team_id=match.away_team_id,
                champion_id=champion_id,
                kills=kills,
                deaths=deaths,
                assists=assists,
                cs=220 + i * 10,
                vision_score=25 + i * 5,
                gold_earned=12000 + i * 500,
                damage_dealt=25000 + i * 1000,
                healing=2000 if i == 4 else 500,  # Support has more healing
                damage_taken=15000 if i == 2 else 10000,  # Top laner takes more damage
                objectives_stolen=1 if i == 1 else 0,  # Jungler steals objectives
                skill_shots_hit=45,
                skill_shots_missed=15,
                crowd_control_score=100 + i * 20,
            )
            session.add(stats)
            performances.append(stats)

    session.commit()

    # Create match performance record linking all these stats
    match_perf = MatchPerformance(
        id=1,  # Explicitly provide an ID for the composite primary key
        match_id=match.id,
    )
    session.add(match_perf)
    session.commit()

    return map_results, performances, match_perf


def test_map_result_creation(create_match_performance):
    """Test creating and retrieving map results."""
    map_results, _, _ = create_match_performance

    # Test first map
    map1 = map_results[0]
    assert map1.map_number == 1
    assert map1.duration_minutes == 35
    assert map1.blue_side_kills == 15
    assert map1.red_side_kills == 10

    # Test that map results track which team was on which side
    assert map1.blue_side_team_id != map_results[1].blue_side_team_id
    assert map1.red_side_team_id != map_results[1].red_side_team_id


def test_player_stats(create_match_performance, create_players):
    """Test player statistics tracking for a match."""
    _, player_stats, _ = create_match_performance

    # Get first player's stats
    faker_stats = None
    for stats in player_stats:
        if stats.player_id == create_players[0].id:
            faker_stats = stats
            break

    assert faker_stats is not None
    assert faker_stats.kills >= 0
    assert faker_stats.deaths >= 0
    assert faker_stats.assists >= 0

    # Test KDA calculation method
    expected_kda = (faker_stats.kills + faker_stats.assists) / max(
        1, faker_stats.deaths
    )
    assert faker_stats.kda == pytest.approx(expected_kda)


def test_player_substitutions(create_match_performance, create_players, session):
    """Test that player substitutions are properly tracked."""
    _, _, _ = create_match_performance

    # Query for player stats for each map
    map1_players = session.exec(
        select(MatchPlayerStats).where(MatchPlayerStats.map_number == 1)
    ).all()

    map2_players = session.exec(
        select(MatchPlayerStats).where(MatchPlayerStats.map_number == 2)
    ).all()

    map3_players = session.exec(
        select(MatchPlayerStats).where(MatchPlayerStats.map_number == 3)
    ).all()

    # We should have 5+5=10 players in map 1
    assert len(map1_players) == 10

    # In map 2, Faker was substituted, so 4+5=9 players
    assert len(map2_players) == 9

    # In map 3, C9 mid was substituted, so 5+4=9 players
    assert len(map3_players) == 9

    # Check that Faker's stats don't exist for map 2
    faker_in_map2 = any(
        ps.player_id == create_players[0].id and ps.map_number == 2
        for ps in map2_players
    )
    assert not faker_in_map2


def test_match_performance_aggregate(create_match_performance, create_match, session):
    """Test the match performance aggregation functionality."""
    map_results, player_stats, match_perf = create_match_performance
    match = create_match

    # Generate aggregate stats
    aggregate_stats = match_perf.aggregate_stats(session=session)

    # Check team stats
    assert len(aggregate_stats["team_stats"]) == 2

    # Check that the home team won 2 maps and away team won 1
    home_stats = next(
        (
            stats
            for stats in aggregate_stats["team_stats"]
            if stats["team_id"] == match.home_team_id
        ),
        None,
    )
    away_stats = next(
        (
            stats
            for stats in aggregate_stats["team_stats"]
            if stats["team_id"] == match.away_team_id
        ),
        None,
    )

    assert home_stats["maps_won"] == 2
    assert away_stats["maps_won"] == 1

    # Check player stats
    assert len(aggregate_stats["player_stats"]) > 0

    # Check that each player has aggregate stats across their played maps
    for player_stat in aggregate_stats["player_stats"]:
        assert "player_id" in player_stat
        assert "kills" in player_stat
        assert "deaths" in player_stat
        assert "assists" in player_stat
        assert "total_cs" in player_stat
        assert "avg_vision_score" in player_stat
        assert "kda" in player_stat
        assert "maps_played" in player_stat

        # Make sure the KDA is calculated correctly
        expected_kda = (player_stat["kills"] + player_stat["assists"]) / max(
            1, player_stat["deaths"]
        )
        assert player_stat["kda"] == pytest.approx(expected_kda)


def test_mvp_calculation(create_match_performance, session):
    """Test the MVP calculation functionality."""
    map_results, player_stats, match_perf = create_match_performance

    # Get MVP data
    mvp_data = match_perf.calculate_mvp(session=session)

    # Check that MVP was calculated
    assert "player_id" in mvp_data
    assert "score" in mvp_data
    assert "stats" in mvp_data

    # MVP score should be positive
    assert mvp_data["score"] > 0

    # MVP should have detailed stats
    assert len(mvp_data["stats"]) > 0


def test_get_player_performance_history(
    create_match_performance, create_players, session
):
    """Test retrieving a player's performance history."""
    _, player_stats, _ = create_match_performance
    faker = create_players[0]  # First player is Faker

    # Get performance history
    performance_history = MatchPlayerStats.get_player_history(session, faker.id)

    # Faker played in maps 1 and 3, so should have 2 entries
    assert len(performance_history) == 2

    # Check that history includes kills, deaths, assists
    for entry in performance_history:
        assert hasattr(entry, "kills")
        assert hasattr(entry, "deaths")
        assert hasattr(entry, "assists")
        assert hasattr(entry, "map_number")
        assert hasattr(entry, "match_id")


def test_str_representation(create_match_performance):
    """Test string representation of match performance models."""
    map_results, player_stats, _ = create_match_performance

    # Test MapResult representation
    map1 = map_results[0]
    expected = f"Map 1: Blue {map1.blue_side_kills}-{map1.red_side_kills} Red (Winner: {map1.winner_team_id})"
    assert str(map1) == expected

    # Test MatchPlayerStats representation
    player_stat = player_stats[0]
    expected = f"Player {player_stat.player_id} on Map {player_stat.map_number}: {player_stat.kills}/{player_stat.deaths}/{player_stat.assists}"
    assert str(player_stat) == expected
