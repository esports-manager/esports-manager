# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from datetime import date, datetime
import logging
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select

from esm.config import Config, FRONTEND_DIR
from esm.models.moba import (
    MobaGameSession,
    MobaGameSessionCreate,
    MobaGameSessionPublic,
)
from esm.models.moba.team import MobaTeam
from esm.services.game_session import (
    copy_base_database,
    list_session_db_paths,
    normalize_session_id,
    session_db_context,
    session_db_name,
    session_db_path,
    session_id_from_path,
    sqlite_url_from_path,
)


session_routes = APIRouter(
    prefix="/sessions",
    tags=["moba_sessions"],
    responses={404: {"description": "Session not found"}},
)

templates_dir = FRONTEND_DIR / "templates"
templates = Jinja2Templates(directory=templates_dir)

logger = logging.getLogger("esm.routes.moba.session")


def build_display_name(
    first_name: str, last_name: str, nickname: Optional[str]
) -> str:
    if nickname:
        return nickname
    parts = [first_name.strip(), last_name.strip()]
    return " ".join(part for part in parts if part)


def build_session_public(
    game_session: MobaGameSession,
    team: Optional[MobaTeam],
    session_id: Optional[str] = None,
    session_database_url: Optional[str] = None,
) -> MobaGameSessionPublic:
    data = game_session.model_dump()
    if session_id:
        data["id"] = session_id
    if session_database_url:
        data["session_database_url"] = session_database_url
    data["manager_display_name"] = build_display_name(
        game_session.manager_first_name,
        game_session.manager_last_name,
        game_session.manager_nickname,
    )
    if team:
        data["team_name"] = team.name
        if team.logo_path:
            filename = Path(team.logo_path).name
            data["team_logo_url"] = f"/api/moba/teams/images/{filename}"
        if team.banner_path:
            filename = Path(team.banner_path).name
            data["team_banner_url"] = f"/api/moba/teams/images/{filename}"
    return MobaGameSessionPublic.model_validate(data)


async def load_session_public(session_id: str) -> MobaGameSessionPublic:
    try:
        resolved_session_id = normalize_session_id(session_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db_path = session_db_path(resolved_session_id)
    if not db_path.exists():
        logger.warning("Session not found session_id=%s", resolved_session_id)
        raise HTTPException(status_code=404, detail="Session not found")

    session_db_url = sqlite_url_from_path(db_path)
    async with session_db_context(session_db_url) as session_db:
        result = await session_db.execute(select(MobaGameSession))
        game_session = result.scalars().first()
        if not game_session:
            logger.warning("Session metadata missing session_id=%s", session_id)
            raise HTTPException(status_code=404, detail="Session not found")
        team = await session_db.get(MobaTeam, game_session.team_id)
        logger.debug("Fetched session session_id=%s", resolved_session_id)
        return build_session_public(
            game_session,
            team,
            session_id=resolved_session_id,
            session_database_url=session_db_url,
        )


@session_routes.get("/", response_model=List[MobaGameSessionPublic])
async def list_sessions(request: Request):
    session_id = request.query_params.get("session_id")
    logger.debug("Listing sessions session_id=%s", session_id)
    public_sessions: list[MobaGameSessionPublic] = []
    for db_path in list_session_db_paths():
        try:
            resolved_session_id = session_id_from_path(db_path)
        except ValueError:
            logger.warning("Skipping invalid session database name path=%s", db_path)
            continue
        session_db_url = sqlite_url_from_path(db_path)
        try:
            async with session_db_context(session_db_url) as session_db:
                result = await session_db.execute(select(MobaGameSession))
                game_session = result.scalars().first()
                if not game_session:
                    logger.warning(
                        "Session metadata missing session_id=%s path=%s",
                        resolved_session_id,
                        db_path,
                    )
                    continue
                team = await session_db.get(MobaTeam, game_session.team_id)
                public_sessions.append(
                    build_session_public(
                        game_session,
                        team,
                        session_id=resolved_session_id,
                        session_database_url=session_db_url,
                    )
                )
        except Exception:
            logger.exception(
                "Failed to load session metadata session_id=%s path=%s",
                resolved_session_id,
                db_path,
            )

    public_sessions.sort(
        key=lambda session_item: session_item.created_at, reverse=True
    )

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            request,
            "components/sessions/sessions_list.html",
            {
                "request": request,
                "sessions": public_sessions,
                "session_id": session_id,
            },
        )

    return public_sessions


@session_routes.get("/current", response_model=MobaGameSessionPublic)
async def get_current_session(request: Request):
    session_id = request.query_params.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session id is required")
    return await load_session_public(session_id)


@session_routes.get("/{session_id}", response_model=MobaGameSessionPublic)
async def get_session_by_id(session_id: str):
    return await load_session_public(session_id)


