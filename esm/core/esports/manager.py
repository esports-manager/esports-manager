#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2022  Pedrenrique G. Guimarães
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
from datetime import datetime, date
from typing import Union

from esm.core.esports.moba.team import Team


class Manager:
    def __init__(
            self, name: str, birthday: Union[date, datetime, str], team: Union[int, Team], is_player: bool, quality: int
    ):
        self.name = name

        # This might be necessary if we are using JSON deserialization
        if isinstance(birthday, str):
            self.birthday = datetime.strptime(birthday, "%Y/%m/%d").date()
        elif isinstance(birthday, date):
            self.birthday = birthday
        elif isinstance(birthday, datetime):
            self.birthday = birthday.date()

        self.team = team
        self.is_player = is_player
        self.quality = quality

    def get_dict(self):
        team = self.team.team_id if isinstance(self.team, Team) else self.team
        return {
            "name": self.name,
            "birthday": self.birthday.strftime("%Y/%m/%d"),
            "team": team,
            "quality": self.quality
        }
