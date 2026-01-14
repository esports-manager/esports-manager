# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import pytest
from esm.app import create_api
from esm.db import get_session


@pytest.fixture(name="session")
async def session_fixture() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(name="client")
async def client_fixture(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    app = create_api(lifespan=None)

    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True
    ) as client:
        yield client
    
    app.dependency_overrides.clear()
