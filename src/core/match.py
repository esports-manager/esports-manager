import random
import time


class Match:
    """
    The Match class is used to simulate the match that is going to be
    played by the user.
    """

    def __init__(self, id, championship_id, team1, team2, show_commentary, match_speed):
        """
        Initiates the elements of the Match class.

        Arguments:
            id {integer} -- match ID. should be unique
            championship_id {integer} -- championship ID. should be unique
            team1 {Team} -- object of the first team drawn from the database
            team2 {Team} -- object of the second team drawn from the database
            elapsed_time {float} -- stores the elapsed time
            firstblood {boolean} -- boolean that tells whether someone has drawn first blood
            victorious_team {Team} -- stores which team won the match
            show_commentary {boolean} -- whether or not to show live game commentary
            match_speed {int} -- fast (1), normal (2), slow (3) -> affects elapsed_time
            is_match_over {boolean} -- if True: terminates the match loop
        """
        self.id = id
        self.championship_id = championship_id
        self.team1 = team1
        self.team2 = team2
        self.elapsed_time = 0.0
        self.firstblood = False
        self.victorious_team = None
        self.show_commentary = show_commentary
        self.match_speed = match_speed
        self.is_match_over = False

    def picks_and_bans(self):
        # TODO: write a proper picks and bans phase
        # Placeholder picks and bans for testing
        self.team1.formation = {
            "top": self.team1.list_players[0],
            "jun": self.team1.list_players[1],
            "mid": self.team1.list_players[2],
            "bot": self.team1.list_players[3],
            "sup": self.team1.list_players[4],
        }
        self.team2.formation = {
            "top": self.team1.list_players[0],
            "jun": self.team1.list_players[1],
            "mid": self.team1.list_players[2],
            "bot": self.team1.list_players[3],
            "sup": self.team1.list_players[4],
        }

    # I'm not entirely sure that this is the way to go
    # But as I'm coding, I will see if this number of event methods
    # Is useful
    def event_team_fight(self, num_players):
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

    def event_kill(self, num_kills):
        pass

    def event_invade(self):
        pass

    def calculate_event(self):
        # TODO: give each event a unique value
        pass

    def match_live(self):
        # Start pick and ban phase
        self.picks_and_bans()

        # Time counter, used for measuring the elapsed time
        start_time = time.time()
        # converts elapsed time into match time
        game_time = 0.0

        print("Match Speed: ", self.match_speed)
        
        while self.is_match_over == False:
            self.elapsed_time = time.time() - start_time
            
            if self.match_speed == 3:
                # SLOW Match Speed
                game_time = self.elapsed_time * 10
            elif self.match_speed == 2: 
                # NORMAL Match Speed
                game_time = self.elapsed_time * 100
            else:
                # FAST Match Speed
                game_time = self.elapsed_time * 1000
            
            print("Elapsed time: ",self.elapsed_time)
            print("Game time: ", game_time)
            
            if(game_time > 5000):
                self.is_match_over = True
                