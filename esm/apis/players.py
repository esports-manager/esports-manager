"""
Players API - Provides endpoints for managing MobaPlayer resources
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from datetime import date

from esm.models.moba_player import (
    MobaPlayer,
    PlayerRole,
    ContractStatus,
    MobaPlayerCreate,
    MobaPlayerRead,
    MobaPlayerUpdate,
)
from esm import get_session

# Create router for player endpoints
player_routes = APIRouter(
    prefix="/api/players",
    tags=["players"],
    responses={404: {"description": "Player not found"}},
)


@player_routes.get("/", response_model=List[MobaPlayerRead])
def get_players(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    role: Optional[PlayerRole] = None,
    contract_status: Optional[ContractStatus] = None,
    team_id: Optional[int] = None,
):
    """Get all players with optional filtering"""
    query = select(MobaPlayer)

    if role:
        query = query.where(MobaPlayer.role == role)

    if contract_status:
        query = query.where(MobaPlayer.contract_status == contract_status)

    if team_id:
        query = query.where(MobaPlayer.team_id == team_id)

    players = session.exec(query.offset(skip).limit(limit)).all()
    return players


@player_routes.get("/{player_id}", response_model=MobaPlayerRead)
def get_player_by_id(player_id: int, session: Session = Depends(get_session)):
    """Get a player by their ID"""
    player = session.get(MobaPlayer, player_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {player_id} not found",
        )
    return player


@player_routes.post(
    "/", response_model=MobaPlayerRead, status_code=status.HTTP_201_CREATED
)
def create_player(
    player_data: MobaPlayerCreate, session: Session = Depends(get_session)
):
    """Create a new player"""
    # Convert API model to DB model
    player = MobaPlayer(
        name=player_data.name,
        full_name=player_data.full_name,
        nationality=player_data.nationality,
        bio=player_data.bio,
        image_path=player_data.image_path,
        role=player_data.role,
        mechanics=player_data.mechanics,
        game_knowledge=player_data.game_knowledge,
        team_fighting=player_data.team_fighting,
        champion_pool_size=player_data.champion_pool_size,
        laning=player_data.laning,
        form=player_data.form,
        morale=player_data.morale,
        contract_status=player_data.contract_status,
        team_id=player_data.team_id,
        salary=player_data.salary,
    )

    # Handle date conversion from string to date object
    try:
        # Convert date of birth
        if player_data.date_of_birth:
            player.date_of_birth = date.fromisoformat(player_data.date_of_birth)

        # Convert contract dates if provided
        if player_data.contract_start_date:
            player.contract_start_date = date.fromisoformat(
                player_data.contract_start_date
            )

        if player_data.contract_end_date:
            player.contract_end_date = date.fromisoformat(player_data.contract_end_date)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format. Use YYYY-MM-DD format: {str(e)}",
        )

    session.add(player)
    session.commit()
    session.refresh(player)
    return player


@player_routes.patch("/{player_id}", response_model=MobaPlayerRead)
def update_player(
    player_id: int,
    player_update: MobaPlayerUpdate,
    session: Session = Depends(get_session),
):
    """Update a player's details"""
    db_player = session.get(MobaPlayer, player_id)
    if not db_player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {player_id} not found",
        )

    # Convert update model to dict, excluding unset values
    update_data = player_update.model_dump(exclude_unset=True)

    # Handle date conversions if dates are provided
    try:
        # Convert date of birth if provided
        if "date_of_birth" in update_data and update_data["date_of_birth"]:
            update_data["date_of_birth"] = date.fromisoformat(
                update_data["date_of_birth"]
            )

        # Convert contract dates if provided
        if "contract_start_date" in update_data and update_data["contract_start_date"]:
            update_data["contract_start_date"] = date.fromisoformat(
                update_data["contract_start_date"]
            )

        if "contract_end_date" in update_data and update_data["contract_end_date"]:
            update_data["contract_end_date"] = date.fromisoformat(
                update_data["contract_end_date"]
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format. Use YYYY-MM-DD format: {str(e)}",
        )

    # Update the player attributes
    for key, value in update_data.items():
        setattr(db_player, key, value)

    session.add(db_player)
    session.commit()
    session.refresh(db_player)
    return db_player


@player_routes.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player(player_id: int, session: Session = Depends(get_session)):
    """Delete a player"""
    player = session.get(MobaPlayer, player_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {player_id} not found",
        )

    session.delete(player)
    session.commit()
    return None


@player_routes.get("/free-agents/", response_model=List[MobaPlayerRead])
def get_free_agents(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    role: Optional[PlayerRole] = None,
):
    """Get all free agent players with optional role filtering"""
    query = select(MobaPlayer).where(
        MobaPlayer.contract_status == ContractStatus.FREE_AGENT
    )

    if role:
        query = query.where(MobaPlayer.role == role)

    players = session.exec(query.offset(skip).limit(limit)).all()
    return players
