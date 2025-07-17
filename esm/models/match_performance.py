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
from sqlmodel import SQLModel, Field, Relationship, Session, select
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from datetime import datetime
import json
from collections import defaultdict

if TYPE_CHECKING:
    from .moba_player import MobaPlayer
    from .moba_team import MobaTeam
    from .match import Match
    from .champion import Champion


class MapResult(SQLModel, table=True):
    """Model representing the result of a single map in a match."""

    __tablename__ = "map_result"

    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="match.id", index=True)
    map_number: int = Field()
    winner_team_id: int = Field(foreign_key="moba_team.id")
    duration_minutes: int = Field()

    # Team sides and IDs
    blue_side_team_id: int = Field(foreign_key="moba_team.id")
    red_side_team_id: int = Field(foreign_key="moba_team.id")

    # Team stats
    blue_side_gold: int = Field(default=0)
    red_side_gold: int = Field(default=0)
    blue_side_kills: int = Field(default=0)
    red_side_kills: int = Field(default=0)
    blue_side_towers: int = Field(default=0)
    red_side_towers: int = Field(default=0)
    blue_side_dragons: int = Field(default=0)
    red_side_dragons: int = Field(default=0)
    blue_side_barons: int = Field(default=0)
    red_side_barons: int = Field(default=0)

    # Additional map data (picks, bans, etc.)
    map_data: Optional[str] = Field(default=None)

    # Relationships
    match: "Match" = Relationship(back_populates="map_results")
    winner_team: "MobaTeam" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "MapResult.winner_team_id"}
    )
    blue_side_team: "MobaTeam" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "MapResult.blue_side_team_id"}
    )
    red_side_team: "MobaTeam" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "MapResult.red_side_team_id"}
    )
    player_stats: List["MatchPlayerStats"] = Relationship(back_populates="map_result")

    def get_map_data(self) -> Dict[str, Any]:
        """
        Get map data as a Python dictionary.

        Returns:
            Dict containing additional map data (picks, bans, etc.)
        """
        if not self.map_data:
            return {}
        return json.loads(self.map_data)

    def set_map_data(self, data: Dict[str, Any]) -> None:
        """
        Set map data from a Python dictionary.

        Args:
            data: Dictionary containing map data
        """
        self.map_data = json.dumps(data)

    def __str__(self) -> str:
        """String representation of a map result."""
        return f"Map {self.map_number}: Blue {self.blue_side_kills}-{self.red_side_kills} Red (Winner: {self.winner_team_id})"


class MatchPlayerStats(SQLModel, table=True):
    """Model representing a player's performance in a single map of a match."""

    __tablename__ = "match_player_stats"

    id: Optional[int] = Field(default=None, primary_key=True)
    player_id: int = Field(foreign_key="moba_player.id", index=True)
    match_id: int = Field(foreign_key="match.id", index=True)
    map_number: int = Field(index=True)
    map_result_id: Optional[int] = Field(default=None, foreign_key="map_result.id")
    team_id: int = Field(foreign_key="moba_team.id")
    champion_id: int = Field(foreign_key="champion.id")

    # Performance stats
    kills: int = Field(default=0)
    deaths: int = Field(default=0)
    assists: int = Field(default=0)
    cs: int = Field(default=0)  # Creep Score
    vision_score: int = Field(default=0)
    gold_earned: int = Field(default=0)
    damage_dealt: int = Field(default=0)
    healing: int = Field(default=0)
    damage_taken: int = Field(default=0)
    objectives_stolen: int = Field(default=0)
    skill_shots_hit: int = Field(default=0)
    skill_shots_missed: int = Field(default=0)
    crowd_control_score: int = Field(default=0)

    # Additional data (runes, items, skill order, etc.)
    additional_data: Optional[str] = Field(default=None)

    # Relationships
    player: "MobaPlayer" = Relationship()
    match: "Match" = Relationship(back_populates="player_stats")
    team: "MobaTeam" = Relationship()
    champion: "Champion" = Relationship()
    map_result: Optional[MapResult] = Relationship(back_populates="player_stats")

    @property
    def kda(self) -> float:
        """Calculate KDA (Kills + Assists / Deaths)."""
        if self.deaths == 0:
            return self.kills + self.assists
        return (self.kills + self.assists) / self.deaths

    def get_additional_data(self) -> Dict[str, Any]:
        """Get additional performance data as a Python dictionary."""
        if not self.additional_data:
            return {}
        return json.loads(self.additional_data)

    def set_additional_data(self, data: Dict[str, Any]) -> None:
        """Set additional performance data from a Python dictionary."""
        self.additional_data = json.dumps(data)

    @staticmethod
    def get_player_history(
        session: Session, player_id: int
    ) -> List["MatchPlayerStats"]:
        """
        Get a player's match performance history.

        Args:
            session: SQLModel session
            player_id: ID of the player

        Returns:
            List of match player stats for the given player
        """
        return session.exec(
            select(MatchPlayerStats)
            .where(MatchPlayerStats.player_id == player_id)
            .order_by(MatchPlayerStats.id.desc())
        ).all()

    def __str__(self) -> str:
        """String representation of a player's match performance."""
        return f"Player {self.player_id} on Map {self.map_number}: {self.kills}/{self.deaths}/{self.assists}"


