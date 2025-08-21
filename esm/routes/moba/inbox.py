# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_
from sqlmodel import Session, select

from esm.config import FRONTEND_DIR
from esm.db import get_session
from esm.models.moba import (
    MobaInbox,
    MobaInboxPublic,
    MobaInboxCreate,
    MobaInboxUpdate,
    MobaInboxStatus,
    MobaInboxCategory,
    MobaInboxPriority,
)


inbox_routes = APIRouter(
    prefix="/inbox",
    tags=["moba_inbox"],
    responses={404: {"description": "Inbox message not found"}},
)

templates_dir = FRONTEND_DIR / "templates"
templates = Jinja2Templates(directory=templates_dir)


def _parse_bool(val: Optional[str]) -> Optional[bool]:
    if val is None:
        return None
    return str(val).lower() in {"1", "true", "yes", "on"}


def _resolve_tab(
    category: Optional[MobaInboxCategory],
    status: Optional[MobaInboxStatus],
    is_starred: Optional[bool],
) -> str:
    if status == MobaInboxStatus.UNREAD:
        return "unread"
    if is_starred:
        return "starred"
    if status == MobaInboxStatus.ARCHIVED:
        return "archived"
    if category == MobaInboxCategory.TRANSFER:
        return "transfer"
    return "all"


@inbox_routes.get("/", response_model=List[MobaInboxPublic])
async def get_inbox(
    request: Request,
    session: Session = Depends(get_session),
):
    # Pagination
    page = max(1, int(request.query_params.get("page", 1)))
    per_page = int(request.query_params.get("per_page", 20))
    per_page = min(100, max(1, per_page))
    skip = (page - 1) * per_page

    # Filters
    category_param = request.query_params.get("category")
    status_param = request.query_params.get("status")
    priority_param = request.query_params.get("priority")
    starred_param = request.query_params.get("is_starred")
    labels_param = request.query_params.get("labels")
    search = (request.query_params.get("search") or "").strip()

    # Sorting
    sort = request.query_params.get("sort", "created_at")
    direction = request.query_params.get("direction", "desc")

    # Selection
    selected_id_param = request.query_params.get("selected_id")
    mark_read = _parse_bool(request.query_params.get("mark_read"))

    # Build base queries
    query = select(MobaInbox)
    count_query = select(MobaInbox)

    # Coerce filters
    category_enum: Optional[MobaInboxCategory] = None
    status_enum: Optional[MobaInboxStatus] = None
    priority_enum: Optional[MobaInboxPriority] = None
    is_starred: Optional[bool] = _parse_bool(starred_param)

    if category_param:
        try:
            category_enum = MobaInboxCategory(category_param)
        except Exception:
            category_enum = None
    if status_param:
        try:
            status_enum = MobaInboxStatus(status_param)
        except Exception:
            status_enum = None
    if priority_param:
        try:
            priority_enum = MobaInboxPriority(priority_param)
        except Exception:
            priority_enum = None

    # Apply filters
    if category_enum is not None:
        query = query.where(MobaInbox.category == category_enum)
        count_query = count_query.where(MobaInbox.category == category_enum)
    if status_enum is not None:
        query = query.where(MobaInbox.status == status_enum)
        count_query = count_query.where(MobaInbox.status == status_enum)
    if priority_enum is not None:
        query = query.where(MobaInbox.priority == priority_enum)
        count_query = count_query.where(MobaInbox.priority == priority_enum)
    if is_starred is not None:
        query = query.where(MobaInbox.is_starred == is_starred)
        count_query = count_query.where(MobaInbox.is_starred == is_starred)
    if labels_param:
        query = query.where(MobaInbox.labels.icontains(labels_param))
        count_query = count_query.where(MobaInbox.labels.icontains(labels_param))
    if search:
        search_expr = or_(
            MobaInbox.subject.icontains(search),
            MobaInbox.body.icontains(search),
            MobaInbox.sender_name.icontains(search),
        )
        query = query.where(search_expr)
        count_query = count_query.where(search_expr)

    # Sorting
    sort_map = {
        "created_at": MobaInbox.created_at,
        "subject": MobaInbox.subject,
        "status": MobaInbox.status,
        "category": MobaInbox.category,
    }
    sort_field = sort_map.get(sort, MobaInbox.created_at)
    if direction == "asc":
        query = query.order_by(sort_field.asc(), MobaInbox.id.asc())
    else:
        query = query.order_by(sort_field.desc(), MobaInbox.id.desc())

    total_messages = len(session.exec(count_query).all())
    total_pages = (total_messages + per_page - 1) // per_page

    messages = session.exec(query.offset(skip).limit(per_page)).all()
    messages_public: List[MobaInboxPublic] = [
        MobaInboxPublic.model_validate(m.model_dump()) for m in messages
    ]

    selected_message_public: Optional[MobaInboxPublic] = None
    current_selected_id: Optional[int] = None
    if selected_id_param:
        try:
            selected_id = int(selected_id_param)
            db_selected = session.get(MobaInbox, selected_id)
            if db_selected:
                # Mark as read if requested
                if mark_read and db_selected.status == MobaInboxStatus.UNREAD:
                    db_selected.status = MobaInboxStatus.READ
                    db_selected.read_at = datetime.now()
                    db_selected.updated_at = datetime.now()
                    session.add(db_selected)
                    session.commit()
                    session.refresh(db_selected)
                selected_message_public = MobaInboxPublic.model_validate(
                    db_selected.model_dump()
                )
                current_selected_id = db_selected.id
        except ValueError:
            pass

    pagination = {
        "page": page,
        "per_page": per_page,
        "total_items": total_messages,
        "total_pages": total_pages,
        "showing_start": min(skip + 1, total_messages) if total_messages > 0 else 0,
        "showing_end": min(skip + per_page, total_messages),
    }

    current_filters = {
        "category": category_param or "",
        "status": status_param or "",
        "priority": priority_param or "",
        "is_starred": bool(is_starred) if is_starred is not None else False,
        "labels": labels_param or "",
        "search": search,
        "sort": sort,
        "direction": direction,
        "selected_id": current_selected_id or "",
    }

    current_tab = _resolve_tab(category_enum, status_enum, is_starred)

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "components/inbox/inbox_list.html",
            {
                "request": request,
                "messages": messages_public,
                "selected_message": selected_message_public,
                "pagination": pagination,
                "current_filters": current_filters,
                "current_tab": current_tab,
            },
        )

    return messages_public


