# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
"""Server rendered game registry pages handled by the frontend."""

from typing import Any

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from esm.config import FRONTEND_DIR
from esm.db import get_session
from esm.models.game import GameCreate, GameGenre
from esm.services.games import GameAlreadyExistsError, create_game
from frontend.context import page_context

game_routes = APIRouter(tags=["games_frontend"])

templates = Jinja2Templates(directory=FRONTEND_DIR / "templates")


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _error_message(exc: Exception) -> str:
    if isinstance(exc, ValidationError):
        first = exc.errors()[0]
        location = ".".join(str(part) for part in first.get("loc", ()))
        message = first.get("msg", "invalid value")
        return f"{location}: {message}" if location else message
    return str(exc)


async def _render_games_page(
    request: Request,
    session: AsyncSession,
    error: str | None = None,
    status_code: int = status.HTTP_200_OK,
):
    context = await page_context(session)
    context.update(
        {
            "request": request,
            "content": "pages/games.html",
            "current_page": "games",
            "error": error,
        }
    )
    return templates.TemplateResponse(
        request, "layout.html", context, status_code=status_code
    )


@game_routes.post("/games")
async def create_game_form(
    request: Request, session: AsyncSession = Depends(get_session)
):
    form = await request.form()
    name = _clean(form.get("name"))
    if name is None:
        return await _render_games_page(
            request, session, error="A game name is required", status_code=400
        )

    try:
        team_size = _clean(form.get("team_size"))
        payload = GameCreate(
            name=name,
            slug=_clean(form.get("slug")),
            abbreviation=_clean(form.get("abbreviation")),
            genre=GameGenre(_clean(form.get("genre")) or GameGenre.OTHER.value),
            publisher=_clean(form.get("publisher")),
            platform=_clean(form.get("platform")),
            team_size=int(team_size) if team_size else 5,
            description=_clean(form.get("description")),
        )
        await create_game(session, payload)
    except GameAlreadyExistsError as exc:
        return await _render_games_page(
            request, session, error=str(exc), status_code=status.HTTP_409_CONFLICT
        )
    except (ValueError, ValidationError) as exc:
        return await _render_games_page(
            request, session, error=_error_message(exc), status_code=400
        )

    return RedirectResponse("/page/games", status_code=status.HTTP_303_SEE_OTHER)
