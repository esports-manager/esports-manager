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


class Commentaries:
    def __init__(
            self,
            event_name,
            kill_dict_event: list = None,
            atk_team_name: str = "",
            def_team_name: str = "",
            defended: bool = False,
            lane: str = "",
            jg_name: str = "",
            stole: bool = False,
            commentaries: list = None,
    ):
        self.commentary = None
        self.event_name = event_name
        self.kill_dict_event = kill_dict_event
        self.atk_team_name = atk_team_name
        self.def_team_name = def_team_name
        self.defended = defended
        self.lane = lane
        self.jg_name = jg_name
        self.stole = stole
        self.commentaries = commentaries

        self.get_commentaries()

    def get_commentaries(self):
        if self.event_name == "KILL" and self.kill_dict_event is not None:
            self._get_kill_commentaries(self.kill_dict_event)

        if self.event_name == "JUNGLE":
            self._get_jg_commentary(
                self.stole,
                self.def_team_name,
                self.atk_team_name,
                self.jg_name,
            )

        if self.event_name == "INHIB ASSAULT":
            self._get_inhib_commentary(
                self.defended,
                self.def_team_name,
                self.atk_team_name,
                self.lane
            )

        elif self.event_name == "NEXUS ASSAULT":
            self.commentary = self.atk_team_name + " won the match!"

        elif self.event_name == "TOWER ASSAULT":
            self._get_tower_commentary(
                self.defended,
                self.def_team_name,
                self.atk_team_name,
                self.lane
            )

    @staticmethod
    def list_names(players: list):
        names = ""
        for i, player in enumerate(players):
            if i == len(players) - 1:
                names = names + player["killed_player"].nick_name + "."
            else:
                names = names + player["killed_player"].nick_name + ", "

        return names

    def _get_kill_commentaries(
            self,
            kill_dict_event,
    ):
        names = self.list_names(kill_dict_event)
        killer = kill_dict_event[0]["killer"]
        amount_kills = len(kill_dict_event)

        if amount_kills == 2:
            self.commentary = killer.nick_name + " got a Double Kill!"
        elif amount_kills == 3:
            self.commentary = killer.nick_name + " got a Triple Kill!"
        elif amount_kills == 4:
            self.commentary = killer.nick_name + " got a QUADRA KILL!"
        elif amount_kills == 5:
            self.commentary = killer.nick_name + " got a PENTAKILL!"

        if amount_kills != 0:
            if self.commentary is not None:
                self.commentary = (
                        self.commentary + "\n" + killer.nick_name + " has slain: " + names
                )
            else:
                self.commentary = killer.nick_name + " has slain " + names

        if self.commentary is not None:
            if killer.is_player_godlike():
                self.commentary = (
                        self.commentary + "\n" + killer.nick_name + " is GODLIKE!"
                )
            if killer.is_player_on_killing_spree():
                self.commentary = (
                        self.commentary + "\n" + killer.nick_name + " is on a KILLING SPREE!"
                )
            if killer.is_player_legendary():
                self.commentary = (
                        self.commentary + "\n" + killer.nick_name + " is LEGENDARY!!"
                )

    def _get_jg_commentary(
            self,
            stole,
            def_team_name,
            atk_team_name,
            jg_name,
    ):
        if stole:
            self.commentary = def_team_name + " stole the " + jg_name
        else:
            self.commentary = atk_team_name + " has slain the " + jg_name

    def _get_inhib_commentary(
            self,
            defended,
            def_team_name,
            atk_team_name,
            lane,
    ):
        if defended:
            self.commentary = (
                    def_team_name
                    + " has defended the "
                    + lane
                    + " inhibitor successfully"
            )
        else:
            self.commentary = (
                    atk_team_name + " has destroyed the " + lane + " inhibitor"
            )

    def _get_tower_commentary(
            self,
            defended,
            def_team_name,
            atk_team_name,
            lane
    ):
        if defended:
            self.commentary = (
                    def_team_name + " has defended the " + lane + " tower successfully"
            )
        else:
            self.commentary = (
                    atk_team_name + " has destroyed the " + lane + " tower"
            )
