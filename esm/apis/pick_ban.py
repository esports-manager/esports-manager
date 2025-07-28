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
"""
Pick/Ban Phase API - Provides endpoints for managing Pick/Ban phase operations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select
from typing import List, Dict, Any, Optional
import json
import logging

from esm.models.moba_player import PlayerRole
from esm.models.pick_ban_phase import (
    PickBanPhase,
    PickBanPhaseBase,
    PickBanPhaseRead,
    PickBanPhaseUpdate,
    PickBanMode,
    PickBanAction,
)
from esm.models.champion import Champion
from esm import get_session

# Configure logger
logger = logging.getLogger(__name__)


# Create a simplified Champion read model for Pick/Ban phase API
class ChampionBasicRead(BaseModel):
    """Simplified Champion read model for Pick/Ban phase API"""

    id: int
    name: str
    primary_role: PlayerRole
    secondary_role: Optional[PlayerRole] = None
    difficulty: int
    image_path: Optional[str] = None

    model_config = {"from_attributes": True}


# Helper function to prepare PickBanPhase for API response
def prepare_pick_ban_phase_for_response(pick_ban_phase: PickBanPhase) -> PickBanPhase:
    """Prepare a PickBanPhase object for API response by deserializing JSON fields"""
    # Create a copy to avoid modifying the database object
    response_phase = PickBanPhase.model_validate(pick_ban_phase)

    # Convert pick_ban_data from JSON string to dict if it exists
    if response_phase.pick_ban_data:
        response_phase.pick_ban_data = json.loads(response_phase.pick_ban_data)

    return response_phase


# Create router for pick/ban phase endpoints
pick_ban_routes = APIRouter(
    prefix="/api/pick-ban-phases",
    tags=["pick-ban-phases"],
    responses={404: {"description": "Pick/Ban phase not found"}},
)


@pick_ban_routes.get("/", response_model=List[PickBanPhaseRead])
def get_pick_ban_phases(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    match_id: Optional[int] = None,
):
    """
    Get all pick/ban phases with optional filtering

    - **match_id**: Filter pick/ban phases by match ID
    """
    query = select(PickBanPhase)

    if match_id:
        query = query.where(PickBanPhase.match_id == match_id)

    query = query.offset(skip).limit(limit)
    result = session.exec(query).all()
    return [prepare_pick_ban_phase_for_response(phase) for phase in result]


@pick_ban_routes.get("/{pick_ban_id}", response_model=PickBanPhaseRead)
def get_pick_ban_phase(
    pick_ban_id: int,
    session: Session = Depends(get_session),
):
    """
    Get a pick/ban phase by ID

    - **pick_ban_id**: ID of the pick/ban phase to retrieve
    """
    pick_ban_phase = session.get(PickBanPhase, pick_ban_id)
    if not pick_ban_phase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pick/Ban phase with ID {pick_ban_id} not found",
        )
    return prepare_pick_ban_phase_for_response(pick_ban_phase)


@pick_ban_routes.post(
    "/", response_model=PickBanPhaseRead, status_code=status.HTTP_201_CREATED
)
def create_pick_ban_phase(
    pick_ban_phase: PickBanPhaseBase,
    session: Session = Depends(get_session),
):
    """
    Create a new pick/ban phase

    - **pick_ban_phase**: Pick/Ban phase data
    """
    db_pick_ban_phase = PickBanPhase.model_validate(pick_ban_phase)
    session.add(db_pick_ban_phase)
    session.commit()
    session.refresh(db_pick_ban_phase)
    return prepare_pick_ban_phase_for_response(db_pick_ban_phase)


@pick_ban_routes.patch("/{pick_ban_id}", response_model=PickBanPhaseRead)
def update_pick_ban_phase(
    pick_ban_id: int,
    pick_ban_update: PickBanPhaseUpdate,
    session: Session = Depends(get_session),
):
    """
    Update a pick/ban phase

    - **pick_ban_id**: ID of the pick/ban phase to update
    - **pick_ban_update**: Updated pick/ban phase data
    """
    db_pick_ban_phase = session.get(PickBanPhase, pick_ban_id)
    if not db_pick_ban_phase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pick/Ban phase with ID {pick_ban_id} not found",
        )

    # Update model fields from the update data, excluding unset fields
    update_data = pick_ban_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_pick_ban_phase, key, value)

    session.add(db_pick_ban_phase)
    session.commit()
    session.refresh(db_pick_ban_phase)
    return prepare_pick_ban_phase_for_response(db_pick_ban_phase)


@pick_ban_routes.delete("/{pick_ban_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pick_ban_phase(
    pick_ban_id: int,
    session: Session = Depends(get_session),
):
    """
    Delete a pick/ban phase

    - **pick_ban_id**: ID of the pick/ban phase to delete
    """
    db_pick_ban_phase = session.get(PickBanPhase, pick_ban_id)
    if not db_pick_ban_phase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pick/Ban phase with ID {pick_ban_id} not found",
        )

    session.delete(db_pick_ban_phase)
    session.commit()


# Special action endpoints
@pick_ban_routes.post("/{pick_ban_id}/start", response_model=PickBanPhaseRead)
def start_pick_ban_phase(
    pick_ban_id: int,
    start_data: Dict[str, Any],
    session: Session = Depends(get_session),
):
    """
    Start a pick/ban phase

    - **pick_ban_id**: ID of the pick/ban phase to start
    - **start_data**: Data containing user_team_id and mode
    """
    db_pick_ban_phase = session.get(PickBanPhase, pick_ban_id)
    if not db_pick_ban_phase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pick/Ban phase with ID {pick_ban_id} not found",
        )

    # Get the user_team_id and mode from start_data
    user_team_id = start_data.get("user_team_id")
    mode_str = start_data.get("mode")
    mode = PickBanMode(mode_str) if mode_str else PickBanMode.USER_PARTICIPATES

    # Start the pick/ban phase
    db_pick_ban_phase.start_pick_ban_phase(user_team_id, mode)

    session.add(db_pick_ban_phase)
    session.commit()
    session.refresh(db_pick_ban_phase)
    return prepare_pick_ban_phase_for_response(db_pick_ban_phase)


@pick_ban_routes.post("/{pick_ban_id}/select", response_model=PickBanPhaseRead)
def make_selection(
    pick_ban_id: int,
    selection_data: Dict[str, Any],
    session: Session = Depends(get_session),
):
    """
    Make a selection in the pick/ban phase

    - **pick_ban_id**: ID of the pick/ban phase
    - **selection_data**: Data containing champion_id and optional role
    """
    db_pick_ban_phase = session.get(PickBanPhase, pick_ban_id)
    if not db_pick_ban_phase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pick/Ban phase with ID {pick_ban_id} not found",
        )

    # Get the champion_id and role from selection_data
    champion_id = selection_data.get("champion_id")
    role = selection_data.get("role")

    if not champion_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Champion ID is required"
        )

    # Check if the champion exists
    champion = session.get(Champion, champion_id)
    if not champion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Champion with ID {champion_id} not found",
        )

    # No need to verify team's turn here - the model will handle this internally

    # Make the selection
    success = db_pick_ban_phase.make_selection(champion_id, role)

    # Update the session and commit changes
    session.add(db_pick_ban_phase)
    session.commit()
    session.refresh(db_pick_ban_phase)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to make selection. Check phase state and champion availability.",
        )

    session.add(db_pick_ban_phase)
    session.commit()
    session.refresh(db_pick_ban_phase)
    return prepare_pick_ban_phase_for_response(db_pick_ban_phase)


@pick_ban_routes.post("/{pick_ban_id}/switch", response_model=PickBanPhaseRead)
def switch_champion(
    pick_ban_id: int,
    switch_data: Dict[str, Any],
    session: Session = Depends(get_session),
):
    """
    Switch a previously picked champion with a new one

    - **pick_ban_id**: ID of the pick/ban phase
    - **switch_data**: Data containing old_champion_id, new_champion_id, and optional role
    """
    db_pick_ban_phase = session.get(PickBanPhase, pick_ban_id)
    if not db_pick_ban_phase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pick/Ban phase with ID {pick_ban_id} not found",
        )

    # Get the champion IDs and role from switch_data
    old_champion_id = switch_data.get("old_champion_id")
    new_champion_id = switch_data.get("new_champion_id")
    role = switch_data.get("role")

    if not old_champion_id or not new_champion_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both old_champion_id and new_champion_id are required",
        )

    # Check if the champions exist
    old_champion = session.get(Champion, old_champion_id)
    new_champion = session.get(Champion, new_champion_id)
    if not old_champion or not new_champion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both champions not found",
        )

    # Switch the champion
    success = db_pick_ban_phase.switch_champion(old_champion_id, new_champion_id, role)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to switch champion. Check phase state and champion availability.",
        )

    session.add(db_pick_ban_phase)
    session.commit()
    session.refresh(db_pick_ban_phase)
    return prepare_pick_ban_phase_for_response(db_pick_ban_phase)


@pick_ban_routes.post("/{pick_ban_id}/assign-role", response_model=PickBanPhaseRead)
def assign_role(
    pick_ban_id: int,
    role_data: Dict[str, Any],
    session: Session = Depends(get_session),
):
    """
    Assign a role to a picked champion

    - **pick_ban_id**: ID of the pick/ban phase
    - **role_data**: Data containing champion_id and role
    """
    db_pick_ban_phase = session.get(PickBanPhase, pick_ban_id)
    if not db_pick_ban_phase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pick/Ban phase with ID {pick_ban_id} not found",
        )

    # Get the champion_id and role from role_data
    champion_id = role_data.get("champion_id")
    role = role_data.get("role")

    if not champion_id or not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both champion_id and role are required",
        )

    # Check if the champion exists
    champion = session.get(Champion, champion_id)
    if not champion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Champion with ID {champion_id} not found",
        )

    # Assign the role
    success = db_pick_ban_phase.assign_role(champion_id, role)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to assign role. Check if champion is picked.",
        )

    session.add(db_pick_ban_phase)
    session.commit()
    session.refresh(db_pick_ban_phase)
    return prepare_pick_ban_phase_for_response(db_pick_ban_phase)


@pick_ban_routes.post("/{pick_ban_id}/ai-select", response_model=PickBanPhaseRead)
def ai_make_selection(
    pick_ban_id: int,
    session: Session = Depends(get_session),
):
    """
    Let AI make a selection in the pick/ban phase

    The AI will select a champion to pick or ban based on the current state of the
    pick/ban phase. The selection is made automatically and follows these rules:
    - In ban phase, the AI will ban champions with highest pick rates
    - In pick phase, the AI will select champions based on team composition and meta
    - The AI respects the current team's turn and action type (pick/ban)

    - **pick_ban_id**: ID of the pick/ban phase

    Returns:
        Updated pick/ban phase with AI's selection recorded
    """
    # Get the pick/ban phase from database
    db_pick_ban_phase = session.get(PickBanPhase, pick_ban_id)
    if not db_pick_ban_phase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pick/Ban phase with ID {pick_ban_id} not found",
        )

    # Get current pick/ban state
    pick_ban_data = db_pick_ban_phase.get_pick_ban_data()

    # Get available champions for the current team and action
    action = pick_ban_data.get("current_action")
    team_id = (
        db_pick_ban_phase.blue_side_team_id
        if pick_ban_data.get("current_team") == "blue"
        else db_pick_ban_phase.red_side_team_id
    )
    available_champs = db_pick_ban_phase.get_available_champions(
        session, team_id, action
    )

    # Log if no champions are available for debugging purposes
    if not available_champs:
        logger.warning(
            f"No available champions for AI selection in pick_ban_phase_id={pick_ban_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No champions available for selection",
        )

    # Let AI make a selection
    result = db_pick_ban_phase.ai_make_selection(session)

    # Log AI selection result at debug level
    logger.debug(f"AI selection result for pick_ban_phase_id={pick_ban_id}: {result}")

    if not result or "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to make AI selection: {result.get('error') if result else 'Unknown error'}",
        )

    # Update the session and commit changes
    session.add(db_pick_ban_phase)
    session.commit()
    session.refresh(db_pick_ban_phase)

    # Return the updated pick/ban phase with deserialized JSON data
    return prepare_pick_ban_phase_for_response(db_pick_ban_phase)


@pick_ban_routes.post("/{pick_ban_id}/complete", response_model=PickBanPhaseRead)
def complete_pick_ban_phase(
    pick_ban_id: int,
    session: Session = Depends(get_session),
):
    """
    Complete the pick/ban phase

    - **pick_ban_id**: ID of the pick/ban phase
    """
    db_pick_ban_phase = session.get(PickBanPhase, pick_ban_id)
    if not db_pick_ban_phase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pick/Ban phase with ID {pick_ban_id} not found",
        )

    # Complete the pick/ban phase
    success = db_pick_ban_phase.complete_pick_ban_phase()
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to complete pick/ban phase. Check if all picks/bans are complete.",
        )

    session.add(db_pick_ban_phase)
    session.commit()
    session.refresh(db_pick_ban_phase)
    return prepare_pick_ban_phase_for_response(db_pick_ban_phase)


@pick_ban_routes.get(
    "/{pick_ban_id}/available-champions", response_model=List[ChampionBasicRead]
)
def get_available_champions(
    pick_ban_id: int,
    team_id: int,
    action: str,
    session: Session = Depends(get_session),
):
    """
    Get available champions for selection

    - **pick_ban_id**: ID of the pick/ban phase
    - **team_id**: ID of the team making the selection
    - **action**: Type of action (pick or ban)
    """
    db_pick_ban_phase = session.get(PickBanPhase, pick_ban_id)
    if not db_pick_ban_phase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pick/Ban phase with ID {pick_ban_id} not found",
        )

    # Validate action
    try:
        pick_ban_action = PickBanAction(action)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action: {action}. Must be 'pick' or 'ban'.",
        )

    # Get available champions
    available_champions = db_pick_ban_phase.get_available_champions(
        session, team_id, pick_ban_action
    )

    return available_champions


# Additional routes for related resources
@pick_ban_routes.get("/match/{match_id}", response_model=List[PickBanPhaseRead])
def get_match_pick_ban_phases(
    match_id: int,
    session: Session = Depends(get_session),
):
    """
    Get all pick/ban phases for a match

    - **match_id**: ID of the match
    """
    query = select(PickBanPhase).where(PickBanPhase.match_id == match_id)
    result = session.exec(query).all()
    return result
