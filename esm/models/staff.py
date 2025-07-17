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
from sqlmodel import Field, Relationship, Column
from sqlalchemy import Enum as SQLAlchemyEnum
from typing import Optional, Dict, List, Any, TYPE_CHECKING
import json
import enum
from datetime import date

from .person import Person

if TYPE_CHECKING:
    from .moba_team import MobaTeam


class CoachType(enum.Enum):
    HEAD_COACH = "head_coach"
    ASSISTANT_COACH = "assistant_coach"
    STRATEGIC_COACH = "strategic_coach"
    POSITIONAL_COACH = "positional_coach"


class Department(enum.Enum):
    """Enumeration of staff departments"""

    COACHING = "coaching"
    PERFORMANCE = "performance"
    ANALYSIS = "analysis"
    MEDICAL = "medical"
    SCOUTING = "scouting"
    MANAGEMENT = "management"
    OTHER = "other"


class CoachingStyle(enum.Enum):
    """Enumeration of coaching styles"""

    OFFENSIVE = "offensive"
    DEFENSIVE = "defensive"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    ANALYTICAL = "analytical"
    ADAPTIVE = "adaptive"


class JobTitle(enum.Enum):
    """Enumeration of staff job titles"""

    # Coaching department
    HEAD_COACH = "head_coach"
    ASSISTANT_COACH = "assistant_coach"
    STRATEGIC_COACH = "strategic_coach"
    POSITIONAL_COACH = "positional_coach"

    # Performance department
    PERFORMANCE_DIRECTOR = "performance_director"
    MENTAL_COACH = "mental_coach"
    FITNESS_TRAINER = "fitness_trainer"

    # Analysis department
    HEAD_ANALYST = "head_analyst"
    DATA_ANALYST = "data_analyst"
    OPPOSITION_ANALYST = "opponent_analyst"

    # Medical department
    TEAM_DOCTOR = "team_doctor"
    PHYSIOTHERAPIST = "physiotherapist"
    NUTRITIONIST = "nutritionist"

    # Scouting department
    HEAD_SCOUT = "head_scout"
    TALENT_SCOUT = "talent_scout"
    REGIONAL_SCOUT = "regional_scout"

    # Management department
    GENERAL_MANAGER = "general_manager"
    TEAM_MANAGER = "team_manager"
    ESPORTS_DIRECTOR = "esports_director"


# Contract status constants (same as other models for consistency)
class ContractStatus(enum.Enum):
    SIGNED = "signed"
    FREE_AGENT = "free_agent"
    TRANSFER_LISTED = "transfer_listed"
    RETIRED = "retired"


# No longer need to define valid statuses as the enum handles this


