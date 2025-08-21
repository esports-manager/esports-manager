# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from datetime import date
from fastapi.testclient import TestClient
from sqlmodel import Session

from esm.models.moba.staff import MobaStaff, MobaStaffRole
from esm.models.moba.team import MobaTeam


def _mk_staff(
    first_name: str, role: MobaStaffRole, years: int, nationality: str, team_id=None
):
    return MobaStaff(
        first_name=first_name,
        last_name="Test",
        date_of_birth=date(1990, 1, 1),
        nationality=nationality,
        role=role,
        years_experience=years,
        team_id=team_id,
    )


def test_staff_list_filters_pagination_sort(client: TestClient, session: Session):
    s1 = _mk_staff("A1", MobaStaffRole.ANALYST, 1, "X")
    s2 = _mk_staff("A2", MobaStaffRole.HEAD_COACH, 5, "Y")
    s3 = _mk_staff("A3", MobaStaffRole.ANALYST, 3, "X")
    session.add(s1)
    session.add(s2)
    session.add(s3)
    session.commit()
    session.refresh(s1)
    session.refresh(s2)
    session.refresh(s3)

    # Filter by role=analyst and nationality=X; sort years_experience desc; paginate per_page=1 page=2 -> should be the 2nd item (years=1)
    resp = client.get(
        "/api/moba/staff",
        params={
            "role": "analyst",
            "nationality": "X",
            "sort": "years_experience",
            "direction": "desc",
            "per_page": 1,
            "page": 2,
        },
    )
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["id"] == s1.id
    assert items[0]["years_experience"] == 1


def test_staff_list_filter_by_team(client: TestClient, session: Session):
    t1 = MobaTeam(name="T1", nationality="A", region="NA")
    t2 = MobaTeam(name="T2", nationality="B", region="EU")
    session.add(t1)
    session.add(t2)
    session.commit()
    session.refresh(t1)
    session.refresh(t2)

    s1 = _mk_staff("S1", MobaStaffRole.SCOUT, 2, "A", team_id=t1.id)
    s2 = _mk_staff("S2", MobaStaffRole.ANALYST, 3, "A", team_id=t2.id)
    s3 = _mk_staff("S3", MobaStaffRole.MEDIA_MANAGER, 1, "A", team_id=None)
    session.add(s1)
    session.add(s2)
    session.add(s3)
    session.commit()

    resp = client.get("/api/moba/staff", params={"team_id": t1.id})
    assert resp.status_code == 200
    body = resp.json()
    assert [it["id"] for it in body] == [s1.id]


def test_staff_list_search(client: TestClient, session: Session):
    s1 = _mk_staff("Alice", MobaStaffRole.ANALYST, 1, "A")
    s2 = _mk_staff("Bob", MobaStaffRole.HEAD_COACH, 2, "A")
    s2.last_name = "Johnson"
    s3 = _mk_staff("Carl", MobaStaffRole.DIRECTOR, 3, "A")
    s3.nick_name = "az"
    session.add(s1)
    session.add(s2)
    session.add(s3)
    session.commit()

    # first_name
    r1 = client.get("/api/moba/staff", params={"search": "ali"})
    assert r1.status_code == 200
    assert [i["first_name"] for i in r1.json()] == ["Alice"]

    # last_name
    r2 = client.get("/api/moba/staff", params={"search": "son"})
    assert r2.status_code == 200
    assert [i["last_name"] for i in r2.json()] == ["Johnson"]

    # nickname
    r3 = client.get("/api/moba/staff", params={"search": "az"})
    assert r3.status_code == 200
    assert [i["id"] for i in r3.json()] == [s3.id]


def test_staff_list_invalid_role_is_ignored(client: TestClient, session: Session):
    s1 = _mk_staff("A", MobaStaffRole.ANALYST, 1, "A")
    s2 = _mk_staff("B", MobaStaffRole.HEAD_COACH, 2, "A")
    session.add(s1)
    session.add(s2)
    session.commit()

    resp = client.get("/api/moba/staff", params={"role": "does_not_exist"})
    assert resp.status_code == 200
    ids = {it["id"] for it in resp.json()}
    assert ids == {s1.id, s2.id}
