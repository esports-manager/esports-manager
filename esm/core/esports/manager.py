#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2024  Pedrenrique G. Guimarães
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
from datetime import date, datetime
from typing import Union

from esm.core.esports.moba.mobateam import MobaTeam

from .player import Player


class Manager(Player):
    def __init__(
        self,
        player_id: int,
        nationality: str,
        first_name: str,
        last_name: str,
        birthday: Union[date, datetime, str],
        nick_name: str,
        team: Union[int, MobaTeam],
        is_player: bool,
        quality: int,
    ):
        super().__init__(
            player_id, nationality, first_name, last_name, birthday, nick_name
        )
        self.team = team
        self.is_player = is_player
        self.quality = quality

    def get_dict(self):
        team = self.team.team_id if isinstance(self.team, MobaTeam) else self.team
        return {
            "id": self.player_id.int,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "birthday": self.birthday.strftime("%Y/%m/%d"),
            "team": team,
            "is_player": self.is_player,
            "quality": self.quality,
        }
