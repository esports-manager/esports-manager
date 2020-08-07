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
                 team2: Team):
        """
        Initializes elements of the match
        :param match_id: match ID
        :param championship_id: championship ID to which the match belongs
        :param team1: first team (blue side/radiant)
        :param team2: second team (red side/dire)
        """
        self.match_id = match_id
        self.championship_id = championship_id
        self.team1 = team1
        self.team2 = team2
        self.teams = [self.team1, self.team2]

    def __repr__(self) -> str:
        return '{0} {1}'.format(self.__class__.__name__, self.match_id)

    def __str__(self) -> str:
        return '{0} ID: {1}'.format(self.__class__.__name__, self.match_id)


if __name__ == '__main__':
    from src.core.match_live import get_live_obj_test

    match = get_live_obj_test()
    match.calculate_both_teams_win_prob()
