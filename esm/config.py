# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
ESM_DIR = ROOT_DIR / "esm"
FRONTEND_DIR = ROOT_DIR / "frontend"


class Config:
    DATABASE_URL = os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(
        ESM_DIR, "app.db"
    )
    API_URL = "http://localhost:8000"  # FastAPI default port
