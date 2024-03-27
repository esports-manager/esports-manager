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
import json
import os

from .esports.moba.champion import Champion
from .esports.moba.generator import (
    ChampionGenerator,
    TeamGenerator,
    get_default_champion_defs,
)
from .esports.moba.mobaregion import MobaRegion
from .esports.moba.mobateam import MobaTeam
from .esports.moba.player import MobaPlayer
from .gamestate import GameState
from .settings import Settings
from .utils import load_list_from_file


class DB:
    def __init__(self, settings: Settings):
        self.settings = settings

    def generate_moba_champions(self) -> list[Champion]:
        champion_gen = ChampionGenerator()
        try:
            champion_defs = load_list_from_file(self.settings.moba_champion_defs)
        except FileNotFoundError:
            champion_defs = get_default_champion_defs()
        return [champion_gen.generate(champion_def) for champion_def in champion_defs]

    def generate_moba_teams(
        self, champions_list: list[Champion]
    ) -> tuple[list[MobaTeam], list[MobaRegion]]:
        player_names = load_list_from_file(self.settings.names_file)
        team_gen = TeamGenerator(champions_list, player_names)

        regions = self.get_region_definitions()
        moba_regions = []
        teams_list = []
        for region in regions:
            region_teams = []
            teams_def = load_list_from_file(region["filename"])
            for team_def in teams_def:
                team = team_gen.generate(team_def)
                region_teams.append(team)
                teams_list.append(team)
            moba_region = MobaRegion(
                region["id"],
                region["name"],
                region["short_name"],
                region_teams,
            )
            moba_regions.append(moba_region)

        return teams_list, moba_regions

    @staticmethod
    def get_moba_players(teams_list: list[MobaTeam]) -> list[MobaPlayer]:
        players_list = []
        for team in teams_list:
            for player in team.roster:
                players_list.append(player)

        return players_list

    @staticmethod
    def serialize_champions(
        champions_list: list[Champion],
    ) -> dict[int, dict[str, str | list[str]]]:
        return {
            champion.champion_id.int: champion.serialize()
            for champion in champions_list
        }

    @staticmethod
    def serialize_teams(
        teams_list: list[MobaTeam],
    ) -> dict[int, dict[str, str | list[str]]]:
        return {team.team_id.int: team.serialize() for team in teams_list}

    @staticmethod
    def serialize_players(
        players_list: list[MobaPlayer],
    ) -> dict[int, dict[str, str | list[str]]]:
        return {player.player_id.int: player.serialize() for player in players_list}

    @staticmethod
    def serialize_regions(regions_list: list[MobaRegion]) -> dict[str, dict]:
        return {region.region_id: region.serialize() for region in regions_list}

    def generate_moba_teams_file(
        self, serialized_teams: dict[int, dict[str, str | list[str]]]
    ) -> None:
        with open(self.settings.moba_teams, "w") as fp:
            json.dump(serialized_teams, fp, indent=4)

    def generate_moba_champions_file(
        self, serialized_champions: dict[int, dict[str, str | list[str]]]
    ) -> None:
        with open(self.settings.moba_champions, "w") as fp:
            json.dump(serialized_champions, fp, indent=4)

    def generate_moba_players_file(
        self, serialized_players: dict[int, dict[str, str | list[str]]]
    ) -> None:
        with self.settings.moba_players.open("w", encoding="utf-8") as fp:
            json.dump(serialized_players, fp, indent=4)

    def generate_moba_regions_file(self, serialized_regions: dict[str, dict]) -> None:
        with open(self.settings.moba_regions, "w") as fp:
            json.dump(serialized_regions, fp, indent=4)

    def generate_moba_files(
        self,
        champions_list: list[Champion],
        teams_list: list[MobaTeam],
        regions: list[MobaRegion],
        players_list: list[MobaPlayer],
    ) -> None:
        serialized_champions = self.serialize_champions(champions_list=champions_list)
        serialized_teams = self.serialize_teams(teams_list=teams_list)
        serialized_players = self.serialize_players(players_list=players_list)
        serialized_regions = self.serialize_regions(regions_list=regions)

        self.settings.db_dir.mkdir(parents=True, exist_ok=True)
        self.settings.db_moba_dir.mkdir(parents=True, exist_ok=True)

        self.generate_moba_champions_file(serialized_champions)
        self.generate_moba_teams_file(serialized_teams)
        self.generate_moba_players_file(serialized_players)
        self.generate_moba_regions_file(serialized_regions)

    def get_region_definitions(self) -> list[dict[str, str]]:
        regions = load_list_from_file(self.settings.moba_region_defs)

        for region in regions:
            directory = self.settings.moba_team_defs
            filename = region["filename"]
            path = os.path.join(directory, filename)
            region["filename"] = path

        return regions

    def load_moba_teams(self) -> list[MobaTeam]:
        pass

    def get_gamestate(self) -> GameState:
        pass

    def load_from_gamestate(self, gamestate: GameState):
        pass
