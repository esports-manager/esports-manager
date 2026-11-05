from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator


class DatabaseManager:
    def __init__(self, database_url: str):
        # Convert sqlite:/// to sqlite+aiosqlite:///
        if database_url.startswith("sqlite:///"):
            database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")
        
        self.engine = create_async_engine(database_url, echo=True)
        self.async_session_maker = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def create_db_and_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        await self._upgrade_legacy_schema()

    async def _upgrade_legacy_schema(self):
        """Add columns introduced after a database was first created.

        ``create_all`` only creates missing tables, it never alters existing
        ones. Games were added after the first tournaments, so databases
        created before that need their ``game_id`` column backfilled.
        """
        if not self.engine.url.drivername.startswith("sqlite"):
            return

        async with self.engine.begin() as conn:
            result = await conn.exec_driver_sql("PRAGMA table_info(moba_tournaments)")
            columns = {row[1] for row in result.fetchall()}
            if columns and "game_id" not in columns:
                await conn.exec_driver_sql(
                    "ALTER TABLE moba_tournaments "
                    "ADD COLUMN game_id INTEGER REFERENCES games(id)"
                )
                await conn.exec_driver_sql(
                    "CREATE INDEX IF NOT EXISTS ix_moba_tournaments_game_id "
                    "ON moba_tournaments (game_id)"
                )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.async_session_maker() as session:
            yield session


db_manager: DatabaseManager = None


async def get_session():
    if not db_manager:
        raise Exception("Database manager not initialized")
    async for session in db_manager.get_session():
        yield session
