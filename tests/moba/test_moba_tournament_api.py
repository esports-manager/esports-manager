# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from fastapi.testclient import TestClient
from sqlmodel import Session
from datetime import datetime

from esm.models.moba.tournament import (
    MobaTournament,
)
from esm.models.tournament import TournamentType, TournamentFormat, TournamentTier


def test_get_tournaments_empty(client: TestClient):
    resp = client.get("/api/moba/tournaments")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_and_get_tournament(client: TestClient, session: Session):
    payload = {
        "name": "LCK Summer 2025",
        "abbreviation": "LCK 2025",
        "type": TournamentType.REGIONAL.value,
        "format": TournamentFormat.LEAGUE.value,
        "tier": TournamentTier.LEAGUE.value,
        "start_date": "2025-06-01T00:00:00",
        "end_date": "2025-08-10T00:00:00",
        "location": "Korea",
        "description": "Top Korean league split.",
        "banner_path": None,
        "default_color": "#111111",
        "logo_path": "/assets/tournaments/lck.png",
    }
    r = client.post("/api/moba/tournaments", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == payload["name"]
    assert data["abbreviation"] == payload["abbreviation"]
    assert data["type"] == payload["type"]
    assert data["format"] == payload["format"]
    assert data["tier"] == payload["tier"]
    assert data["location"] == payload["location"]
    assert data["default_color"] == payload["default_color"]

    tid = data["id"]

    # Fetch by id
    gr = client.get(f"/api/moba/tournaments/{tid}")
    assert gr.status_code == 200
    assert gr.json()["id"] == tid


def test_update_tournament(client: TestClient, session: Session):
    # Seed a tournament directly
    t = MobaTournament(
        name="MSI 2025",
        abbreviation="MSI",
        type=TournamentType.INTERNATIONAL,
        format=TournamentFormat.GSL,
        tier=TournamentTier.MAJOR,
        start_date=datetime(2025, 5, 1),
        end_date=datetime(2025, 5, 20),
        location="UK",
        default_color="#222222",
    )
    session.add(t)
    session.commit()
    session.refresh(t)

    ur = client.patch(
        f"/api/moba/tournaments/{t.id}",
        json={
            "name": "MSI 2025 London",
            "location": "London",
            "default_color": "#333333",
        },
    )
    assert ur.status_code == 200
    body = ur.json()
    assert body["name"] == "MSI 2025 London"
    assert body["location"] == "London"
    assert body["default_color"] == "#333333"


def test_delete_tournament(client: TestClient, session: Session):
    t = MobaTournament(
        name="EU Masters 2025",
        abbreviation="EUM",
        type=TournamentType.REGIONAL,
        format=TournamentFormat.DOUBLE_ELIMINATION,
        tier=TournamentTier.MINOR,
    )
    session.add(t)
    session.commit()
    session.refresh(t)

    dr = client.delete(f"/api/moba/tournaments/{t.id}")
    assert dr.status_code == 204
    assert session.get(MobaTournament, t.id) is None
