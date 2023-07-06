class Tile:
    def __init__(self, x: int, y: int, rubble: int, resource: int) -> None:
        self.x = x
        self.y = y
        self.rubble = rubble
        self.resource = resource
        self.occupant = None

    def __str__(self) -> str:
        return f"Tile(({self.x}, {self.y}), {self.rubble}, {self.resource})"
