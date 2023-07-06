from tile import Tile
from unit import Unit


class Board:
    def __init__(self, rubble: list[list[int]], resource: list[list[int]]) -> None:
        assert len(rubble) == len(resource)
        for i in range(len(rubble)):
            assert len(rubble[i]) == len(resource[i])
        self.tiles = []
        for i in range(len(rubble)):
            row = []
            for j in range(len(rubble[i])):
                row.append(Tile(j, i, rubble[i][j], resource[i][j]))
            self.tiles.append(row)

    def width(self) -> int:
        return len(self.tiles[0])

    def height(self) -> int:
        return len(self.tiles)

    def get_tile(self, x: int, y: int) -> Tile:
        return self.tiles[y][x]

    def is_occupied(self, x: int, y: int) -> bool:
        return self.tiles[y][x].occupant is not None

    def get_occupant(self, x: int, y: int) -> Unit:
        return self.tiles[y][x].occupant

    def set_occupant(self, x: int, y: int, unit: Unit) -> None:
        if self.is_occupied(x, y):
            raise Exception("Tile already occupied")
        self.tiles[y][x].occupant = unit

    def remove_occupant(self, x: int, y: int) -> None:
        if not self.is_occupied(x, y):
            raise Exception("Tile not occupied")
        self.tiles[y][x].occupant = None

    def get_rubble(self, x: int, y: int) -> int:
        rubble = self.tiles[y][x].rubble
        if not 0 < rubble <= 5:
            raise Exception(f"Invalid rubble: {rubble}")
        return self.tiles[y][x].rubble

    def get_resource(self, x: int, y: int) -> int:
        return self.tiles[y][x].resource

    def tiles_in_radius(self, x: int, y: int, radius: int) -> list:
        tiles = []
        radius_squared = radius**2
        for i in range(-radius, radius + 1):
            for j in range(-radius, radius + 1):
                if i == 0 and j == 0:
                    continue
                if (
                    x + i >= 0
                    and x + i < self.width()
                    and y + j >= 0
                    and y + j < self.height()
                ):
                    if i**2 + j**2 <= radius_squared:
                        tiles.append(self.get_tile(x + i, y + j))
        return tiles

    def occupied_tiles_in_radius(self, x: int, y: int, radius: int) -> list:
        tiles = []
        for tile in self.tiles_in_radius(x, y, radius):
            if tile.occupant is not None:
                tiles.append(tile)
        return tiles

    def resource_tiles_in_radius(self, x: int, y: int, radius: int) -> list:
        tiles = []
        for tile in self.tiles_in_radius(x, y, radius):
            if tile.resource > 0:
                tiles.append(tile)
        return tiles

    def __str__(self) -> str:
        return str(self.tiles)
