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

import os
import json
import random

from ..utils import write_to_json


# THIS FILE HAS THE SOLE PURPOSE OF GENERATING A JSON FILE
# WITH CHAMPION NAMES AND RANDOM SKILL LEVELS

champion_names = [
    "AATROX",
    "AHRI",
    "AKALI",
    "ALISTAR",
    "AMUMU",
    "ANIVIA",
    "ANNIE",
    "APHELIOS",
    "ASHE",
    "AURELION SOL",
    "AZIR",
    "BARD",
    "BLITZCRANK",
    "BRAND",
    "BRAUM",
    "CAITLYN",
    "CAMILLE",
    "CASSIOPEIA",
    "CHO'GATH",
    "CORKI",
    "DARIUS",
    "DIANA",
    "DR. MUNDO",
    "DRAVEN",
    "EKKO",
    "ELISE",
    "EVELYNN",
    "EZREAL",
    "FIDDLESTICKS",
    "FIORA",
    "FIZZ",
    "GALIO",
    "GANGPLANK",
    "GAREN",
    "GNAR",
    "GRAGAS",
    "GRAVES",
    "HECARIM",
    "HEIMERDINGER",
    "ILLAOI",
    "IRELIA",
    "IVERN",
    "JANNA",
    "JARVAN IV",
    "JAX",
    "JAYCE",
    "JHIN",
    "JINX",
    "KAI'SA",
    "KALISTA",
    "KARMA",
    "KARTHUS",
    "KASSADIN",
    "KATARINA",
    "KAYLE",
    "KAYN",
    "KENNEN",
    "KHA'ZIX",
    "KINDRED",
    "KLED",
    "KOG'MAW",
    "LEBLANC",
    "LEE SIN",
    "LEONA",
    "LISSANDRA",
    "LILIA",
    "LUCIAN",
    "LULU",
    "LUX",
    "MALPHITE",
    "MALZAHAR",
    "MAOKAI",
    "MASTER YI",
    "MISS FORTUNE",
    "MORDEKAISER",
    "MORGANA",
    "NAMI",
    "NASUS",
    "NAUTILUS",
    "NEEKO",
    "NIDALEE",
    "NOCTURNE",
    "NUNU & WILLUMP",
    "OLAF",
    "ORIANNA",
    "ORNN",
    "PANTHEON",
    "POPPY",
    "PYKE",
    "QIYANA",
    "QUINN",
    "RAKAN",
    "RAMMUS",
    "REK'SAI",
    "RENEKTON",
    "RENGAR",
    "RIVEN",
    "RUMBLE",
    "RYZE",
    "SEJUANI",
    "SENNA",
    "SETT",
    "SHACO",
    "SHEN",
    "SHYVANA",
    "SINGED",
    "SION",
    "SIVIR",
    "SKARNER",
    "SONA",
    "SORAKA",
    "SWAIN",
    "SYLAS",
    "SYNDRA",
    "TAHM KENCH",
    "TALIYAH",
    "TALON",
    "TARIC",
    "TEEMO",
    "THRESH",
    "TRISTANA",
    "TRUNDLE",
    "TRYNDAMERE",
    "TWISTED FATE",
    "TWITCH",
    "UDYR",
    "URGOT",
    "VARUS",
    "VAYNE",
    "VEIGAR",
    "VEL'KOZ",
    "VI",
    "VIKTOR",
    "VLADIMIR",
    "VOLIBEAR",
    "WARWICK",
    "WUKONG",
    "XAYAH",
    "XERATH",
    "XIN ZHAO",
    "YASUO",
    "YORICK",
    "YONE",
    "YUUMI",
    "ZAC",
    "ZED",
    "ZIGGS",
    "ZILEAN",
    "ZOE",
    "ZYRA"
]


def generate_champion_dict(champion_name: str, counter: int) -> dict:
    if champion_name == "TEEMO":
        skill = random.randint(0, 50)
    else:
        skill = random.randint(50, 99)

    return {"name": champion_name,
            "id": counter,
            "skill": skill
            }


def create_champions_list() -> list:
    list_champions = []
    for counter, champion_name in enumerate(champion_names):
        champion = generate_champion_dict(champion_name, counter)
        list_champions.append(champion)
    return list_champions


def generate_champion_file() -> None:
    list_of_champions = create_champions_list()
    write_to_json(list_of_champions, 'champions.json')
