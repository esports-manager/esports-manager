class Champion:
    def __init__(self, champion_id: int, name: str, skill: int):
        self.champion_id = champion_id
        self.name = name

        # TODO: champions should belong to different classes such as mages, carries, etc
        # TODO: implement attributes dictionary for skill
        self.skill = skill

    def __repr__(self):
        return '{0} {1}'.format(self.__class__.__name__, self.name)

    def __str__(self):
        return '{0}'.format(self.name)
