import os

from fastapi import HTTPException, Request
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator, Optional


class DatabaseManager:
    def __init__(self, database_url: str):
        # Convert sqlite:/// to sqlite+aiosqlite:///
        if database_url.startswith("sqlite:///"):
            database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")

        echo_setting = os.getenv("ESM_SQL_ECHO", "").lower()
        echo_enabled = echo_setting in {"1", "true", "yes", "on"}
        self.engine = create_async_engine(database_url, echo=echo_enabled)
        self.async_session_maker = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def create_db_and_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.async_session_maker() as session:
            yield session


db_manager: DatabaseManager = None


async def get_session(request: Optional[Request] = None):
    if request:
        session_id = request.query_params.get("session_id")
    else:
        session_id = None

    if session_id:
        from esm.services.game_session import (
            normalize_session_id,
            session_db_context,
            session_db_path,
            sqlite_url_from_path,
        )

        try:
            resolved_session_id = normalize_session_id(session_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        db_path = session_db_path(resolved_session_id)
        if not db_path.exists():
            raise HTTPException(status_code=404, detail="Session not found")
        session_db_url = sqlite_url_from_path(db_path)
        async with session_db_context(session_db_url) as session:
            yield session
        return

    if not db_manager:
        raise Exception("Database manager not initialized")
    async for session in db_manager.get_session():
        yield session
