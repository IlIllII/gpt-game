class Tile:
    def __init__(self, x: int, y: int, rubble: int, resource: int) -> None:
        self.x = x
        self.y = y
        self.rubble = rubble
        self.resource = resource
        self.occupant = None

    def __str__(self) -> str:
        return f"Tile(({self.x}, {self.y}), {self.rubble}, {self.resource})"

    def is_occupied(self):
        return self.occupant is not None
    
    def __hash__(self) -> int:
        return hash((self.x, self.y))