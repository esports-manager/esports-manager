from .champion import Champion


class Player:
    def __init__(self,
                 player_id: int,
                 nationality: str,
                 first_name: str,
                 last_name: str,
                 nick_name: str,
                 skill: int):
        self.player_id = player_id

        self.first_name = first_name
        self.last_name = last_name
        self.nick_name = nick_name

        self.nationality = nationality

        # TODO: replace skill by attribute dictionary
        self._skill = skill

        # TODO: players should have a "potential" value too. This value tells the game that the player
        # can improve his overall skill to a certain level

    @property
    def skill(self):
        return self._skill

    @skill.setter
    def skill(self, skill):
        self._skill = skill
        return self._skill


class MobaPlayer(Player):
    def __init__(self,
                 player_id: int,
                 nationality: str,
                 first_name: str,
                 last_name: str,
                 nick_name: str,
                 skill: int):
        self._champion = None
        self._kills = 0
        self._deaths = 0
        self._assists = 0
        self._points = 0
        super().__init__(player_id, nationality, first_name, last_name, nick_name, skill)

    @property
    def champion(self):
        return self._champion

    @property
    def kills(self):
        return self._kills

    @property
    def deaths(self):
        return self._deaths

    @property
    def assists(self):
        return self._assists

    @property
    def points(self):
        return self._points

    @champion.setter
    def champion(self, champion: Champion):
        self._champion = champion

    @kills.setter
    def kills(self, kills: int):
        self._kills = kills

    @assists.setter
    def assists(self, assists: int):
        self._assists = assists

    @points.setter
    def points(self, add_pts: int):
        self._points += add_pts

    def __repr__(self):
        return '{0} {1}'.format(self.__class__.__name__, self.nick_name)

    def __str__(self):
        return '{0}'.format(self.nick_name)
