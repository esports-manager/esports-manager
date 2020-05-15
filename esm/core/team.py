class Team:
    def __init__(self, name, list_players):
        """
        Initiates the team object.

        Arguments:
            name {string} -- team name.
            list_players {list<Player>} -- list of players
        """
        self.name = name
        self.list_players = list_players
