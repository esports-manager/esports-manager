#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2023  Pedrenrique G. Guimarães
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
import uuid
from datetime import date, datetime
from typing import Union


class Player:
    """
    Base player class.
    May be used by all other eSports.
    """

    def __init__(
            self,
            player_id: Union[int, uuid.UUID],
            nationality: str,
            first_name: str,
            last_name: str,
            birthday: Union[date, datetime, str],
            nick_name: str,
    ):
        if isinstance(player_id, int):
            self.player_id = uuid.UUID(int=player_id)
        elif isinstance(player_id, uuid.UUID):
            self.player_id = player_id
        # TODO: players should include team's id as well

        self.first_name = first_name
        self.last_name = last_name

        # This might be necessary if we are using JSON deserialization
        if isinstance(birthday, str):
            self.birthday = datetime.strptime(birthday, "%Y/%m/%d").date()
        elif isinstance(birthday, date):
            self.birthday = birthday
        elif isinstance(birthday, datetime):
            self.birthday = birthday.date()

        self.nick_name = nick_name

        self.nationality = nationality

        # TODO: players should have a "potential" value too. This value tells the game that the player
        # can improve his overall skill to a certain level

    def get_age(self, today: date = date.today()) -> int:
        """
        Defines the player's age. Today generally refers to the datetime.today function, but when we implement
        a calendar, it will all be based on the current calendar date in-game.
        """
        age = today - self.birthday
        return int(age.days * 0.0027379070)

    def __eq__(self, other):
        return self.player_id == other.player_id if isinstance(other, Player) else NotImplemented
