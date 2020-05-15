class Player:
    def __init__(self, player_id, nationality, name, nick_name, skill):
        self.player_id = player_id

        self.name = name
        self.nick_name = nick_name

        self.nationality = nationality

        # TODO: replace skill by attribute dictionary
        self.skill = skill

        # Live Match-related variables. It will be changed in the future.
        self.champion = None
        self.kills = 0
        self.deaths = 0
        self.assists = 0
