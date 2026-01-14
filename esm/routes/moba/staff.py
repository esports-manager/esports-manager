# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from fastapi import APIRouter, status, Request
from fastapi import Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from esm.db import get_session
from esm.models.moba.staff import (
    MobaStaff,
    MobaStaffPublic,
    MobaStaffCreate,
    MobaStaffUpdate,
    MobaStaffRole,
)

staff_routes = APIRouter(
    prefix="/staff",
    tags=["moba_staff"],
    responses={404: {"description": "Staff not found"}},
)


@staff_routes.get("/", response_model=list[MobaStaffPublic])
async def get_staff(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    query = select(MobaStaff)
    count_query = select(MobaStaff)

    # Pagination
    page = 1
    per_page = 20
    current_page = request.query_params.get("page")
    per_page_param = request.query_params.get("per_page")
    if current_page:
        try:
            page = max(1, int(current_page))
        except ValueError:
            page = 1
    if per_page_param:
        try:
            per_page = min(100, max(1, int(per_page_param)))
        except ValueError:
            per_page = 20
    skip = (page - 1) * per_page

    # Filters
    role = request.query_params.get("role")
    team_id = request.query_params.get("team_id")
    nationality = request.query_params.get("nationality")
    search = request.query_params.get("search")

    if role:
        try:
            role_enum = MobaStaffRole(role)
            query = query.where(MobaStaff.role == role_enum)
            count_query = count_query.where(MobaStaff.role == role_enum)
        except Exception:
            pass
    if team_id:
        try:
            tid = int(team_id)
            query = query.where(MobaStaff.team_id == tid)
            count_query = count_query.where(MobaStaff.team_id == tid)
        except ValueError:
            pass
    if nationality:
        query = query.where(MobaStaff.nationality == nationality)
        count_query = count_query.where(MobaStaff.nationality == nationality)
    if search:
        query = query.where(
            (MobaStaff.nick_name.icontains(search))
            | (MobaStaff.first_name.icontains(search))
            | (MobaStaff.last_name.icontains(search))
        )
        count_query = count_query.where(
            (MobaStaff.nick_name.icontains(search))
            | (MobaStaff.first_name.icontains(search))
            | (MobaStaff.last_name.icontains(search))
        )

    # Sorting
    sort = request.query_params.get("sort")
    sort_direction = request.query_params.get("direction", "asc")
    sort_map = {
        "name": MobaStaff.nick_name,
        "role": MobaStaff.role,
        "years_experience": MobaStaff.years_experience,
        "nationality": MobaStaff.nationality,
    }
    if sort in sort_map:
        sort_field = sort_map[sort]
        if sort_direction == "desc":
            query = query.order_by(sort_field.desc())
        else:
            query = query.order_by(sort_field.asc())

    result = await session.execute(query.offset(skip).limit(per_page))
    items = result.scalars().all()
    return items


@staff_routes.post(
    "/", response_model=MobaStaffPublic, status_code=status.HTTP_201_CREATED
)
async def create_staff(
    *, session: AsyncSession = Depends(get_session), staff: MobaStaffCreate
):
    db_staff = MobaStaff.model_validate(staff)
    session.add(db_staff)
    await session.commit()
    await session.refresh(db_staff)
    return db_staff


@staff_routes.get("/{id}", response_model=MobaStaffPublic)
async def get_staff_member(*, session: AsyncSession = Depends(get_session), id: int):
    staff = await session.get(MobaStaff, id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return staff


@staff_routes.patch("/{id}", response_model=MobaStaffPublic)
async def update_staff(
    *, session: AsyncSession = Depends(get_session), id: int, staff: MobaStaffUpdate
):
    db_staff = await session.get(MobaStaff, id)
    if not db_staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    staff_data = staff.model_dump(exclude_unset=True)
    db_staff.sqlmodel_update(staff_data)
    session.add(db_staff)
    await session.commit()
    await session.refresh(db_staff)
    return db_staff


@staff_routes.delete("/{id}", response_model=dict[str, str])
async def delete_staff(*, session: AsyncSession = Depends(get_session), id: int):
    staff = await session.get(MobaStaff, id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    await session.delete(staff)
    await session.commit()
    return {"message": "Staff deleted"}
