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
from typing import Dict, List, Optional, Any, TYPE_CHECKING
import json
import time
import random
from sqlalchemy import Column, Enum as SQLAlchemyEnum
from sqlmodel import Field, Relationship, SQLModel
from pydantic import ConfigDict
from enum import Enum

if TYPE_CHECKING:
    from .match import Match
    from .moba_team import MobaTeam


class PickBanMode(str, Enum):
    """Mode of the pick/ban phase - user participation or AI-controlled"""

    USER_PARTICIPATES = "user_participates"
    USER_DELEGATES = "user_delegates"


class PickBanState(str, Enum):
    """Current state of the pick/ban phase"""

    NOT_STARTED = "not_started"
    BAN_PHASE_1 = "ban_phase_1"
    PICK_PHASE_1 = "pick_phase_1"
    BAN_PHASE_2 = "ban_phase_2"
    PICK_PHASE_2 = "pick_phase_2"
    COMPLETED = "completed"


class PickBanAction(str, Enum):
    """Action type in the pick/ban sequence"""

    BAN = "ban"
    PICK = "pick"


class PickBanPhase(SQLModel, table=True):
    """
    Model representing a Pick/Ban phase for a match map.

    This model tracks the pick and ban selections for both teams
    and maintains the state of the pick/ban process.
    """

    __tablename__ = "pick_ban_phase"

    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="match.id", index=True)
    map_number: int = Field()

    # Teams involved
    blue_side_team_id: int = Field(foreign_key="moba_team.id")
    red_side_team_id: int = Field(foreign_key="moba_team.id")
    user_team_id: Optional[int] = Field(foreign_key="moba_team.id", default=None)

    # Mode and state
    mode: PickBanMode = Field(
        sa_column=Column(SQLAlchemyEnum(PickBanMode)),
        default=PickBanMode.USER_PARTICIPATES,
    )
    state: PickBanState = Field(
        sa_column=Column(SQLAlchemyEnum(PickBanState)), default=PickBanState.NOT_STARTED
    )

    # Pick/Ban data (champion selections, role assignments)
    pick_ban_data: Optional[str] = Field(default=None)

    # Timestamps
    start_time: Optional[float] = Field(default=None)
    end_time: Optional[float] = Field(default=None)

    # Relationships
    match: "Match" = Relationship()
    blue_side_team: "MobaTeam" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "PickBanPhase.blue_side_team_id"}
    )
    red_side_team: "MobaTeam" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "PickBanPhase.red_side_team_id"}
    )
    user_team: Optional["MobaTeam"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "PickBanPhase.user_team_id"}
    )

    def get_pick_ban_data(self) -> Dict[str, Any]:
        """
        Get pick/ban data as a Python dictionary.

        Returns:
            Dict containing pick/ban selections and state
        """
        if not self.pick_ban_data:
            return {
                "blue_picks": [],
                "blue_bans": [],
                "red_picks": [],
                "red_bans": [],
                "current_action": None,
                "current_team": None,
                "blue_role_assignments": {},
                "red_role_assignments": {},
            }
        return json.loads(self.pick_ban_data)

    def set_pick_ban_data(self, data: Dict[str, Any]) -> None:
        """
        Set pick/ban data from a Python dictionary.

        Args:
            data: Dictionary containing pick/ban data
        """
        self.pick_ban_data = json.dumps(data)

    def start_pick_ban_phase(
        self,
        user_team_id: Optional[int] = None,
        mode: PickBanMode = PickBanMode.USER_PARTICIPATES,
    ) -> None:
        """
        Start the pick/ban phase.

        Args:
            user_team_id: ID of the user's team (None if not user-controlled)
            mode: Mode of the pick/ban phase (user participates or delegates)
        """

        self.user_team_id = user_team_id
        self.mode = mode
        self.state = PickBanState.BAN_PHASE_1
        self.start_time = time.time()

        # Initialize pick/ban data
        data = self.get_pick_ban_data()
        data["current_action"] = "ban"
        data["current_team"] = "blue"  # Blue side typically starts
        self.set_pick_ban_data(data)

    def get_available_champions(
        self, session, team_id: int, action: PickBanAction
    ) -> List[Dict[str, Any]]:
        """
        Get available champions for the given team and action.

        Args:
            session: SQLModel session
            team_id: Team ID making the selection
            action: Whether this is for a pick or ban

        Returns:
            List of available champions with their details
        """
        from sqlmodel import select
        from .champion import Champion

        data = self.get_pick_ban_data()

        # Get all banned champions
        banned_ids = data["blue_bans"] + data["red_bans"]

        # Get all picked champions
        picked_ids = data["blue_picks"] + data["red_picks"]

        # Query for available champions (not banned or picked)
        # Handle empty list case to avoid SQL error
        if banned_ids or picked_ids:
            query = select(Champion).where(Champion.id.not_in(banned_ids + picked_ids))
        else:
            query = select(Champion)
        champions = session.exec(query).all()

        return [
            {
                "id": champ.id,
                "name": champ.name,
                "primary_role": champ.primary_role,
                "secondary_role": champ.secondary_role,
                "difficulty": champ.difficulty,
                "image_path": champ.image_path,
            }
            for champ in champions
        ]

    def make_selection(self, champion_id: int, role: Optional[str] = None) -> bool:
        """
        Make a pick or ban selection.

        Args:
            champion_id: ID of the champion to select
            role: Role to assign (required for picks, ignored for bans)

        Returns:
            True if the selection was successful, False otherwise
        """
        data = self.get_pick_ban_data()
        current_team = data["current_team"]
        current_action = data["current_action"]

        # Validate the selection based on current state
        if self.state == PickBanState.COMPLETED:
            return False

        # Add to appropriate list
        if current_action == "ban":
            if current_team == "blue":
                data["blue_bans"].append(champion_id)
            else:
                data["red_bans"].append(champion_id)
        else:  # pick
            if current_team == "blue":
                data["blue_picks"].append(champion_id)
                if role:
                    data["blue_role_assignments"][str(champion_id)] = role
            else:
                data["red_picks"].append(champion_id)
                if role:
                    data["red_role_assignments"][str(champion_id)] = role

        # Advance to next action and team
        self._advance_state(data)
        self.set_pick_ban_data(data)

        return True

    def switch_champion(
        self, old_champion_id: int, new_champion_id: int, role: Optional[str] = None
    ) -> bool:
        """
        Switch a previously picked champion with a new one.

        Args:
            old_champion_id: ID of the champion to replace
            new_champion_id: ID of the new champion
            role: Optional new role assignment

        Returns:
            True if successful, False otherwise
        """
        data = self.get_pick_ban_data()

        # Only allow switches during the pick phase and before completion
        if "pick" not in self.state.value or self.state == PickBanState.COMPLETED:
            return False

        # Check which team's champion we're updating
        if old_champion_id in data["blue_picks"]:
            # Process blue team picks
            idx = data["blue_picks"].index(old_champion_id)
            data["blue_picks"][idx] = new_champion_id

            if role:
                # Remove old assignment and add new
                if str(old_champion_id) in data["blue_role_assignments"]:
                    del data["blue_role_assignments"][str(old_champion_id)]
                data["blue_role_assignments"][str(new_champion_id)] = role

        elif old_champion_id in data["red_picks"]:
            # Process red team picks
            idx = data["red_picks"].index(old_champion_id)
            data["red_picks"][idx] = new_champion_id

            if role:
                # Remove old assignment and add new
                if str(old_champion_id) in data["red_role_assignments"]:
                    del data["red_role_assignments"][str(old_champion_id)]
                data["red_role_assignments"][str(new_champion_id)] = role
        else:
            return False  # Champion not found

        self.set_pick_ban_data(data)
        return True

    def assign_role(self, champion_id: int, role: str) -> bool:
        """
        Assign or reassign a role to a picked champion.

        Args:
            champion_id: ID of the champion
            role: Role to assign

        Returns:
            True if successful, False otherwise
        """
        data = self.get_pick_ban_data()

        # Only allow role assignments during the pick phase and before completion
        if "pick" not in self.state.value or self.state == PickBanState.COMPLETED:
            return False

        # Check which team the champion belongs to
        if champion_id in data["blue_picks"]:
            data["blue_role_assignments"][str(champion_id)] = role
        elif champion_id in data["red_picks"]:
            data["red_role_assignments"][str(champion_id)] = role
        else:
            return False  # Champion not picked

        self.set_pick_ban_data(data)
        return True

    def get_next_action(self) -> Dict[str, Any]:
        """
        Get the next action in the pick/ban sequence.

        Returns:
            Dict with information about the next action
        """
        data = self.get_pick_ban_data()
        return {
            "team": data["current_team"],
            "action": data["current_action"],
            "state": self.state.value,
            "user_turn": data["current_team"] == "blue"
            and self.user_team_id == self.blue_side_team_id
            or data["current_team"] == "red"
            and self.user_team_id == self.red_side_team_id,
        }

    def ai_make_selection(self, session) -> Dict[str, Any]:
        """
        Let AI make a pick or ban selection.

        Args:
            session: SQLModel session

        Returns:
            Dict with information about the AI's selection
        """
        # Only proceed if it's not the user's turn or if mode is delegated
        if self.mode != PickBanMode.USER_DELEGATES:
            data = self.get_pick_ban_data()
            user_turn = (
                data["current_team"] == "blue"
                and self.user_team_id == self.blue_side_team_id
                or data["current_team"] == "red"
                and self.user_team_id == self.red_side_team_id
            )

            if user_turn:
                return {"error": "Cannot use AI selection during user's turn"}

        # Get available champions and make a strategic selection
        data = self.get_pick_ban_data()
        action = PickBanAction(data["current_action"])
        team_id = (
            self.blue_side_team_id
            if data["current_team"] == "blue"
            else self.red_side_team_id
        )

        available = self.get_available_champions(session, team_id, action)

        if not available:
            return {"error": "No available champions for selection"}

        # Simple AI logic - prioritize high difficulty champions for bans,
        # and role-appropriate champions for picks

        if action == PickBanAction.BAN:
            # Ban high difficulty champions
            sorted_by_difficulty = sorted(
                available, key=lambda x: x["difficulty"], reverse=True
            )
            # Take one of the top 3 difficult champions
            top_choices = sorted_by_difficulty[:3]
            selected = (
                random.choice(top_choices) if top_choices else sorted_by_difficulty[0]
            )

            self.make_selection(selected["id"])
            return {
                "action": "ban",
                "team": data["current_team"],
                "champion_id": selected["id"],
                "champion_name": selected["name"],
            }
        else:  # pick
            # Determine which roles need to be filled
            filled_roles = set()
            if data["current_team"] == "blue":
                for champ_id, role in data["blue_role_assignments"].items():
                    filled_roles.add(role)
            else:
                for champ_id, role in data["red_role_assignments"].items():
                    filled_roles.add(role)

            all_roles = {"top", "jungle", "mid", "bot", "support"}
            needed_roles = all_roles - filled_roles

            if needed_roles:
                # Pick a champion for an unfilled role
                target_role = random.choice(list(needed_roles))
                suitable_champions = [
                    c
                    for c in available
                    if c["primary_role"] == target_role
                    or c["secondary_role"] == target_role
                ]

                if suitable_champions:
                    selected = random.choice(suitable_champions)
                else:
                    # If no suitable champion, pick any available
                    selected = random.choice(available)

                self.make_selection(selected["id"], target_role)
                return {
                    "action": "pick",
                    "team": data["current_team"],
                    "champion_id": selected["id"],
                    "champion_name": selected["name"],
                    "role": target_role,
                }
            else:
                # All roles filled, just pick any champion
                selected = random.choice(available)
                random_role = random.choice(list(all_roles))
                self.make_selection(selected["id"], random_role)
                return {
                    "action": "pick",
                    "team": data["current_team"],
                    "champion_id": selected["id"],
                    "champion_name": selected["name"],
                    "role": random_role,
                }

    def complete_pick_ban_phase(self) -> bool:
        """
        Complete the pick/ban phase.

        Returns:
            True if the phase was completed successfully, False otherwise
        """
        if self.state == PickBanState.COMPLETED:
            return False

        data = self.get_pick_ban_data()

        # Check that all selections have been made
        if (
            len(data["blue_picks"]) < 5
            or len(data["red_picks"]) < 5
            or len(data["blue_bans"]) < 5
            or len(data["red_bans"]) < 5
        ):
            return False

        # Check that all roles have been assigned
        blue_roles = set(data["blue_role_assignments"].values())
        red_roles = set(data["red_role_assignments"].values())

        if len(blue_roles) < 5 or len(red_roles) < 5:
            return False

        # Update state
        self.state = PickBanState.COMPLETED
        self.end_time = time.time()

        return True

    def _advance_state(self, data: Dict[str, Any]) -> None:
        """
        Advance the pick/ban state to the next step.

        Args:
            data: Current pick/ban data
        """
        # Define the sequence of actions
        # Standard pick/ban sequence:
        # 3 bans per team, then 3 picks per team, then 2 more bans per team, then 2 more picks per team
        # Total: 5 bans and 5 picks per team
        ban_phase_1_limit = 3  # Bans per team in first ban phase
        pick_phase_1_limit = 3  # Picks per team in first pick phase
        ban_phase_2_limit = 2  # Bans per team in second ban phase
        pick_phase_2_limit = 2  # Picks per team in second pick phase

        current_team = data["current_team"]
        # Action type is tracked in data but not needed here

        # Switch teams for each action
        if current_team == "blue":
            data["current_team"] = "red"
        else:
            data["current_team"] = "blue"

            # Check if we need to transition to the next phase
            if self.state == PickBanState.BAN_PHASE_1:
                # After both teams complete their ban_phase_1 turns (3 bans each)
                blue_bans_count = len(data["blue_bans"])
                red_bans_count = len(data["red_bans"])

                if (
                    blue_bans_count >= ban_phase_1_limit
                    and red_bans_count >= ban_phase_1_limit
                ):
                    self.state = PickBanState.PICK_PHASE_1
                    data["current_action"] = "pick"

            elif self.state == PickBanState.PICK_PHASE_1:
                # After both teams complete their pick_phase_1 turns (3 picks each)
                blue_picks_count = len(data["blue_picks"])
                red_picks_count = len(data["red_picks"])

                if (
                    blue_picks_count >= pick_phase_1_limit
                    and red_picks_count >= pick_phase_1_limit
                ):
                    self.state = PickBanState.BAN_PHASE_2
                    data["current_action"] = "ban"

            elif self.state == PickBanState.BAN_PHASE_2:
                # After both teams complete their ban_phase_2 turns (2 more bans each, total 5)
                blue_bans_count = len(data["blue_bans"])
                red_bans_count = len(data["red_bans"])

                if (
                    blue_bans_count >= ban_phase_1_limit + ban_phase_2_limit
                    and red_bans_count >= ban_phase_1_limit + ban_phase_2_limit
                ):
                    self.state = PickBanState.PICK_PHASE_2
                    data["current_action"] = "pick"

            elif self.state == PickBanState.PICK_PHASE_2:
                # After both teams complete their pick_phase_2 turns (2 more picks each, total 5)
                blue_picks_count = len(data["blue_picks"])
                red_picks_count = len(data["red_picks"])

                if (
                    blue_picks_count >= pick_phase_1_limit + pick_phase_2_limit
                    and red_picks_count >= pick_phase_1_limit + pick_phase_2_limit
                ):
                    self.state = PickBanState.COMPLETED
                    import time

                    self.end_time = time.time()


# API Models
class PickBanPhaseBase(SQLModel):
    """Base model for PickBanPhase API operations"""

    match_id: int
    map_number: int
    blue_side_team_id: int
    red_side_team_id: int
    user_team_id: Optional[int] = None
    mode: PickBanMode = PickBanMode.USER_PARTICIPATES


class PickBanPhaseCreate(PickBanPhaseBase):
    """Model for creating a PickBanPhase via API"""

    pass


class PickBanPhaseRead(PickBanPhaseBase):
    """Model for reading a PickBanPhase from API"""

    id: int
    state: PickBanState
    pick_ban_data: Optional[Dict[str, Any]] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class PickBanPhaseUpdate(SQLModel):
    """Model for updating a PickBanPhase via API"""

    user_team_id: Optional[int] = None
    mode: Optional[PickBanMode] = None
    state: Optional[PickBanState] = None
    pick_ban_data: Optional[Dict[str, Any]] = None