class MatchPerformance(SQLModel, table=True):
    """
    Model for aggregating and analyzing match performance data.
    This serves as a central point for accessing all performance data for a match.
    """

    __tablename__ = "match_performance"

    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="match.id", primary_key=True)
    analysis_date: datetime = Field(default_factory=datetime.now)

    # Relationships
    match: "Match" = Relationship()

    def aggregate_stats(self, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Aggregate match statistics from all maps and players.

        Args:
            session: SQLModel session to use for database queries

        Returns:
            Dictionary containing aggregated team and player stats
        """
        # Ensure match and related data are loaded
        match = self.match

        # Get all map results for this match
        map_results = match.map_results

        # Query for player stats
        player_stats_query = select(MatchPlayerStats).where(
            MatchPlayerStats.match_id == match.id
        )

        # Use provided session or get player stats directly from existing data
        if session:
            player_stats_list = session.exec(player_stats_query).all()
        else:
            # Fallback to getting stats from match relationship if available
            player_stats_list = (
                match.player_stats
                if hasattr(match, "player_stats") and match.player_stats
                else []
            )

        # Organize player stats by player ID
        player_stats_by_id = defaultdict(list)
        for ps in player_stats_list:
            player_stats_by_id[ps.player_id].append(ps)

        # Initialize result structure
        result = {
            "team_stats": [],
            "player_stats": [],
        }

        # Aggregate team stats
        team_stats = {
            match.home_team_id: {
                "team_id": match.home_team_id,
                "team_name": match.home_team.name,
                "maps_won": 0,
                "total_kills": 0,
                "total_deaths": 0,
                "total_gold": 0,
                "total_barons": 0,
                "total_dragons": 0,
            },
            match.away_team_id: {
                "team_id": match.away_team_id,
                "team_name": match.away_team.name,
                "maps_won": 0,
                "total_kills": 0,
                "total_deaths": 0,
                "total_gold": 0,
                "total_barons": 0,
                "total_dragons": 0,
            },
        }

        # Process map results
        for map_result in map_results:
            # Update winner
            team_stats[map_result.winner_team_id]["maps_won"] += 1

            # Add blue side stats to the correct team
            blue_team_id = map_result.blue_side_team_id
            team_stats[blue_team_id]["total_kills"] += map_result.blue_side_kills
            team_stats[blue_team_id]["total_deaths"] += map_result.red_side_kills
            team_stats[blue_team_id]["total_gold"] += map_result.blue_side_gold
            team_stats[blue_team_id]["total_barons"] += map_result.blue_side_barons
            team_stats[blue_team_id]["total_dragons"] += map_result.blue_side_dragons

            # Add red side stats to the correct team
            red_team_id = map_result.red_side_team_id
            team_stats[red_team_id]["total_kills"] += map_result.red_side_kills
            team_stats[red_team_id]["total_deaths"] += map_result.blue_side_kills
            team_stats[red_team_id]["total_gold"] += map_result.red_side_gold
            team_stats[red_team_id]["total_barons"] += map_result.red_side_barons
            team_stats[red_team_id]["total_dragons"] += map_result.red_side_dragons

        # Add team stats to result
        result["team_stats"] = list(team_stats.values())

        # Aggregate player stats
        for player_id, stats_list in player_stats_by_id.items():
            if not stats_list:
                continue

            # Get player reference from first stats entry
            player = stats_list[0].player

            # Aggregate player stats across all maps
            aggregate = {
                "player_id": player_id,
                "player_name": player.name,
                "team_id": stats_list[0].team_id,
                "maps_played": len(stats_list),
                "kills": sum(ps.kills for ps in stats_list),
                "deaths": sum(ps.deaths for ps in stats_list),
                "assists": sum(ps.assists for ps in stats_list),
                "total_cs": sum(ps.cs for ps in stats_list),
                "avg_vision_score": sum(ps.vision_score for ps in stats_list)
                / len(stats_list),
                "total_damage_dealt": sum(ps.damage_dealt for ps in stats_list),
                "avg_damage_per_map": sum(ps.damage_dealt for ps in stats_list)
                / len(stats_list),
                "total_healing": sum(ps.healing for ps in stats_list),
                "champions_played": len(set(ps.champion_id for ps in stats_list)),
            }

            # Calculate KDA
            aggregate["kda"] = (aggregate["kills"] + aggregate["assists"]) / max(
                1, aggregate["deaths"]
            )

            # Add to result
            result["player_stats"].append(aggregate)

        return result

    def calculate_mvp(self, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Calculate the MVP (Most Valuable Player) of the match.

        Args:
            session: SQLModel session to use for database queries

        Returns:
            Dictionary with MVP information including player ID and statistics
        """
        # Get player stats for this match
        player_stats_query = select(MatchPlayerStats).where(
            MatchPlayerStats.match_id == self.match_id
        )

        # Use provided session or get player stats directly from existing data
        if session:
            player_stats_list = session.exec(player_stats_query).all()
        else:
            # Fallback to getting stats from match relationship if available
            player_stats_list = (
                self.match.player_stats
                if hasattr(self.match, "player_stats") and self.match.player_stats
                else []
            )

        # Organize player stats by player ID
        player_stats_by_id = defaultdict(list)
        for ps in player_stats_list:
            player_stats_by_id[ps.player_id].append(ps)

        # Calculate MVP score for each player
        mvp_scores = []
        for player_id, stats_list in player_stats_by_id.items():
            if not stats_list:
                continue

            # MVP score factors
            total_kills = sum(ps.kills for ps in stats_list)
            total_deaths = sum(ps.deaths for ps in stats_list)
            total_assists = sum(ps.assists for ps in stats_list)
            total_cs = sum(ps.cs for ps in stats_list)
            total_vision = sum(ps.vision_score for ps in stats_list)
            total_damage = sum(ps.damage_dealt for ps in stats_list)
            objectives_stolen = sum(ps.objectives_stolen for ps in stats_list)
            maps_played = len(stats_list)

            # Create a weighted score
            kda = (total_kills + total_assists) / max(1, total_deaths)
            kill_participation = (total_kills + total_assists) / max(
                1,
                sum(
                    ps.team.kills if hasattr(ps.team, "kills") else 10
                    for ps in stats_list
                ),
            )

            # MVP score formula
            mvp_score = (
                kda * 0.3
                + (total_damage / maps_played) * 0.25
                + kill_participation * 0.2
                + (total_vision / maps_played) * 0.15
                + (objectives_stolen * 2)
                + (total_cs / maps_played) * 0.1
            )

            mvp_scores.append(
                {
                    "player_id": player_id,
                    "player": stats_list[0].player,
                    "score": mvp_score,
                    "stats": {
                        "kills": total_kills,
                        "deaths": total_deaths,
                        "assists": total_assists,
                        "kda": kda,
                        "vision_score": total_vision,
                        "damage_dealt": total_damage,
                        "objectives_stolen": objectives_stolen,
                        "cs": total_cs,
                    },
                }
            )

        # Sort by MVP score (descending)
        mvp_scores.sort(key=lambda x: x["score"], reverse=True)

        # Return the top player (MVP)
        return (
            mvp_scores[0]
            if mvp_scores
            else {"player_id": None, "score": 0, "stats": {}}
        )
