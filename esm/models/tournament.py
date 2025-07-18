#      eSports Manager - A free and open source eSports management simulation game
#      Copyright (C) 2020-2025  Pedrenrique G. Guimarães
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Enum as SQLAlchemyEnum
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from datetime import date, datetime
from enum import Enum
import json

from .moba_team import TeamRegion

if TYPE_CHECKING:
    from .moba_team import MobaTeam
    from .match import Match


# Tournament type enum
class TournamentType(str, Enum):
    """Enum representing tournament types"""

    LEAGUE = "league"
    CUP = "cup"
    INTERNATIONAL = "international"


# Tournament format enum
class TournamentFormat(str, Enum):
    """Enum representing tournament formats"""

    ROUND_ROBIN = "round_robin"
    SINGLE_ELIMINATION = "single_elimination"
    DOUBLE_ELIMINATION = "double_elimination"
    GROUP_SWISS = "group_swiss"
    GROUP_KNOCKOUT = "group_knockout"


# Stage type enum
class StageType(str, Enum):
    """Enum representing tournament stage types"""

    GROUPS = "groups"
    PLAYOFFS = "playoffs"
    QUARTERFINALS = "quarterfinals"
    SEMIFINALS = "semifinals"
    FINALS = "finals"
    THIRD_PLACE = "third_place"
    RELEGATION = "relegation"


class TournamentTeamLink(SQLModel, table=True):
    """Link table between tournaments and teams."""

    __tablename__ = "tournament_team_link"

    tournament_id: int = Field(foreign_key="tournament.id", primary_key=True)
    team_id: int = Field(foreign_key="moba_team.id", primary_key=True)
    seed: Optional[int] = Field(default=None)
    group: Optional[str] = Field(default=None)


class Tournament(SQLModel, table=True):
    """Model representing an esports tournament."""

    __tablename__ = "tournament"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    tournament_type: TournamentType = Field(
        sa_column=Column(SQLAlchemyEnum(TournamentType)), default=TournamentType.LEAGUE
    )
    tournament_format: TournamentFormat = Field(
        sa_column=Column(SQLAlchemyEnum(TournamentFormat)),
        default=TournamentFormat.ROUND_ROBIN,
    )
    start_date: date = Field()
    end_date: date = Field()
    region: TeamRegion = Field(
        sa_column=Column(SQLAlchemyEnum(TeamRegion)), default=TeamRegion.NA
    )
    prize_pool: float = Field(default=0.0)
    description: Optional[str] = Field(default=None)
    logo_path: Optional[str] = Field(default=None)  # Path to local logo image file
    season_id: Optional[int] = Field(default=None, foreign_key="season.id")
    teams_data: Optional[str] = Field(default=None)  # JSON string storing team metadata

    # Relationships
    teams: List["MobaTeam"] = Relationship(
        link_model=TournamentTeamLink, sa_relationship_kwargs={"cascade": "all, delete"}
    )
    matches: List["Match"] = Relationship(
        back_populates="tournament", sa_relationship_kwargs={"cascade": "all, delete"}
    )
    stages: List["TournamentStage"] = Relationship(
        back_populates="tournament", sa_relationship_kwargs={"cascade": "all, delete"}
    )
    season: Optional["Season"] = Relationship(back_populates="tournaments")

    def get_teams_data(self) -> Optional[List[Dict[str, Any]]]:
        """Get the teams data from JSON field."""
        if not self.teams_data:
            return None
        return json.loads(self.teams_data)

    def set_teams_data(self, data: List[Dict[str, Any]]) -> None:
        """Set the teams data as JSON string."""
        self.teams_data = json.dumps(data) if data else None

    def generate_standings(self) -> List[Dict[str, Any]]:
        """
        Generate standings for the tournament based on match results.

        Returns:
            List of dictionaries containing team standing information
        """
        # Create a dictionary to track team stats
        team_stats = {}

        # Initialize team stats for all teams in the tournament
        for team in self.teams:
            team_stats[team.id] = {
                "team_id": team.id,
                "team_name": team.name,
                "matches_played": 0,
                "wins": 0,
                "losses": 0,
                "draws": 0,
                "maps_won": 0,
                "maps_lost": 0,
                "points": 0,
            }

        # Process all matches in the tournament
        for match in self.matches:
            # Only count completed matches
            if match.status != "completed":
                continue

            home_team_id = match.home_team_id
            away_team_id = match.away_team_id

            # Increment matches played
            if home_team_id in team_stats:
                team_stats[home_team_id]["matches_played"] += 1
                team_stats[home_team_id]["maps_won"] += match.home_team_score
                team_stats[home_team_id]["maps_lost"] += match.away_team_score

            if away_team_id in team_stats:
                team_stats[away_team_id]["matches_played"] += 1
                team_stats[away_team_id]["maps_won"] += match.away_team_score
                team_stats[away_team_id]["maps_lost"] += match.home_team_score

            # Process match result
            result = match.match_result
            if result is not None:
                if result.name == "HOME_WIN":
                    if home_team_id in team_stats:
                        team_stats[home_team_id]["wins"] += 1
                        team_stats[home_team_id]["points"] += 3
                    if away_team_id in team_stats:
                        team_stats[away_team_id]["losses"] += 1
                elif result.name == "AWAY_WIN":
                    if away_team_id in team_stats:
                        team_stats[away_team_id]["wins"] += 1
                        team_stats[away_team_id]["points"] += 3
                    if home_team_id in team_stats:
                        team_stats[home_team_id]["losses"] += 1
                elif result.name == "DRAW":
                    if home_team_id in team_stats:
                        team_stats[home_team_id]["draws"] += 1
                        team_stats[home_team_id]["points"] += 1
                    if away_team_id in team_stats:
                        team_stats[away_team_id]["draws"] += 1
                        team_stats[away_team_id]["points"] += 1

        # Convert dictionary to sorted list
        standings = list(team_stats.values())

        # Sort by points (descending), then by map win percentage
        standings.sort(
            key=lambda x: (
                x["points"],
                x["maps_won"] / max(1, (x["maps_won"] + x["maps_lost"])),
            ),
            reverse=True,
        )

        return standings

    def __str__(self) -> str:
        """String representation of a tournament."""
        # Use the region value directly since it's already properly formatted
        return f"Tournament: {self.name} ({self.region.value}, {self.start_date} to {self.end_date})"


