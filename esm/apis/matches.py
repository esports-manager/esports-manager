"""
Matches API - Provides endpoints for managing Match resources
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from esm.models.match import (
    Match,
    MatchStatus,
    MatchType,
    MatchCreate,
    MatchRead,
    MatchUpdate,
)
from esm import get_session

# Create router for match endpoints
match_routes = APIRouter(
    prefix="/api/matches",
    tags=["matches"],
    responses={404: {"description": "Match not found"}},
)


@match_routes.get("/", response_model=List[MatchRead])
def get_matches(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    team_id: Optional[int] = None,
    status: Optional[MatchStatus] = None,
    match_type: Optional[MatchType] = None,
    tournament_id: Optional[int] = None,
):
    """Get all matches with optional filtering"""
    query = select(Match)

    if team_id:
        # Get matches where the team is either home or away
        query = query.where(
            (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
        )

    if status:
        query = query.where(Match.status == status)

    if match_type:
        query = query.where(Match.match_type == match_type)

    if tournament_id:
        query = query.where(Match.tournament_id == tournament_id)

    matches = session.exec(query.offset(skip).limit(limit)).all()
    return matches


@match_routes.get("/upcoming", response_model=List[MatchRead])
def get_upcoming_matches(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    team_id: Optional[int] = None,
):
    """Get upcoming matches (scheduled or in progress)"""
    query = (
        select(Match)
        .where(Match.status.in_([MatchStatus.SCHEDULED, MatchStatus.IN_PROGRESS]))
        .order_by(Match.scheduled_date)
    )

    if team_id:
        query = query.where(
            (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
        )

    matches = session.exec(query.offset(skip).limit(limit)).all()
    return matches


@match_routes.get("/{match_id}", response_model=MatchRead)
def get_match_by_id(match_id: int, session: Session = Depends(get_session)):
    """Get a match by its ID"""
    match = session.get(Match, match_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID {match_id} not found",
        )
    return match


@match_routes.post("/", response_model=MatchRead, status_code=status.HTTP_201_CREATED)
def create_match(match: MatchCreate, session: Session = Depends(get_session)):
    """Create a new match"""
    # Validate that home and away teams are different
    if match.home_team_id == match.away_team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Home team and away team cannot be the same",
        )

    try:
        # Convert string datetime to datetime objects
        scheduled_date = datetime.fromisoformat(match.scheduled_date)

        # Convert optional completed_date if provided
        completed_date = None
        if match.completed_date:
            completed_date = datetime.fromisoformat(match.completed_date)

        # Create a Match database model from the API model
        db_match = Match(
            **match.model_dump(exclude={"scheduled_date", "completed_date"}),
            scheduled_date=scheduled_date,
            completed_date=completed_date,
        )

        session.add(db_match)
        session.commit()
        session.refresh(db_match)
        return db_match
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid datetime format: {str(e)}",
        )


@match_routes.patch("/{match_id}", response_model=MatchRead)
def update_match(
    match_id: int, match_update: MatchUpdate, session: Session = Depends(get_session)
):
    """Update a match's details"""
    db_match = session.get(Match, match_id)
    if not db_match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID {match_id} not found",
        )

    # Convert update data to dict, excluding None values
    update_data = match_update.model_dump(exclude_none=True)

    try:
        # Handle datetime fields specially
        if "scheduled_date" in update_data:
            scheduled_date_str = update_data.pop("scheduled_date")
            if scheduled_date_str:
                db_match.scheduled_date = datetime.fromisoformat(scheduled_date_str)

        if "completed_date" in update_data:
            completed_date_str = update_data.pop("completed_date")
            if completed_date_str:
                db_match.completed_date = datetime.fromisoformat(completed_date_str)
            else:
                db_match.completed_date = None

        # Validate changes if the match is being marked as completed
        if "status" in update_data and update_data["status"] == MatchStatus.COMPLETED:
            # Ensure we have scores
            if not db_match.home_team_score and "home_team_score" not in update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Home team score is required to mark match as completed",
                )
            if not db_match.away_team_score and "away_team_score" not in update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Away team score is required to mark match as completed",
                )

            # Set completed_date if not provided
            if not db_match.completed_date and "completed_date" not in update_data:
                db_match.completed_date = datetime.now()

        # Update remaining fields
        for key, value in update_data.items():
            setattr(db_match, key, value)

        session.add(db_match)
        session.commit()
        session.refresh(db_match)
        return db_match
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid datetime format: {str(e)}",
        )


@match_routes.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match(match_id: int, session: Session = Depends(get_session)):
    """Delete a match"""
    match = session.get(Match, match_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID {match_id} not found",
        )

    session.delete(match)
    session.commit()
    return None
