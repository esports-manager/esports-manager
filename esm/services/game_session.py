# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
import asyncio
import shutil
from pathlib import Path
from typing import Optional
from uuid import uuid4

from esm.config import ESM_DIR

SESSION_DB_DIR = ESM_DIR / "sessions"


def sqlite_path_from_url(database_url: str) -> Path:
    if database_url.startswith("sqlite+aiosqlite:///"):
        path_str = database_url.replace("sqlite+aiosqlite:///", "")
    elif database_url.startswith("sqlite:///"):
        path_str = database_url.replace("sqlite:///", "")
    else:
        raise ValueError("Unsupported database URL")

    if path_str == ":memory:":
        raise ValueError("In-memory database cannot be used for session copies")

    return Path(path_str)


def sqlite_url_from_path(path: Path) -> str:
    return f"sqlite+aiosqlite:///{path.as_posix()}"


async def copy_base_database(
    base_database_url: str, session_db_name: Optional[str] = None
) -> str:
    base_path = sqlite_path_from_url(base_database_url)
    if not base_path.exists():
        raise FileNotFoundError(f"Base database not found: {base_path}")

    SESSION_DB_DIR.mkdir(parents=True, exist_ok=True)
    session_db_name = session_db_name or f"session_{uuid4().hex}.db"
    session_path = SESSION_DB_DIR / session_db_name

    await asyncio.to_thread(shutil.copy2, base_path, session_path)
    return sqlite_url_from_path(session_path)
