# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from esm.models.moba.inbox import (
    MobaInbox,
    MobaInboxStatus,
    MobaInboxCategory,
    MobaInboxPriority,
)


async def test_get_inbox_empty(client: AsyncClient):
    resp = await client.get("/api/moba/inbox")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_inbox_message(client: AsyncClient, session: AsyncSession):
    resp = await client.post(
        "/api/moba/inbox",
        json={
            "subject": "Welcome",
            "body": "Welcome to the league!",
            "category": "general",
            # Omitting status and priority to test defaults
        },
    )
    assert resp.status_code == 201
    inbox_id = resp.json()["id"]
    msg = await session.get(MobaInbox, inbox_id)
    assert isinstance(msg, MobaInbox)
    assert msg.subject == "Welcome"
    assert msg.body == "Welcome to the league!"
    assert msg.category == MobaInboxCategory.GENERAL
    assert msg.status == MobaInboxStatus.UNREAD
    assert msg.priority == MobaInboxPriority.NORMAL
    assert msg.created_at is not None


async def test_get_inbox_message_by_id(client: AsyncClient, session: AsyncSession):
    m = MobaInbox(subject="Test", body="Body", category=MobaInboxCategory.MARKET)
    session.add(m)
    await session.commit()
    await session.refresh(m)
    resp = await client.get(f"/api/moba/inbox/{m.id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == m.id
    assert body["subject"] == m.subject
    assert body["category"] == MobaInboxCategory.MARKET.value


async def test_get_inbox_message_not_found(client: AsyncClient):
    resp = await client.get("/api/moba/inbox/9999")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Inbox message not found"}


async def test_mark_read_via_get_by_id(client: AsyncClient, session: AsyncSession):
    m = MobaInbox(subject="Read me", body="...", category=MobaInboxCategory.GENERAL)
    session.add(m)
    await session.commit()
    await session.refresh(m)
    assert m.status == MobaInboxStatus.UNREAD
    resp = await client.get(f"/api/moba/inbox/{m.id}?mark_read=true")
    assert resp.status_code == 200
    updated = await session.get(MobaInbox, m.id)
    assert updated.status == MobaInboxStatus.READ
    assert isinstance(updated.read_at, datetime)


async def test_update_inbox_message(client: AsyncClient, session: AsyncSession):
    m = MobaInbox(subject="Update", body="Body", category=MobaInboxCategory.GENERAL)
    session.add(m)
    await session.commit()
    await session.refresh(m)
    resp = await client.patch(
        f"/api/moba/inbox/{m.id}",
        json={
            "subject": "Updated",
            "priority": "urgent",
            "is_starred": True,
            "labels": "important,ops",
            "status": "archived",
        },
    )
    assert resp.status_code == 200
    updated = await session.get(MobaInbox, m.id)
    assert updated.subject == "Updated"
    assert updated.priority == MobaInboxPriority.URGENT
    assert updated.is_starred is True
    assert updated.labels == "important,ops"
    assert updated.status == MobaInboxStatus.ARCHIVED
    assert isinstance(updated.archived_at, datetime)
    assert isinstance(updated.updated_at, datetime)


async def test_delete_inbox_message(client: AsyncClient, session: AsyncSession):
    m = MobaInbox(subject="Bye", body="Body", category=MobaInboxCategory.ADMIN)
    session.add(m)
    await session.commit()
    await session.refresh(m)
    resp = await client.delete(f"/api/moba/inbox/{m.id}")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Inbox message deleted"}
    assert await session.get(MobaInbox, m.id) is None
