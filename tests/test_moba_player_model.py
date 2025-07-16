import pytest
from datetime import date
from sqlmodel import SQLModel, Session, create_engine, select
from sqlmodel.pool import StaticPool

# Import the models we're testing
from esm.models.moba_player import (
    MobaPlayer,
    ROLE_MID,
    ROLE_ADC,
    ROLE_JUNGLE,
    ROLE_TOP,
    ROLE_SUPPORT,
)


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
def create_player(session) -> MobaPlayer:
    """Create a sample MobaPlayer for testing"""
    # Create the moba player directly with Person attributes
    player = MobaPlayer(
        name="Faker",
        full_name="Lee Sang-hyeok",
        nationality="South Korea",
        date_of_birth=date(1996, 5, 7),
        role=ROLE_MID,
        mechanics=95,
        game_knowledge=98,
        team_fighting=94,
        champion_pool_size=90,
        laning=92,
        contract_status="signed",
    )
    session.add(player)
    session.commit()

    # Refresh to ensure all attributes are loaded
    session.refresh(player)

    return player


def test_moba_player_creation(create_player):
    """Test creating a MobaPlayer instance"""
    player = create_player

    # Basic person attributes (inherited)
    assert player.name == "Faker"
    assert player.full_name == "Lee Sang-hyeok"
    assert player.nationality == "South Korea"

    # MOBA-specific attributes
    assert player.role == ROLE_MID
    assert player.mechanics == 95
    assert player.game_knowledge == 98
    assert player.team_fighting == 94
    assert player.champion_pool_size == 90
    assert player.laning == 92

    # Contract information
    assert player.contract_status == "signed"
    assert player.team_id is None  # No team assigned by default


def test_moba_player_role_assignment(session):
    """Test setting different roles for MobaPlayer"""
    # Create players with different roles
    roles = [ROLE_TOP, ROLE_JUNGLE, ROLE_MID, ROLE_ADC, ROLE_SUPPORT]

    players = []
    for i, role in enumerate(roles):
        player = MobaPlayer(
            name=f"Player{i}",
            nationality="Denmark",
            date_of_birth=date(1999, 11, 17),
            role=role,
            mechanics=80 + i,
        )
        session.add(player)
        players.append(player)

    session.commit()

    # Check each player has the correct role
    for i, role in enumerate(roles):
        assert players[i].role == role


def test_inheritance_model(session):
    """Test that the inheritance model works correctly"""
    # Create a moba player with person attributes
    player = MobaPlayer(
        name="Rookie",
        nationality="China",
        date_of_birth=date(1998, 4, 23),
        role=ROLE_MID,
        mechanics=93,
        game_knowledge=91,
    )
    session.add(player)
    session.commit()

    # Query the player and check both Person and MobaPlayer attributes
    queried_player = session.exec(
        select(MobaPlayer).where(MobaPlayer.name == "Rookie")
    ).first()

    # Test Person attributes
    assert queried_player.name == "Rookie"
    assert queried_player.nationality == "China"
    assert queried_player.date_of_birth == date(1998, 4, 23)

    # Test MobaPlayer attributes
    assert queried_player.role == ROLE_MID
    assert queried_player.mechanics == 93
    assert queried_player.game_knowledge == 91


def test_moba_player_overall_rating(create_player):
    """Test calculation of the overall rating"""
    player = create_player

    # With the given attributes, the overall rating should be:
    # (95*0.3 + 98*0.25 + 94*0.2 + 90*0.15 + 92*0.1)
    # = 28.5 + 24.5 + 18.8 + 13.5 + 9.2 = 94.5 -> 94 (round to nearest integer)
    assert player.overall_rating == 94

    # Test that changing attributes updates the rating
    player.mechanics = 80
    assert player.overall_rating == 90  # Recalculated with new mechanics value


def test_moba_player_database_operations(session):
    """Test CRUD operations with MobaPlayer using inheritance"""
    # Create
    player = MobaPlayer(
        name="Bjergsen",
        nationality="Denmark",
        date_of_birth=date(1996, 2, 21),
        role=ROLE_MID,
        mechanics=90,
        game_knowledge=92,
        champion_pool_size=89,
        team_fighting=87,
        laning=91,
        contract_status="signed",
        salary=400000.0,
    )
    session.add(player)
    session.commit()
    player_id = player.id

    # Read
    db_player = session.get(MobaPlayer, player_id)
    assert db_player.role == ROLE_MID
    assert db_player.mechanics == 90
    assert db_player.name == "Bjergsen"

    # Test query to get player by name
    statement = select(MobaPlayer).where(MobaPlayer.name == "Bjergsen")
    db_player2 = session.exec(statement).first()
    assert db_player2 is not None
    assert db_player2.id == player_id

    # Update
    db_player.role = ROLE_SUPPORT
    db_player.mechanics = 85
    session.add(db_player)
    session.commit()
    session.refresh(db_player)

    updated_player = session.get(MobaPlayer, player_id)
    assert updated_player.role == ROLE_SUPPORT
    assert updated_player.mechanics == 85

    # Delete
    session.delete(db_player)
    session.commit()
    assert session.get(MobaPlayer, player_id) is None


def test_champion_mastery(session):
    """Test champion mastery JSON functionality"""
    # Create a player directly
    player = MobaPlayer(
        name="ShowMaker",
        nationality="South Korea",
        date_of_birth=date(2000, 7, 22),
        role=ROLE_MID,
        mechanics=93,
    )
    session.add(player)
    session.commit()

    # Test getting empty champion mastery
    assert player.get_champion_mastery() == {}

    # Set champion mastery and test retrieval
    champion_mastery = {
        "Syndra": 95,
        "Zoe": 92,
        "LeBlanc": 91,
        "Azir": 89,
        "Viktor": 87,
    }
    player.set_champion_mastery(champion_mastery)
    session.add(player)
    session.commit()
    session.refresh(player)

    # Check that the mastery was stored and can be retrieved
    retrieved_mastery = player.get_champion_mastery()
    assert retrieved_mastery == champion_mastery

    # Update mastery and check updates
    champion_mastery["Syndra"] = 97  # Improve mastery
    champion_mastery["Ryze"] = 84  # Add new champion
    player.set_champion_mastery(champion_mastery)
    session.add(player)
    session.commit()
    session.refresh(player)

    # Check updates were saved
    updated_mastery = player.get_champion_mastery()
    assert updated_mastery["Syndra"] == 97
    assert updated_mastery["Ryze"] == 84
    assert len(updated_mastery) == 6