class Staff(Person, table=True):
    """
    Model representing staff members in the esports ecosystem.
    Inherits from Person base model using SQLModel inheritance.
    This consolidated model handles both coaching staff and other team staff.

    Attributes:
        id: Inherited from Person, primary key
        name, full_name, nationality, date_of_birth: Inherited from Person

        # Staff identification
        staff_type: Type of staff (coach or assistant)
        department: The department this staff member works in
        job_title: The staff member's specific role/title
        years_experience: Years of experience in their field
        former_player: Whether the staff was a former professional player

        # For coaching staff (when staff_type = coach)
        coaching_style: Preferred coaching style
        tactics: Tactical knowledge and ability to create strategies
        player_development: Skill at developing players' abilities
        motivation: Ability to motivate players
        game_knowledge: Understanding of game mechanics and meta
        draft_skill: Skill at drafting team compositions

        # For general staff
        knowledge: Domain knowledge in their specialized field
        work_rate: Work ethic and productivity
        communication: Communication and interpersonal skills
        adaptability: Ability to adapt to changes and learn new things
        management: Leadership and management capabilities
        technical_skill: Technical expertise in their field
        innovation: Ability to innovate and find creative solutions

        # Contract information
        contract_status: Current contract status
        salary: Annual salary in currency units
        contract_start_date: When the current contract started
        contract_end_date: When the current contract will end

        # Additional information
        achievements: JSON string containing career achievements
        specializations: JSON string containing areas of specialization (for coaches)
        education: JSON string containing education history
        certifications: JSON string containing professional certifications
        previous_experience: JSON string containing work history
        previous_teams: JSON string containing previous teams (mainly for coaches)
    """

    __tablename__ = "staff"

    # Staff identification
    staff_type: str = Field(
        sa_column=Column(SQLAlchemyEnum(CoachType)),
        description="Type of staff (coach or assistant)",
    )
    department: Department = Field(
        sa_column=Column(SQLAlchemyEnum(Department)), description="Staff department"
    )
    job_title: JobTitle = Field(
        sa_column=Column(SQLAlchemyEnum(JobTitle)), description="Specific role or title"
    )
    years_experience: int = Field(default=0)
    former_player: bool = Field(default=False)

    # Coach-specific attributes (when staff_type = coach)
    coaching_style: Optional[CoachingStyle] = Field(
        sa_column=Column(SQLAlchemyEnum(CoachingStyle)), default=CoachingStyle.BALANCED
    )
    tactics: int = Field(default=50, description="Tactical knowledge and game strategy")
    player_development: int = Field(
        default=50, description="Ability to improve players"
    )
    motivation: int = Field(default=50, description="Leadership and team motivation")
    game_knowledge: int = Field(
        default=50, description="Understanding of game mechanics and meta"
    )
    draft_skill: int = Field(
        default=50, description="Champion draft and composition building"
    )

    # Staff attributes (0-100 scale)
    knowledge: int = Field(default=50, description="Domain knowledge in their field")
    work_rate: int = Field(default=50, description="Work ethic and productivity")
    communication: int = Field(
        default=50, description="Communication and interpersonal skills"
    )
    adaptability: int = Field(default=50, description="Ability to adapt to changes")
    management: int = Field(
        default=50, description="Leadership and management capability"
    )

    # Department-specific attributes (0-100 scale)
    technical_skill: int = Field(
        default=50, description="Technical expertise in their field"
    )
    innovation: int = Field(default=50, description="Creativity and innovation ability")

    # Contract information
    contract_status: ContractStatus = Field(
        sa_column=Column(SQLAlchemyEnum(ContractStatus), index=True),
        default=ContractStatus.FREE_AGENT,
    )
    salary: Optional[float] = Field(default=None)
    contract_start_date: Optional[date] = Field(default=None)
    contract_end_date: Optional[date] = Field(default=None)

    # JSON stored data
    achievements: Optional[str] = Field(default=None)
    specializations: Optional[str] = Field(default=None)  # For coaches
    education: Optional[str] = Field(default=None)
    certifications: Optional[str] = Field(default=None)
    previous_experience: Optional[str] = Field(default=None)
    previous_teams: Optional[str] = Field(default=None)  # For coaches

    # Relationships
    team_id: Optional[int] = Field(default=None, foreign_key="moba_team.id")
    team: Optional["MobaTeam"] = Relationship(back_populates="staff")
    is_head_coach: bool = Field(
        default=False, description="Whether this staff member is the team's head coach"
    )

    @property
    def overall_rating(self) -> int:
        """
        Calculate the staff member's overall rating based on their attributes
        Different weights are assigned to different attributes based on department and staff type

        Returns:
            Integer representing overall staff rating (0-100)
        """
        # If staff type is coach, use coach-specific rating calculation
        if self.staff_type == CoachType.HEAD_COACH:
            # Coach rating weights
            coach_weights = {
                "tactics": 0.25,
                "player_development": 0.20,
                "motivation": 0.15,
                "game_knowledge": 0.25,
                "draft_skill": 0.15,
            }

            # Calculate weighted average for coach
            weighted_sum = (
                self.tactics * coach_weights["tactics"]
                + self.player_development * coach_weights["player_development"]
                + self.motivation * coach_weights["motivation"]
                + self.game_knowledge * coach_weights["game_knowledge"]
                + self.draft_skill * coach_weights["draft_skill"]
            )

            return round(weighted_sum)
        else:
            # Base weights for regular staff
            base_weights = {
                "knowledge": 0.15,
                "work_rate": 0.15,
                "communication": 0.1,
                "adaptability": 0.1,
                "management": 0.1,
                "technical_skill": 0.2,
                "innovation": 0.2,
            }

            # Department-specific weight adjustments
            dept_adjustments = {
                Department.COACHING: {
                    "knowledge": 0.2,
                    "communication": 0.15,
                    "management": 0.15,
                },
                Department.PERFORMANCE: {"technical_skill": 0.25, "adaptability": 0.15},
                Department.ANALYSIS: {
                    "knowledge": 0.2,
                    "technical_skill": 0.3,
                    "innovation": 0.25,
                },
                Department.MEDICAL: {"technical_skill": 0.3, "knowledge": 0.25},
                Department.SCOUTING: {"knowledge": 0.2, "innovation": 0.25},
                Department.MANAGEMENT: {"management": 0.25, "communication": 0.2},
            }

            # Apply department-specific adjustments if applicable
            weights = base_weights.copy()
            if self.department in dept_adjustments:
                for attr, val in dept_adjustments[self.department].items():
                    weights[attr] = val

            # Normalize weights to ensure they sum to 1.0
            total_weight = sum(weights.values())
            if total_weight != 1.0:
                for key in weights:
                    weights[key] /= total_weight

            # Calculate weighted average for regular staff
            weighted_sum = (
                self.knowledge * weights["knowledge"]
                + self.work_rate * weights["work_rate"]
                + self.communication * weights["communication"]
                + self.adaptability * weights["adaptability"]
                + self.management * weights["management"]
                + self.technical_skill * weights["technical_skill"]
                + self.innovation * weights["innovation"]
            )

            # Round to nearest integer
            return round(weighted_sum)

    def get_achievements(self) -> Dict[str, Any]:
        """
        Get staff achievements as a dictionary.

        Returns:
            Dict containing achievement data or empty dict if no data is set
        """
        if not self.achievements:
            return {}
        return json.loads(self.achievements)

    def set_achievements(self, achievements_dict: Dict[str, Any]) -> None:
        """
        Set staff achievements from a dictionary.

        Args:
            achievements_dict: Dictionary containing achievement data
        """
        self.achievements = json.dumps(achievements_dict)

    def get_specializations(self) -> List[str]:
        """
        Get staff's areas of specialization.
        Primarily used for coaching staff, but can apply to others.

        Returns:
            List of specialization areas (e.g. ["mid lane", "team fighting"])
        """
        if not self.specializations:
            return []
        return json.loads(self.specializations)

    def set_specializations(self, specializations_list: List[str]) -> None:
        """
        Set staff's areas of specialization.

        Args:
            specializations_list: List of specialization areas
        """
        self.specializations = json.dumps(specializations_list)

    def get_previous_teams(self) -> List[Dict[str, Any]]:
        """
        Get staff's previous teams and positions.
        Primarily used for coaching staff, but can apply to others.

        Returns:
            List of dictionaries with previous team data
        """
        if not self.previous_teams:
            return []
        return json.loads(self.previous_teams)

    def set_previous_teams(self, teams_list: List[Dict[str, Any]]) -> None:
        """
        Set staff's previous teams and positions.

        Args:
            teams_list: List of dictionaries with previous team data
        """
        self.previous_teams = json.dumps(teams_list)

    def get_education(self) -> List[Dict[str, Any]]:
        """
        Get staff's education history.

        Returns:
            List of dictionaries with education details
        """
        if not self.education:
            return []
        return json.loads(self.education)

    def set_education(self, education_list: List[Dict[str, Any]]) -> None:
        """
        Set staff's education history.

        Args:
            education_list: List of dictionaries with education details
        """
        self.education = json.dumps(education_list)

    def get_certifications(self) -> List[Dict[str, Any]]:
        """
        Get staff's professional certifications.

        Returns:
            List of dictionaries with certification details
        """
        if not self.certifications:
            return []
        return json.loads(self.certifications)

    def set_certifications(self, certifications_list: List[Dict[str, Any]]) -> None:
        """
        Set staff's professional certifications.

        Args:
            certifications_list: List of dictionaries with certification details
        """
        self.certifications = json.dumps(certifications_list)

    def get_previous_experience(self) -> List[Dict[str, Any]]:
        """
        Get staff's work history.

        Returns:
            List of dictionaries with previous work experience details
        """
        if not self.previous_experience:
            return []
        return json.loads(self.previous_experience)

    def set_previous_experience(self, experience_list: List[Dict[str, Any]]) -> None:
        """
        Set staff's work history.

        Args:
            experience_list: List of dictionaries with previous work experience details
        """
        self.previous_experience = json.dumps(experience_list)

    def is_contract_expired(self) -> bool:
        """
        Check if the staff member's contract is expired.

        Returns:
            True if contract has expired, False otherwise
        """
        if not self.contract_end_date:
            return False

        today = date.today()
        return today > self.contract_end_date

    def contract_years_remaining(self) -> float:
        """
        Calculate years remaining on current contract.

        Returns:
            Number of years remaining on contract (can be fractional)
            Returns 0 if no contract or contract expired
        """
        if not self.contract_end_date or self.is_contract_expired():
            return 0.0

        today = date.today()
        days_remaining = (self.contract_end_date - today).days
        return max(0.0, days_remaining / 365.0)

    def __repr__(self) -> str:
        """
        String representation of a Staff member
        """
        if self.department == Department.COACHING:
            if self.staff_type == CoachType.HEAD_COACH and self.is_head_coach:
                return f"<Staff: {self.name} (Head Coach, {self.nationality}, Style: {self.coaching_style.value})>"
            elif self.staff_type == CoachType.ASSISTANT_COACH:
                return f"<Staff: {self.name} (Coach, {self.nationality}, Style: {self.coaching_style.value})>"

        # For non-coaches and other staff
        return f"<Staff: {self.name} ({self.nationality}, Dept: {self.department.value}, Role: {self.job_title.value})>"

    def __str__(self) -> str:
        """
        String representation, same as __repr__
        """
        return self.__repr__()
