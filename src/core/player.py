class Player:
    def __init__(self, player_id, nationality, first_name, last_name, nick_name, skill):
        self.player_id = player_id

        self.first_name = first_name
        self.last_name = last_name
        self.nick_name = nick_name

        self.nationality = nationality

        # TODO: replace skill by attribute dictionary
        self.skill = skill

        # TODO: players should have a "potential" value too. This value tells the game that the player
        # can improve his overall skill to a certain level

        # Live Match-related variables
        self.champion = None
        self._points = 0
        self.kills = 0
        self.deaths = 0
        self.assists = 0

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, add_pts):
        self._points += add_pts
