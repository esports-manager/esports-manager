"""
Staff API - Provides endpoints for managing Staff resources
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from datetime import date

from esm.models.staff import (
    Staff,
    Department,
    JobTitle,
    ContractStatus,
    StaffCreate,
    StaffRead,
    StaffUpdate,
)
from esm.models.moba_team import MobaTeam
from esm import get_session

# Create router for staff endpoints
staff_routes = APIRouter(
    prefix="/api/staff",
    tags=["staff"],
    responses={404: {"description": "Staff member not found"}},
)


@staff_routes.get("/", response_model=List[StaffRead])
def get_staff(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    department: Optional[Department] = None,
    job_title: Optional[JobTitle] = None,
    team_id: Optional[int] = None,
    contract_status: Optional[ContractStatus] = None,
):
    """Get all staff members with optional filtering"""
    query = select(Staff)

    if department:
        query = query.where(Staff.department == department)

    if job_title:
        query = query.where(Staff.job_title == job_title)

    if team_id:
        query = query.where(Staff.team_id == team_id)

    if contract_status:
        query = query.where(Staff.contract_status == contract_status)

    staff_members = session.exec(query.offset(skip).limit(limit)).all()
    return staff_members


@staff_routes.get("/{staff_id}", response_model=StaffRead)
def get_staff_by_id(staff_id: int, session: Session = Depends(get_session)):
    """Get a staff member by their ID"""
    staff = session.get(Staff, staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff member with ID {staff_id} not found",
        )
    return staff


@staff_routes.post("/", response_model=StaffRead, status_code=status.HTTP_201_CREATED)
def create_staff(staff: StaffCreate, session: Session = Depends(get_session)):
    """Create a new staff member"""
    try:
        # Convert string dates to date objects
        date_of_birth = date.fromisoformat(staff.date_of_birth)

        # Convert optional contract dates if provided
        contract_start_date = None
        if staff.contract_start_date:
            contract_start_date = date.fromisoformat(staff.contract_start_date)

        contract_end_date = None
        if staff.contract_end_date:
            contract_end_date = date.fromisoformat(staff.contract_end_date)

        # Create a Staff database model from the API model
        db_staff = Staff(
            **staff.model_dump(
                exclude={"date_of_birth", "contract_start_date", "contract_end_date"}
            ),
            date_of_birth=date_of_birth,
            contract_start_date=contract_start_date,
            contract_end_date=contract_end_date,
        )

        session.add(db_staff)
        session.commit()
        session.refresh(db_staff)
        return db_staff
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid date format: {str(e)}",
        )


@staff_routes.patch("/{staff_id}", response_model=StaffRead)
def update_staff(
    staff_id: int, staff_update: StaffUpdate, session: Session = Depends(get_session)
):
    """Update a staff member's details"""
    db_staff = session.get(Staff, staff_id)
    if not db_staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff member with ID {staff_id} not found",
        )

    # Convert update data to dict, excluding None values
    update_data = staff_update.model_dump(exclude_none=True)

    try:
        # Handle date fields specially
        if "date_of_birth" in update_data:
            date_of_birth_str = update_data.pop("date_of_birth")
            if date_of_birth_str:
                db_staff.date_of_birth = date.fromisoformat(date_of_birth_str)

        if "contract_start_date" in update_data:
            contract_start_date_str = update_data.pop("contract_start_date")
            if contract_start_date_str:
                db_staff.contract_start_date = date.fromisoformat(
                    contract_start_date_str
                )
            else:
                db_staff.contract_start_date = None

        if "contract_end_date" in update_data:
            contract_end_date_str = update_data.pop("contract_end_date")
            if contract_end_date_str:
                db_staff.contract_end_date = date.fromisoformat(contract_end_date_str)
            else:
                db_staff.contract_end_date = None

        # Handle special case for JSON fields that use custom getters/setters
        if "achievements" in update_data:
            db_staff.set_achievements(update_data.pop("achievements"))

        if "specializations" in update_data:
            db_staff.set_specializations(update_data.pop("specializations"))

        if "previous_teams" in update_data:
            db_staff.set_previous_teams(update_data.pop("previous_teams"))

        if "education" in update_data:
            db_staff.set_education(update_data.pop("education"))

        if "certifications" in update_data:
            db_staff.set_certifications(update_data.pop("certifications"))

        if "previous_experience" in update_data:
            db_staff.set_previous_experience(update_data.pop("previous_experience"))

        # Update remaining fields
        for key, value in update_data.items():
            setattr(db_staff, key, value)

        session.add(db_staff)
        session.commit()
        session.refresh(db_staff)
        return db_staff
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid date format: {str(e)}",
        )
    return db_staff


@staff_routes.delete("/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_staff(staff_id: int, session: Session = Depends(get_session)):
    """Delete a staff member"""
    staff = session.get(Staff, staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff member with ID {staff_id} not found",
        )

    session.delete(staff)
    session.commit()
    return None


@staff_routes.post("/{staff_id}/assign/{team_id}", response_model=Staff)
def assign_staff_to_team(
    staff_id: int, team_id: int, session: Session = Depends(get_session)
):
    """Assign a staff member to a team"""
    staff = session.get(Staff, staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff member with ID {staff_id} not found",
        )

    team = session.get(MobaTeam, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found",
        )

    # Check if this is a head coach assignment
    if staff.is_head_coach and staff.department == Department.COACHING:
        # Find any existing head coaches on this team
        existing_head_coach = session.exec(
            select(Staff).where(
                (Staff.team_id == team_id)
                & (Staff.is_head_coach)
                & (Staff.id != staff_id)
            )
        ).first()

        if existing_head_coach:
            # Demote the existing head coach
            existing_head_coach.is_head_coach = False
            session.add(existing_head_coach)

    # Assign the staff to the team
    staff.team_id = team_id
    session.add(staff)
    session.commit()
    session.refresh(staff)
    return staff


@staff_routes.post("/{staff_id}/unassign", response_model=Staff)
def unassign_staff_from_team(staff_id: int, session: Session = Depends(get_session)):
    """Remove a staff member from their team"""
    staff = session.get(Staff, staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff member with ID {staff_id} not found",
        )

    if staff.team_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Staff member is not assigned to any team",
        )

    # Unassign the staff member
    staff.team_id = None
    session.add(staff)
    session.commit()
    session.refresh(staff)
    return staff
