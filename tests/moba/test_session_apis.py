# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from pathlib import Path

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel, select

from esm.models.moba.game_session import MobaGameSession
from esm.models.moba.team import MobaTeam
from esm.services.game_session import sqlite_path_from_url


async def _create_base_database(
    base_path: Path, team_name: str = "Base Team"
) -> tuple[str, int]:
    base_url = f"sqlite+aiosqlite:///{base_path.as_posix()}"
    engine = create_async_engine(
        base_url,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_maker() as session:
        base_team = MobaTeam(name=team_name)
        session.add(base_team)
        await session.commit()
        await session.refresh(base_team)
        team_id = base_team.id

    await engine.dispose()
    return base_url, team_id


async def test_create_session_copies_base_db(
    client: AsyncClient, tmp_path: Path
):
    base_db_path = tmp_path / "base.db"
    base_db_url, base_team_id = await _create_base_database(base_db_path)

    response = await client.post(
        "/api/moba/sessions",
        json={
            "manager_first_name": "Alex",
            "manager_last_name": "Stone",
            "manager_nickname": "Ace",
            "manager_birthdate": "1995-04-12",
            "manager_nationality": "Brazil",
            "team_id": base_team_id,
            "base_database_url": base_db_url,
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["base_database_url"] == base_db_url
    assert payload["manager_first_name"] == "Alex"
    assert payload["manager_last_name"] == "Stone"
    assert payload["manager_nickname"] == "Ace"
    assert payload["manager_birthdate"] == "1995-04-12"
    assert payload["manager_nationality"] == "Brazil"
    assert payload["manager_display_name"] == "Ace"
    assert payload["name"] == "Ace's Career"

    assert payload["id"]

    session_db_url = payload["session_database_url"]
    session_db_path = sqlite_path_from_url(session_db_url)
    assert session_db_path.exists()

    engine = create_async_engine(
        session_db_url,
        connect_args={"check_same_thread": False},
    )
    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_maker() as session_db:
        result = await session_db.execute(select(MobaGameSession))
        game_session = result.scalars().first()
        assert game_session is not None
        assert game_session.team_id == base_team_id

        result = await session_db.execute(
            select(MobaTeam).where(MobaTeam.name == "Base Team")
        )
        base_team = result.scalars().first()
        assert base_team is not None

    await engine.dispose()
    if session_db_path.exists():
        session_db_path.unlink()


async def test_list_sessions(client: AsyncClient, tmp_path: Path):
    base_db_path = tmp_path / "base_list.db"
    base_db_url, base_team_id = await _create_base_database(
        base_db_path, team_name="Roster Team"
    )

    create_response = await client.post(
        "/api/moba/sessions",
        json={
            "manager_first_name": "Riley",
            "manager_last_name": "Quinn",
            "team_id": base_team_id,
            "base_database_url": base_db_url,
            "name": "Riley Save",
        },
    )
    assert create_response.status_code == 201

    list_response = await client.get("/api/moba/sessions")
    assert list_response.status_code == 200
    sessions = list_response.json()
    assert len(sessions) == 1
    assert sessions[0]["name"] == "Riley Save"
    assert sessions[0]["manager_display_name"] == "Riley Quinn"

    session_db_url = sessions[0]["session_database_url"]
    session_db_path = sqlite_path_from_url(session_db_url)
    if session_db_path.exists():
        session_db_path.unlink()


async def test_get_current_session(client: AsyncClient, tmp_path: Path):
    base_db_path = tmp_path / "base_current.db"
    base_db_url, base_team_id = await _create_base_database(
        base_db_path, team_name="Current Team"
    )

    create_response = await client.post(
        "/api/moba/sessions",
        json={
            "manager_first_name": "Jordan",
            "manager_last_name": "Lane",
            "team_id": base_team_id,
            "base_database_url": base_db_url,
        },
    )
    assert create_response.status_code == 201
    payload = create_response.json()
    session_id = payload["id"]

    current_response = await client.get(
        f"/api/moba/sessions/current?session_id={session_id}"
    )
    assert current_response.status_code == 200
    current_payload = current_response.json()
    assert current_payload["id"] == session_id

    session_db_url = payload["session_database_url"]
    session_db_path = sqlite_path_from_url(session_db_url)
    if session_db_path.exists():
        session_db_path.unlink()
