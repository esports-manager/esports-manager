import random
import time


class Match:
    """
    The Match class is used to simulate matches, whether they include
    the user's team or not.
    """

    def __init__(self, id, championship_id, team1, team2, show_commentary, match_speed):
        """
        Initiates the elements of the Match class.

        Arguments:
            id {integer} -- match ID. should be unique
            championship_id {integer} -- championship ID. should be unique
            team1 {Team} -- object of the first team drawn from the database
            team2 {Team} -- object of the second team drawn from the database
            game_time {float} -- stores the current game time
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
        self.game_time = 0.0
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
        
    def event_team_fight(self, players_atk, players_def):
        pass

    def event_major_jungle(self, players_atk, jg_monster):
        pass

    def event_minor_jungle(self, players_atk, jg_monster):
        pass

    def event_gank(self, players_atk, players_def):
        pass

    def event_tower_assault(self, players_atk, players_def):
        pass

    def event_barracks_assault(self, players_atk, players_def):
        pass

    def event_nexus_assault(self, players_atk, players_def):
        pass

    def event_kill(self, num_kills, player_kill, player_assist, players_killed):
        pass

    def event_invade(self, players_atk, players_def):
        # TODO: Define commentary as Invade, and improve what happens here
        self.event_team_fight(players_atk, players_def)
    
    def decide_aggressive_team(self):
        if (self.game_time == 0.0):
            team1_aggr = self.team1.get_team_aggr()
            team2_aggr = self.team2.get_team_aggr()
            
            # Calculates what is the likelihood in percentage
            # that each team will get aggressive in the early game
            if (team1_aggr != team2_aggr):
                factor = team1_aggr - team2_aggr
                factor = float(factor/100.00)
            else:
                factor = 0.5 # equal likelihood for both teams
            
            prob = random.gauss(0.0,1.0)
            if (factor > 0.0):
                if (prob > factor): # team1 does not get aggressive
                    pass
                else:
                    self.event_invade(self.team1.list_players, self.team2.list_players) # team fight happens
            elif (factor < 0.0):
                if (prob > factor):
                    self.event_invade(self.team2.list_players, self.team1.list_players)
                else:
                    pass
            else:
                alternatives = [1,2,3]
                choice = random.choice(alternatives)
                if (choice == 1):
                    self.event_invade(self.team1.list_players, self.team2.list_players)
                elif (choice == 2):
                    self.event_invade(self.team2.list_players, self.team1.list_players)
                else:
                    pass
                
                # TODO: substitute "pass" with relevant events to start early game without fight
        
    
    def calculate_event(self):
        """
        This method is used to calculate which events are going to be triggered
        in the match
        """
        print(self.game_time) # Debugging
        
        if (self.game_time == 0.0):
            team1_aggr = self.team1.get_team_aggr()
            team2_aggr = self.team2.get_team_aggr()
            
            # Calculates what is the likelihood in percentage
            # that each team will get aggressive in the early game
            if (team1_aggr != team2_aggr):
                factor = team1_aggr - team2_aggr
                factor = float(factor/100.00)
            else:
                factor = 0.5 # equal likelihood for both teams
            
            prob = random.gauss(0.0,1.0)
            if (factor > 0.0):
                if (prob > factor): # team1 does not get aggressive
                    pass
                else:
                    self.event_team_fight(self.team1.list_players, self.team2.list_players) # team fight happens
            elif (factor < 0.0):
                if (prob > factor):
                    self.event_team_fight(self.team2.list_players, self.team1.list_players)
                else:
                    pass
            else:
                alternatives = [1,2,3]
                choice = random.choice(alternatives)
                if (choice == 1):
                    self.event_team_fight(self.team1.list_players, self.team2.list_players)
                elif (choice == 2):
                    self.event_team_fight(self.team2.list_players, self.team1.list_players)
                else:
                    pass
                
                # TODO: substitute "pass" with relevant events to start early game without fight
                
        elif (self.game_time <= 3.0):
            pass
        elif (self.game_time <= 10.0):
            pass
        elif (self.game_time <= 20.0):
            pass
        elif (self.game_time <= 30.0):
            pass
        elif (self.game_time <= 40.0):
            pass
        else:
            pass
    
    def get_time(self):
        """This method is used to iterate over the game time.
        
        Returns:
            game_time {float} -- the calculated game_time
        """
        if (self.game_time == 0):
            pass
        elif (self.game_time <= 10):
            pass
        elif (self.game_time <= 20):
            pass
        elif (self.game_time <= 30):
            pass
        elif (self.game_time <= 40):
            pass
        else:
            pass
        
        self.game_time += 1

    def match_live(self):
        # Start pick and ban phase
        self.picks_and_bans()
        
        # Live Match loop
        # Should probably be asynchronous
        while(self.is_match_over == False):
            
            # Just testing
            if (self.game_time >= 10.00):
                self.is_match_over = True
            
            # Get match speed values, can be improved in the future
            # TODO: Substitute each delay value by a constant defined in a Settings file
            if (self.match_speed == 4): # REAL TIME SPEED
                delay = 30
            if (self.match_speed == 3): # SLOW SPEED
                delay = 15
            elif (self.match_speed == 2): # NORMAL SPEED
                delay = 5
            else: # FAST SPEED
                delay = 1
            
            # Calculate probabilities according to the self.game_time
            self.calculate_event()
            
            # Gets the self.game_time for next iteration
            self.get_time()
            
            # Waits the a 'delay' number of seconds until next iteration,
            # making calculations take a little while according to the Match_Speed
            time.sleep(delay)
            