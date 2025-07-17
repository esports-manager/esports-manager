import pytest
from datetime import date
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

# Import the models we're testing
from esm.models.staff import (
    Staff,
    # Enums
    CoachType,
    Department,
    JobTitle,
    CoachingStyle,
    ContractStatus,
)
from esm.models.moba_team import MobaTeam, TeamRegion


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
def create_staff(session) -> Staff:
    """Create a sample regular Staff member for testing"""
    # Create a staff member with Person attributes
    staff = Staff(
        name="Analyst1",
        full_name="John Data",
        nationality="United States",
        date_of_birth=date(1990, 5, 15),
        staff_type=CoachType.ASSISTANT_COACH,
        department=Department.ANALYSIS,
        job_title=JobTitle.DATA_ANALYST,
        years_experience=5,
        knowledge=85,
        technical_skill=88,
        innovation=82,
        communication=78,
        work_rate=90,
        adaptability=75,
        management=68,
        contract_status=ContractStatus.SIGNED,
        salary=65000.0,
    )
    session.add(staff)
    session.commit()

    # Refresh to ensure all attributes are loaded
    session.refresh(staff)

    return staff


@pytest.fixture
def create_coach(session) -> Staff:
    """Create a sample Coach (Staff member with coach type) for testing"""
    # Create a coach using the Staff model
    coach = Staff(
        name="CoachPro",
        full_name="Michael Strategy",
        nationality="South Korea",
        date_of_birth=date(1985, 10, 20),
        staff_type=CoachType.HEAD_COACH,
        department=Department.COACHING,
        job_title=JobTitle.HEAD_COACH,
        is_head_coach=True,
        years_experience=8,
        former_player=True,
        coaching_style=CoachingStyle.ANALYTICAL,
        # Coach skills
        tactics=92,
        player_development=85,
        motivation=88,
        game_knowledge=95,
        draft_skill=90,
        # General skills
        knowledge=90,
        communication=82,
        work_rate=88,
        contract_status=ContractStatus.SIGNED,
        salary=120000.0,
        contract_start_date=date.today().replace(year=date.today().year - 1),
        contract_end_date=date.today().replace(year=date.today().year + 2),
    )
    session.add(coach)
    session.commit()

    # Refresh to ensure all attributes are loaded
    session.refresh(coach)

    return coach


@pytest.fixture
def create_team_with_staff(session, create_staff, create_coach) -> MobaTeam:
    """Create a sample team with a staff member and coach for testing relationships"""
    staff = create_staff
    coach = create_coach

    team = MobaTeam(
        name="T1", tag="T1", region=TeamRegion.NA, founded_date=date(2019, 2, 25)
    )
    session.add(team)
    session.commit()
    session.refresh(team)

    # Link staff to team
    staff.team_id = team.id
    coach.team_id = team.id

    session.add(staff)
    session.add(coach)
    session.commit()
    session.refresh(staff)
    session.refresh(coach)
    session.refresh(team)

    return team


def test_overall_rating(create_staff, create_coach):
    """Test the overall_rating property of Staff for both regular staff and coach"""
    staff = create_staff
    coach = create_coach

    # Verify the regular staff overall rating is calculated correctly
    staff_rating = staff.overall_rating
    assert isinstance(staff_rating, int)
    assert 0 <= staff_rating <= 100

    # For an analyst with the skills we set, should be close to this range
    assert 80 <= staff_rating <= 90

    # Verify the coach overall rating is calculated correctly
    coach_rating = coach.overall_rating
    assert isinstance(coach_rating, int)
    assert 0 <= coach_rating <= 100

    # For a coach with the high skills we set, should be in this range
    assert 90 <= coach_rating <= 95


