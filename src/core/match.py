import random

class Match:
    """
    The Match class is used to represent a match, whether they include
    the user's team or not.
    """

    def __init__(self,
                 match_id: int,
                 championship_id: int,
                 team1: "Team",
                 team2: "Team",
                 show_commentary: bool,
                 match_speed: int):
        """
        Initializes elements of the match
        :param match_id: match ID
        :param championship_id: championship ID to which the match belongs
        :param team1: first team (blue side/radiant)
        :param team2: second team (red side/dire)
        :param show_commentary: True or False to show match live commentary
        :param match_speed: defines the speed with which match live commentary will be shown
        """

        self.match_id = match_id
        self.championship_id = championship_id
        self.team1 = team1
        self.team2 = team2
        self.teams = [self.team1, self.team2]
        self.game_time = 0.0
        self.first_blood = False
        self.victorious_team = None
        self.show_commentary = show_commentary
        self.match_speed = match_speed
        self.is_match_over = False

    def event_team_fight(self, atk_team, def_team):
        prob = random.gauss(0, 1)

        duel_pl_factor = atk_team.avg_player_skill / def_team.avg_player_skill
        duel_ch_factor = atk_team.avg_champion_skill / def_team.avg_champion_skill

        # TODO: FINISH THIS LOGIC FOR TEAM FIGHT

    def event_invade(self):
        prob = random.gauss(0, 1)
        if prob > 1:
            print("{} decides to invade!".format(self.team1))
        elif prob < -1:
            print("{} decides to invade!".format(self.team2))
        else:
            print("Teams are starting passively this game!")
