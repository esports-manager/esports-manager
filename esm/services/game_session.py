# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
import asyncio
from contextlib import asynccontextmanager
import logging
import re
import shutil
from pathlib import Path
from typing import AsyncGenerator, Optional
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from esm.config import ESM_DIR
from esm.db import DatabaseManager

logger = logging.getLogger("esm.services.game_session")

SESSION_DB_DIR = ESM_DIR / "sessions"
SESSION_DB_PREFIX = "session_"
SESSION_DB_SUFFIX = ".db"
SESSION_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def normalize_session_id(session_id: str) -> str:
    if session_id is None:
        raise ValueError("Session id is required")
    normalized = str(session_id).strip()
    if not normalized:
        raise ValueError("Session id is required")
    if not SESSION_ID_PATTERN.fullmatch(normalized):
        raise ValueError("Invalid session id")
    return normalized


def session_db_name(session_id: str) -> str:
    normalized = normalize_session_id(session_id)
    return f"{SESSION_DB_PREFIX}{normalized}{SESSION_DB_SUFFIX}"


def session_db_path(session_id: str) -> Path:
    return SESSION_DB_DIR / session_db_name(session_id)


def session_id_from_path(path: Path) -> str:
    filename = path.name
    if not filename.startswith(SESSION_DB_PREFIX) or not filename.endswith(
        SESSION_DB_SUFFIX
    ):
        raise ValueError("Invalid session database filename")
    return filename[len(SESSION_DB_PREFIX) : -len(SESSION_DB_SUFFIX)]


def list_session_db_paths() -> list[Path]:
    if not SESSION_DB_DIR.exists():
        return []
    return sorted(SESSION_DB_DIR.glob(f"{SESSION_DB_PREFIX}*{SESSION_DB_SUFFIX}"))


def sqlite_path_from_url(database_url: str) -> Path:
    if database_url.startswith("sqlite+aiosqlite:///"):
        path_str = database_url.replace("sqlite+aiosqlite:///", "")
    elif database_url.startswith("sqlite:///"):
        path_str = database_url.replace("sqlite:///", "")
    else:
        logger.warning("Unsupported database URL %s", database_url)
        raise ValueError("Unsupported database URL")

    if path_str == ":memory:":
        raise ValueError("In-memory database cannot be used for session copies")

    return Path(path_str)


def sqlite_url_from_path(path: Path) -> str:
    return f"sqlite+aiosqlite:///{path.as_posix()}"


async def ensure_base_database(base_database_url: str) -> None:
    base_path = sqlite_path_from_url(base_database_url)
    if base_path.exists():
        return
    base_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Base database missing, creating %s", base_path)
    db_manager = DatabaseManager(base_database_url)
    await db_manager.create_db_and_tables()
    await db_manager.engine.dispose()
    logger.info("Base database created %s", base_path)


@asynccontextmanager
async def session_db_context(
    database_url: str,
) -> AsyncGenerator[AsyncSession, None]:
    db_manager = DatabaseManager(database_url)
    async with db_manager.async_session_maker() as session:
        yield session
    await db_manager.engine.dispose()


async def copy_base_database(
    base_database_url: str, session_db_filename: Optional[str] = None
) -> str:
    await ensure_base_database(base_database_url)
    base_path = sqlite_path_from_url(base_database_url)
    if not base_path.exists():
        logger.warning(
            "Base database not found base_database_url=%s resolved_path=%s",
            base_database_url,
            base_path,
        )
        raise FileNotFoundError(f"Base database not found: {base_path}")

    SESSION_DB_DIR.mkdir(parents=True, exist_ok=True)
    session_db_filename = session_db_filename or session_db_name(uuid4().hex)
    session_path = SESSION_DB_DIR / session_db_filename

    logger.info("Copying base database to %s", session_path)
    await asyncio.to_thread(shutil.copy2, base_path, session_path)
    logger.info("Session database created at %s", session_path)
    return sqlite_url_from_path(session_path)