def test_json_fields(create_staff, create_coach):
    """Test JSON field getters and setters for both regular staff and coach"""
    staff = create_staff
    coach = create_coach

    # Test regular staff fields
    # Test achievements
    achievements = {"awards": ["Best Analyst 2022"], "recognition": "Top 5 Analysts"}
    staff.set_achievements(achievements)
    assert staff.get_achievements() == achievements

    # Test education
    education = [
        {"degree": "BSc Computer Science", "institution": "MIT", "year": 2015},
        {"degree": "MSc Data Science", "institution": "Stanford", "year": 2017},
    ]
    staff.set_education(education)
    assert staff.get_education() == education

    # Test certifications
    certifications = [
        {"name": "Advanced Analytics", "issuer": "Google", "year": 2019},
        {"name": "Esports Data Science", "issuer": "Riot Games", "year": 2020},
    ]
    staff.set_certifications(certifications)
    assert staff.get_certifications() == certifications

    # Test previous experience
    experience = [
        {"role": "Junior Analyst", "team": "TSM", "years": "2017-2019"},
        {"role": "Senior Analyst", "team": "Cloud9", "years": "2019-2022"},
    ]
    staff.set_previous_experience(experience)
    assert staff.get_previous_experience() == experience

    # Test coach-specific fields
    # Test specializations
    specializations = ["Draft Strategy", "Mid Lane", "Objective Control"]
    coach.set_specializations(specializations)
    assert coach.get_specializations() == specializations

    # Test previous teams
    previous_teams = [
        {"team": "SKT T1", "role": "Assistant Coach", "years": "2015-2018"},
        {"team": "Gen.G", "role": "Head Coach", "years": "2018-2021"},
    ]
    coach.set_previous_teams(previous_teams)
    assert coach.get_previous_teams() == previous_teams

    # Get session from an object
    session = staff.__dict__["_sa_instance_state"].session
    session.commit()

    # Test creating a new staff member with empty JSON fields
    new_staff = Staff(
        name="EmptyFields",
        nationality="Norway",
        date_of_birth=date(1990, 5, 15),
        department=Department.MEDICAL,
        job_title=JobTitle.TEAM_DOCTOR,
    )
    session.add(new_staff)
    session.commit()

    # Test getting empty JSON fields
    assert new_staff.get_certifications() == []
    assert new_staff.get_achievements() == {}

    # Set certifications and test retrieval
    certifications = [
        {
            "name": "Certified Sports Medicine Specialist",
            "provider": "American Board of Sports Medicine",
            "date_issued": "2018-05-20",
            "expiry_date": "2023-05-20",
        },
        {
            "name": "Advanced Life Support",
            "provider": "American Heart Association",
            "date_issued": "2020-02-15",
            "expiry_date": "2022-02-15",
        },
    ]
    staff.set_certifications(certifications)
    session.add(staff)
    session.commit()
    session.refresh(staff)

    # Check that the certifications were stored and can be retrieved
    retrieved_certs = staff.get_certifications()
    assert retrieved_certs == certifications
    assert retrieved_certs[0]["name"] == "Certified Sports Medicine Specialist"
    assert retrieved_certs[1]["provider"] == "American Heart Association"
    assert len(retrieved_certs) == 2

    # Update certifications and check updates
    certifications[1]["expiry_date"] = "2024-02-15"  # Renewed
    certifications.append(
        {
            "name": "Esports Medical Specialist",
            "provider": "International Esports Federation",
            "date_issued": "2022-07-10",
            "expiry_date": "2025-07-10",
        }
    )
    staff.set_certifications(certifications)
    session.add(staff)
    session.commit()
    session.refresh(staff)

    # Check updates were saved
    updated_certs = staff.get_certifications()
    assert len(updated_certs) == 3
    assert updated_certs[1]["expiry_date"] == "2024-02-15"
    assert updated_certs[2]["name"] == "Esports Medical Specialist"


def test_staff_previous_experience_json_handling(session):
    """Test JSON handling for previous experience"""
    # Create a staff member
    staff = Staff(
        name="ExpPro",
        nationality="United Kingdom",
        date_of_birth=date(1985, 11, 18),
        department=Department.PERFORMANCE,
        job_title=JobTitle.ASSISTANT_COACH,
        knowledge=82,
    )
    session.add(staff)
    session.commit()

    # Test getting empty previous experience
    assert staff.get_previous_experience() == []

    # Set previous experience and test retrieval
    previous_experience = [
        {
            "organization": "Cloud9",
            "position": "Performance Analyst",
            "start_date": "2018-01-01",
            "end_date": "2020-12-31",
            "responsibilities": [
                "Player performance tracking",
                "Training program development",
            ],
        },
        {
            "organization": "Team Liquid",
            "position": "Assistant Coach",
            "start_date": "2015-06-01",
            "end_date": "2017-12-31",
            "responsibilities": ["Draft strategy", "Player mentoring"],
        },
    ]
    staff.set_previous_experience(previous_experience)
    session.add(staff)
    session.commit()
    session.refresh(staff)

    # Check that the previous experience was stored and can be retrieved
    retrieved_experience = staff.get_previous_experience()
    assert retrieved_experience == previous_experience
    assert retrieved_experience[0]["organization"] == "Cloud9"
    assert retrieved_experience[1]["position"] == "Assistant Coach"
    assert len(retrieved_experience) == 2

    # Update previous experience and check updates
    previous_experience.append(
        {
            "organization": "100 Thieves",
            "position": "Head of Performance",
            "start_date": "2021-01-01",
            "end_date": "2022-12-31",
            "responsibilities": ["Department management", "Performance innovation"],
        }
    )
    staff.set_previous_experience(previous_experience)
    session.add(staff)
    session.commit()
    session.refresh(staff)

    # Check updates were saved
    updated_experience = staff.get_previous_experience()
    assert len(updated_experience) == 3
    assert updated_experience[2]["organization"] == "100 Thieves"
    assert updated_experience[2]["position"] == "Head of Performance"


