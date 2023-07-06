import random


class Player:
    def __init__(self, id: int) -> None:
        self._units = []
        self.resources = 0
        self.id = id
        self.color = self.random_color()

    def random_color(self):
        return (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )

    def get_units(self) -> list:
        return self._units

    def add_unit(self, unit) -> None:
        self._units.append(unit)
    
    def remove_unit(self, unit) -> None:
        self._units.remove(unit)
    
