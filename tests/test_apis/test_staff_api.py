"""
Tests for the Staff API endpoints.
"""

from fastapi.testclient import TestClient
import pytest

from esm.models.staff import Department, JobTitle, ContractStatus, CoachType
from esm.models.moba_team import TeamRegion


@pytest.fixture
def create_test_team(client_fixture: TestClient):
    """Create a test team for staff assignments"""
    team_data = {
        "name": "T1",
        "region": TeamRegion.KR.value,
        "founded_date": "2019-02-25",
    }

    team_response = client_fixture.post("/api/teams", json=team_data)
    return team_response.json()


def test_get_staff(client_fixture: TestClient):
    """Test getting all staff members"""
    response = client_fixture.get("/api/staff")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_staff_by_id(client_fixture: TestClient):
    """Test getting a single staff member by ID"""
    # First create a staff member
    staff_data = {
        "name": "Kim Jeong-soo",
        "full_name": "Kim Jeong-soo",
        "nationality": "Korea",
        "date_of_birth": "1986-05-01",
        "department": Department.COACHING.value,
        "job_title": JobTitle.HEAD_COACH.value,
        "staff_type": CoachType.HEAD_COACH.value,
        "is_head_coach": True,
        "years_experience": 10,
        "contract_status": ContractStatus.SIGNED.value,
        "knowledge": 95,
        "work_rate": 90,
        "communication": 88,
        "adaptability": 92,
        "management": 94,
        "technical_skill": 85,
        "innovation": 89,
    }
    create_response = client_fixture.post("/api/staff", json=staff_data)
    assert create_response.status_code == 201
    staff_id = create_response.json()["id"]

    # Now get the staff member by ID
    response = client_fixture.get(f"/api/staff/{staff_id}")
    assert response.status_code == 200
    assert response.json()["id"] == staff_id
    assert response.json()["name"] == "Kim Jeong-soo"
    assert response.json()["job_title"] == JobTitle.HEAD_COACH.value


def test_create_staff(client_fixture: TestClient):
    """Test creating a new staff member"""
    staff_data = {
        "name": "Choi Seong-hoon",
        "full_name": "Choi Seong-hoon",
        "nationality": "Korea",
        "date_of_birth": "1989-10-18",
        "department": Department.COACHING.value,
        "job_title": JobTitle.ASSISTANT_COACH.value,
        "staff_type": CoachType.ASSISTANT_COACH.value,
        "years_experience": 5,
        "contract_status": ContractStatus.FREE_AGENT.value,
        "former_player": True,
        "knowledge": 88,
        "work_rate": 85,
        "communication": 90,
        "adaptability": 87,
        "management": 82,
        "technical_skill": 90,
        "innovation": 75,
    }

    response = client_fixture.post("/api/staff", json=staff_data)
    assert response.status_code == 201
    assert response.json()["name"] == "Choi Seong-hoon"
    assert "id" in response.json()


