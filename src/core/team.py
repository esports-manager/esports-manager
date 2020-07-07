class Team:
    def __init__(self, team_id, name, list_players):
        """
        Initiates the team object.

        Arguments:
            name {string} -- team name.
            list_players {list<Player>} -- list of players
        """
        self._points = 0
        self.team_id = team_id
        self.name = name

        self.towers = {
            "top": 3,
            "mid": 3,
            "bot": 3,
            "base": 2
        }
        self.inhibitors = {
            "top": 1,
            "mid": 1,
            "bot": 1
        }

        self.win_prob = 0

        # list of all players in the roster
        self.list_players = list_players

        self._player_overall = 0
        self._champion_overall = 0

    def is_tower_up(self, lane: str) -> bool:
        return self.towers[lane] != 0

    def are_all_towers_up(self) -> bool:
        return 0 not in self.towers.values()

    def is_inhibitor_up(self, lane: str) -> bool:
        return self.inhibitors[lane] != 0

    def are_all_inhibitors_up(self) -> bool:
        return 0 not in self.inhibitors.values()

    @property
    def points(self) -> int:
        self._points = 0
        for player in self.list_players:
            self._points += player.points

        return self._points

    @property
    def player_overall(self) -> int:
        """
        This method is calculating team's overall
        :return:
        """
        self._player_overall = 0

        skill_list = []
        for player in self.list_players:
            skill_list.append(player.skill)

        for skill in skill_list:
            self._player_overall += skill

        self._player_overall = int(self._player_overall / len(self.list_players))

        return self._player_overall

    @property
    def champion_overall(self) -> int:
        self._champion_overall = 0

        for player in self.list_players:
            self._champion_overall += player.champion.skill

        self._champion_overall = int(self._champion_overall / len(self.list_players))

        return self._champion_overall
