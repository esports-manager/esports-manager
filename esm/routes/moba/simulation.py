# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from esm.db import get_session
from esm.config import FRONTEND_DIR
from frontend.sidebar import sidebar
from esm.models.moba import MobaMatch
from esm.models.moba.champion import MobaChampion
from esm.models.moba.moba_match_simulation import (
    MobaMatchSimulation,
    MobaMatchStatus,
)
from esm.models.moba.player import MobaPlayer, MobaPlayerRole
from esm.models.moba.player_simulation import MobaPlayerSimulation
from esm.models.moba.team import MobaTeam
from esm.models.moba.team_simulation import MobaTeamSimulation

simulation_routes = APIRouter(
    prefix="/simulation",
    tags=["moba_simulation"],
    responses={404: {"description": "Simulation not found"}},
)

templates_dir = FRONTEND_DIR / "templates"
templates = Jinja2Templates(directory=templates_dir)

logger = logging.getLogger("esm.routes.moba.simulation")


@dataclass
class SimulationSession:
    sim_id: str
    simulation: MobaMatchSimulation
    paused: bool = False
    speed: float = 1.0
    task: Optional[asyncio.Task] = None


_SIMULATIONS: Dict[str, SimulationSession] = {}
_BASE_TICK_SECONDS = 0.5


async def _run_simulation_loop(sess: SimulationSession):
    try:
        while sess.simulation.state.status != MobaMatchStatus.COMPLETED:
            if sess.paused:
                await asyncio.sleep(0.1)
                continue
            # Step the simulation
            sess.simulation.step()
            # Sleep based on speed multiplier
            sleep_for = max(0.05, _BASE_TICK_SECONDS / max(0.25, sess.speed))
            await asyncio.sleep(sleep_for)
    except Exception:
        # Never crash the server due to a simulation error
        logger.exception("Simulation loop failed sim_id=%s", sess.sim_id)


def _serialize_simulation(
    sim: MobaMatchSimulation,
    commentary_from: int | None = None,
) -> Dict[str, Any]:
    def serialize_team(ts: MobaTeamSimulation) -> Dict[str, Any]:
        return {
            "team": {
                "id": ts.team.id,
                "name": ts.team.name,
                "logo_path": getattr(ts.team, "logo_path", None),
            },
            "state": {
                "towers": ts.state.towers.model_dump(),
                "inhibitors": ts.state.inhibitors.model_dump(),
                "dragons": ts.state.dragons,
                "barons": ts.state.barons,
                "grubs": ts.state.grubs,
                "first_blood": ts.state.first_blood,
                "first_tower": ts.state.first_tower,
                "win_probability": ts.state.win_probability,
            },
            "players": [
                {
                    "id": ps.player.id,
                    "name": ps.player.nick_name
                    or f"{ps.player.first_name} {ps.player.last_name}",
                    "role": (ps.role.value if ps.role else None),
                    "champion": {
                        "id": ps.champion.id,
                        "name": ps.champion.name,
                        "image_path": getattr(ps.champion, "image_path", None),
                        "primary_role": getattr(ps.champion, "primary_role", None),
                    },
                    "kills": ps.kills,
                    "deaths": ps.deaths,
                    "assists": ps.assists,
                    "farm": ps.farm,
                    "points": ps.points,
                    "kda": ps.kda,
                    "strength": ps.get_strength(),
                    "score": ps.get_score(),
                }
                for ps in ts.players
            ],
            "summary": {
                "kills": ts.kills,
                "deaths": ts.deaths,
                "assists": ts.assists,
                "kda": ts.kda,
                "points": ts.points,
                "towers_remaining": ts.towers_remaining,
                "inhibitors_exposed": ts.are_inhibitors_exposed,
            },
        }

    commentary_log = list(sim.commentary_log)
    commentary_total = len(commentary_log)
    if commentary_from is not None and commentary_from >= 0:
        commentary = commentary_log[commentary_from:]
    else:
        commentary = commentary_log

    return {
        "status": sim.state.status.value,
        "time": sim.state.time,
        "minutes": sim.state.minutes_played,
        "seconds": sim.state.seconds_played,
        "winner": sim.state.winner,
        "team1": serialize_team(sim.team1),
        "team2": serialize_team(sim.team2),
        "commentary": commentary,
        "commentary_total": commentary_total,
        "enabled_events": [
            {"event": ev.value, "jungle_type": (jt.value if jt else None)}
            for ev, jt in sim.enabled_events
        ],
    }


