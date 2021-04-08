#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2021  Pedrenrique G. Guimarães
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

class Champion:
    def __init__(self, champion_id: int, name: str, skill: int):
        self.champion_id = champion_id
        self.name = name

        # TODO: champions should belong to different classes such as mages, carries, etc
        # TODO: implement attributes dictionary for skill
        self.skill = skill

    def __repr__(self):
        return '{0} {1}'.format(self.__class__.__name__, self.name)

    def __str__(self):
        return '{0}'.format(self.name)
