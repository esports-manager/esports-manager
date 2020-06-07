class Champion:
    def __init__(self, champion_id, name, skill):
        self.champion_id = champion_id
        self.name = name

        # TODO: champions should belong to different classes such as mages, carries, etc
        # TODO: implement attributes dictionary for skill
        self.skill = skill
