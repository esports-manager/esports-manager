import pytest
from datetime import date
from sqlmodel import SQLModel, Session, create_engine, select
from sqlmodel.pool import StaticPool

# Import the models we're testing
from esm.models.moba_team import MobaTeam, TeamRegion
from esm.models.moba_player import MobaPlayer, PlayerRole, ContractStatus


@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    """Create a new database session for a test"""
    with Session(in_memory_db) as session:
        yield session


@pytest.fixture
def create_team(session) -> MobaTeam:
    """Create a sample MobaTeam for testing"""
    team = MobaTeam(
        name="T1",
        tag="T1",
        region=TeamRegion.KR,
        founded_date=date(2019, 2, 25),  # T1 rebranded from SKT in 2019
        logo_path="assets/images/teams/t1_logo.png",
        description="The most successful League of Legends team in history.",
        home_venue="LoL Park, Seoul",
        current_ranking=1,
        organization_value=100000000.0,
        yearly_revenue=25000000.0,
        salary_cap=3000000.0,
    )
    session.add(team)
    session.commit()
    session.refresh(team)
    return team


@pytest.fixture
def create_team_with_players(session, create_team) -> MobaTeam:
    """Create a sample team with players for testing relationships"""
    team = create_team

    # Create players with different roles
    roles = [
        PlayerRole.TOP,
        PlayerRole.JUNGLE,
        PlayerRole.MID,
        PlayerRole.ADC,
        PlayerRole.SUPPORT,
    ]
    names = ["Zeus", "Oner", "Faker", "Gumayusi", "Keria"]

    for i, (role, name) in enumerate(zip(roles, names)):
        player = MobaPlayer(
            name=name,
            nationality="South Korea",
            date_of_birth=date(2000, 1, 1),
            role=role,
            mechanics=90 + i,
            game_knowledge=88 + i,
            team_fighting=85 + i,
            champion_pool_size=82 + i,
            laning=89 + i,
            contract_status=ContractStatus.SIGNED,
            team_id=team.id,
        )
        session.add(player)

    # Add a substitute player
    sub_player = MobaPlayer(
        name="Substitute",
        nationality="South Korea",
        date_of_birth=date(2002, 5, 15),
        role=PlayerRole.MID,
        mechanics=82,
        game_knowledge=80,
        team_id=team.id,
    )
    session.add(sub_player)

    session.commit()
    session.refresh(team)
    return team


def test_moba_team_creation(create_team):
    """Test creating a MobaTeam instance"""
    team = create_team

    # Basic team attributes
    assert team.name == "T1"
    assert team.tag == "T1"
    assert team.region == TeamRegion.KR
    assert team.founded_date == date(2019, 2, 25)
    assert team.logo_path == "assets/images/teams/t1_logo.png"
    assert team.description == "The most successful League of Legends team in history."
    assert team.home_venue == "LoL Park, Seoul"
    assert team.current_ranking == 1

    # Financial data
    assert team.organization_value == 100000000.0
    assert team.yearly_revenue == 25000000.0
    assert team.salary_cap == 3000000.0

    # Default values
    assert team.head_coach is None  # Using head_coach property instead of coach_id
    assert team.staff == []  # Should have empty staff list
    assert team.players == []
    assert team.achievements is None
    assert team.social_media is None
    assert team.sponsors is None


def test_moba_team_database_operations(session):
    """Test CRUD operations with MobaTeam"""
    # Create
    team = MobaTeam(
        name="Cloud9",
        tag="C9",
        region=TeamRegion.NA,
        founded_date=date(2013, 1, 1),
        current_ranking=2,
    )
    session.add(team)
    session.commit()
    team_id = team.id

    # Read
    db_team = session.get(MobaTeam, team_id)
    assert db_team.name == "Cloud9"
    assert db_team.tag == "C9"
    assert db_team.region == TeamRegion.NA

    # Query to get team by name
    statement = select(MobaTeam).where(MobaTeam.name == "Cloud9")
    db_team2 = session.exec(statement).first()
    assert db_team2 is not None
    assert db_team2.id == team_id

    # Update
    db_team.current_ranking = 1
    db_team.organization_value = 50000000.0
    session.add(db_team)
    session.commit()
    session.refresh(db_team)

    updated_team = session.get(MobaTeam, team_id)
    assert updated_team.current_ranking == 1
    assert updated_team.organization_value == 50000000.0

    # Delete
    session.delete(db_team)
    session.commit()
    assert session.get(MobaTeam, team_id) is None


