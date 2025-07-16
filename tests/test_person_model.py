import pytest
from datetime import date, timedelta
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool
from esm.models.person import Person


# Create a concrete test model that inherits from Person for database tests
class MockPerson(Person, table=True):
    """Test model that inherits from Person for database testing"""

    __tablename__ = "mock_person"


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


def test_person_creation():
    """Test creating a basic Person instance"""
    person = Person(
        name="Faker",
        full_name="Lee Sang-hyeok",
        nationality="South Korea",
        date_of_birth=date(1996, 5, 7),
    )

    assert person.name == "Faker"
    assert person.full_name == "Lee Sang-hyeok"
    assert person.nationality == "South Korea"
    assert person.date_of_birth == date(1996, 5, 7)
    assert person.bio is None
    assert person.image_url is None

    # Test default values
    assert person.created_at is not None
    assert person.updated_at is not None


def test_person_age_calculation():
    """Test the age calculation property"""
    today = date.today()

    # Test person with birthday today
    birth_date = date(today.year - 25, today.month, today.day)
    person = Person(
        name="TestPerson1", nationality="TestCountry", date_of_birth=birth_date
    )
    assert person.age == 25

    # Test person with birthday tomorrow (age should be one less)
    birth_date_tomorrow = date(today.year - 25, today.month, today.day) + timedelta(
        days=1
    )
    if birth_date_tomorrow.year == today.year:  # Handle year boundary
        birth_date_tomorrow = birth_date_tomorrow.replace(year=today.year - 25)
    person = Person(
        name="TestPerson2", nationality="TestCountry", date_of_birth=birth_date_tomorrow
    )
    assert person.age == 24

    # Test person with birthday yesterday
    birth_date_yesterday = date(today.year - 25, today.month, today.day) - timedelta(
        days=1
    )
    if birth_date_yesterday.year == today.year:  # Handle year boundary
        birth_date_yesterday = birth_date_yesterday.replace(year=today.year - 25)
    person = Person(
        name="TestPerson3",
        nationality="TestCountry",
        date_of_birth=birth_date_yesterday,
    )
    assert person.age == 25


def test_person_database_operations(session):
    """Test CRUD operations with Person inheritance model via TestPerson"""
    # Create a mock person that inherits from Person
    person = MockPerson(
        name="Caps",
        full_name="Rasmus Borregaard Winther",
        nationality="Denmark",
        date_of_birth=date(1999, 11, 17),
        bio="Famous mid laner for G2 Esports",
    )

    # Add to database
    session.add(person)
    session.commit()

    # Verify ID was assigned
    assert person.id is not None

    # Query from database
    retrieved_person = session.get(MockPerson, person.id)
    assert retrieved_person.name == "Caps"
    assert retrieved_person.nationality == "Denmark"
    assert retrieved_person.age == date.today().year - 1999 - (
        1 if (date.today().month, date.today().day) < (11, 17) else 0
    )

    # Update person
    retrieved_person.bio = "World-class mid laner for G2 Esports"
    session.add(retrieved_person)
    session.commit()

    # Verify update
    updated_person = session.get(MockPerson, person.id)
    assert updated_person.bio == "World-class mid laner for G2 Esports"

    # Delete person
    session.delete(updated_person)
    session.commit()

    # Verify deletion
    assert session.get(MockPerson, person.id) is None


def test_repr_method():
    """Test the __repr__ method of Person"""
    person = Person(name="Uzi", nationality="China", date_of_birth=date(1997, 4, 5))

    # Get the string representation
    repr_str = repr(person)

    # Should contain the name, nationality, and age
    assert "Uzi" in repr_str
    assert "China" in repr_str

    # Should contain the age (exact value will depend on current date)
    age = (
        date.today().year
        - 1997
        - (1 if (date.today().month, date.today().day) < (4, 5) else 0)
    )
    assert str(age) in repr_str
