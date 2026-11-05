# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
"""Server rendered tournament pages: details and the create form."""

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from esm.config import FRONTEND_DIR
from esm.db import get_session
from esm.models.bgmi.tournament import (
    DEFAULT_MAP_POOL,
    BgmiGameMode,
    BgmiTournament,
    BgmiTournamentCreate,
)
from esm.models.bgmi.tournament_participant import BgmiTournamentParticipant
from esm.models.game import Game, TournamentSystem
from esm.models.moba.team import MobaTeam, MobaTeamPublic
from esm.models.moba.tournament import MobaTournament, MobaTournamentCreate
from esm.models.moba.tournament_participant import MobaTournamentParticipant
from esm.models.tournament import (
    TournamentFormat,
    TournamentStatus,
    TournamentTier,
    TournamentType,
)
from esm.services.games import get_game_by_slug
from frontend.context import page_context

tournament_routes = APIRouter(tags=["tournaments_frontend"])

templates = Jinja2Templates(directory=FRONTEND_DIR / "templates")


def _clean(value: Any) -> str | None:
    """Normalize a form value to a trimmed string or None."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _parse_date(value: Any) -> date | None:
    text = _clean(value)
    if text is None:
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        raise ValueError(f"'{text}' is not a valid date (expected YYYY-MM-DD)")


def _parse_int(value: Any, field: str, default: int) -> int:
    text = _clean(value)
    if text is None:
        return default
    try:
        return int(text)
    except ValueError:
        raise ValueError(f"'{text}' is not a valid number for {field}")


def _tournament_payload(form: Any) -> dict[str, Any]:
    """Fields shared by every tournament flavour."""
    name = _clean(form.get("name"))
    if name is None:
        raise ValueError("A tournament name is required")

    return {
        "name": name,
        "abbreviation": _clean(form.get("abbreviation")),
        "type": TournamentType(
            _clean(form.get("type")) or TournamentType.REGIONAL.value
        ),
        "format": TournamentFormat(
            _clean(form.get("format")) or TournamentFormat.LEAGUE.value
        ),
        "tier": TournamentTier(_clean(form.get("tier")) or TournamentTier.LEAGUE.value),
        "status": TournamentStatus(
            _clean(form.get("status")) or TournamentStatus.NOT_STARTED.value
        ),
        "start_date": _parse_date(form.get("start_date")),
        "end_date": _parse_date(form.get("end_date")),
        "location": _clean(form.get("location")),
        "description": _clean(form.get("description")),
        "default_color": _clean(form.get("default_color")),
        "logo_path": _clean(form.get("logo_path")),
    }


def _bgmi_payload(form: Any) -> dict[str, Any]:
    map_pool = [str(value) for value in form.getlist("map_pool") if str(value).strip()]
    return {
        "game_mode": BgmiGameMode(_clean(form.get("game_mode")) or "squad"),
        "map_pool": map_pool or list(DEFAULT_MAP_POOL),
        "points_per_kill": _parse_int(
            form.get("points_per_kill"), "points per kill", 1
        ),
        "teams_per_lobby": _parse_int(
            form.get("teams_per_lobby"), "teams per lobby", 16
        ),
        "match_count": _parse_int(form.get("match_count"), "match count", 6),
    }


def _error_message(exc: Exception) -> str:
    if isinstance(exc, ValidationError):
        first = exc.errors()[0]
        location = ".".join(str(part) for part in first.get("loc", ()))
        message = first.get("msg", "invalid value")
        return f"{location}: {message}" if location else message
    return str(exc)


async def _render_page(
    request: Request,
    session: AsyncSession,
    template: str,
    current_page: str,
    extra: dict[str, Any] | None = None,
    error: str | None = None,
    status_code: int = 200,
):
    context = await page_context(session)
    context.update(
        {
            "request": request,
            "content": template,
            "current_page": current_page,
            "error": error,
        }
    )
    if extra:
        context.update(extra)
    return templates.TemplateResponse(
        request, "layout.html", context, status_code=status_code
    )


@tournament_routes.post("/tournaments")
async def create_tournament_form(
    request: Request, session: AsyncSession = Depends(get_session)
):
    form = await request.form()
    game_slug = _clean(form.get("game"))
    game = await get_game_by_slug(session, game_slug) if game_slug else None

    if game is None:
        return await _render_page(
            request,
            session,
            "pages/tournaments.html",
            "tournaments",
            error="Choose a game for the new tournament.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    system = game.tournament_system
    if system is None:
        return await _render_page(
            request,
            session,
            "pages/tournaments.html",
            "tournaments",
            error=f"'{game.name}' does not have a tournament format yet.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        payload = _tournament_payload(form)
        if system is TournamentSystem.BGMI:
            tournament = BgmiTournament.model_validate(
                BgmiTournamentCreate(**payload, game_id=game.id, **_bgmi_payload(form))
            )
            session.add(tournament)
            await session.commit()
            await session.refresh(tournament)
            return RedirectResponse(
                f"/tournaments/bgmi/{tournament.id}",
                status_code=status.HTTP_303_SEE_OTHER,
            )

        tournament = MobaTournament.model_validate(
            MobaTournamentCreate(**payload, game_id=game.id)
        )
        session.add(tournament)
        await session.commit()
        await session.refresh(tournament)
        return RedirectResponse(
            f"/tournaments/{tournament.id}", status_code=status.HTTP_303_SEE_OTHER
        )
    except (ValueError, ValidationError) as exc:
        return await _render_page(
            request,
            session,
            "pages/tournaments.html",
            "tournaments",
            error=_error_message(exc),
            status_code=status.HTTP_400_BAD_REQUEST,
        )


async def _participating_team_ids(session: AsyncSession, id: int) -> list[int]:
    result = await session.execute(
        select(BgmiTournamentParticipant).where(
            BgmiTournamentParticipant.tournament_id == id
        )
    )
    return [participant.team_id for participant in result.scalars().all()]


@tournament_routes.get("/tournaments/bgmi/{id}")
async def get_bgmi_tournament_page(
    request: Request, id: int, session: AsyncSession = Depends(get_session)
):
    tournament = await session.get(BgmiTournament, id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    game = await session.get(Game, tournament.game_id) if tournament.game_id else None
    team_ids = await _participating_team_ids(session, id)
    teams = []
    if team_ids:
        result = await session.execute(
            select(MobaTeam).where(MobaTeam.id.in_(team_ids))
        )
        teams = list(result.scalars().all())

    available_query = select(MobaTeam).order_by(MobaTeam.name)
    if team_ids:
        available_query = available_query.where(MobaTeam.id.notin_(team_ids))
    available_teams = list((await session.execute(available_query)).scalars().all())

    return await _render_page(
        request,
        session,
        "components/tournaments/bgmi_tournament_info.html",
        "tournaments",
        extra={
            "tournament": tournament,
            "game": game,
            "teams": teams,
            "available_teams": available_teams,
        },
    )


@tournament_routes.post("/tournaments/bgmi/{id}/teams")
async def register_bgmi_team(
    request: Request, id: int, session: AsyncSession = Depends(get_session)
):
    tournament = await session.get(BgmiTournament, id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    form = await request.form()
    team_id = _parse_int(form.get("team_id"), "team", 0)
    team = await session.get(MobaTeam, team_id) if team_id else None
    if team is not None:
        existing = await _participating_team_ids(session, id)
        if team_id not in existing:
            session.add(BgmiTournamentParticipant(tournament_id=id, team_id=team_id))
            await session.commit()

    return RedirectResponse(
        f"/tournaments/bgmi/{id}", status_code=status.HTTP_303_SEE_OTHER
    )


@tournament_routes.get("/tournaments/{id}")
async def get_tournament_page(
    request: Request, id: int, session: AsyncSession = Depends(get_session)
):
    tournament = await session.get(MobaTournament, id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    game = await session.get(Game, tournament.game_id) if tournament.game_id else None

    result = await session.execute(
        select(MobaTournamentParticipant).where(
            MobaTournamentParticipant.tournament_id == id
        )
    )
    team_ids = [participant.team_id for participant in result.scalars().all()]
    teams: list[MobaTeamPublic] = []
    if team_ids:
        teams_result = await session.execute(
            select(MobaTeam).where(MobaTeam.id.in_(team_ids))
        )
        teams = [
            MobaTeamPublic.model_validate(team.model_dump())
            for team in teams_result.scalars().all()
        ]

    return await _render_page(
        request,
        session,
        "components/tournaments/tournament_info.html",
        "tournaments",
        extra={"tournament": tournament, "game": game, "teams": teams},
    )
