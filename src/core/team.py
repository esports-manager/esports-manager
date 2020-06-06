class Team:
    def __init__(self, team_id, name, list_players):
        """
        Initiates the team object.

        Arguments:
            name {string} -- team name.
            list_players {list<Player>} -- list of players
        """
        self.team_id = team_id
        self.name = name

        # list of all players in the roster
        self.list_players = list_players

    def get_avg_skill(self):
        # TODO: there should be a check whether the player is playing the match or not, to avoid messing up this list
        avg = 0
        for player in self.list_players:
            avg = player.skill + avg

        avg = avg / len(self.list_players)

        return avg
