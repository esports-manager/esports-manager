# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from sqlmodel import SQLModel
from datetime import date
from typing import Optional


class Person(SQLModel):
    first_name: str
    last_name: str
    date_of_birth: date
    nick_name: Optional[str] = None
    nationality: Optional[str] = None
    bio: Optional[str] = None
    image_path: Optional[str] = None
