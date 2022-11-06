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

from .controllerinterface import IController, IGameController
from ..debugmatch import DebugMatchLayout
from ....core.esports.moba.modules.match_factory import MatchFactory


class DebugMatchController(IController):
    def __init__(self, controller: IGameController):
        super().__init__(controller)
        self.layout = DebugMatchLayout(self)
        self.queue = Queue()
        self.match_sim = MatchFactory()
        self.buttons_disabled = False

    def start_match(self):
        self.controller.update_element_on_screen("debug_match_output", value="", append=False)
        self.match_sim.is_game_running = True
        self.reset_match()
        self.match_sim.current_game.is_match_over = False
        self.start_match_sim_thread()

    def get_queue_messages_and_update(self):
        if not self.queue.empty():
            message = self.queue.get(block=False)
            self.controller.update_element_on_screen("debug_match_output", value=message, append=True)

    def get_team_data(self):
        if self.match_sim.current_game is None:
            return None
        players = [list(team.list_players) for team in self.match_sim.current_live_game.match.teams]

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
        self.match_sim.reset_game(self.queue)
        self.match_sim.reset_team_values()
        data = self.get_team_data()
        self.update_debug_match_info(data)

    def update_debug_match_info(self, data):
        current_game = self.match_sim.current_live_game
        win_prob = current_game.match.team1.win_prob * 100
        self.controller.update_element_on_screen("debug_team1table", values=data[0])
        self.controller.update_element_on_screen("debug_team2table", values=data[1])
        self.controller.update_element_on_screen("debug_team1skill", value=current_game.match.team1.total_skill)
        self.controller.update_element_on_screen("debug_team2skill", value=current_game.match.team2.total_skill)
        self.controller.update_element_on_screen("debug_team1winprob", value=current_game.match.team1.win_prob)
        self.controller.update_element_on_screen("debug_team2winprob", value=current_game.match.team2.win_prob)
        self.controller.update_progress_bar("debug_winprob", win_prob)
        self.controller.update_element_on_screen("debug_match_current_time", value=current_game.game_time)
        self.controller.update_element_on_screen("debug_team1towers", value=current_game.match.team1.towers)
        self.controller.update_element_on_screen("debug_team2towers", value=current_game.match.team2.towers)
        self.controller.update_element_on_screen("debug_team1inhibs", value=current_game.match.team1.inhibitors)
        self.controller.update_element_on_screen("debug_team2inhibs", value=current_game.match.team2.inhibitors)
        self.controller.update_element_on_screen("debug_team1name", value=current_game.match.team1.name)
        self.controller.update_element_on_screen("debug_team2name", value=current_game.match.team2.name)

    def enable_debug_buttons(self):
        self._change_button_status(False)

    def disable_debug_buttons(self):
        self._change_button_status(True)
        self.buttons_disabled = True

    def _change_button_status(self, disabled):
        self.controller.update_element_on_screen("debug_startmatch_btn", disabled=disabled)
        self.controller.update_element_on_screen("debug_newteams_btn", disabled=disabled)
        self.controller.update_element_on_screen("debug_resetmatch_btn", disabled=disabled)

    def start_match_sim_thread(self) -> None:
        if e := self.match_sim.run_game():
            self.controller.print_error(e)

    def update_match_sim_values(self, values):
        if (
                self.match_sim.current_live_game is not None
                and self.match_sim.current_live_game.is_match_over
                and not self.match_sim.game_thread.is_alive()
        ):
            self.match_sim.is_game_running = False

        if self.match_sim.current_live_game is not None:
            self.match_sim.current_live_game.simulate = bool(
                values["debug_simulate_checkbox"]
            )
            self.update_debug_match_info(self.get_team_data())

    def check_disabled_buttons(self):
        if self.match_sim.is_game_running and not self.buttons_disabled:
            self.disable_debug_buttons()
        else:
            self.enable_debug_buttons()

    def get_new_teams(self):
        try:
            self.controller.core.check_files()
        except FileNotFoundError:
            self.controller.core.db.generate_all()
        teams = self.controller.core.db.load_moba_teams()
        self.match_sim.initialize_random_debug_game(teams)
        self.update_debug_match_info(self.get_team_data())

    def cancel_match(self, make_screen):
        if self.match_sim.is_game_running:
            self.match_sim.current_live_game.is_match_over = True
        self.match_sim = MatchFactory()
        make_screen("debug_match_screen", "main_screen")

    def update(self, event, values, make_screen):
        if not self.controller.get_gui_element("debug_match_screen").visible:
            self.match_sim = MatchFactory()
            self.queue = Queue()
        else:
            self.check_disabled_buttons()

            self.match_sim.check_game_running_thread()

            if self.match_sim.current_game is None:
                self.get_new_teams()

            self.get_queue_messages_and_update()

            # Click the Start Match button
            if event == "debug_startmatch_btn":
                self.start_match()

            # Click the Cancel button
            if event == "debug_cancel_btn":
                self.cancel_match(make_screen)

            # Click the New Teams button
            elif event == "debug_newteams_btn":
                self.get_new_teams()

            # Click the Reset Match button
            elif event == "debug_resetmatch_btn":
                self.reset_match()

            # Check if the match is running to update values on the fly
            if self.match_sim.is_game_running:
                self.update_match_sim_values(values)
