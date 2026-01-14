# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from datetime import date
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from esm.models.moba.staff import MobaStaff, MobaStaffRole
from esm.models.moba.team import MobaTeam


@pytest.fixture
def staff() -> MobaStaff:
    return MobaStaff(
        first_name="John",
        last_name="Doe",
        nick_name="JD",
        date_of_birth=date(1990, 1, 1),
        nationality="Testland",
        role=MobaStaffRole.HEAD_COACH,
        years_experience=5,
    )


async def test_create_moba_staff(staff: MobaStaff):
    assert staff.first_name == "John"
    assert staff.last_name == "Doe"
    assert staff.nick_name == "JD"
    assert staff.date_of_birth == date(1990, 1, 1)
    assert staff.nationality == "Testland"
    assert staff.role == MobaStaffRole.HEAD_COACH
    assert staff.years_experience == 5
    # display_name uses nickname when present
    assert staff.display_name() == "JD"


async def test_display_name_fallback():
    s = MobaStaff(
        first_name="Foo",
        last_name="Bar",
        date_of_birth=date(1991, 2, 2),
        nationality="X",
        role=MobaStaffRole.ANALYST,
    )
    assert s.display_name() == "Foo Bar"


async def test_update_moba_staff(staff: MobaStaff):
    staff.first_name = "Jane"
    staff.years_experience = 7
    assert staff.first_name == "Jane"
    assert staff.years_experience == 7


async def test_staff_role_assignment(staff: MobaStaff):
    for role in MobaStaffRole:
        staff.role = role
        assert staff.role == role


async def test_create_moba_staff_instance(staff: MobaStaff, session: AsyncSession):
    session.add(staff)
    await session.commit()
    await session.refresh(staff)
    assert staff.id is not None
    assert staff.created_at is not None
    # updated_at is None until explicitly updated
    assert staff.updated_at is None
    assert await session.get(MobaStaff, staff.id) == staff


async def test_staff_team_relationship(session: AsyncSession):
    team = MobaTeam(
        name="Test Team",
        nationality="Testland",
        region="NA",
    )
    session.add(team)
    await session.commit()
    await session.refresh(team)

    staff = MobaStaff(
        first_name="Sam",
        last_name="Smith",
        date_of_birth=date(1988, 5, 5),
        nationality="Testland",
        role=MobaStaffRole.ANALYST,
        years_experience=3,
    )
    # Assign staff to team
    staff.team_id = team.id
    session.add(staff)
    await session.commit()
    await session.refresh(staff)

    assert staff.team_id == team.id

    # Verify reverse relation lists staff
    t = await session.get(MobaTeam, team.id)
    await session.refresh(t, ["staff"])
    assert len(t.staff) == 1
    assert t.staff[0].id == staff.id
