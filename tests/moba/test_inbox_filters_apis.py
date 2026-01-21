# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from esm.models.moba.inbox import (
    MobaInbox,
    MobaInboxCategory,
    MobaInboxPriority,
    MobaInboxStatus,
)


async def seed_messages(session: AsyncSession):
    m1 = MobaInbox(
        subject="A - transfer urgent",
        body="",
        category=MobaInboxCategory.TRANSFER,
        status=MobaInboxStatus.UNREAD,
        priority=MobaInboxPriority.URGENT,
        is_starred=True,
        labels="ops,urgent",
    )
    m2 = MobaInbox(
        subject="B - general normal",
        body="",
        category=MobaInboxCategory.GENERAL,
        status=MobaInboxStatus.READ,
        priority=MobaInboxPriority.NORMAL,
        is_starred=False,
        labels="misc",
    )
    m3 = MobaInbox(
        subject="C - transfer low star",
        body="",
        category=MobaInboxCategory.TRANSFER,
        status=MobaInboxStatus.UNREAD,
        priority=MobaInboxPriority.LOW,
        is_starred=True,
        labels="ops,backlog",
    )
    m4 = MobaInbox(
        subject="D - admin star unread",
        body="",
        category=MobaInboxCategory.ADMIN,
        status=MobaInboxStatus.UNREAD,
        priority=MobaInboxPriority.HIGH,
        is_starred=True,
        labels="admin,ops",
    )
    m5 = MobaInbox(
        subject="E - transfer archived",
        body="",
        category=MobaInboxCategory.TRANSFER,
        status=MobaInboxStatus.ARCHIVED,
        priority=MobaInboxPriority.HIGH,
        is_starred=False,
        labels="ops",
    )
    session.add(m1)
    session.add(m2)
    session.add(m3)
    session.add(m4)
    session.add(m5)
    await session.commit()
    await session.refresh(m1)
    await session.refresh(m2)
    await session.refresh(m3)
    await session.refresh(m4)
    await session.refresh(m5)
    return m1, m2, m3, m4, m5


async def test_inbox_list_filters_and_sort_pagination(
    client: AsyncClient, session: AsyncSession
):
    m1, m2, m3, m4, m5 = await seed_messages(session)

    # Filter: category=transfer, status=unread, is_starred=true
    r = await client.get(
        "/api/moba/inbox",
        params={
            "category": "transfer",
            "status": "unread",
            "is_starred": "true",
        },
    )
    assert r.status_code == 200
    ids = [it["id"] for it in r.json()]
    # default sort: created_at desc -> later created first (m3 then m1)
    assert ids == [m3.id, m1.id]

    # Filter by labels contains 'ops'
    r2 = await client.get(
        "/api/moba/inbox",
        params={"labels": "ops", "sort": "subject", "direction": "asc"},
    )
    assert r2.status_code == 200
    subjects = [it["subject"] for it in r2.json()]
    # m1, m3, m4, m5 contain 'ops'
    assert subjects == [
        "A - transfer urgent",
        "C - transfer low star",
        "D - admin star unread",
        "E - transfer archived",
    ]

    # Search term over subject
    r3 = await client.get("/api/moba/inbox", params={"search": "transfer"})
    assert r3.status_code == 200
    ids3 = {it["id"] for it in r3.json()}
    assert ids3 == {m1.id, m3.id, m5.id}

    # Pagination with sorting by subject asc -> page 2 returns C and D
    r4 = await client.get(
        "/api/moba/inbox",
        params={"sort": "subject", "direction": "asc", "per_page": 2, "page": 2},
    )
    assert r4.status_code == 200
    assert [it["subject"] for it in r4.json()] == [
        "C - transfer low star",
        "D - admin star unread",
    ]


async def test_inbox_list_selected_mark_read(
    client: AsyncClient, session: AsyncSession
):
    m = MobaInbox(subject="Mark me", body="", category=MobaInboxCategory.GENERAL)
    session.add(m)
    await session.commit()
    await session.refresh(m)
    assert m.status == MobaInboxStatus.UNREAD

    r = await client.get(
        "/api/moba/inbox", params={"selected_id": m.id, "mark_read": "true"}
    )
    assert r.status_code == 200
    refreshed = await session.get(MobaInbox, m.id)
    assert refreshed.status == MobaInboxStatus.READ
    assert refreshed.read_at is not None


async def test_inbox_htmx_list_returns_html(client: AsyncClient, session: AsyncSession):
    # ensure at least one
    m = MobaInbox(subject="Hello", body="", category=MobaInboxCategory.GENERAL)
    session.add(m)
    await session.commit()

    r = await client.get("/api/moba/inbox", headers={"HX-Request": "true"})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")


async def test_inbox_htmx_get_message_returns_html(
    client: AsyncClient, session: AsyncSession
):
    m = MobaInbox(subject="Hello", body="", category=MobaInboxCategory.GENERAL)
    session.add(m)
    await session.commit()
    await session.refresh(m)

    r = await client.get(f"/api/moba/inbox/{m.id}", headers={"HX-Request": "true"})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")


async def test_inbox_htmx_patch_query_params_updates_and_rerenders(
    client: AsyncClient, session: AsyncSession
):
    m = MobaInbox(subject="Patch me", body="", category=MobaInboxCategory.GENERAL)
    session.add(m)
    await session.commit()
    await session.refresh(m)

    r = await client.patch(
        f"/api/moba/inbox/{m.id}",
        params={"status": "archived", "is_starred": "true", "labels": "ops"},
        headers={"HX-Request": "true"},
    )
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")
    updated = await session.get(MobaInbox, m.id)
    assert updated.status == MobaInboxStatus.ARCHIVED
    assert updated.is_starred is True
    assert updated.labels == "ops"


async def test_inbox_htmx_delete_rerenders_list(
    client: AsyncClient, session: AsyncSession
):
    m = MobaInbox(subject="Delete me", body="", category=MobaInboxCategory.GENERAL)
    session.add(m)
    await session.commit()
    await session.refresh(m)

    r = await client.delete(f"/api/moba/inbox/{m.id}", headers={"HX-Request": "true"})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")
    assert await session.get(MobaInbox, m.id) is None
