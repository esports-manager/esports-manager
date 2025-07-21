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
from pydantic import field_serializer
from datetime import datetime
import json
from enum import Enum, auto

if TYPE_CHECKING:
    from .moba_team import MobaTeam
    from .match_performance import MapResult, MatchPlayerStats, MatchPerformance
    from .tournament import Tournament, TournamentStage


# Match status enum
class MatchStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


# Match type enum
class MatchType(str, Enum):
    REGULAR_SEASON = "regular_season"
    PLAYOFFS = "playoffs"
    FINALS = "finals"
    INTERNATIONAL = "international"
    EXHIBITION = "exhibition"


# Match format enum
class MatchFormat(str, Enum):
    BO1 = "bo1"
    BO2 = "bo2"
    BO3 = "bo3"
    BO5 = "bo5"


# Match result enum
class MatchResult(Enum):
    HOME_WIN = auto()
    AWAY_WIN = auto()
    DRAW = auto()


class Match(SQLModel, table=True):
    """
    Model representing a match between two MOBA teams.
    """

    __tablename__ = "match"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Team relationships
    home_team_id: int = Field(foreign_key="moba_team.id")
    away_team_id: int = Field(foreign_key="moba_team.id")

    # Match details
    scheduled_date: datetime = Field(index=True)
    completed_date: Optional[datetime] = Field(default=None)
    match_type: MatchType = Field(
        sa_column=Column(SQLAlchemyEnum(MatchType)), default=MatchType.REGULAR_SEASON
    )
    match_format: MatchFormat = Field(
        sa_column=Column(SQLAlchemyEnum(MatchFormat)), default=MatchFormat.BO3
    )
    venue: Optional[str] = Field(default=None)

    # Match status and score
    status: MatchStatus = Field(
        sa_column=Column(SQLAlchemyEnum(MatchStatus)), default=MatchStatus.SCHEDULED
    )
    home_team_score: int = Field(default=0)
    away_team_score: int = Field(default=0)

    # Match data (detailed statistics) stored as JSON
    match_data: Optional[str] = Field(default=None)

    # Tournament relationships
    tournament_id: Optional[int] = Field(default=None, foreign_key="tournament.id")
    tournament_stage_id: Optional[int] = Field(
        default=None, foreign_key="tournament_stage.id"
    )

    # Relationships
    home_team: "MobaTeam" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "Match.home_team_id"}
    )
    away_team: "MobaTeam" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "Match.away_team_id"}
    )
    tournament: Optional["Tournament"] = Relationship(back_populates="matches")
    tournament_stage: Optional["TournamentStage"] = Relationship(
        back_populates="matches"
    )
    map_results: List["MapResult"] = Relationship(back_populates="match")
    player_stats: List["MatchPlayerStats"] = Relationship(back_populates="match")
    performance: Optional["MatchPerformance"] = Relationship(back_populates="match")

    @property
    def match_result(self) -> Optional[MatchResult]:
        """
        Determine the result of the match based on scores.
        Returns None if the match is not completed.
        """
        if self.status != MatchStatus.COMPLETED:
            return None

        if self.home_team_score > self.away_team_score:
            return MatchResult.HOME_WIN
        elif self.away_team_score > self.home_team_score:
            return MatchResult.AWAY_WIN
        else:
            return MatchResult.DRAW

    def get_match_data(self) -> Dict[str, Any]:
        """
        Get match data as a Python dictionary.

        Returns:
            Dict containing detailed match statistics
        """
        if not self.match_data:
            return {}
        return json.loads(self.match_data)

    def set_match_data(self, data: Dict[str, Any]) -> None:
        """
        Set match data from a Python dictionary.

        Args:
            data: Dictionary containing detailed match statistics
        """
        self.match_data = json.dumps(data)

    def get_player_stats(self, player_id: int) -> List[Dict[str, Any]]:
        """
        Get stats for a specific player in this match.

        Args:
            player_id: ID of the player

        Returns:
            List of performance stats for each map played
        """
        result = []
        if not hasattr(self, "player_stats"):
            return result

        for stat in self.player_stats:
            if stat.player_id == player_id:
                result.append(
                    {
                        "map_number": stat.map_number,
                        "kills": stat.kills,
                        "deaths": stat.deaths,
                        "assists": stat.assists,
                        "cs": stat.cs,
                        "vision_score": stat.vision_score,
                        "kda": stat.kda,
                        "champion_id": stat.champion_id,
                    }
                )
        return result

    def get_mvp(self) -> Optional[Dict[str, Any]]:
        """
        Get the MVP of the match.

        Returns:
            MVP information if available, None otherwise
        """
        if hasattr(self, "performance") and self.performance is not None:
            return self.performance.calculate_mvp()
        return None

    def generate_performance_summary(self) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of the match performance.

        Returns:
            Dictionary with match performance summary
        """
        summary = {
            "match_id": self.id,
            "home_team": {
                "id": self.home_team_id,
                "name": self.home_team.name,
                "score": self.home_team_score,
            },
            "away_team": {
                "id": self.away_team_id,
                "name": self.away_team.name,
                "score": self.away_team_score,
            },
            "maps": [],
            "result": self.match_result.name if self.match_result else None,
            "player_performances": [],
            "mvp": self.get_mvp(),
        }

        # Add map results
        if hasattr(self, "map_results"):
            for map_result in self.map_results:
                summary["maps"].append(
                    {
                        "map_number": map_result.map_number,
                        "winner_team_id": map_result.winner_team_id,
                        "duration_minutes": map_result.duration_minutes,
                        "blue_side_kills": map_result.blue_side_kills,
                        "red_side_kills": map_result.red_side_kills,
                    }
                )

        # Add aggregate player stats if we have a performance record
        if hasattr(self, "performance") and self.performance is not None:
            aggregate = self.performance.aggregate_stats()
            summary["player_performances"] = aggregate["player_stats"]

        return summary

    def schedule_match(self, scheduled_date: datetime, venue: str = None) -> None:
        """
        Schedule or reschedule a match.

        Args:
            scheduled_date: New scheduled date and time
            venue: Venue for the match
        """
        self.scheduled_date = scheduled_date
        if venue:
            self.venue = venue
        self.status = MatchStatus.SCHEDULED

    def start_match(self) -> None:
        """
        Mark the match as in progress.
        """
        self.status = MatchStatus.IN_PROGRESS

    def complete_match(self, home_team_score: int, away_team_score: int) -> None:
        """
        Complete a match with final scores.

        Args:
            home_team_score: Score for the home team
            away_team_score: Score for the away team
        """
        self.home_team_score = home_team_score
        self.away_team_score = away_team_score
        self.status = MatchStatus.COMPLETED
        self.completed_date = datetime.now()

    def postpone_match(self, new_date: Optional[datetime] = None) -> None:
        """
        Postpone a match to a later date.

        Args:
            new_date: Optional new date for the match
        """
        self.status = MatchStatus.POSTPONED
        if new_date:
            self.scheduled_date = new_date

    def cancel_match(self) -> None:
        """
        Cancel a match.
        """
        self.status = MatchStatus.CANCELLED

    def __str__(self) -> str:
        """String representation of a match."""
        # For tournaments, include tournament info if available
        tournament_info = ""
        if hasattr(self, "tournament") and self.tournament is not None:
            tournament_info = f" ({self.tournament.name})"

        if self.status == MatchStatus.COMPLETED:
            return f"Match: {self.home_team.name} {self.home_team_score}-{self.away_team_score} {self.away_team.name} (Completed){tournament_info}"
        elif self.status == MatchStatus.IN_PROGRESS:
            return f"Match: {self.home_team.name} vs {self.away_team.name} (In Progress){tournament_info}"
        else:
            return f"Match: {self.home_team.name} vs {self.away_team.name} (Scheduled for {self.scheduled_date}){tournament_info}"

    def __repr__(self) -> str:
        """Developer representation of a match."""
        return (
            f"<Match: {self.home_team_id} vs {self.away_team_id}, status={self.status}>"
        )


# API Models
class MatchBase(SQLModel):
    """Base model for Match API operations"""

    home_team_id: int
    away_team_id: int
    match_type: MatchType = MatchType.REGULAR_SEASON
    match_format: MatchFormat = MatchFormat.BO3
    venue: Optional[str] = None
    status: MatchStatus = MatchStatus.SCHEDULED
    home_team_score: int = 0
    away_team_score: int = 0
    tournament_id: Optional[int] = None
    tournament_stage_id: Optional[int] = None


class MatchCreate(MatchBase):
    """Model for creating match via API"""

    scheduled_date: str
    completed_date: Optional[str] = None
    match_data: Optional[Dict[str, Any]] = None


class MatchRead(MatchBase):
    """Model for reading match from API"""

    id: int
    scheduled_date: datetime
    completed_date: Optional[datetime] = None
    match_data: Optional[Dict[str, Any]] = None

    model_config = {"from_attributes": True}

    @field_serializer("scheduled_date", "completed_date")
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """Serialize datetime fields to ISO format strings"""
        return dt.isoformat() if dt else None


class MatchUpdate(SQLModel):
    """Model for updating match via API"""

    home_team_id: Optional[int] = None
    away_team_id: Optional[int] = None
    scheduled_date: Optional[str] = None
    completed_date: Optional[str] = None
    match_type: Optional[MatchType] = None
    match_format: Optional[MatchFormat] = None
    venue: Optional[str] = None
    status: Optional[MatchStatus] = None
    home_team_score: Optional[int] = None
    away_team_score: Optional[int] = None
    match_data: Optional[Dict[str, Any]] = None
    tournament_id: Optional[int] = None
    tournament_stage_id: Optional[int] = None