def test_staff_team_relationship(create_team_with_staff):
    """Test the relationship between MobaTeam and Staff"""
    team = create_team_with_staff
    assert len(team.staff) == 2  # Should have both a regular staff member and a coach

    # Check that all staff members are linked to the team
    for staff_member in team.staff:
        assert staff_member.team_id == team.id
        assert staff_member.team == team

    # Check that we can find a regular staff and a coach
    staff_types = [s.staff_type for s in team.staff]
    assert CoachType.ASSISTANT_COACH in staff_types
    assert CoachType.HEAD_COACH in staff_types


def test_head_coach_property(create_team_with_staff):
    """Test the head_coach property on MobaTeam"""
    team = create_team_with_staff

    # Verify the head_coach property returns the correct coach
    head_coach = team.head_coach
    assert head_coach is not None
    assert head_coach.name == "CoachPro"
    assert head_coach.staff_type == CoachType.HEAD_COACH
    assert head_coach.is_head_coach

    # Change the head coach and verify the property updates
    session = head_coach.__dict__["_sa_instance_state"].session

    # Create a new coach
    new_coach = Staff(
        name="NewCoach",
        nationality="Brazil",
        date_of_birth=date(1982, 3, 10),
        staff_type=CoachType.HEAD_COACH,
        department=Department.COACHING,
        job_title=JobTitle.HEAD_COACH,
        is_head_coach=True,
        team_id=team.id,
    )
    session.add(new_coach)

    # Set the existing head coach to not be head coach anymore
    head_coach.is_head_coach = False
    session.add(head_coach)

    session.commit()

    # Verify the head_coach property now returns the new coach
    team_refreshed = session.get(MobaTeam, team.id)
    assert team_refreshed.head_coach.name == "NewCoach"
    assert team_refreshed.head_coach.is_head_coach

    # Create a new staff member
    new_staff = Staff(
        name="ScoutGuy",
        nationality="Canada",
        date_of_birth=date(1988, 6, 12),
        department=Department.SCOUTING,
        job_title=JobTitle.HEAD_SCOUT,
        team_id=team.id,
    )
    session.add(new_staff)
    session.commit()
    session.refresh(new_staff)
    session.refresh(team)

    # Team should now have four staff members (original staff + coach + new coach + new staff)
    assert len(team.staff) == 4
    assert "Analyst1" in [s.name for s in team.staff]
    assert "ScoutGuy" in [s.name for s in team.staff]


def test_contract_functions(session):
    """Test contract-related functions"""
    # Create staff with future contract end date
    future_staff = Staff(
        name="FutureStaff",
        nationality="Japan",
        date_of_birth=date(1990, 3, 15),
        department=Department.ANALYSIS,
        job_title=JobTitle.DATA_ANALYST,
        contract_status=ContractStatus.SIGNED,
        contract_start_date=date.today().replace(
            year=date.today().year - 1
        ),  # Last year
        contract_end_date=date.today().replace(year=date.today().year + 1),  # Next year
    )

    # Create staff with expired contract
    expired_staff = Staff(
        name="ExpiredStaff",
        nationality="Spain",
        date_of_birth=date(1985, 6, 20),
        department=Department.COACHING,
        job_title=JobTitle.ASSISTANT_COACH,
        contract_status=ContractStatus.SIGNED,
        contract_start_date=date.today().replace(
            year=date.today().year - 2
        ),  # 2 years ago
        contract_end_date=date.today().replace(year=date.today().year - 1),  # Last year
    )

    # Create staff with no contract
    no_contract_staff = Staff(
        name="FreelanceStaff",
        nationality="Italy",
        date_of_birth=date(1992, 9, 30),
        department=Department.PERFORMANCE,
        job_title=JobTitle.DATA_ANALYST,
        contract_status=ContractStatus.FREE_AGENT,
    )

    session.add(future_staff)
    session.add(expired_staff)
    session.add(no_contract_staff)
    session.commit()

    # Test is_contract_expired
    assert not future_staff.is_contract_expired()
    assert expired_staff.is_contract_expired()
    assert not no_contract_staff.is_contract_expired()  # No contract means not expired

    # Test contract_years_remaining
    assert future_staff.contract_years_remaining() > 0.9  # About 1 year remaining
    assert future_staff.contract_years_remaining() < 1.1  # About 1 year remaining
    assert expired_staff.contract_years_remaining() == 0.0
    assert no_contract_staff.contract_years_remaining() == 0.0


def test_str_representation(create_staff):
    """Test string representation of Staff"""
    staff = create_staff
    expected_str = f"<Staff: Analyst1 (United States, Dept: {Department.ANALYSIS.value}, Role: {JobTitle.DATA_ANALYST.value})>"
    assert str(staff) == expected_str
    assert repr(staff) == expected_str
