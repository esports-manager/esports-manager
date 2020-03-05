class Team:
    def __init__(self, name, list_players):
        self.name = name
        self.list_players = list_players
        self.advantage = 0
        self.towers = {"top" : 3,
                      "mid" : 3,
                      "bot" : 3,
                      "base" : 2
                      } # lol's turrets
        self.structures = 3 # inhibitors/barracks
