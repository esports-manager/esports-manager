"""
Champions API - Provides endpoints for managing Champion resources
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional

from esm.models.champion import Champion, ChampionRead, ChampionUpdate, ChampionCreate
from esm.models.moba_player import PlayerRole
from esm import get_session


# Create router for champion endpoints
champion_routes = APIRouter(
    prefix="/api/champions",
    tags=["champions"],
    responses={404: {"description": "Champion not found"}},
)


@champion_routes.get("/", response_model=List[ChampionRead])
def get_champions(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    primary_role: Optional[PlayerRole] = None,
    name: Optional[str] = None,
    min_difficulty: Optional[int] = None,
    max_difficulty: Optional[int] = None,
):
    """
    Get all champions with optional filtering

    - **primary_role**: Filter champions by their primary role
    - **name**: Filter champions by name (case insensitive partial match)
    - **min_difficulty**: Filter champions with difficulty >= value
    - **max_difficulty**: Filter champions with difficulty <= value
    """
    query = select(Champion)

    if primary_role:
        query = query.where(Champion.primary_role == primary_role)

    if name:
        query = query.where(Champion.name.ilike(f"%{name}%"))

    if min_difficulty is not None:
        query = query.where(Champion.difficulty >= min_difficulty)

    if max_difficulty is not None:
        query = query.where(Champion.difficulty <= max_difficulty)

    champions = session.exec(query.offset(skip).limit(limit)).all()

    # Convert JSON fields
    result = []
    for champion in champions:
        champion_dict = ChampionRead(
            id=champion.id,
            name=champion.name,
            title=champion.title,
            primary_role=champion.primary_role,
            secondary_role=champion.secondary_role,
            difficulty=champion.difficulty,
            release_date=champion.release_date,
            rework_date=champion.rework_date,
            description=champion.description,
            image_path=champion.image_path,
            abilities=champion.get_abilities(),
            stats=champion.get_stats(),
        )
        result.append(champion_dict)

    return result


@champion_routes.get("/{champion_id}", response_model=ChampionRead)
def get_champion(champion_id: int, session: Session = Depends(get_session)):
    """Get a champion by ID"""
    champion = session.get(Champion, champion_id)
    if not champion:
        raise HTTPException(
            status_code=404, detail=f"Champion with ID {champion_id} not found"
        )

    return ChampionRead(
        id=champion.id,
        name=champion.name,
        title=champion.title,
        primary_role=champion.primary_role,
        secondary_role=champion.secondary_role,
        difficulty=champion.difficulty,
        release_date=champion.release_date,
        rework_date=champion.rework_date,
        description=champion.description,
        image_path=champion.image_path,
        abilities=champion.get_abilities(),
        stats=champion.get_stats(),
    )


@champion_routes.post(
    "/", response_model=ChampionRead, status_code=status.HTTP_201_CREATED
)
def create_champion(champion: ChampionCreate, session: Session = Depends(get_session)):
    """Create a new champion"""
    # Check for duplicate name
    existing = session.exec(
        select(Champion).where(Champion.name == champion.name)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Champion with name '{champion.name}' already exists",
        )

    db_champion = Champion(
        name=champion.name,
        title=champion.title,
        primary_role=champion.primary_role,
        secondary_role=champion.secondary_role,
        difficulty=champion.difficulty,
        release_date=champion.release_date,
        rework_date=champion.rework_date,
        description=champion.description,
        image_path=champion.image_path,
    )

    # Set JSON fields if provided
    if champion.abilities:
        db_champion.set_abilities(champion.abilities)
    if champion.stats:
        db_champion.set_stats(champion.stats)

    session.add(db_champion)
    session.commit()
    session.refresh(db_champion)

    return ChampionRead(
        id=db_champion.id,
        name=db_champion.name,
        title=db_champion.title,
        primary_role=db_champion.primary_role,
        secondary_role=db_champion.secondary_role,
        difficulty=db_champion.difficulty,
        release_date=db_champion.release_date,
        rework_date=db_champion.rework_date,
        description=db_champion.description,
        image_path=db_champion.image_path,
        abilities=db_champion.get_abilities(),
        stats=db_champion.get_stats(),
    )


@champion_routes.patch("/{champion_id}", response_model=ChampionRead)
def update_champion(
    champion_id: int,
    champion_update: ChampionUpdate,
    session: Session = Depends(get_session),
):
    """Update a champion"""
    db_champion = session.get(Champion, champion_id)
    if not db_champion:
        raise HTTPException(
            status_code=404, detail=f"Champion with ID {champion_id} not found"
        )

    # Check for duplicate name if changing the name
    if champion_update.name and champion_update.name != db_champion.name:
        existing = session.exec(
            select(Champion).where(Champion.name == champion_update.name)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Champion with name '{champion_update.name}' already exists",
            )

    # Update champion fields if provided
    update_data = champion_update.dict(exclude_unset=True)

    # Handle abilities and stats specially
    abilities = update_data.pop("abilities", None)
    stats = update_data.pop("stats", None)

    # Update other fields
    for key, value in update_data.items():
        setattr(db_champion, key, value)

    # Update JSON fields if provided
    if abilities is not None:
        db_champion.set_abilities(abilities)
    if stats is not None:
        db_champion.set_stats(stats)

    session.commit()
    session.refresh(db_champion)

    return ChampionRead(
        id=db_champion.id,
        name=db_champion.name,
        title=db_champion.title,
        primary_role=db_champion.primary_role,
        secondary_role=db_champion.secondary_role,
        difficulty=db_champion.difficulty,
        release_date=db_champion.release_date,
        rework_date=db_champion.rework_date,
        description=db_champion.description,
        image_path=db_champion.image_path,
        abilities=db_champion.get_abilities(),
        stats=db_champion.get_stats(),
    )


@champion_routes.delete("/{champion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_champion(champion_id: int, session: Session = Depends(get_session)):
    """Delete a champion"""
    db_champion = session.get(Champion, champion_id)
    if not db_champion:
        raise HTTPException(
            status_code=404, detail=f"Champion with ID {champion_id} not found"
        )

    session.delete(db_champion)
    session.commit()

    return None


@champion_routes.get("/roles/", response_model=List[str])
def get_champion_roles():
    """Get all possible champion roles"""
    return [role.value for role in PlayerRole]
