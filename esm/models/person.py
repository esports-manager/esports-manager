#      eSports Manager - A free and open source eSports management simulation game
#      Copyright (C) 2020-2025  Pedrenrique G. Guimarães
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date, datetime


class Person(SQLModel):
    """
    Base person model representing any individual in the esports ecosystem.
    This serves as a foundation for players, staff members, etc.
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    # Basic personal information
    name: str = Field(index=True)  # In-game name/nickname
    full_name: Optional[str] = Field(default=None)  # Real full name
    nationality: str  # Country of origin

    # Date information
    date_of_birth: date

    # Calculated property, not stored in database
    @property
    def age(self) -> int:
        """Calculate age based on date of birth"""
        today = date.today()
        age = today.year - self.date_of_birth.year

        # Adjust age if birthday hasn't occurred yet this year
        if (today.month, today.day) < (
            self.date_of_birth.month,
            self.date_of_birth.day,
        ):
            age -= 1

        return age

    # Optional biography/profile
    bio: Optional[str] = Field(default=None)
    image_path: Optional[str] = Field(default=None)  # Local path to profile picture

    # Common metadata
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)

    def __repr__(self) -> str:
        """String representation of a person"""
        return f"<Person: {self.name} ({self.nationality}, {self.age})>"
