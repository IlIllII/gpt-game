from tile import Tile
from action import Action, AttackAction, MoveAction


class Unit:
    def __init__(self) -> None:
        self.alive = True
        self.attack_damage = 0
        self.x = 0
        self.y = 0
        self.player = None
        self.health = 0
        self.max_health = 0
        self.attack_range = 0
        self.vision_range = 0

    def act(self, board) -> Action:
        raise NotImplementedError

    def is_alive(self) -> bool:
        return self.alive

    def attack(self, tile: Tile) -> Action:
        if not self.in_range(tile):
            raise Exception("Tile not in range")
        if not tile.is_occupied():
            raise Exception("Tile not occupied")
        if tile.occupant.player == self.player:
            # TODO: friendly fire?
            raise Exception("Tile occupied by friendly unit")

        return AttackAction(self, tile)

    def move(self, tile: Tile) -> Action:
        if not self.in_range(tile, 1):
            raise Exception("Tile not in range")
        if tile.is_occupied():
            raise Exception("Tile occupied")
        if tile.get_rubble() > 0:
            raise Exception("Tile blocked by rubble")

        return MoveAction(self, tile)

    def in_range(self, tile: Tile, radius: int) -> bool:
        x_distance = abs(self.x - tile.x)
        y_distance = abs(self.y - tile.y)
        if x_distance**2 + y_distance**2 <= radius**2:
            return True
        return False

    def in_attack_range(self, tile: Tile) -> bool:
        return self.in_range(tile, self.attack_range)

    def in_vision_range(self, tile: Tile) -> bool:
        return self.in_range(tile, self.vision_range)

    def adjacent_tiles(self, board) -> list:
        return board.tiles_in_radius(self.x, self.y, 1)

    def adjacent_occupied_tiles(self, board) -> list:
        return board.occupied_tiles_in_radius(self.x, self.y, 1)

    def enemies_in_sight(self, board) -> list:
        return [
            tile.occupant
            for tile in board.occupied_tiles_in_radius(
                self.x, self.y, self.vision_range
            )
            if tile.occupant.player != self.player
        ]

    def enemies_in_attack_range(self, board) -> list:
        return [
            tile.occupant
            for tile in board.occupied_tiles_in_radius(
                self.x, self.y, self.attack_range
            )
            if tile.occupant.player != self.player
        ]

    def allies_in_sight(self, board) -> list:
        return [
            tile.occupant
            for tile in board.occupied_tiles_in_radius(
                self.x, self.y, self.vision_range
            )
            if tile.occupant.player == self.player
        ]
