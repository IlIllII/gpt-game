from tile import Tile
from action import Action, AttackAction, MoveAction, DieAction, IdleAction, SpawnAction
import random


class Unit:
    def __init__(self) -> None:
        self.alive = True
        self.attack_damage = 0
        self.x = 0
        self.y = 0
        self.player = None
        self.health = 0
        self.max_health = 0
        self.action_range = 0
        self.vision_range = 0
        self.move_cooldown = 0
        self.action_cooldown = 0
        self.bounty = 10
    
    def __str__(self) -> str:
        return f"{__class__}({self.x}, {self.y})"

    def take_turn(self, board) -> tuple[Action, Action]:
        # (Move, Act)
        self.cooldown()
        if not self.is_alive():
            return self.die()
        return (self.move(board), self.act(board))

    def die(self) -> tuple[Action, Action]:
        return (IdleAction(self), DieAction(self))

    def act(self, board) -> Action:
        raise NotImplementedError

    def move(self, board) -> Action:
        raise NotImplementedError

    def cooldown(self) -> None:
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
        if self.action_cooldown > 0:
            self.action_cooldown -= 1

    def can_move(self) -> bool:
        return self.move_cooldown == 0

    def can_act(self) -> bool:
        return self.action_cooldown == 0

    def is_alive(self) -> bool:
        return self.alive

    def move(self, tile: Tile) -> Action:
        return MoveAction(self, tile)

    def in_range(self, tile: Tile, radius: int) -> bool:
        x_distance = abs(self.x - tile.x)
        y_distance = abs(self.y - tile.y)
        if x_distance**2 + y_distance**2 <= radius**2:
            return True
        return False

    def in_action_range(self, tile: Tile) -> bool:
        return self.in_range(tile, self.action_range)

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

    def enemies_in_action_range(self, board) -> list:
        return [
            tile.occupant
            for tile in board.occupied_tiles_in_radius(
                self.x, self.y, self.action_range
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


class Soldier(Unit):
    def __init__(self) -> None:
        super().__init__()
        self.attack_damage = 1
        self.health = 3
        self.max_health = 3
        self.action_range = 3
        self.vision_range = 5
        self.move_cooldown = 1
        self.action_cooldown = 1
        self.bounty = 10
    
    def act(self, board) -> Action:
        enemies = self.enemies_in_action_range(board)
        if len(enemies) > 0:
            return AttackAction(self, enemies[0])
        return IdleAction(self)
    
    def move(self, board) -> Action:
        # enemies = self.enemies_in_sight(board)
        # if len(enemies) > 0:
            # print("Found enemies")
            # return MoveAction(self, enemies[0])
        movable_tiles = self.adjacent_tiles(board)
        random.shuffle(movable_tiles)
        for tile in movable_tiles:
            if not tile.is_occupied():
                return MoveAction(self, tile)
            
        return IdleAction(self)

class Spawner(Unit):
    def __init__(self) -> None:
        super().__init__()
        self.attack_damage = 0
        self.health = 100
        self.max_health = 100
        self.action_range = 2
        self.vision_range = 3
        self.move_cooldown = 1
        self.action_cooldown = 1
        self.bounty = 100
    
    def act(self, board) -> Action:
        if self.can_act():
            adjacent_tiles = self.adjacent_tiles(board)
            random.shuffle(adjacent_tiles)
            for tile in adjacent_tiles:
                if not tile.is_occupied():
                    unit = Soldier()
                    unit.player = self.player
                    return SpawnAction(unit, tile)
        return IdleAction(self)
    
    def move(self, board) -> Action:
        return IdleAction(self)