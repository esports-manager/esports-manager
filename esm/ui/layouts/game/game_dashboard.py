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

from esm.ui.gui_components import *

from esm.ui.layouts.layoutinterface import ILayout


class GameDashboardLayout(ILayout):
    def __init__(self):
        self.lay = self.layout()
        self.col = self.column()

    def column(self) -> sg.Column:
        return sg.Column(
            self.lay,
            key="game_dashboard_screen",
            visible=False,
            justification="left",
            element_justification="left",
        )

    def layout(self) -> list:
        """
        Defines the main game dashboard screen.
        """
        tab_home = [
            [esm_form_text("Next match details:", font=(bold_font, default_font_size))],
            [esm_form_text("Team"), esm_form_text("TEAMNAME123456789101112131415", key="game_dashboard_oppteamname")],
            [esm_table(values=[['LANE', 'PLAYERNAME1234567891011121314151617', '1515']],
                       headings=["Lane", "Nickname", "Skill"], key="game_dashboard_oppteamroster", size=(100, 30))],
            [esm_form_text("Avg skill level: ", font=(bold_font, default_font_size)),
             esm_form_text("100", key="game_dashboard_oppteamskill_lvl")]
        ]

        team_roster_table = [
            [esm_form_text("Team roster:", font=(bold_font, default_font_size))],
            [esm_table(values=[['LANE', 'PLAYERNAME1234567891011121314151617', '1515']],
                       headings=["Lane", "Nickname", "Skill"], key="game_dashboard_roster")],
        ]

        player_champion_data = [
            [esm_form_text("Player details:", font=(bold_font, default_font_size))],
            [esm_table(values=[['No player selected', '00']], headings=["Champion Name", "Skill"],
                       key="game_dashboard_player_details")],
        ]

        tab_roster = [
            [esm_title_text("ROSTER\n", justification="center")],
            [sg.Column(team_roster_table), sg.Column(player_champion_data)]
        ]

        tab_championship = [
            [esm_title_text("CHAMPIONSHIP\n", justification="center")],
            [esm_table(
                values=[
                    ["100", "TEAMNAME12345678910111213141517181920", "00", "00", "00"]
                ],
                headings=["Position", "Team Name", "Victories", "Defeats", "Points"],
                key="game_dashboard_championship",
                size=(100, 30)),
            ]
        ]

        tab_scheduled_matches = [
            [esm_title_text("SCHEDULED MATCHES\n", justification="center")],
            [esm_table(values=[
                ["2020/01/01", "TEAMNAME12345678910111213141517181920", "TEAMNAME12345678910111213141517181920"]],
                       headings=["Date", "Team 1", "Team 2"], size=(100, 300))]
        ]

        tab_game_details = [
            [esm_title_text("CHAMPIONS\n", justification="center")],
            [esm_table(values=[["CHAMPION_NAME123456789101112", "100"]], headings=["Champion Name", "Skill"],
                       key="game_dashboard_championstable", size=(100, 30))]
        ]

        return [
            [esm_title_text("TEAMNAME1234567891011121314151617181920\n", key="game_dashboard_teamname")],
            [esm_form_text("Manager: ", font=(bold_font, default_font_size)),
             esm_form_text("Managername12345678", key="game_dashboard_managername")],
            [esm_form_text("Current day: ", font=(bold_font, default_font_size)),
             esm_form_text("2020/01/01", key="game_dashboard_current_day")],
            [sg.TabGroup([
                [sg.Tab('Home', tab_home),
                 sg.Tab('Roster', tab_roster),
                 sg.Tab('Scheduled Matches', tab_scheduled_matches),
                 sg.Tab('Championship Standings', tab_championship),
                 sg.Tab('Champions', tab_game_details)]
            ],
                border_width=0,
                font=(default_font, default_font_size),
            )],
            [esm_button("Next match", size=(15, 2), pad=(None, 80)),
             esm_button("Save game", key="game_dashboard_save"), ],
        ]

