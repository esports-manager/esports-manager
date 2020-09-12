#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020  Pedrenrique G. Guimarães
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

from .champion import Champion


class Player:
    def __init__(self,
                 player_id: int,
                 nationality: str,
                 first_name: str,
                 last_name: str,
                 nick_name: str,
                 skill: int):
        self.player_id = player_id

        # TODO: players should include team's id as well

        self.first_name = first_name
        self.last_name = last_name
        self.nick_name = nick_name

        self.nationality = nationality

        # TODO: replace skill by attribute dictionary
        self._skill = skill

        # TODO: players should have a "potential" value too. This value tells the game that the player
        # can improve his overall skill to a certain level

    @property
    def skill(self):
        return self._skill

    @skill.setter
    def skill(self, skill):
        self._skill = skill


class MobaPlayer(Player):
    def __init__(self,
                 player_id: int,
                 nationality: str,
                 first_name: str,
                 last_name: str,
                 nick_name: str,
                 skill: int):
        self._champion = None
        self._kills = 0
        self._deaths = 0
        self._assists = 0
        self._points = 0
        super().__init__(player_id, nationality, first_name, last_name, nick_name, skill)

    @property
    def champion(self):
        return self._champion

    @property
    def kills(self):
        return self._kills

    @property
    def deaths(self):
        return self._deaths

    @property
    def assists(self):
        return self._assists

    @property
    def points(self):
        return self._points

    @champion.setter
    def champion(self, champion: Champion):
        self._champion = champion

    @kills.setter
    def kills(self, kills: int):
        self._kills = kills

    @assists.setter
    def assists(self, assists: int):
        self._assists = assists

    @points.setter
    def points(self, add_pts: int):
        self._points = add_pts

    def __repr__(self):
        return '{0} {1}'.format(self.__class__.__name__, self.nick_name)

    def __str__(self):
        return '{0}'.format(self.nick_name)
