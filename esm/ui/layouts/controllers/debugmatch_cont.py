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
from queue import Queue

from .controllerinterface import IController
from ..debugmatch import DebugMatchLayout
from ....core.esports.moba.modules.game_simulation import GameSimulation


class DebugMatchController(IController):
    def __init__(self, controller):
        super().__init__(controller)
        self.layout = DebugMatchLayout(self)
        self.queue = Queue()
        self.game_simulation = GameSimulation()
        self.buttons_disabled = False

    def get_queue_messages_and_update(self):
        if not self.queue.empty():
            message = self.queue.get(block=False)
            self.controller.update_gui_element("debug_match_output", value=message, append=True)

    def get_team_data(self):
        if self.current_match is None:
            return None
        players = [list(team.list_players) for team in self.current_match.match.teams]

        data = []
        for team in players:
            team_data = [
                [
                    player.lane.name,
                    player.nick_name,
                    player.kills,
                    player.deaths,
                    player.assists,
                    player.champion,
                    int(player.get_player_total_skill()),
                ]
                for player in team
            ]
            data.append(team_data)

        return data

    def reset_match(self):
        self.game_simulation.reset_game(self.queue)
        self.game_simulation.reset_team_values()

    def update_debug_match_info(self, data):
        win_prob = self.current_match.match.team1.win_prob * 100
        self.controller.update_gui_element("debug_team1table", values=data[0])
        self.controller.update_gui_element("debug_team2table", values=data[1])
        self.controller.update_gui_element("debug_team1skill", value=self.current_match.match.team1.total_skill)
        self.controller.update_gui_element("debug_team2skill", value=self.current_match.match.team2.total_skill)
        self.controller.update_gui_element("debug_team1winprob", value=self.current_match.match.team1.win_prob)
        self.controller.update_gui_element("debug_team2winprob", value=self.current_match.match.team2.win_prob)
        self.controller.update_progress_bar("debug_winprob", win_prob)
        self.controller.update_gui_element("debug_match_current_time", value=self.current_match.game_time)
        self.controller.update_gui_element("debug_team1towers", value=self.current_match.match.team1.towers)
        self.controller.update_gui_element("debug_team2towers", value=self.current_match.match.team2.towers)
        self.controller.update_gui_element("debug_team1inhibs", value=self.current_match.match.team1.inhibitors)
        self.controller.update_gui_element("debug_team2inhibs", value=self.current_match.match.team2.inhibitors)
        self.controller.update_gui_element("debug_team1name", value=self.current_match.match.team1.name)
        self.controller.update_gui_element("debug_team2name", value=self.current_match.match.team2.name)

    def enable_debug_buttons(self):
        self._change_button_status(False)

    def disable_debug_buttons(self):
        self._change_button_status(True)
        self.buttons_disabled = True

    def _change_button_status(self, disabled):
        self.controller.update_gui_element("debug_startmatch_btn", disabled=disabled)
        self.controller.update_gui_element("debug_newteams_btn", disabled=disabled)
        self.controller.update_gui_element("debug_resetmatch_btn", disabled=disabled)

    def start_match_sim_thread(self) -> None:
        if e := self.game_simulation.run_game():
            self.controller.print_error(e)

    def update(self, event, values, make_screen):
        if not self.controller.get_gui_element("debug_match_screen").visible:
            self.game_simulation.current_live_game = None
            self.game_simulation.game_thread = None
            self.game_simulation.is_game_running = False
        else:

            get_team_data = self.get_team_data
            update_debug_match_info = self.update_debug_match_info

            if self.game_simulation.is_game_running and not self.buttons_disabled:
                self.disable_debug_buttons()
            else:
                self.enable_debug_buttons()

            self.game_simulation.check_game_running_thread()

            if self.game_simulation.current_game is None:
                self.current_match = self.game_simulation.initialize_random_debug_game()
                update_debug_match_info(get_team_data())

            self.get_queue_messages_and_update()

            # Click the Start Match button
            if event == "debug_startmatch_btn":
                self.controller.update_gui_element("debug_match_output", value="", append=False)
                self.is_match_running = True
                self.reset_match()
                self.current_match.is_match_over = False
                self.start_match_sim_thread()

            # Click the Cancel button
            if event == "debug_cancel_btn":
                if self.is_match_running:
                    self.current_match.is_match_over = True
                self.current_match = None
                make_screen("debug_match_screen", "main_screen")

            # Click the New Teams button
            elif event == "debug_newteams_btn":
                self.controller.check_files()
                self.current_match = self.game_simulation.initialize_random_debug_match()
                data = get_team_data()
                update_debug_match_info(data)

            # Click the Reset Match button
            elif event == "debug_resetmatch_btn":
                self.reset_match()
                data = get_team_data()
                update_debug_match_info(data)

            # Check if the match is running to update values on the fly
            if self.is_match_running:
                if (
                        self.current_match is not None
                        and self.current_match.is_match_over
                        and not self.match_thread.is_alive()
                ):
                    self.is_match_running = False

                if self.current_match is not None:
                    self.current_match.simulate = bool(
                        values["debug_simulate_checkbox"]
                    )
                    data = get_team_data()
                    update_debug_match_info(data)
