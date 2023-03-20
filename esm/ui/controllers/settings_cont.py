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

from .controllerinterface import IController
from esm.ui.layouts.settings import SettingsLayout
from esm.ui.igamecontroller import IGameController
from esm.core.esmcore import ESMCore


class SettingsController(IController):
    def __init__(self, controller: IGameController, core: ESMCore):
        self.controller = controller
        self.layout = SettingsLayout()
        self.core = core
        self.loaded_data = False

    @property
    def amount_players(self) -> int:
        return self.core.settings.amount_players

    @amount_players.setter
    def amount_players(self, amount):
        self.core.settings.amount_players = amount

    def generate_all_data(self) -> None:
        self.core.db.generate_moba_files()

    def update_inputs(self):
        self.controller.update_element_on_screen("settings_root_dir", value=self.core.settings.root_dir)
        self.controller.update_element_on_screen("settings_fontsize_input", value=self.core.settings.font_scale)
        self.controller.update_element_on_screen("settings_amount_input", value=self.core.settings.amount_players)
        self.controller.update_element_on_screen("settings_enable_autosave", value=self.core.settings.enable_auto_save)
        self.controller.update_element_on_screen("settings_res_dir", value=self.core.settings.res_dir)
        self.controller.update_element_on_screen("settings_db_dir", value=self.core.settings.db_dir)
        self.controller.update_element_on_screen("settings_saves_dir", value=self.core.settings.save_file_dir)
        self.controller.update_element_on_screen("settings_ch_file", value=self.core.settings.champions_file)
        self.controller.update_element_on_screen("settings_pl_file", value=self.core.settings.players_file)
        self.controller.update_element_on_screen("settings_t_file", value=self.core.settings.teams_file)

    def update_settings_data(
            self,
            font_size: str,
            root_dir: str,
            res_dir: str,
            db_dir: str,
            save_file_dir: str,
            champions_file: str,
            players_file: str,
            teams_file: str,
    ):
        if font_size != '':
            self.core.settings.font_scale = font_size
        if root_dir != '':
            self.core.settings.root_dir = root_dir
        if res_dir != '':
            self.core.settings.res_dir = res_dir
        if db_dir != '':
            self.core.settings.db_dir = db_dir
        if save_file_dir != '':
            self.core.settings.save_file_dir = save_file_dir
        if champions_file != '':
            self.core.settings.champions_file = champions_file
        if players_file != '':
            self.core.settings.players_file = players_file
        if teams_file != '':
            self.core.settings.teams_file = teams_file
        self.update_inputs()

    def update(self, event, values, make_screen):
        if not self.controller.get_gui_element("settings_screen").visible:
            self.loaded_data = False
        else:
            if not self.loaded_data:
                self.update_inputs()
                self.loaded_data = True

            if event == "settings_cancel_btn":
                make_screen("settings_screen", "main_screen")

            if event == "settings_enable_autosave":
                self.core.settings.enable_auto_save = True
                self.update_inputs()

            if event == "settings_apply_btn":
                self.update_settings_data(
                    values['settings_fontsize_input'],
                    values['settings_root_dir'],
                    values["settings_res_dir"],
                    values["settings_db_dir"],
                    values["settings_saves_dir"],
                    values["settings_ch_file"],
                    values["settings_pl_file"],
                    values["settings_t_file"],
                )
                self.core.settings.create_config_file()
                self.update_inputs()

            elif event == "settings_generate_btn":
                try:
                    value = int(values["settings_amount_input"])
                    self.core.check_player_amount()
                except ValueError as e:
                    self.controller.get_gui_information_window(
                        e,
                        'Error in number of players!'
                    )
                    self.amount_players = 50
                else:
                    self.controller.amount_players = value
                finally:
                    self.core.db.generate_moba_files()
                    self.update_inputs()
