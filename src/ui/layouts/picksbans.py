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

import PySimpleGUI as sg
from ..gui_components import *
from .layoutinterface import LayoutInterface


class PicksBansLayout(LayoutInterface):
    def __init__(self, controller):
        super().__init__(controller)
        self.lay = self.layout()
        self.col = self.column()

    def column(self):
        return sg.Column(self.lay,
                         key='debug_picks_bans_screen',
                         visible=False,
                         element_justification="center"
                         )

    def layout(self):
        team_headings = ['Lane', 'Nickname', 'Skill', 'Champion', 'Ch. Skill']

        champion_headings = ['Name', 'Skill', 'Status']

        col_team1 = [
            [esm_form_text('Team1WholeName')],
            [esm_table(values=[
                ['PLAYERLANE', 'PLAYERNICKNAME', 'PLAYERSKILLLEVEL', 'PLAYERCHAMPIONNAME', 'PLAYERCHAMPIONSKILLLEVEL']],
                headings=team_headings, key='pickban_team1_table', num_rows=5)]
        ]

        col_team2 = [
            [esm_form_text('Team2WholeName')],
            [esm_table(values=[
                ['PLAYERLANE', 'PLAYERNICKNAME', 'PLAYERSKILLLEVEL', 'PLAYERCHAMPIONNAME', 'PLAYERCHAMPIONSKILLLEVEL']],
                headings=team_headings, key='pickban_team2_table', num_rows=5)]
        ]

        col_champion = [
            [esm_form_text('Champions')],
            [esm_table(values=[['CHAMPIONWHOLENAME', 'CHAMPIONSKILLLV', 'CHAMPIONSTATUS']], headings=champion_headings,
                       key='pickban_champion_table', num_rows=10)]
        ]

        return [
            [esm_title_text('Picks and Bans')],
            [sg.Column(col_team1)],
            [sg.Column(col_champion)],
            [sg.Column(col_team2)],
            [esm_button('Pick', key='pickban_pick_btn'), esm_button('Cancel', key='pickban_cancel_btn')]
        ]

    def update(self, event, values, make_screen, *args, **kwargs):
        if event == 'pickban_cancel_btn':
            make_screen('debug_picks_bans_screen', 'debug_game_mode_screen')