@inbox_routes.get("/{id}", response_model=MobaInboxPublic)
async def get_inbox_message(
    *, session: Session = Depends(get_session), id: int, request: Request
):
    message = session.get(MobaInbox, id)
    if not message:
        raise HTTPException(status_code=404, detail="Inbox message not found")

    # Optional mark as read
    mark_read = _parse_bool(request.query_params.get("mark_read"))
    if mark_read and message.status == MobaInboxStatus.UNREAD:
        message.status = MobaInboxStatus.READ
        message.read_at = datetime.now()
        message.updated_at = datetime.now()
        session.add(message)
        session.commit()
        session.refresh(message)

    public = MobaInboxPublic.model_validate(message.model_dump())

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "components/inbox/inbox_message.html",
            {"request": request, "message": public},
        )

    return public


@inbox_routes.post(
    "/", response_model=MobaInboxPublic, status_code=status.HTTP_201_CREATED
)
async def create_inbox_message(
    *, session: Session = Depends(get_session), inbox: MobaInboxCreate
):
    db_message = MobaInbox.model_validate(inbox)
    session.add(db_message)
    session.commit()
    session.refresh(db_message)
    return db_message


@inbox_routes.patch("/{id}")
async def update_inbox_message(
    *,
    session: Session = Depends(get_session),
    id: int,
    request: Request,
    inbox: MobaInboxUpdate | None = None,
):
    db_message = session.get(MobaInbox, id)
    if not db_message:
        raise HTTPException(status_code=404, detail="Inbox message not found")

    # Prefer JSON body when provided, else derive from query/form params (HTMX friendly)
    data: dict = {}
    if inbox is not None:
        data = inbox.model_dump(exclude_unset=True)
    else:
        qp = request.query_params
        # Strings
        if qp.get("subject"):
            data["subject"] = qp.get("subject")
        if qp.get("body"):
            data["body"] = qp.get("body")
        if qp.get("labels"):
            data["labels"] = qp.get("labels")
        if qp.get("action_url"):
            data["action_url"] = qp.get("action_url")
        if qp.get("sender_name"):
            data["sender_name"] = qp.get("sender_name")
        if qp.get("sender_title"):
            data["sender_title"] = qp.get("sender_title")
        if qp.get("sender_avatar_path"):
            data["sender_avatar_path"] = qp.get("sender_avatar_path")
        # Enums
        if qp.get("status"):
            try:
                data["status"] = MobaInboxStatus(qp.get("status"))
            except Exception:
                pass
        if qp.get("category"):
            try:
                data["category"] = MobaInboxCategory(qp.get("category"))
            except Exception:
                pass
        if qp.get("priority"):
            try:
                data["priority"] = MobaInboxPriority(qp.get("priority"))
            except Exception:
                pass
        # Bools / ints
        if qp.get("is_starred") is not None:
            data["is_starred"] = _parse_bool(qp.get("is_starred"))
        if qp.get("sender_team_id"):
            try:
                data["sender_team_id"] = int(qp.get("sender_team_id"))
            except ValueError:
                pass
        if qp.get("sender_player_id"):
            try:
                data["sender_player_id"] = int(qp.get("sender_player_id"))
            except ValueError:
                pass
        if qp.get("sender_staff_id"):
            try:
                data["sender_staff_id"] = int(qp.get("sender_staff_id"))
            except ValueError:
                pass
    # Manage timestamps for status transitions
    if "status" in data:
        new_status = data["status"]
        if new_status == MobaInboxStatus.READ and db_message.read_at is None:
            db_message.read_at = datetime.now()
        elif new_status == MobaInboxStatus.UNREAD:
            db_message.read_at = None
        elif new_status == MobaInboxStatus.ARCHIVED:
            db_message.archived_at = datetime.now()
    db_message.updated_at = datetime.now()

    db_message.sqlmodel_update(data)
    session.add(db_message)
    session.commit()
    session.refresh(db_message)

    if request.headers.get("HX-Request"):
        # After update, re-render list preserving filters and selection
        return await get_inbox(request=request, session=session)

    return MobaInboxPublic.model_validate(db_message.model_dump())


@inbox_routes.delete("/{id}")
async def delete_inbox_message(
    *, session: Session = Depends(get_session), id: int, request: Request
):
    db_message = session.get(MobaInbox, id)
    if not db_message:
        raise HTTPException(status_code=404, detail="Inbox message not found")
    session.delete(db_message)
    session.commit()

    if request.headers.get("HX-Request"):
        return await get_inbox(request=request, session=session)

    return {"message": "Inbox message deleted"}
