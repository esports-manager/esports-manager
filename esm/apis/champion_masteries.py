"""
Champion Mastery API - Provides endpoints for managing ChampionMastery resources
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional

from esm.models.champion_mastery import (
    ChampionMastery,
    ChampionMasteryRead,
    ChampionMasteryUpdate,
    ChampionMasteryCreate,
)
from esm.models.moba_player import MobaPlayer
from esm.models.champion import Champion
from esm import get_session


# Create router for champion mastery endpoints
champion_mastery_routes = APIRouter(
    prefix="/api/champion-masteries",
    tags=["champion-masteries"],
    responses={404: {"description": "Champion mastery not found"}},
)


@champion_mastery_routes.get("/", response_model=List[ChampionMasteryRead])
def get_champion_masteries(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    player_id: Optional[int] = None,
    champion_id: Optional[int] = None,
    is_comfort_pick: Optional[bool] = None,
    min_mastery_level: Optional[int] = None,
):
    """
    Get all champion masteries with optional filtering

    - **player_id**: Filter by player ID
    - **champion_id**: Filter by champion ID
    - **is_comfort_pick**: Filter by comfort pick status
    - **min_mastery_level**: Filter by minimum mastery level
    """
    query = select(ChampionMastery)

    if player_id:
        query = query.where(ChampionMastery.player_id == player_id)

    if champion_id:
        query = query.where(ChampionMastery.champion_id == champion_id)

    if is_comfort_pick is not None:
        query = query.where(ChampionMastery.is_comfort_pick == is_comfort_pick)

    if min_mastery_level is not None:
        query = query.where(ChampionMastery.mastery_level >= min_mastery_level)

    masteries = session.exec(query.offset(skip).limit(limit)).all()

    # Include calculated win_rate in response
    result = []
    for mastery in masteries:
        mastery_dict = ChampionMasteryRead(
            id=mastery.id,
            player_id=mastery.player_id,
            champion_id=mastery.champion_id,
            mastery_level=mastery.mastery_level,
            games_played=mastery.games_played,
            wins=mastery.wins,
            losses=mastery.losses,
            kda_ratio=mastery.kda_ratio,
            is_comfort_pick=mastery.is_comfort_pick,
            notes=mastery.notes,
            win_rate=mastery.win_rate,
        )
        result.append(mastery_dict)

    return result


@champion_mastery_routes.get(
    "/player/{player_id}", response_model=List[ChampionMasteryRead]
)
def get_player_champion_masteries(
    player_id: int,
    session: Session = Depends(get_session),
    min_mastery_level: Optional[int] = None,
    is_comfort_pick: Optional[bool] = None,
):
    """
    Get all champion masteries for a specific player

    - **player_id**: Player ID to filter by
    - **min_mastery_level**: Filter by minimum mastery level
    - **is_comfort_pick**: Filter by comfort pick status
    """
    player = session.get(MobaPlayer, player_id)
    if not player:
        raise HTTPException(
            status_code=404, detail=f"Player with ID {player_id} not found"
        )

    query = select(ChampionMastery).where(ChampionMastery.player_id == player_id)

    if min_mastery_level is not None:
        query = query.where(ChampionMastery.mastery_level >= min_mastery_level)

    if is_comfort_pick is not None:
        query = query.where(ChampionMastery.is_comfort_pick == is_comfort_pick)

    masteries = session.exec(query).all()

    # Include calculated win_rate in response
    result = []
    for mastery in masteries:
        mastery_dict = ChampionMasteryRead(
            id=mastery.id,
            player_id=mastery.player_id,
            champion_id=mastery.champion_id,
            mastery_level=mastery.mastery_level,
            games_played=mastery.games_played,
            wins=mastery.wins,
            losses=mastery.losses,
            kda_ratio=mastery.kda_ratio,
            is_comfort_pick=mastery.is_comfort_pick,
            notes=mastery.notes,
            win_rate=mastery.win_rate,
        )
        result.append(mastery_dict)

    return result


@champion_mastery_routes.get(
    "/champion/{champion_id}", response_model=List[ChampionMasteryRead]
)
def get_champion_player_masteries(
    champion_id: int,
    session: Session = Depends(get_session),
    min_mastery_level: Optional[int] = None,
    is_comfort_pick: Optional[bool] = None,
):
    """
    Get all player masteries for a specific champion

    - **champion_id**: Champion ID to filter by
    - **min_mastery_level**: Filter by minimum mastery level
    - **is_comfort_pick**: Filter by comfort pick status
    """
    champion = session.get(Champion, champion_id)
    if not champion:
        raise HTTPException(
            status_code=404, detail=f"Champion with ID {champion_id} not found"
        )

    query = select(ChampionMastery).where(ChampionMastery.champion_id == champion_id)

    if min_mastery_level is not None:
        query = query.where(ChampionMastery.mastery_level >= min_mastery_level)

    if is_comfort_pick is not None:
        query = query.where(ChampionMastery.is_comfort_pick == is_comfort_pick)

    masteries = session.exec(query).all()

    result = []
    for mastery in masteries:
        mastery_dict = ChampionMasteryRead(
            id=mastery.id,
            player_id=mastery.player_id,
            champion_id=mastery.champion_id,
            mastery_level=mastery.mastery_level,
            games_played=mastery.games_played,
            wins=mastery.wins,
            losses=mastery.losses,
            kda_ratio=mastery.kda_ratio,
            is_comfort_pick=mastery.is_comfort_pick,
            notes=mastery.notes,
            win_rate=mastery.win_rate,
        )
        result.append(mastery_dict)

    return result


@champion_mastery_routes.get("/{mastery_id}", response_model=ChampionMasteryRead)
def get_champion_mastery(mastery_id: int, session: Session = Depends(get_session)):
    """Get a specific champion mastery by ID"""
    mastery = session.get(ChampionMastery, mastery_id)
    if not mastery:
        raise HTTPException(
            status_code=404, detail=f"Champion mastery with ID {mastery_id} not found"
        )

    return ChampionMasteryRead(
        id=mastery.id,
        player_id=mastery.player_id,
        champion_id=mastery.champion_id,
        mastery_level=mastery.mastery_level,
        games_played=mastery.games_played,
        wins=mastery.wins,
        losses=mastery.losses,
        kda_ratio=mastery.kda_ratio,
        is_comfort_pick=mastery.is_comfort_pick,
        notes=mastery.notes,
        win_rate=mastery.win_rate,
    )


@champion_mastery_routes.post(
    "/", response_model=ChampionMasteryRead, status_code=status.HTTP_201_CREATED
)
def create_champion_mastery(
    mastery: ChampionMasteryCreate, session: Session = Depends(get_session)
):
    """Create a new champion mastery"""
    player = session.get(MobaPlayer, mastery.player_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Player with ID {mastery.player_id} not found",
        )

    champion = session.get(Champion, mastery.champion_id)
    if not champion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Champion with ID {mastery.champion_id} not found",
        )

    existing = session.exec(
        select(ChampionMastery)
        .where(ChampionMastery.player_id == mastery.player_id)
        .where(ChampionMastery.champion_id == mastery.champion_id)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Champion mastery for player {mastery.player_id} and champion {mastery.champion_id} already exists",
        )

    db_mastery = ChampionMastery(
        player_id=mastery.player_id,
        champion_id=mastery.champion_id,
        mastery_level=mastery.mastery_level,
        games_played=mastery.games_played,
        wins=mastery.wins,
        losses=mastery.losses,
        kda_ratio=mastery.kda_ratio,
        is_comfort_pick=mastery.is_comfort_pick,
        notes=mastery.notes,
    )

    session.add(db_mastery)
    session.commit()
    session.refresh(db_mastery)

    return ChampionMasteryRead(
        id=db_mastery.id,
        player_id=db_mastery.player_id,
        champion_id=db_mastery.champion_id,
        mastery_level=db_mastery.mastery_level,
        games_played=db_mastery.games_played,
        wins=db_mastery.wins,
        losses=db_mastery.losses,
        kda_ratio=db_mastery.kda_ratio,
        is_comfort_pick=db_mastery.is_comfort_pick,
        notes=db_mastery.notes,
        win_rate=db_mastery.win_rate,
    )


@champion_mastery_routes.patch("/{mastery_id}", response_model=ChampionMasteryRead)
def update_champion_mastery(
    mastery_id: int,
    mastery_update: ChampionMasteryUpdate,
    session: Session = Depends(get_session),
):
    """Update a champion mastery"""
    db_mastery = session.get(ChampionMastery, mastery_id)
    if not db_mastery:
        raise HTTPException(
            status_code=404, detail=f"Champion mastery with ID {mastery_id} not found"
        )

    update_data = mastery_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_mastery, key, value)

    session.commit()
    session.refresh(db_mastery)

    return ChampionMasteryRead(
        id=db_mastery.id,
        player_id=db_mastery.player_id,
        champion_id=db_mastery.champion_id,
        mastery_level=db_mastery.mastery_level,
        games_played=db_mastery.games_played,
        wins=db_mastery.wins,
        losses=db_mastery.losses,
        kda_ratio=db_mastery.kda_ratio,
        is_comfort_pick=db_mastery.is_comfort_pick,
        notes=db_mastery.notes,
        win_rate=db_mastery.win_rate,
    )


@champion_mastery_routes.delete("/{mastery_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_champion_mastery(mastery_id: int, session: Session = Depends(get_session)):
    """Delete a champion mastery"""
    db_mastery = session.get(ChampionMastery, mastery_id)
    if not db_mastery:
        raise HTTPException(
            status_code=404, detail=f"Champion mastery with ID {mastery_id} not found"
        )

    session.delete(db_mastery)
    session.commit()

    return None


@champion_mastery_routes.get(
    "/player/{player_id}/champion/{champion_id}", response_model=ChampionMasteryRead
)
def get_player_champion_mastery(
    player_id: int, champion_id: int, session: Session = Depends(get_session)
):
    """
    Get champion mastery for a specific player and champion

    - **player_id**: Player ID
    - **champion_id**: Champion ID
    """
    mastery = session.exec(
        select(ChampionMastery)
        .where(ChampionMastery.player_id == player_id)
        .where(ChampionMastery.champion_id == champion_id)
    ).first()

    if not mastery:
        raise HTTPException(
            status_code=404,
            detail=f"No mastery found for player {player_id} and champion {champion_id}",
        )

    return ChampionMasteryRead(
        id=mastery.id,
        player_id=mastery.player_id,
        champion_id=mastery.champion_id,
        mastery_level=mastery.mastery_level,
        games_played=mastery.games_played,
        wins=mastery.wins,
        losses=mastery.losses,
        kda_ratio=mastery.kda_ratio,
        is_comfort_pick=mastery.is_comfort_pick,
        notes=mastery.notes,
        win_rate=mastery.win_rate,
    )
