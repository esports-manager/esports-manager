"""
Tournaments API - Provides endpoints for managing Tournament resources
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlmodel import Session, select, func
from datetime import datetime
from typing import List, Optional
from datetime import date

from esm.models.tournament import (
    Tournament,
    Season,
    TournamentType,
    TeamRegion,
    TournamentCreate,
    TournamentRead,
    TournamentUpdate,
    SeasonCreate,
    SeasonRead,
    SeasonUpdate,
)
from esm.models.moba_team import MobaTeam
from esm import get_session

# Create router for tournament endpoints
tournament_routes = APIRouter(
    tags=["tournaments"],
    responses={404: {"description": "Tournament not found"}},
)


@tournament_routes.get("/api/tournaments", response_model=List[TournamentRead])
def get_tournaments(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    tournament_type: Optional[TournamentType] = None,
    region: Optional[TeamRegion] = None,
    season_id: Optional[int] = None,
):
    """Get all tournaments with optional filtering"""
    query = select(Tournament)

    if tournament_type:
        query = query.where(Tournament.tournament_type == tournament_type)

    if region:
        query = query.where(Tournament.region == region)

    if season_id:
        query = query.where(Tournament.season_id == season_id)

    tournaments = session.exec(query.offset(skip).limit(limit)).all()
    return tournaments


@tournament_routes.get(
    "/api/tournaments/{tournament_id}", response_model=TournamentRead
)
def get_tournament_by_id(tournament_id: int, session: Session = Depends(get_session)):
    """Get a tournament by its ID"""
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tournament with ID {tournament_id} not found",
        )
    return tournament


@tournament_routes.post(
    "/api/tournaments",
    response_model=TournamentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_tournament(
    tournament: TournamentCreate, session: Session = Depends(get_session)
):
    """Create a new tournament"""
    # Convert string dates to date objects
    try:
        start_date = date.fromisoformat(tournament.start_date)
        end_date = date.fromisoformat(tournament.end_date)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use ISO format (YYYY-MM-DD)",
        )

    # Create database model from API input model
    db_tournament = Tournament(
        name=tournament.name,
        tournament_type=tournament.tournament_type,
        tournament_format=tournament.tournament_format,
        start_date=start_date,
        end_date=end_date,
        region=tournament.region,
        prize_pool=tournament.prize_pool,
        description=tournament.description,
        logo_path=tournament.logo_path,
        season_id=tournament.season_id,
    )

    session.add(db_tournament)
    session.commit()
    session.refresh(db_tournament)
    return db_tournament


@tournament_routes.patch(
    "/api/tournaments/{tournament_id}", response_model=TournamentRead
)
def update_tournament(
    tournament_id: int,
    tournament_update: TournamentUpdate,
    session: Session = Depends(get_session),
):
    """Update a tournament's details"""
    db_tournament = session.get(Tournament, tournament_id)
    if not db_tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tournament with ID {tournament_id} not found",
        )

    # Update fields if provided in the request
    update_data = tournament_update.model_dump(exclude_unset=True)

    # Handle date string conversions
    if "start_date" in update_data and update_data["start_date"] is not None:
        try:
            update_data["start_date"] = date.fromisoformat(update_data["start_date"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date format. Use ISO format (YYYY-MM-DD)",
            )

    if "end_date" in update_data and update_data["end_date"] is not None:
        try:
            update_data["end_date"] = date.fromisoformat(update_data["end_date"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end_date format. Use ISO format (YYYY-MM-DD)",
            )

    for key, value in update_data.items():
        setattr(db_tournament, key, value)

    session.add(db_tournament)
    session.commit()
    session.refresh(db_tournament)

    return db_tournament


@tournament_routes.delete(
    "/api/tournaments/{tournament_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_tournament(tournament_id: int, session: Session = Depends(get_session)):
    """Delete a tournament"""
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tournament with ID {tournament_id} not found",
        )

    session.delete(tournament)
    session.commit()
    return None


@tournament_routes.post("/api/tournaments/{tournament_id}/teams")
def add_team_to_tournament(
    tournament_id: int,
    team_data: dict = Body(...),
    session: Session = Depends(get_session),
):
    """Add a team to a tournament with optional seed and group info"""
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tournament with ID {tournament_id} not found",
        )

    team_id = team_data.get("team_id")
    if not team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Team ID is required"
        )

    team = session.get(MobaTeam, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found",
        )

    # Get current teams_data or initialize empty list
    teams_data = tournament.get_teams_data() or []

    # Check if team is already in the tournament
    if any(td.get("team_id") == team_id for td in teams_data):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Team with ID {team_id} is already registered for this tournament",
        )

    # Create new team entry with metadata
    new_team_entry = {
        "team_id": team_id,
        "seed": team_data.get("seed"),
        "group": team_data.get("group"),
        "added_at": datetime.now().isoformat(),
    }

    teams_data.append(new_team_entry)
    tournament.set_teams_data(teams_data)
    tournament.set_teams_data(teams_data)

    session.add(tournament)
    session.commit()
    session.refresh(tournament)

    # Return the updated team
    return team


@tournament_routes.get(
    "/api/tournaments/{tournament_id}/teams", response_model=List[MobaTeam]
)
def get_tournament_teams(tournament_id: int, session: Session = Depends(get_session)):
    """Get all teams registered for a tournament"""
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tournament with ID {tournament_id} not found",
        )

    teams_data = tournament.get_teams_data() or []
    team_ids = [td.get("team_id") for td in teams_data if td.get("team_id")]

    if not team_ids:
        return []

    # Query all teams in the list
    teams = session.exec(select(MobaTeam).where(MobaTeam.id.in_(team_ids))).all()
    return teams