def test_achievements_json_handling(session):
    """Test achievements JSON field handling"""
    team = MobaTeam(
        name="G2 Esports",
        tag="G2",
        region=TeamRegion.EU,
    )
    session.add(team)
    session.commit()

    # Test getting empty achievements
    assert team.get_achievements() == {}

    # Set achievements and test retrieval
    achievements = {
        "LEC_titles": 9,
        "MSI_titles": 1,
        "Worlds_finals": 1,
        "years": [2019, 2020, 2021, 2022, 2023],
        "notable_achievements": {
            "2019": "MSI Champions, Worlds Finalist",
            "2020": "LEC Spring and Summer Champions",
        },
    }
    team.set_achievements(achievements)
    session.add(team)
    session.commit()
    session.refresh(team)

    # Check that achievements were stored and can be retrieved
    retrieved_achievements = team.get_achievements()
    assert retrieved_achievements == achievements
    assert retrieved_achievements["LEC_titles"] == 9
    assert retrieved_achievements["years"] == [2019, 2020, 2021, 2022, 2023]

    # Update achievements and check updates
    achievements["LEC_titles"] = 10  # Add another title
    achievements["notable_achievements"]["2023"] = "LEC Winter Champion"
    team.set_achievements(achievements)
    session.add(team)
    session.commit()
    session.refresh(team)

    # Check updates were saved
    updated_achievements = team.get_achievements()
    assert updated_achievements["LEC_titles"] == 10
    assert updated_achievements["notable_achievements"]["2023"] == "LEC Winter Champion"


def test_social_media_json_handling(session):
    """Test social media JSON field handling"""
    team = MobaTeam(
        name="Fnatic",
        tag="FNC",
        region=TeamRegion.EU,
    )
    session.add(team)
    session.commit()

    # Test getting empty social media
    assert team.get_social_media() == {}

    # Set social media and test retrieval
    social_media = {
        "twitter": "https://twitter.com/FNATIC",
        "instagram": "https://instagram.com/fnatic",
        "facebook": "https://facebook.com/fnatic",
        "youtube": "https://youtube.com/fnatic",
        "twitch": "https://twitch.tv/fnatic",
    }
    team.set_social_media(social_media)
    session.add(team)
    session.commit()
    session.refresh(team)

    # Check that social media was stored and can be retrieved
    retrieved_social_media = team.get_social_media()
    assert retrieved_social_media == social_media
    assert retrieved_social_media["twitter"] == "https://twitter.com/FNATIC"

    # Update social media and check updates
    social_media["tiktok"] = "https://tiktok.com/@fnatic"
    team.set_social_media(social_media)
    session.add(team)
    session.commit()
    session.refresh(team)

    # Check updates were saved
    updated_social_media = team.get_social_media()
    assert updated_social_media["tiktok"] == "https://tiktok.com/@fnatic"
    assert len(updated_social_media) == 6


def test_sponsors_json_handling(session):
    """Test sponsors JSON field handling"""
    team = MobaTeam(
        name="100 Thieves",
        tag="100T",
        region=TeamRegion.NA,
    )
    session.add(team)
    session.commit()

    # Test getting empty sponsors
    assert team.get_sponsors() == []

    # Set sponsors and test retrieval
    sponsors = [
        {
            "name": "Cash App",
            "type": "Main Sponsor",
            "deal_value": 5000000,
            "start_date": "2022-01-01",
            "end_date": "2024-12-31",
        },
        {
            "name": "JBL",
            "type": "Technology Partner",
            "deal_value": 2000000,
            "start_date": "2021-01-01",
            "end_date": "2023-12-31",
        },
    ]
    team.set_sponsors(sponsors)
    session.add(team)
    session.commit()
    session.refresh(team)

    # Check that sponsors were stored and can be retrieved
    retrieved_sponsors = team.get_sponsors()
    assert len(retrieved_sponsors) == 2
    assert retrieved_sponsors[0]["name"] == "Cash App"
    assert retrieved_sponsors[1]["name"] == "JBL"
    assert retrieved_sponsors[0]["deal_value"] == 5000000

    # Update sponsors and check updates
    sponsors.append(
        {
            "name": "AT&T",
            "type": "Technology Partner",
            "deal_value": 3000000,
            "start_date": "2023-01-01",
            "end_date": "2025-12-31",
        }
    )
    team.set_sponsors(sponsors)
    session.add(team)
    session.commit()
    session.refresh(team)

    # Check updates were saved
    updated_sponsors = team.get_sponsors()
    assert len(updated_sponsors) == 3
    assert updated_sponsors[2]["name"] == "AT&T"


