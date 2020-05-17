import json
import os
import random

import esm.core.match_live
import esm.core.match
import esm.core.team
import esm.core.player

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))


def read_file(file):
    with open(file, 'r') as fp:
        content = json.load(fp)

    return content


def get_team_from_db(team_id):
    pass


def get_player_from_db(player_id):
    pass
