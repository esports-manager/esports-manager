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

    @property
    def avg_player_skill(self):
        # TODO: there should be a check whether the player is playing the match or not, to avoid messing up this list
        self._avg_player_skill = 0
        for player in self.list_players:
            self._avg_player_skill += player.skill

        self._avg_player_skill = self._avg_player_skill / len(self.list_players)

        return self._avg_player_skill

    @property
    def avg_champion_skill(self):
        self._avg_champion_skill = 0
        for player in self.list_players:
            self._avg_champion_skill += player.champion.skill

        self._avg_champion_skill = self._avg_champion_skill / len(self.list_players)

        return self._avg_champion_skill
