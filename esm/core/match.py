class Match:
    """
    The Match class is used to represent a match, whether they include
    the user's team or not.
    """

    def __init__(self, match_id, championship_id, team1, team2, show_commentary, match_speed):
        """
        Initiates the elements of the Match class.

        Arguments:
            id {integer} -- match ID. should be unique
            championship_id {integer} -- championship ID. should be unique
            team1 {Team} -- object of the first team drawn from the database
            team2 {Team} -- object of the second team drawn from the database
            game_time {float} -- stores the current game time
            first_blood {boolean} -- boolean that tells whether someone has drawn first blood
            victorious_team {Team} -- stores which team won the match
            show_commentary {boolean} -- whether or not to show live game commentary (for user's matches only)
            match_speed {int} -- fast (1), normal (2), slow (3) -> affects elapsed_time
            is_match_over {boolean} -- if True: terminates the match loop
        """
        self.id = match_id
        self.championship_id = championship_id
        self.team1 = team1
        self.team2 = team2
        self.game_time = 0.0
        self.first_blood = False
        self.victorious_team = None
        self.show_commentary = show_commentary
        self.match_speed = match_speed
        self.is_match_over = False
