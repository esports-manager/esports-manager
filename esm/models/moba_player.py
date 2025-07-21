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
from sqlmodel import Field, Relationship, Column, SQLModel
from sqlalchemy import Enum as SQLAlchemyEnum
from typing import Optional, Dict, List, TYPE_CHECKING
import json
import enum
from datetime import date, datetime

from .person import Person

if TYPE_CHECKING:
    from .champion_mastery import ChampionMastery
    from .moba_team import MobaTeam


class PlayerRole(str, enum.Enum):
    TOP = "top"
    JUNGLE = "jungle"
    MID = "mid"
    ADC = "adc"
    SUPPORT = "support"


class ContractStatus(str, enum.Enum):
    SIGNED = "signed"
    FREE_AGENT = "free_agent"
    TRANSFER_LISTED = "transfer_listed"
    RETIRED = "retired"


# Base class for shared player attributes
class MobaPlayerBase(SQLModel):
    name: str
    full_name: Optional[str] = None
    nationality: str
    bio: Optional[str] = None
    image_path: Optional[str] = None

    # Role and skills
    role: PlayerRole = PlayerRole.MID
    mechanics: int = 50
    game_knowledge: int = 50
    team_fighting: int = 50
    champion_pool_size: int = 50
    laning: int = 50

    # Performance stats
    form: int = Field(default=75)
    morale: int = Field(default=75)