def test_team_player_relationship(create_team_with_players):
    """Test relationship between MobaTeam and MobaPlayer"""
    team = create_team_with_players

    # Test that team has players
    assert len(team.players) == 6  # 5 main roster + 1 substitute

    # Verify player roles
    roles = [player.role for player in team.players]
    assert PlayerRole.TOP in roles
    assert PlayerRole.JUNGLE in roles
    assert PlayerRole.MID in roles
    assert PlayerRole.ADC in roles
    assert PlayerRole.SUPPORT in roles

    # Verify specific player
    faker = next(player for player in team.players if player.name == "Faker")
    assert faker.role == PlayerRole.MID
    assert faker.team_id == team.id

    # Test adding a new player to the team
    session = team.__dict__["_sa_instance_state"].session
    new_player = MobaPlayer(
        name="Bengi",
        nationality="South Korea",
        date_of_birth=date(1993, 9, 7),
        role=PlayerRole.JUNGLE,
        mechanics=85,
        game_knowledge=95,
        team_id=team.id,
    )
    session.add(new_player)
    session.commit()
    session.refresh(team)

    assert len(team.players) == 7
    bengi = next(player for player in team.players if player.name == "Bengi")
    assert bengi.role == PlayerRole.JUNGLE


def test_get_roster_by_role(create_team_with_players):
    """Test get_roster_by_role method"""
    team = create_team_with_players
    roster = team.get_roster_by_role()

    # Check that each role has the correct number of players
    assert len(roster[PlayerRole.TOP]) == 1
    assert len(roster[PlayerRole.JUNGLE]) == 1
    assert len(roster[PlayerRole.MID]) == 2  # Faker + substitute
    assert len(roster[PlayerRole.ADC]) == 1
    assert len(roster[PlayerRole.SUPPORT]) == 1

    # Check specific players in roles
    assert roster[PlayerRole.TOP][0].name == "Zeus"
    assert roster[PlayerRole.JUNGLE][0].name == "Oner"

    # Check both mid laners
    mid_names = [player.name for player in roster[PlayerRole.MID]]
    assert "Faker" in mid_names
    assert "Substitute" in mid_names


def test_calculate_avg_player_rating(create_team_with_players, session):
    """Test calculate_avg_player_rating method"""
    team = create_team_with_players

    # Calculate the expected average manually
    total_rating = 0
    for player in team.players:
        total_rating += player.overall_rating
    expected_avg = total_rating / len(team.players)

    # Test the method
    assert team.calculate_avg_player_rating() == expected_avg

    # Test with empty team
    empty_team = MobaTeam(
        name="Empty Team",
        tag="ET",
        region=TeamRegion.OTHER,
    )
    session.add(empty_team)
    session.commit()

    assert empty_team.calculate_avg_player_rating() == 0.0


def test_years_active(session):
    """Test years_active method"""
    # Test with a team founded in the past
    old_team = MobaTeam(
        name="SKT T1",
        tag="SKT",
        region=TeamRegion.KR,
        founded_date=date(2013, 3, 1),
    )
    session.add(old_team)

    # Test with a recently founded team
    new_team = MobaTeam(
        name="GenG",
        tag="GEN",
        region=TeamRegion.KR,
        founded_date=date(2017, 5, 10),
    )
    session.add(new_team)

    # Test with future date (should return 0)
    future_team = MobaTeam(
        name="Future Team",
        tag="FT",
        region=TeamRegion.EU,
        founded_date=date(2099, 1, 1),
    )
    session.add(future_team)

    # Test with no founding date
    unknown_team = MobaTeam(
        name="Unknown Team",
        tag="UT",
        region=TeamRegion.NA,
    )
    session.add(unknown_team)

    session.commit()

    # Calculate expected years
    today = date.today()
    old_team_years = today.year - 2013
    if (today.month, today.day) < (3, 1):
        old_team_years -= 1

    new_team_years = today.year - 2017
    if (today.month, today.day) < (5, 10):
        new_team_years -= 1

    # Assert years active
    assert old_team.years_active() == old_team_years
    assert new_team.years_active() == new_team_years
    assert future_team.years_active() == 0
    assert unknown_team.years_active() == 0


def test_str_representation(create_team):
    """Test string representation of MobaTeam"""
    team = create_team
    expected_str = f"<MobaTeam: T1 (T1, {TeamRegion.KR.value})>"
    assert str(team) == expected_str
    assert repr(team) == expected_str