@session_routes.post("/form", response_class=HTMLResponse)
async def create_session_form(
    request: Request,
    manager_first_name: str = Form(...),
    manager_last_name: str = Form(...),
    team_id: int = Form(...),
    manager_nickname: Optional[str] = Form(None),
    manager_birthdate: Optional[date] = Form(None),
    manager_nationality: Optional[str] = Form(None),
    name: Optional[str] = Form(None),
    seed: Optional[int] = Form(None),
    base_database_url: Optional[str] = Form(None),
):
    payload = MobaGameSessionCreate(
        manager_first_name=manager_first_name,
        manager_last_name=manager_last_name,
        manager_nickname=manager_nickname or None,
        manager_birthdate=manager_birthdate or None,
        manager_nationality=manager_nationality or None,
        team_id=team_id,
        name=name or None,
        seed=seed,
        base_database_url=base_database_url or None,
    )

    try:
        created_session = await create_session(
            payload=payload,
        )
    except HTTPException as exc:
        logger.warning(
            "Session creation failed status=%s detail=%s",
            exc.status_code,
            exc.detail,
        )
        if request.headers.get("HX-Request"):
            return HTMLResponse(
                content=str(exc.detail),
                status_code=status.HTTP_200_OK,
            )
        raise

    redirect_url = f"/home?session_id={created_session.id}"
    if request.headers.get("HX-Request"):
        response = HTMLResponse(
            content="",
            status_code=status.HTTP_201_CREATED,
            headers={"HX-Redirect": redirect_url},
        )
        return response

    return RedirectResponse(
        url=redirect_url,
        status_code=status.HTTP_303_SEE_OTHER,
    )


@session_routes.post(
    "/", response_model=MobaGameSessionPublic, status_code=status.HTTP_201_CREATED
)
async def create_session(
    payload: MobaGameSessionCreate,
):
    config = Config()
    config.load_config()
    base_database_url = payload.base_database_url or config.database_url

    logger.info(
        "Creating session team_id=%s base_database_url=%s seed=%s",
        payload.team_id,
        base_database_url,
        payload.seed,
    )

    if payload.team_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid team selection")

    manager_first_name = payload.manager_first_name.strip()
    manager_last_name = payload.manager_last_name.strip()
    manager_nickname = (payload.manager_nickname or "").strip() or None
    manager_nationality = (payload.manager_nationality or "").strip() or None

    if not manager_first_name or not manager_last_name:
        raise HTTPException(
            status_code=400, detail="Manager first and last name are required"
        )

    display_name = build_display_name(
        manager_first_name, manager_last_name, manager_nickname
    )
    session_name = payload.name or f"{display_name}'s Career"

    session_id = uuid4().hex
    try:
        session_db_url = await copy_base_database(
            base_database_url,
            session_db_filename=session_db_name(session_id),
        )
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    seed = payload.seed if payload.seed is not None else 0

    session_db_file = session_db_path(session_id)
    try:
        async with session_db_context(session_db_url) as session_db:
            team = await session_db.get(MobaTeam, payload.team_id)
            if not team:
                raise HTTPException(status_code=404, detail="Team not found")

            game_session = MobaGameSession(
                name=session_name,
                manager_first_name=manager_first_name,
                manager_last_name=manager_last_name,
                manager_nickname=manager_nickname,
                manager_birthdate=payload.manager_birthdate,
                manager_nationality=manager_nationality,
                team_id=payload.team_id,
                base_database_url=base_database_url,
                session_database_url=session_db_url,
                current_day=1,
                seed=seed,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

            session_db.add(game_session)
            await session_db.commit()
            await session_db.refresh(game_session)

            logger.info(
                "Session created session_id=%s team_id=%s",
                session_id,
                game_session.team_id,
            )

            return build_session_public(
                game_session,
                team,
                session_id=session_id,
                session_database_url=session_db_url,
            )
    except HTTPException:
        if session_db_file.exists():
            session_db_file.unlink()
        raise
    except Exception as exc:
        if session_db_file.exists():
            session_db_file.unlink()
        logger.exception("Session creation failed session_id=%s", session_id)
        raise HTTPException(
            status_code=500, detail="Failed to create session"
        ) from exc


@session_routes.post(
    "/{session_id}/save", response_model=MobaGameSessionPublic
)
async def save_session(
    session_id: str,
    request: Request,
):
    try:
        resolved_session_id = normalize_session_id(session_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db_path = session_db_path(resolved_session_id)
    if not db_path.exists():
        logger.warning(
            "Session not found for save session_id=%s", resolved_session_id
        )
        raise HTTPException(status_code=404, detail="Session not found")

    session_db_url = sqlite_url_from_path(db_path)
    async with session_db_context(session_db_url) as session_db:
        result = await session_db.execute(select(MobaGameSession))
        game_session = result.scalars().first()
        if not game_session:
            logger.warning(
                "Session metadata missing for save session_id=%s",
                resolved_session_id,
            )
            raise HTTPException(status_code=404, detail="Session not found")
        game_session.updated_at = datetime.now()
        session_db.add(game_session)
        await session_db.commit()
        await session_db.refresh(game_session)
        logger.info("Session saved session_id=%s", resolved_session_id)

        team = await session_db.get(MobaTeam, game_session.team_id)
        public = build_session_public(
            game_session,
            team,
            session_id=resolved_session_id,
            session_database_url=session_db_url,
        )

    if request.headers.get("HX-Request") == "true":
        html = f"""
        <span
            hx-trigger="load delay:2.5s"
            hx-get="/_empty"
            hx-swap="outerHTML"
        >Saved</span>
        """
        return HTMLResponse(content=html)
    
    return public
