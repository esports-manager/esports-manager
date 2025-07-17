"""
MOBA Team Model

This module defines the MobaTeam model for representing professional esports teams.
"""

from sqlmodel import Field, SQLModel, Relationship, Column
from sqlalchemy import Enum as SQLAlchemyEnum
from typing import Optional, List, Dict, Any, TYPE_CHECKING
import json
import enum
from datetime import date

if TYPE_CHECKING:
    from .moba_player import MobaPlayer
    from .staff import Staff


class TeamRegion(enum.Enum):
    NA = "na"
    EU = "eu"
    KR = "kr"
    CN = "cn"
    OTHER = "other"


class MobaTeam(SQLModel, table=True):
    """
    Model representing a professional MOBA team.

    Attributes:
        id: Unique identifier
        name: Team name
        tag: Short team tag (usually 2-4 letters)
        region: Team's primary region
        founded_date: When the team was established
        logo_path: Local path to team logo image file
        # website field removed as it's not needed for offline use
        description: Team description or history
        home_venue: Team's home venue for matches
        current_ranking: Current ranking in their region
        coach_id: Foreign key to Person model for the team's coach (to be implemented)
        achievements: JSON string containing team's achievements
        social_media: JSON string containing social media handles
        sponsors: JSON string containing team's sponsors
        organization_value: Estimated value of the team organization
    """

    __tablename__ = "moba_team"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    tag: str = Field(max_length=10)
    region: TeamRegion = Field(
        sa_column=Column(SQLAlchemyEnum(TeamRegion)),
        default=TeamRegion.NA,
        description="Team's primary region",
    )
    founded_date: Optional[date] = Field(default=None)
    logo_path: Optional[str] = Field(default=None)  # Path to local image file
    # website field removed as it's not needed for offline use
    description: Optional[str] = Field(default=None)
    home_venue: Optional[str] = Field(default=None)
    current_ranking: Optional[int] = Field(default=None)
    # No longer need coach_id as coaches are now part of staff

    # JSON stored data
    achievements: Optional[str] = Field(default=None)
    social_media: Optional[str] = Field(default=None)
    sponsors: Optional[str] = Field(default=None)

    # Financial data
    organization_value: Optional[float] = Field(default=None)
    yearly_revenue: Optional[float] = Field(default=None)
    salary_cap: Optional[float] = Field(default=None)

    # Relationships
    players: List["MobaPlayer"] = Relationship(back_populates="team")
    staff: List["Staff"] = Relationship(back_populates="team")

    @property
    def head_coach(self) -> Optional["Staff"]:
        """Get the team's head coach (a staff member with is_head_coach=True)"""
        for staff_member in self.staff:
            if staff_member.is_head_coach:
                return staff_member
        return None

    def get_achievements(self) -> Dict[str, Any]:
        """
        Get team achievements as a dictionary.

        Returns:
            Dict containing achievement data or empty dict if no data is set
        """
        if not self.achievements:
            return {}
        return json.loads(self.achievements)

    def set_achievements(self, achievements_dict: Dict[str, Any]) -> None:
        """
        Set team achievements from a dictionary.

        Args:
            achievements_dict: Dictionary containing achievement data
        """
        self.achievements = json.dumps(achievements_dict)

    def get_social_media(self) -> Dict[str, str]:
        """
        Get team social media handles as a dictionary.

        Returns:
            Dict containing social media platforms mapped to handles
        """
        if not self.social_media:
            return {}
        return json.loads(self.social_media)

    def set_social_media(self, social_media_dict: Dict[str, str]) -> None:
        """
        Set team social media handles from a dictionary.

        Args:
            social_media_dict: Dictionary mapping platforms to handles
        """
        self.social_media = json.dumps(social_media_dict)

    def get_sponsors(self) -> List[Dict[str, Any]]:
        """
        Get team sponsors as a list of dictionaries.

        Returns:
            List of sponsor data or empty list if no sponsors
        """
        if not self.sponsors:
            return []
        return json.loads(self.sponsors)

    def set_sponsors(self, sponsors_list: List[Dict[str, Any]]) -> None:
        """
        Set team sponsors from a list of dictionaries.

        Args:
            sponsors_list: List of dictionaries with sponsor data
        """
        self.sponsors = json.dumps(sponsors_list)

    def get_roster_by_role(self) -> Dict[str, List["MobaPlayer"]]:
        """
        Get team roster organized by player roles.

        Returns:
            Dictionary with roles as keys and lists of players as values
        """
        from .moba_player import PlayerRole

        roster = {
            PlayerRole.TOP: [],
            PlayerRole.JUNGLE: [],
            PlayerRole.MID: [],
            PlayerRole.ADC: [],
            PlayerRole.SUPPORT: [],
            "substitute": [],
            "other": [],
        }

        for player in self.players:
            if player.role in roster:
                roster[player.role].append(player)
            else:
                roster["other"].append(player)

        return roster

    def calculate_avg_player_rating(self) -> float:
        """
        Calculate the average player rating for the team.

        Returns:
            Float representing average overall rating of all players
        """
        if not self.players:
            return 0.0

        total_rating = sum(player.overall_rating for player in self.players)
        return total_rating / len(self.players)

    def years_active(self) -> int:
        """
        Calculate years the team has been active.

        Returns:
            Number of years since the team was founded
            Returns 0 for future dates or if no founding date is set
        """
        if not self.founded_date:
            return 0

        today = date.today()
        years = today.year - self.founded_date.year

        # Adjust if founding date hasn't occurred yet this year
        if (today.month, today.day) < (self.founded_date.month, self.founded_date.day):
            years -= 1

        # Return 0 for future or current dates
        return max(0, years)

    def __repr__(self) -> str:
        """
        Return string representation of the Team.

        Returns:
            String containing team name, tag, and region
        """
        return f"<MobaTeam: {self.name} ({self.tag}, {self.region.value})>"

    def __str__(self) -> str:
        """
        String representation, same as __repr__
        """
        return self.__repr__()
