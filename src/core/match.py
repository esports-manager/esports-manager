from src.core.team import Team
import random


class Match:
    """
    The Match class is used to represent a match, whether they include
    the user's team or not.
    """

    def __init__(self,
                 match_id: int,
                 championship_id: int,
                 team1: Team,
                 team2: Team,
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

    def calculate_both_teams_win_prob(self) -> None:
        total_prob = sum(
            team.player_overall + team.champion_overall + team.points for team in self.teams
        )

        for team in self.teams:
            team.win_prob = (team.player_overall + team.champion_overall + team.points) / total_prob

    def __repr__(self) -> str:
        return '{0} {1}'.format(self.__class__.__name__, self.match_id)

    def __str__(self) -> str:
        return '{0} ID: {1}'.format(self.__class__.__name__, self.match_id)

    def get_speed(self) -> int:
        if self.match_speed == 1:
            return 5
        elif self.match_speed == 2:
            return 10
        elif self.match_speed == 3:
            return 15


if __name__ == '__main__':
    from src.core.match_live import get_match_obj_test

    match = get_match_obj_test()
    match.calculate_both_teams_win_prob()
