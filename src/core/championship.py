class Championship:
    def __init__(self, name: str, championship_id: int, country: str):
        self.name = name
        self.id = championship_id
        self.country = country

    def __repr__(self):
        return '{0}'.format(self.__class__.__name__)

    def __str__(self):
        return '{0}'.format(self.__class__.__name__)
