import random


class Player:
    def __init__(self, id: int) -> None:
        self.units = []
        self.resources = 0
        self.id = id
        self.color = self.random_color()

    def random_color(self):
        return (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )
