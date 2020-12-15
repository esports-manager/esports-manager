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
from src.core.esports.moba.moba_enums_def import MobaEventType


class Moba:
    def __init__(self):
        self.major_jg = [
            {
                'name': 'Baron',
                'id': 1,
                'priority': 10,
                'spawn_time': 20.0,
                'cooldown': 6.0
            },
            {
                'name': 'Dragon',
                'id': 2,
                'priority': 5,
                'spawn_time': 5.0,
                'cooldown': 5.0
            }
        ]
        self.tower_time = 15.0

    def get_jg_spawn_time(self, jg_name):
        for jg in self.major_jg:
            if jg['name'] == jg_name:
                return jg['spawn_time']

    def get_jg_cooldown(self, jg_name):
        for jg in self.major_jg:
            if jg['name'] == jg_name:
                return jg['cooldown']

    def get_jg_priority(self, jg_name):
        for jg in self.major_jg:
            if jg['name'] == jg_name:
                if jg['name'] == jg_name:
                    return jg['priority']
