class Team:
    def __init__(self, name, list_players):
        self.name = name
        self.list_players = list_players
        self.advantage_points = 0
        # defining towers
        self.towers = {"top" : 3,
                      "mid" : 3,
                      "bot" : 3,
                      "base" : 2
                      } # lol's turrets
        self.barracks = 3 # inhibitors/barracks
        # formation will be changed in the future
        # right now it only accepts formation as defined in lol matches
        # but in the future moba manager will support different strategies
        # so you can create your own moba
        # the formation is set up in picks and bans
        self.formation = {"top" : None, "jun" : None, "mid" : None, "bot" : None, "sup" : None}