def test_update_staff(client_fixture: TestClient):
    """Test updating an existing staff member"""
    # First create a staff member
    staff_data = {
        "name": "Park Jae-seok",
        "full_name": "Park Jae-seok",
        "nationality": "Korea",
        "date_of_birth": "1988-07-22",
        "staff_type": "head_coach",
        "department": Department.ANALYSIS.value,
        "job_title": JobTitle.HEAD_ANALYST.value,
        "years_experience": 6,
        "contract_status": ContractStatus.SIGNED.value,
        "knowledge": 85,
        "work_rate": 80,
        "communication": 75,
        "adaptability": 70,
        "management": 65,
        "technical_skill": 90,
        "innovation": 85,
    }
    create_response = client_fixture.post("/api/staff", json=staff_data)
    staff_id = create_response.json()["id"]

    # Now update the staff member
    update_data = {
        "years_experience": 7,
        "management": 96,
        "contract_status": ContractStatus.SIGNED.value,
        "contract_start_date": "2023-01-01",
        "contract_end_date": "2025-12-31",
    }

    response = client_fixture.patch(f"/api/staff/{staff_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["years_experience"] == 7
    assert response.json()["management"] == 96
    assert response.json()["contract_status"] == ContractStatus.SIGNED.value
    assert response.json()["contract_start_date"] == "2023-01-01"
    assert response.json()["contract_end_date"] == "2025-12-31"


def test_delete_staff(client_fixture: TestClient):
    """Test deleting a staff member"""
    # First create a staff member
    staff_data = {
        "name": "Max Smith",
        "full_name": "Max Smith",
        "nationality": "UK",
        "date_of_birth": "1985-05-15",
        "department": Department.ANALYSIS.value,
        "job_title": JobTitle.HEAD_ANALYST.value,
        "staff_type": CoachType.STRATEGIC_COACH.value,
        "years_experience": 8,
        "contract_status": ContractStatus.SIGNED.value,
        "knowledge": 95,
        "work_rate": 90,
        "communication": 85,
        "adaptability": 88,
        "technical_skill": 98,
    }
    create_response = client_fixture.post("/api/staff", json=staff_data)
    staff_id = create_response.json()["id"]

    # Delete the staff member
    delete_response = client_fixture.delete(f"/api/staff/{staff_id}")
    assert delete_response.status_code == 204

    # Verify it's gone
    get_response = client_fixture.get(f"/api/staff/{staff_id}")
    assert get_response.status_code == 404


def test_assign_staff_to_team(client_fixture: TestClient):
    """Test assigning a staff member to a team"""
    # First create a team
    team_data = {
        "name": "T1",
        "tag": "T1",
        "region": "kr",
        "description": "Korean powerhouse esports team",
        "founded_date": "2019-01-01",
    }
    team_response = client_fixture.post("/api/teams", json=team_data)
    assert team_response.status_code == 201
    team_id = team_response.json()["id"]

    # Create a staff member
    staff_data = {
        "name": "Choi Seong-hoon",
        "full_name": "Choi Seong-hoon",
        "nationality": "Korea",
        "date_of_birth": "1988-10-10",
        "staff_type": CoachType.HEAD_COACH.value,
        "department": Department.COACHING.value,
        "job_title": JobTitle.HEAD_COACH.value,
        "years_experience": 8,
        "contract_status": ContractStatus.SIGNED.value,
        "knowledge": 92,
        "work_rate": 90,
        "communication": 88,
        "adaptability": 89,
        "management": 93,
        "technical_skill": 85,
        "innovation": 80,
    }
    create_response = client_fixture.post("/api/staff", json=staff_data)
    assert create_response.status_code == 201
    staff_id = create_response.json()["id"]

    # Assign staff to team
    response = client_fixture.post(f"/api/staff/{staff_id}/assign/{team_id}")
    assert response.status_code == 200
    assert response.json()["team_id"] == team_id

    # Get staff for team
    response = client_fixture.get(f"/api/teams/{team_id}/staff")
    assert response.status_code == 200
    staff_list = response.json()
    assert len(staff_list) > 0
    assert any(staff["id"] == staff_id for staff in staff_list)


def test_get_staff_by_department(client_fixture: TestClient):
    """Test filtering staff by department"""
    # Create staff members with different departments
    coaching_staff = {
        "name": "Coaching Staff",
        "full_name": "Coaching Staff Member",
        "nationality": "USA",
        "date_of_birth": "1990-01-01",
        "staff_type": "head_coach",
        "department": Department.COACHING.value,
        "job_title": JobTitle.HEAD_COACH.value,
        "years_experience": 5,
        "contract_status": ContractStatus.SIGNED.value,
        "knowledge": 85,
        "work_rate": 82,
        "communication": 78,
        "adaptability": 75,
        "management": 90,
        "technical_skill": 80,
        "innovation": 70,
    }
    client_fixture.post("/api/staff", json=coaching_staff)

    scouting_staff = {
        "name": "Scouting Staff",
        "full_name": "Scouting Staff Member",
        "nationality": "USA",
        "date_of_birth": "1990-01-01",
        "staff_type": "head_coach",
        "department": Department.SCOUTING.value,
        "job_title": JobTitle.HEAD_SCOUT.value,
        "years_experience": 5,
        "contract_status": ContractStatus.SIGNED.value,
        "knowledge": 90,
        "work_rate": 85,
        "communication": 75,
        "adaptability": 80,
        "management": 70,
        "technical_skill": 75,
        "innovation": 85,
    }
    client_fixture.post("/api/staff", json=scouting_staff)

    # Get only coaching department staff
    response = client_fixture.get(f"/api/staff?department={Department.COACHING.value}")
    assert response.status_code == 200
    staff_list = response.json()
    assert len(staff_list) >= 1
    # All returned staff should be from coaching department
    for staff in staff_list:
        assert staff["department"] == Department.COACHING.value

    # Get only scouting department staff
    response = client_fixture.get(f"/api/staff?department={Department.SCOUTING.value}")
    assert response.status_code == 200
    staff_list = response.json()
    assert len(staff_list) >= 1
    # All returned staff should be from scouting department
    for staff in staff_list:
        assert staff["department"] == Department.SCOUTING.value
