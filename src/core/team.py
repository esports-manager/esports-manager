class Team:
    def __init__(self, name, list_players):
        """
        Initiates the team object.

        Arguments:
            name {string} -- team name.
            list_players {List<Player>} -- list of players
        """
        self.name = name
        self.list_players = list_players

        # Points are awarded each time the team gets a kill
        # an assist or a major objective
        self.points = 0
        self.towers = {"top": 3, "mid": 3, "bot": 3, "base": 2}  # lol's turrets
        self.barracks = {"top": 1, "mid": 1, "bot": 1}

        # Formation will be changed in the future
        # right now it only accepts formation as defined in lol matches
        # but in the future moba manager will support different strategies
        # so you can create your own moba
        # The formation is set up in picks and bans
        self.formation = {
            "top": None,
            "jun": None,
            "mid": None,
            "bot": None,
            "sup": None,
        }
