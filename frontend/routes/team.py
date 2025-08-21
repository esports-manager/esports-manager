# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from esm.db import get_session
from fastapi import Request, Depends, APIRouter, HTTPException, status
from sqlmodel import Session, Field
from fastapi.templating import Jinja2Templates
from esm.models.moba.player import MobaPlayerPublic
from esm.models.moba.team import MobaTeamPublic, MobaTeam, MobaTeamTier
from esm.config import FRONTEND_DIR
from frontend.sidebar import sidebar

team_routes = APIRouter(
    tags=["moba_teams"],
    responses={404: {"description": "Team not found"}},
)

templates_dir = FRONTEND_DIR / "templates"
templates = Jinja2Templates(directory=templates_dir)


class MobaTeamWithPlayers(MobaTeamPublic):
    players: list[MobaPlayerPublic] = Field(default_factory=list)

    @property
    def overall(self) -> int:
        if not self.players:
            return 0
        return sum(player.overall for player in self.players) // len(self.players)

    @property
    def tier(self) -> MobaTeamTier:
        if self.overall >= 95:
            return MobaTeamTier.SP
        elif self.overall >= 90:
            return MobaTeamTier.S
        elif self.overall >= 85:
            return MobaTeamTier.A
        elif self.overall >= 80:
            return MobaTeamTier.B
        elif self.overall >= 75:
            return MobaTeamTier.C
        elif self.overall >= 70:
            return MobaTeamTier.D

        return MobaTeamTier.F


@team_routes.get("/teams/{id}")
async def get_team(
    *, request: Request, session: Session = Depends(get_session), id: int
):
    global current_page
    global sidebar
    current_page = "teams"
    contentview = "components/teams/team_info.html"
    team = session.get(MobaTeam, id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    team_data = team.model_dump()
    team_public = MobaTeamPublic.model_validate(team_data)

    if team.current_players:
        team_data["players"] = [
            MobaPlayerPublic.model_validate(player.model_dump())
            for player in team.current_players
        ]
    team_public = MobaTeamWithPlayers.model_validate(team_data)
    return templates.TemplateResponse(
        "layout.html",
        {
            "sidebar": sidebar,
            "current_page": current_page,
            "content": contentview,
            "request": request,
            "team": team_public,
        },
    )
