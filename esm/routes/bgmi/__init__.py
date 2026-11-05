# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from fastapi import APIRouter

from .tournament import bgmi_tournament_routes

bgmi_router = APIRouter(
    prefix="/bgmi",
    tags=["bgmi"],
    responses={404: {"description": "Resource not found"}},
)

bgmi_router.include_router(bgmi_tournament_routes)