async def _build_team_sim(
    db: AsyncSession,
    team_id: int,
    roster: list[dict[str, Any]],
) -> MobaTeamSimulation:
    team = await db.get(MobaTeam, team_id)
    if not team:
        logger.warning("Simulation team not found team_id=%s", team_id)
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
    players: list[MobaPlayerSimulation] = []
    for slot in roster:
        player = await db.get(MobaPlayer, int(slot["player_id"]))
        champion = await db.get(MobaChampion, int(slot["champion_id"]))
        if not player or not champion:
            logger.warning(
                "Simulation roster invalid player_id=%s champion_id=%s",
                slot.get("player_id"),
                slot.get("champion_id"),
            )
            raise HTTPException(status_code=404, detail="Player or Champion not found")
        role_str = slot.get("role")
        role = None
        if role_str:
            try:
                role = MobaPlayerRole(role_str)
            except Exception:
                # Attempt uppercase mapping
                try:
                    role = MobaPlayerRole[role_str.upper()]
                except Exception:
                    role = None
        ps = MobaPlayerSimulation(player=player, champion=champion, role=role)
        players.append(ps)
    return MobaTeamSimulation(team=team, players=players)


async def _create_simulation_from_payload(
    payload: Dict[str, Any],
    session: AsyncSession,
) -> str:
    try:
        t1 = await _build_team_sim(
            session, int(payload["team1_id"]), payload["team1_roster"]
        )  # type: ignore[index]
        t2 = await _build_team_sim(
            session, int(payload["team2_id"]), payload["team2_roster"]
        )  # type: ignore[index]
    except KeyError as exc:
        logger.warning("Simulation payload missing key error=%s", exc)
        raise HTTPException(status_code=400, detail="Invalid roster payload") from exc

    sim = MobaMatchSimulation(team1=t1, team2=t2)
    sim.state.update_jungle_objectives()
    sim_id = uuid.uuid4().hex
    sess = SimulationSession(sim_id=sim_id, simulation=sim)
    _SIMULATIONS[sim_id] = sess
    logger.info(
        "Simulation session created sim_id=%s team1_id=%s team2_id=%s",
        sim_id,
        payload.get("team1_id"),
        payload.get("team2_id"),
    )
    return sim_id


@simulation_routes.post("/create")
async def create_simulation(
    payload: Dict[str, Any], session: AsyncSession = Depends(get_session)
):
    """
    Create a new simulation session.
    Expected payload:
    {
      "team1_id": int,
      "team2_id": int,
      "team1_roster": [ {"player_id": int, "champion_id": int, "role": "top"|... } x5 ],
      "team2_roster": [ ... ]
    }
    """
    logger.info(
        "Creating simulation from payload team1_id=%s team2_id=%s",
        payload.get("team1_id"),
        payload.get("team2_id"),
    )
    sim_id = await _create_simulation_from_payload(payload, session)
    return {"sim_id": sim_id}


