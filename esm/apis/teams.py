"""
Teams API - Provides endpoints for managing MobaTeam resources
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from datetime import date

from esm.models.moba_team import (
    MobaTeam,
    TeamRegion,
    MobaTeamRead,
    MobaTeamCreate,
    MobaTeamUpdate,
)
from esm import get_session

# Create router for team endpoints
team_routes = APIRouter(
    prefix="/api/teams",
    tags=["teams"],
    responses={404: {"description": "Team not found"}},
)


@team_routes.get("/", response_model=List[MobaTeamRead])
def get_teams(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    region: Optional[TeamRegion] = None,
):
    """Get all teams with optional filtering by region"""
    query = select(MobaTeam)

    if region:
        query = query.where(MobaTeam.region == region)

    teams = session.exec(query.offset(skip).limit(limit)).all()
    return teams


@team_routes.get("/{team_id}", response_model=MobaTeamRead)
def get_team_by_id(team_id: int, session: Session = Depends(get_session)):
    """Get a team by its ID"""
    team = session.get(MobaTeam, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found",
        )
    return team


@team_routes.post("/", response_model=MobaTeamRead, status_code=status.HTTP_201_CREATED)
def create_team(team_data: MobaTeamCreate, session: Session = Depends(get_session)):
    """Create a new team"""
    # Check if team with same name already exists
    existing_team = session.exec(
        select(MobaTeam).where(MobaTeam.name == team_data.name)
    ).first()

    if existing_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Team with name '{team_data.name}' already exists",
        )

    # Convert from API model to DB model
    team = MobaTeam.model_validate(team_data)

    # Handle date conversion manually if provided as string
    if team_data.founded_date:
        try:
            # Try to parse ISO format date string (YYYY-MM-DD)
            year, month, day = map(int, team_data.founded_date.split("-"))
            team.founded_date = date(year, month, day)
        except (ValueError, AttributeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format for founded_date. Use YYYY-MM-DD format.",
            )

    session.add(team)
    session.commit()
    session.refresh(team)
    return team


@team_routes.patch("/{team_id}", response_model=MobaTeamRead)
def update_team(
    team_id: int, team_update: MobaTeamUpdate, session: Session = Depends(get_session)
):
    """Update a team's details"""
    db_team = session.get(MobaTeam, team_id)
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found",
        )

    # Convert the update model to a dict, excluding None values
    update_data = team_update.model_dump(exclude_unset=True)

    # Handle founded_date conversion if provided
    if "founded_date" in update_data and update_data["founded_date"]:
        try:
            # Try to parse ISO format date string (YYYY-MM-DD)
            year, month, day = map(int, update_data["founded_date"].split("-"))
            update_data["founded_date"] = date(year, month, day)
        except (ValueError, AttributeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format for founded_date. Use YYYY-MM-DD format.",
            )

    # Update the team attributes
    for key, value in update_data.items():
        setattr(db_team, key, value)

    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team


@team_routes.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(team_id: int, session: Session = Depends(get_session)):
    """Delete a team"""
    team = session.get(MobaTeam, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found",
        )

    session.delete(team)
    session.commit()
    return None


@team_routes.get("/{team_id}/roster", response_model=List)
def get_team_roster(team_id: int, session: Session = Depends(get_session)):
    """Get the current roster of players for a team"""
    team = session.get(MobaTeam, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found",
        )

    return team.players


@team_routes.get("/{team_id}/staff")
def get_team_staff(team_id: int, session: Session = Depends(get_session)):
    """Get all staff members for a team"""

    team = session.get(MobaTeam, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found",
        )

    return team.staff
