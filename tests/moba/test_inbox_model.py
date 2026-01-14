# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from esm.models.moba.inbox import (
    MobaInbox,
    MobaInboxCategory,
    MobaInboxStatus,
    MobaInboxPriority,
)
from esm.models.moba.team import MobaTeam


@pytest.fixture
def inbox_msg() -> MobaInbox:
    return MobaInbox(
        subject="Welcome",
        body="Welcome to the league!",
        category=MobaInboxCategory.GENERAL,
        priority=MobaInboxPriority.HIGH,
        sender_name="League Ops",
        is_starred=True,
        labels="intro,system",
    )


async def test_create_moba_inbox(inbox_msg: MobaInbox):
    assert inbox_msg.subject == "Welcome"
    assert inbox_msg.body == "Welcome to the league!"
    assert inbox_msg.category == MobaInboxCategory.GENERAL
    # Explicit priority
    assert inbox_msg.priority == MobaInboxPriority.HIGH
    # Default UNREAD when not overridden
    assert inbox_msg.status == MobaInboxStatus.UNREAD
    assert inbox_msg.is_starred is True
    assert inbox_msg.labels == "intro,system"


async def test_moba_inbox_defaults():
    msg = MobaInbox(
        subject="Test",
        body="Body",
        category=MobaInboxCategory.CONTRACT,
    )
    assert msg.status == MobaInboxStatus.UNREAD
    assert msg.priority == MobaInboxPriority.NORMAL
    assert msg.is_starred is False
    assert msg.read_at is None
    assert msg.archived_at is None
    assert msg.updated_at is None


async def test_enum_assignment(inbox_msg: MobaInbox):
    for cat in MobaInboxCategory:
        inbox_msg.category = cat
        assert inbox_msg.category == cat
    for status in MobaInboxStatus:
        inbox_msg.status = status
        assert inbox_msg.status == status
    for prio in MobaInboxPriority:
        inbox_msg.priority = prio
        assert inbox_msg.priority == prio


async def test_persist_inbox_instance(inbox_msg: MobaInbox, session: AsyncSession):
    session.add(inbox_msg)
    await session.commit()
    await session.refresh(inbox_msg)
    assert inbox_msg.id is not None
    assert inbox_msg.created_at is not None
    # No auto-update for updated_at at model level
    assert inbox_msg.updated_at is None
    db_obj = await session.get(MobaInbox, inbox_msg.id)
    assert db_obj is not None


async def test_inbox_sender_team_relationship(session: AsyncSession):
    team = MobaTeam(name="Org A", nationality="X", region="NA")
    session.add(team)
    await session.commit()
    await session.refresh(team)

    msg = MobaInbox(
        subject="Offer",
        body="We'd like to arrange a friendly match.",
        category=MobaInboxCategory.MATCH,
        sender_team_id=team.id,
    )
    session.add(msg)
    await session.commit()
    await session.refresh(msg)

    assert msg.sender_team_id == team.id
    fetched = await session.get(MobaInbox, msg.id)
    assert fetched.sender_team_id == team.id
