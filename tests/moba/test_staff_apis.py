# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from datetime import date
from fastapi.testclient import TestClient
from sqlmodel import Session

from esm.models.moba.staff import MobaStaff, MobaStaffRole


def test_get_staff_empty(client: TestClient):
    response = client.get("/api/moba/staff")
    assert response.status_code == 200
    assert response.json() == []


def test_create_staff(client: TestClient, session: Session):
    response = client.post(
        "/api/moba/staff",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "nick_name": "JD",
            "date_of_birth": "1990-01-01",
            "nationality": "Testland",
            "role": "head_coach",
            "years_experience": 5,
        },
    )
    assert response.status_code == 201
    staff_id = response.json()["id"]
    staff = session.get(MobaStaff, staff_id)
    assert isinstance(staff, MobaStaff)
    assert staff.first_name == "John"
    assert staff.last_name == "Doe"
    assert staff.nick_name == "JD"
    assert staff.date_of_birth == date(1990, 1, 1)
    assert staff.nationality == "Testland"
    assert staff.role == MobaStaffRole.HEAD_COACH
    assert staff.years_experience == 5


def test_get_staff_by_id(client: TestClient, session: Session):
    staff = MobaStaff(
        first_name="Jane",
        last_name="Smith",
        date_of_birth=date(1992, 2, 2),
        nationality="Testland",
        role=MobaStaffRole.ANALYST,
        years_experience=3,
    )
    session.add(staff)
    session.commit()
    session.refresh(staff)

    response = client.get(f"/api/moba/staff/{staff.id}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == staff.id
    assert body["first_name"] == staff.first_name
    assert body["last_name"] == staff.last_name
    assert body["role"] == MobaStaffRole.ANALYST.value


def test_get_staff_by_id_not_found(client: TestClient):
    response = client.get("/api/moba/staff/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Staff not found"}


def test_update_staff(client: TestClient, session: Session):
    staff = MobaStaff(
        first_name="Alex",
        last_name="Johnson",
        date_of_birth=date(1991, 3, 3),
        nationality="Testland",
        role=MobaStaffRole.SCOUT,
        years_experience=2,
    )
    session.add(staff)
    session.commit()
    session.refresh(staff)

    response = client.patch(
        f"/api/moba/staff/{staff.id}",
        json={
            "first_name": "Alexander",
            "years_experience": 4,
            "role": "analyst",
        },
    )
    assert response.status_code == 200
    updated = session.get(MobaStaff, staff.id)
    assert updated.first_name == "Alexander"
    assert updated.years_experience == 4
    assert updated.role == MobaStaffRole.ANALYST


def test_delete_staff(client: TestClient, session: Session):
    staff = MobaStaff(
        first_name="Taylor",
        last_name="Lee",
        date_of_birth=date(1993, 4, 4),
        nationality="Testland",
        role=MobaStaffRole.MEDIA_MANAGER,
        years_experience=1,
    )
    session.add(staff)
    session.commit()
    session.refresh(staff)

    response = client.delete(f"/api/moba/staff/{staff.id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Staff deleted"}
    assert session.get(MobaStaff, staff.id) is None