# Database model inheriting from Person
class MobaPlayer(Person, table=True):
    """Database model representing a MOBA (League of Legends) player.
    Inherits from Person base model using SQLModel inheritance.
    """

    __tablename__ = "moba_player"

    role: PlayerRole = Field(
        sa_column=Column(SQLAlchemyEnum(PlayerRole)), default=PlayerRole.MID
    )

    # Player skills (0-100 scale)
    mechanics: int = Field(
        default=50, description="Technical skill at executing game mechanics"
    )
    game_knowledge: int = Field(
        default=50, description="Understanding of game strategy and decision making"
    )
    team_fighting: int = Field(default=50, description="Ability in team fights")
    champion_pool_size: int = Field(
        default=50, description="Versatility with different champions"
    )
    laning: int = Field(default=50, description="Skill during the laning phase")

    # Champion mastery stored as JSON string
    champion_mastery: Optional[str] = Field(default=None)

    # Contract information
    contract_status: ContractStatus = Field(
        sa_column=Column(SQLAlchemyEnum(ContractStatus)),
        default=ContractStatus.FREE_AGENT,
        description="Contract status",
    )
    team_id: Optional[int] = Field(default=None, foreign_key="moba_team.id")
    salary: Optional[float] = Field(default=None)
    contract_start_date: Optional[date] = Field(default=None)
    contract_end_date: Optional[date] = Field(default=None)

    # Performance stats
    matches_played: int = Field(default=0)
    wins: int = Field(default=0)
    losses: int = Field(default=0)
    kda_ratio: float = Field(default=0.0)

    # Form and fitness (0-100 scale)
    form: int = Field(default=75)
    morale: int = Field(default=75)

    # Relationships
    champion_masteries: List["ChampionMastery"] = Relationship(back_populates="player")
    team: Optional["MobaTeam"] = Relationship(back_populates="players")

    # No relationship to Person needed since we inherit directly

    @property
    def overall_rating(self) -> int:
        """
        Calculate the player's overall rating based on their attributes
        Different weights are assigned to different attributes based on importance
        """
        weights = {
            "mechanics": 0.3,
            "game_knowledge": 0.25,
            "team_fighting": 0.2,
            "champion_pool_size": 0.15,
            "laning": 0.1,
        }

        # Calculate weighted average
        weighted_sum = (
            self.mechanics * weights["mechanics"]
            + self.game_knowledge * weights["game_knowledge"]
            + self.team_fighting * weights["team_fighting"]
            + self.champion_pool_size * weights["champion_pool_size"]
            + self.laning * weights["laning"]
        )

        # Round to nearest integer
        return round(weighted_sum)

    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage"""
        if self.matches_played == 0:
            return 0.0
        return (self.wins / self.matches_played) * 100

    def get_champion_mastery_dict(self) -> Dict[str, int]:
        """Get legacy champion mastery as a dictionary.

        This method is maintained for backward compatibility.
        New code should use the champion_masteries relationship instead.

        Returns:
            Dict containing champion names mapped to mastery levels
        """
        if not self.champion_mastery:
            return {}
        return json.loads(self.champion_mastery)

    def set_champion_mastery_dict(self, mastery_dict: Dict[str, int]) -> None:
        """Set legacy champion mastery from a dictionary.

        This method is maintained for backward compatibility.
        New code should use the champion_masteries relationship instead.

        Args:
            mastery_dict: Dictionary mapping champion names to mastery levels
        """
        self.champion_mastery = json.dumps(mastery_dict)

    # Maintain old method names for backward compatibility
    get_champion_mastery = get_champion_mastery_dict
    set_champion_mastery = set_champion_mastery_dict

    def get_effective_champion_pool(
        self, min_mastery_level: int = 70
    ) -> List["ChampionMastery"]:
        """Get the player's effective champion pool based on mastery level.

        Returns a list of ChampionMastery objects where the player has at least the
        specified minimum mastery level. This represents champions the player can
        effectively play in competitive matches.

        Args:
            min_mastery_level: Minimum mastery level to consider a champion in the pool
                              (default: 70)

        Returns:
            List of ChampionMastery objects meeting the minimum mastery criteria
        """
        return [
            cm
            for cm in self.champion_masteries
            if cm.mastery_level >= min_mastery_level
        ]

    def get_champion_pool_size(self, min_mastery_level: int = 70) -> int:
        """Get the size of the player's effective champion pool.

        Counts champions where the player has at least the specified minimum mastery level.

        Args:
            min_mastery_level: Minimum mastery level to consider a champion in the pool
                              (default: 70)

        Returns:
            Integer count of champions in the player's effective pool
        """
        return len(self.get_effective_champion_pool(min_mastery_level))

    def get_role_champion_pool(
        self, role: str, min_mastery_level: int = 70
    ) -> List["ChampionMastery"]:
        """Get the player's champion pool for a specific role.

        Args:
            role: The role to filter champions by (e.g., ROLE_MID)
            min_mastery_level: Minimum mastery level to consider a champion in the pool
                              (default: 70)

        Returns:
            List of ChampionMastery objects for the specified role meeting the minimum mastery
        """
        from sqlmodel import select
        from sqlalchemy.orm import selectinload

        session = getattr(self, "_sa_instance_state", None)
        if session and session.session:
            from .champion import Champion
            from .champion_mastery import ChampionMastery

            stmt = (
                select(ChampionMastery)
                .join(Champion)
                .where(
                    ChampionMastery.player_id == self.id,
                    ChampionMastery.mastery_level >= min_mastery_level,
                    Champion.primary_role == role,
                )
                .options(selectinload(ChampionMastery.champion))
            )

            return session.session.exec(stmt).all()
        else:
            return [
                cm
                for cm in self.champion_masteries
                if cm.mastery_level >= min_mastery_level
                and cm.champion
                and cm.champion.primary_role == role
            ]

    def __repr__(self):
        return f"<Player {self.name} ({self.role.value})>"

    def __str__(self):
        return self.name


# API Models for Player
class MobaPlayerCreate(MobaPlayerBase):
    date_of_birth: str
    contract_status: Optional[ContractStatus] = ContractStatus.FREE_AGENT
    team_id: Optional[int] = None
    salary: Optional[float] = None
    contract_start_date: Optional[str] = None
    contract_end_date: Optional[str] = None


class MobaPlayerRead(MobaPlayerBase):
    id: int
    date_of_birth: date
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Contract information
    contract_status: ContractStatus = ContractStatus.FREE_AGENT
    team_id: Optional[int] = None
    salary: Optional[float] = None
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None

    # Performance stats
    matches_played: int
    wins: int
    losses: int
    kda_ratio: float

    # Champion mastery as parsed dictionary
    champion_mastery: Optional[Dict[str, int]] = None

    model_config = {"from_attributes": True}


class MobaPlayerUpdate(SQLModel):
    name: Optional[str] = None
    full_name: Optional[str] = None
    nationality: Optional[str] = None
    date_of_birth: Optional[str] = None
    bio: Optional[str] = None
    image_path: Optional[str] = None

    # Role and skills
    role: Optional[PlayerRole] = None
    mechanics: Optional[int] = None
    game_knowledge: Optional[int] = None
    team_fighting: Optional[int] = None
    champion_pool_size: Optional[int] = None
    laning: Optional[int] = None

    # Contract information
    contract_status: Optional[ContractStatus] = None
    team_id: Optional[int] = None
    salary: Optional[float] = None
    contract_start_date: Optional[str] = None
    contract_end_date: Optional[str] = None

    # Performance stats
    form: Optional[int] = None
    morale: Optional[int] = None