class TournamentStage(SQLModel, table=True):
    """Model representing a stage within a tournament."""

    __tablename__ = "tournament_stage"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field()
    stage_type: StageType = Field(
        sa_column=Column(SQLAlchemyEnum(StageType)), default=StageType.GROUPS
    )
    tournament_id: int = Field(foreign_key="tournament.id")
    start_date: date = Field()
    end_date: date = Field()
    description: Optional[str] = Field(default=None)

    # Relationships
    tournament: Tournament = Relationship(back_populates="stages")
    matches: List["Match"] = Relationship(back_populates="tournament_stage")

    def __str__(self) -> str:
        """String representation of a tournament stage."""
        return f"Stage: {self.name} ({self.tournament.name}, {self.start_date} to {self.end_date})"


class Season(SQLModel, table=True):
    """Model representing an esports season."""

    __tablename__ = "season"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    start_date: date = Field()
    end_date: date = Field()
    description: Optional[str] = Field(default=None)

    # Relationships
    tournaments: List[Tournament] = Relationship(back_populates="season")

    def __str__(self) -> str:
        """String representation of a season."""
        return f"Season: {self.name} ({self.start_date} to {self.end_date})"


# API Models
class TournamentBase(SQLModel):
    """Base model for Tournament API operations"""

    name: str
    tournament_type: TournamentType
    tournament_format: TournamentFormat
    region: TeamRegion
    prize_pool: float = 0.0
    description: Optional[str] = None
    logo_path: Optional[str] = None


class TournamentCreate(TournamentBase):
    """Model for creating tournaments via API"""

    start_date: str  # Accept string dates from API
    end_date: str  # Accept string dates from API
    season_id: Optional[int] = None


class TournamentRead(TournamentBase):
    """Model for reading tournaments from API"""

    id: int
    start_date: date
    end_date: date
    season_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TournamentUpdate(SQLModel):
    """Model for updating tournaments via API"""

    name: Optional[str] = None
    tournament_type: Optional[TournamentType] = None
    tournament_format: Optional[TournamentFormat] = None
    start_date: Optional[str] = None  # Accept string dates from API
    end_date: Optional[str] = None  # Accept string dates from API
    region: Optional[TeamRegion] = None
    prize_pool: Optional[float] = None
    description: Optional[str] = None
    logo_path: Optional[str] = None
    season_id: Optional[int] = None


class SeasonBase(SQLModel):
    """Base model for Season API operations"""

    name: str
    description: Optional[str] = None


class SeasonCreate(SeasonBase):
    """Model for creating seasons via API"""

    start_date: str  # Accept string dates from API
    end_date: str  # Accept string dates from API


class SeasonRead(SeasonBase):
    """Model for reading seasons from API"""

    id: int
    start_date: date
    end_date: date

    model_config = {"from_attributes": True}


class SeasonUpdate(SQLModel):
    """Model for updating seasons via API"""

    name: Optional[str] = None
    start_date: Optional[str] = None  # Accept string dates from API
    end_date: Optional[str] = None  # Accept string dates from API
    description: Optional[str] = None
