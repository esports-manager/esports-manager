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

        # list of all players in the roster
        self.list_players = list_players

    def is_tower_up(self, lane) -> bool:
        if self.towers[lane] == 0:
            return False
        else:
            return True

    def are_all_towers_up(self) -> bool:
        for lane, num in self.towers.items():
            if num == 0:
                return False

        return True

    def is_inhibitor_up(self, lane) -> bool:
        if self.inhibitors[lane] == 0:
            return False
        else:
            return True

    def are_all_inhibitors_up(self) -> bool:
        for lane, num in self.inhibitors.items():
            if num == 0:
                return False

        return True

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
        # TODO: there should be a check whether the player is playing the match or not, to avoid messing up this list
        self._player_overall = 0
        skill_list = []
        for player in self.list_players:
            skill_list.append(player.skill)

        highest_rated = max(skill_list)

        for skill in skill_list:
            self._player_overall = (skill * (skill/highest_rated)) + self._player_overall

        self._player_overall = int(self._player_overall / len(self.list_players))

        return self._player_overall

    @property
    def champion_overall(self) -> int:
        self._avg_champion_skill = 0
        for player in self.list_players:
            self._avg_champion_skill += player.champion.skill

        self._avg_champion_skill = int(self._avg_champion_skill / len(self.list_players))

        return self._avg_champion_skill