@tournament_routes.delete("/api/tournaments/{tournament_id}/teams/{team_id}")
def remove_team_from_tournament(
    tournament_id: int, team_id: int, session: Session = Depends(get_session)
):
    """Remove a team from a tournament"""
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tournament with ID {tournament_id} not found",
        )

    # Get current teams_data
    teams_data = tournament.get_teams_data() or []

    # Filter out the team to remove
    updated_teams_data = [td for td in teams_data if td.get("team_id") != team_id]

    if len(updated_teams_data) == len(teams_data):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} is not registered for this tournament",
        )

    tournament.set_teams_data(updated_teams_data)

    session.add(tournament)
    session.commit()
    session.refresh(tournament)

    return {"message": f"Team with ID {team_id} removed from tournament"}


@tournament_routes.get("/api/tournaments/{tournament_id}/standings")
def get_tournament_standings(
    tournament_id: int, session: Session = Depends(get_session)
):
    """Get current standings for a tournament"""
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tournament with ID {tournament_id} not found",
        )

    # This would typically involve complex logic to calculate standings based on matches
    # For now, return the teams with their records from teams_data
    teams_data = tournament.get_teams_data() or []

    standings = []
    team_ids = [td.get("team_id") for td in teams_data if td.get("team_id")]

    if not team_ids:
        return []

    teams = {
        team.id: team
        for team in session.exec(
            select(MobaTeam).where(MobaTeam.id.in_(team_ids))
        ).all()
    }

    for team_data in teams_data:
        team_id = team_data.get("team_id")
        if team_id in teams:
            team = teams[team_id]
            standings.append(
                {
                    "id": team.id,
                    "name": team.name,
                    "seed": team_data.get("seed"),
                    "group": team_data.get("group"),
                    "matches_played": team_data.get("matches_played", 0),
                    "wins": team_data.get("wins", 0),
                    "losses": team_data.get("losses", 0),
                    "points": team_data.get("points", 0),
                }
            )

    return standings


# Season endpoints


@tournament_routes.get("/api/seasons", response_model=List[SeasonRead])
def get_seasons(
    session: Session = Depends(get_session), skip: int = 0, limit: int = 100
):
    """Get all seasons"""
    seasons = session.exec(select(Season).offset(skip).limit(limit)).all()
    return seasons


@tournament_routes.get("/api/seasons/{season_id}", response_model=SeasonRead)
def get_season_by_id(season_id: int, session: Session = Depends(get_session)):
    """Get a season by its ID"""
    season = session.get(Season, season_id)
    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Season with ID {season_id} not found",
        )
    return season


@tournament_routes.post(
    "/api/seasons", response_model=SeasonRead, status_code=status.HTTP_201_CREATED
)
def create_season(season: SeasonCreate, session: Session = Depends(get_session)):
    """Create a new season"""
    # Convert string dates to date objects
    try:
        start_date = date.fromisoformat(season.start_date)
        end_date = date.fromisoformat(season.end_date)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use ISO format (YYYY-MM-DD)",
        )

    # Create database model from API input model
    db_season = Season(
        name=season.name,
        start_date=start_date,
        end_date=end_date,
        description=season.description,
    )

    session.add(db_season)
    session.commit()
    session.refresh(db_season)
    return db_season


@tournament_routes.put("/api/seasons/{season_id}", response_model=SeasonRead)
def update_season(
    season_id: int, season_update: SeasonUpdate, session: Session = Depends(get_session)
):
    """Update a season's details"""
    db_season = session.get(Season, season_id)
    if not db_season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Season with ID {season_id} not found",
        )

    # Update fields if provided in the request
    update_data = season_update.model_dump(exclude_unset=True)

    # Handle date string conversions
    if "start_date" in update_data and update_data["start_date"] is not None:
        try:
            update_data["start_date"] = date.fromisoformat(update_data["start_date"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date format. Use ISO format (YYYY-MM-DD)",
            )

    if "end_date" in update_data and update_data["end_date"] is not None:
        try:
            update_data["end_date"] = date.fromisoformat(update_data["end_date"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end_date format. Use ISO format (YYYY-MM-DD)",
            )

    for key, value in update_data.items():
        setattr(db_season, key, value)

    session.add(db_season)
    session.commit()
    session.refresh(db_season)

    return db_season


@tournament_routes.delete(
    "/api/seasons/{season_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_season(season_id: int, session: Session = Depends(get_session)):
    """Delete a season"""
    season = session.get(Season, season_id)
    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Season with ID {season_id} not found",
        )

    # Check if there are tournaments in this season
    tournaments_count = session.exec(
        select(func.count(Tournament.id)).where(Tournament.season_id == season_id)
    ).one()

    if tournaments_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete season that has tournaments. Remove tournaments first.",
        )

    session.delete(season)
    session.commit()
    return None


@tournament_routes.get(
    "/api/seasons/{season_id}/tournaments", response_model=List[TournamentRead]
)
def get_season_tournaments(
    season_id: int,
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
):
    """Get all tournaments for a specific season"""
    season = session.get(Season, season_id)
    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Season with ID {season_id} not found",
        )

    tournaments = session.exec(
        select(Tournament)
        .where(Tournament.season_id == season_id)
        .offset(skip)
        .limit(limit)
    ).all()

    return tournaments
