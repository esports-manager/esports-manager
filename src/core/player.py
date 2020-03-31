import random

class Player:
    def __init__(self, name, skill):
        self.name = name
        self.skill = skill
        self.champion = None
        
        # TODO: implement country and current team id
        
        # Aggression is a temporary variable
        self.aggression = random.randint(0,100) # generating player aggression for testing purposes
        
        # TODO: implement attribute dictionary
        
        # Live Match-related variables. It will be changed in the future.
        self.kills = 0
        self.deaths = 0
        self.assists = 0
        
    # TODO: implement database-related functions
    def get_from_database(self):
        # This function will get every data from the database
        pass
    
    def get_statistics(self):
        # Gets player statistics from database
        pass
    
    def write_database(self):
        # Will write things on database
        pass