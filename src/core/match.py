import numpy as np

from .champion import Champion
from .player import Player
from .team import Team
from .patch import Patch

class Match:
    """
    The Match class is used to simulate the match that is going to be
    played by the user.
    """
    def __init__(self, id, championship_id, team1, team2):
        """
        Initiates the elements of the Match class.
        
        Arguments:
            id {integer} -- match ID. should be unique
            championship_id {integer} -- championship ID. should be unique
            team1 {Team} -- object of the first team drawn from the database
            team2 {Team} -- object of the second team drawn from the database
            time {float} -- stores the elapsed time
            firstblood {boolean} -- boolean that tells whether someone has drawn first blood
            victorious_team {Team} -- stores which team won the match
        """
        self.id = id
        self.championship_id = championship_id
        self.team1 = team1
        self.team2 = team2
        self.time = 0
        self.firstblood = False
        self.victorious_team = None
        
    def picks_and_bans(self):
        # Placeholder picks and bans for testing
        self.team1.formation = {"top": self.team1.list_players[0],
        "jun": self.team1.list_players[1], "mid": self.team1.list_players[2], "bot": self.team1.list_players[3], "sup": self.team1.list_players[4]}
        self.team2.formation = {"top": self.team1.list_players[0],
        "jun": self.team1.list_players[1], "mid": self.team1.list_players[2], "bot": self.team1.list_players[3], "sup": self.team1.list_players[4]}
    
    # I'm not entirely sure that this is the way to go
    # But as I'm coding, I will see if this number of event methods
    # is the way to go
    def event_team_fight(self):
        pass

    def event_major_jungle(self):
        pass

    def event_minor_jungle(self):
        pass

    def event_gank(self):
        pass

    def event_tower_assault(self):
        pass

    def event_barracks_assault(self):
        pass
    
    def event_nexus_assault(self):
        pass

    def event_kill(self):
        pass

    def event_invade(self):
        pass

    def calculate_event(self, event_name):
        # TODO: give each event a unique value
        pass
    
    def match_live(self):
        self.is_match_over = False
        self.picks_and_bans()

        self.team1.advantage_points = 0
        self.team2.advantage_points = 0
        self.time = 0

        while(self.is_match_over == False):
            # TODO: Values of time should vary with VERBOSE
            # VERBOSE will be a parameter that
            # changes how much info is printed to the user
            if(time > 0 and time < 200):
                # early game aggression
                # TODO: implement a way of deciding team aggression
                pass
            elif(time >= 200 and time < 1500):
                # early to mid game decisions
                pass
            elif(time >= 1500 and time < 2000):
                # mid to late game preparation
                pass
            elif(time >= 2000):
                # going to late game
                pass
            time += 10