@simulation_routes.post("/from-draft/{draft_id}")
async def create_simulation_from_draft(
    draft_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    from esm.routes.moba.draft import get_draft_composition

    composition = await get_draft_composition(draft_id, session)
    match = await session.get(MobaMatch, composition["match_id"])
    if not match:
        logger.warning(
            "Simulation draft match not found draft_id=%s match_id=%s",
            draft_id,
            composition.get("match_id"),
        )
        raise HTTPException(status_code=404, detail="Match not found")

    payload = {
        "team1_id": match.blue_team_id,
        "team2_id": match.red_team_id,
        "team1_roster": composition["blue_team"],
        "team2_roster": composition["red_team"],
    }

    logger.info(
        "Creating simulation from draft draft_id=%s match_id=%s",
        draft_id,
        match.id,
    )
    sim_id = await _create_simulation_from_payload(payload, session)
    session_id = request.query_params.get("session_id")
    redirect_url = f"/api/moba/simulation/view/{sim_id}"
    if session_id:
        redirect_url = f"{redirect_url}?session_id={session_id}"

    if request.headers.get("HX-Request"):
        return HTMLResponse(
            content="",
            status_code=201,
            headers={"HX-Redirect": redirect_url},
        )

    return {"sim_id": sim_id, "redirect_url": redirect_url}


def _get_session_or_404(sim_id: str) -> SimulationSession:
    sess = _SIMULATIONS.get(sim_id)
    if not sess:
        logger.warning("Simulation not found sim_id=%s", sim_id)
        raise HTTPException(status_code=404, detail="Simulation not found")
    return sess


@simulation_routes.post("/start/{sim_id}")
async def start_simulation(sim_id: str):
    sess = _get_session_or_404(sim_id)
    if sess.simulation.state.status == MobaMatchStatus.COMPLETED:
        logger.warning("Simulation already ended sim_id=%s", sim_id)
        raise HTTPException(status_code=400, detail="Simulation already ended")
    if sess.task and not sess.task.done():
        # Already running
        logger.debug("Simulation already running sim_id=%s", sim_id)
        return {"status": "already running"}
    sess.paused = False
    # Ensure objectives are initialized
    if not sess.simulation.state.jungle_objectives:
        sess.simulation.state.update_jungle_objectives()
    # Create and start the background loop
    loop = asyncio.get_event_loop()
    sess.task = loop.create_task(_run_simulation_loop(sess))
    # Also start if not started
    if sess.simulation.state.status == MobaMatchStatus.NOT_STARTED:
        sess.simulation.start()
    logger.info("Simulation started sim_id=%s", sim_id)
    return {"status": "started"}


@simulation_routes.post("/pause/{sim_id}")
async def pause_simulation(sim_id: str):
    sess = _get_session_or_404(sim_id)
    sess.paused = True
    logger.info("Simulation paused sim_id=%s", sim_id)
    return {"status": "paused"}


@simulation_routes.post("/resume/{sim_id}")
async def resume_simulation(sim_id: str):
    sess = _get_session_or_404(sim_id)
    sess.paused = False
    if not sess.task or sess.task.done():
        loop = asyncio.get_event_loop()
        sess.task = loop.create_task(_run_simulation_loop(sess))
    logger.info("Simulation resumed sim_id=%s", sim_id)
    return {"status": "resumed"}


@simulation_routes.post("/speed/{sim_id}")
async def set_speed(sim_id: str, speed: float = 1.0):
    sess = _get_session_or_404(sim_id)
    sess.speed = max(0.25, min(8.0, speed))
    logger.info("Simulation speed set sim_id=%s speed=%s", sim_id, sess.speed)
    return {"speed": sess.speed}


@simulation_routes.get("/state/{sim_id}")
async def get_state(sim_id: str, commentary_from: int | None = None):
    sess = _get_session_or_404(sim_id)
    data = _serialize_simulation(
        sess.simulation,
        commentary_from=commentary_from,
    )
    data.update({"paused": sess.paused, "speed": sess.speed, "sim_id": sim_id})
    return data


@simulation_routes.get("/view/{sim_id}")
async def view_simulation(sim_id: str, request: Request):
    _get_session_or_404(sim_id)
    session_id = request.query_params.get("session_id")
    logger.debug("Simulation view loaded sim_id=%s session_id=%s", sim_id, session_id)

    context = {
        "request": request,
        "sim_id": sim_id,
        "session_id": session_id,
    }

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            request,
            "pages/match_live.html",
            context,
        )

    layout_context = {
        **context,
        "content": "pages/match_live.html",
        "sidebar": sidebar,
        "current_page": "matches",
    }

    return templates.TemplateResponse(
        request,
        "layout.html",
        layout_context,
    )


@simulation_routes.delete("/{sim_id}")
async def delete_simulation(sim_id: str):
    sess = _SIMULATIONS.pop(sim_id, None)
    if not sess:
        raise HTTPException(status_code=404, detail="Simulation not found")
    # cancel background task if running
    if sess.task and not sess.task.done():
        sess.task.cancel()
    logger.info("Simulation deleted sim_id=%s", sim_id)
    return {"status": "deleted"}
