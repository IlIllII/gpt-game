from tile import Tile
from action import Action, AttackAction, MoveAction, DieAction, IdleAction, SpawnAction
import random
from math import sqrt
from queue import PriorityQueue
import time
from copy import deepcopy


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
        self.move_cooldown = 1
        self.action_cooldown = 1
        self.bounty = 10

    def __str__(self) -> str:
        return f"{__class__}({self.x}, {self.y})"

    def take_turn(self, board) -> tuple[Action, Action]:
        # (Move, Act)
        self.cooldown()
        if not self.is_alive():
            return self.die()
        if self.can_move():
            move_action = self.move(board)
        else:
            move_action = IdleAction(self)
        if self.can_act():
            act_action = self.act(board)
        else:
            act_action = IdleAction(self)
        return (move_action, act_action)

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
        return board.tiles_in_radius(self.x, self.y, 1.5)

    def adjacent_occupied_tiles(self, board) -> list:
        return board.occupied_tiles_in_radius(self.x, self.y, 1.5)

    def enemies_in_sight(self, board) -> list:
        return [
            tile.occupant
            for tile in board.occupied_tiles_in_radius(
                self.x, self.y, self.vision_range
            )
            if tile.occupant.player != self.player and tile.occupant.is_alive()
        ]

    def enemies_in_action_range(self, board) -> list:
        return [
            tile.occupant
            for tile in board.occupied_tiles_in_radius(
                self.x, self.y, self.action_range
            )
            if tile.occupant.player != self.player and tile.occupant.is_alive()
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
        self.action_range = 4
        self.vision_range = 6
        self.move_cooldown = 2
        self.action_cooldown = 2
        self.bounty = 10

    def act(self, board) -> Action:
        enemies = self.enemies_in_action_range(board)
        if len(enemies) > 0:
            return AttackAction(self, enemies[0])
        return IdleAction(self)

    def move(self, board) -> Action:
        movable_tiles = self.adjacent_tiles(board)
        random.shuffle(movable_tiles)
        for tile in movable_tiles:
            if not tile.is_occupied():
                return MoveAction(self, tile)

        return IdleAction(self)


class QueueItem:
    def __init__(self, cost, tile):
        self.cost = cost
        self.tile = tile

    def __lt__(self, other):
        return self.cost < other.cost


class Soldier1(Soldier):
    def move(self, board) -> Action:
        if not self.can_move():
            return IdleAction(self)

        enemies = self.enemies_in_sight(board)
        if len(enemies) > 0:
            closest_enemy = min(enemies, key=lambda enemy: self.distance_to(enemy))
            came_from, start, goal = self.astar_path(
                (self.x, self.y), (closest_enemy.x, closest_enemy.y), board
            )
            path = self.reconstruct_path(came_from, start, goal)
            if path and len(path) > 1:
                if path[1].is_occupied():
                    return IdleAction(self)
                return MoveAction(
                    self, path[1]
                )  # Moving to the second tile in the path, as the first one is the current location of the unit

        movable_tiles = self.adjacent_tiles(board)
        random.shuffle(movable_tiles)
        for tile in movable_tiles:
            if not tile.is_occupied():
                return MoveAction(self, tile)

        return IdleAction(self)

        return IdleAction(self)

    def astar_path(self, start, goal, board):
        frontier = PriorityQueue()
        start_tile = board.get_tile(start[0], start[1])
        frontier.put(QueueItem(0, start_tile))
        came_from = {start_tile: None}
        cost_so_far = {start_tile: 0}

        while not frontier.empty():
            current = frontier.get().tile

            if (current.x, current.y) == goal:
                if current not in came_from:
                    came_from[
                        current
                    ] = current  # Add the goal tile to the came_from dictionary
                break

            for next_tile in board.tiles_in_radius(current.x, current.y, 1):
                if next_tile.is_occupied() and (next_tile.x, next_tile.y) != goal:
                    continue

                new_cost = cost_so_far[current] + next_tile.rubble + 1
                if next_tile not in cost_so_far or new_cost < cost_so_far[next_tile]:
                    cost_so_far[next_tile] = new_cost
                    priority = new_cost + self.heuristic(goal, next_tile)
                    frontier.put(QueueItem(priority, next_tile))
                    came_from[
                        next_tile
                    ] = current  # this line updates came_from for every explored tile

        return came_from, start_tile, board.get_tile(goal[0], goal[1])

    # ... existing code ...

    def reconstruct_path(self, came_from, start, goal):
        current = goal
        path = []
        while current != start:
            if current not in came_from:
                # If the current tile is not in came_from, a path could not be found.
                return None
            path.append(current)
            try:
                current = came_from[current]
            except KeyError:
                # If the current tile is not in came_from, a path could not be found.
                return None
        path.append(start)  # optional
        path.reverse()  # optional
        return path

    def heuristic(self, goal, next):
        # Chebyshev distance
        dx = abs(goal[0] - next.x)
        dy = abs(goal[1] - next.y)
        return max(dx, dy)

    def distance_to(self, unit):
        return abs(self.x - unit.x) + abs(self.y - unit.y)


class Soldier2(Soldier):
    def act(self, board) -> Action:
        enemies = self.enemies_in_action_range(board)
        if len(enemies) > 0:
            # Attack only if the health is not critically low
            if self.health > 1:
                return AttackAction(self, enemies[0])
        return IdleAction(self)

    def move(self, board) -> Action:
        if not self.can_move():
            return IdleAction(self)

        enemies = self.enemies_in_sight(board)
        if len(enemies) > 0:
            closest_enemy = min(enemies, key=lambda enemy: self.distance_to(enemy))
            came_from, start, goal = self.astar_path(
                (self.x, self.y), (closest_enemy.x, closest_enemy.y), board
            )
            path = self.reconstruct_path(came_from, start, goal)
            if path and len(path) > 1:
                if path[1].is_occupied():
                    return IdleAction(self)
                return MoveAction(
                    self, path[1]
                )  # Moving to the second tile in the path, as the first one is the current location of the unit

        movable_tiles = self.adjacent_tiles(board)
        random.shuffle(movable_tiles)
        for tile in movable_tiles:
            if not tile.is_occupied():
                return MoveAction(self, tile)

        return IdleAction(self)

    def astar_path(self, start, goal, board):
        frontier = PriorityQueue()
        start_tile = board.get_tile(start[0], start[1])
        frontier.put(QueueItem(0, start_tile))
        came_from = {start_tile: None}
        cost_so_far = {start_tile: 0}

        while not frontier.empty():
            current = frontier.get().tile

            if (current.x, current.y) == goal:
                if current not in came_from:
                    came_from[
                        current
                    ] = current  # Add the goal tile to the came_from dictionary
                break

            for next_tile in board.tiles_in_radius(current.x, current.y, 1):
                if next_tile.is_occupied() and (next_tile.x, next_tile.y) != goal:
                    continue

                new_cost = cost_so_far[current] + next_tile.rubble + 1
                if next_tile not in cost_so_far or new_cost < cost_so_far[next_tile]:
                    cost_so_far[next_tile] = new_cost
                    priority = new_cost + self.heuristic(goal, next_tile)
                    frontier.put(QueueItem(priority, next_tile))
                    came_from[
                        next_tile
                    ] = current  # this line updates came_from for every explored tile

        return came_from, start_tile, board.get_tile(goal[0], goal[1])

    # ... existing code ...

    def reconstruct_path(self, came_from, start, goal):
        current = goal
        path = []
        while current != start:
            if current not in came_from:
                # If the current tile is not in came_from, a path could not be found.
                return None
            path.append(current)
            try:
                current = came_from[current]
            except KeyError:
                # If the current tile is not in came_from, a path could not be found.
                return None
        path.append(start)  # optional
        path.reverse()  # optional
        return path

    def heuristic(self, goal, next):
        # Chebyshev distance
        dx = abs(goal[0] - next.x)
        dy = abs(goal[1] - next.y)
        return max(dx, dy)

    def distance_to(self, unit):
        return abs(self.x - unit.x) + abs(self.y - unit.y)


class Soldier21(Soldier2):
    def act(self, board) -> Action:
        enemies = self.enemies_in_action_range(board)
        if len(enemies) > 0:
            # Attack the enemy with the least health
            weakest_enemy = min(enemies, key=lambda enemy: enemy.health)
            return AttackAction(self, weakest_enemy)
        return IdleAction(self)

    def move(self, board) -> Action:
        if not self.can_move():
            return IdleAction(self)
        
        if self.health < 2:
            return self.retreat(board)

        enemies = self.enemies_in_sight(board)
        action_range_enemies = self.enemies_in_action_range(board)
        if len(enemies) > 0:
            # Move towards the closest enemy that is not in action range
            closest_enemy = min(enemies, key=lambda enemy: self.distance_to(enemy) and enemy not in action_range_enemies)
            came_from, start, goal = self.astar_path(
                (self.x, self.y), (closest_enemy.x, closest_enemy.y), board
            )
            path = self.reconstruct_path(came_from, start, goal)
            if path and len(path) > 1:
                if path[1].is_occupied():
                    return IdleAction(self)
                return MoveAction(
                    self, path[1]
                )

        movable_tiles = self.adjacent_tiles(board)
        random.shuffle(movable_tiles)
        for tile in movable_tiles:
            if not tile.is_occupied():
                return MoveAction(self, tile)

        return IdleAction(self)

    def astar_path(self, start, goal, board):

        frontier = PriorityQueue()
        start_tile = board.get_tile(start[0], start[1])
        frontier.put(QueueItem(0, start_tile))
        came_from = {start_tile: None}
        cost_so_far = {start_tile: 0}

        while not frontier.empty():
            current = frontier.get().tile

            if (current.x, current.y) == goal:
                if current not in came_from:
                    came_from[
                        current
                    ] = current  # Add the goal tile to the came_from dictionary
                break

            for next_tile in board.tiles_in_radius(current.x, current.y, 1):
                if next_tile.is_occupied() and (next_tile.x, next_tile.y) != goal:
                    continue

                new_cost = cost_so_far[current] + next_tile.rubble * 10 + 1  # increase cost if tile has high rubble

                if next_tile not in cost_so_far or new_cost < cost_so_far[next_tile]:
                    cost_so_far[next_tile] = new_cost
                    priority = new_cost + self.heuristic(goal, next_tile)
                    frontier.put(QueueItem(priority, next_tile))
                    came_from[
                        next_tile
                    ] = current  # this line updates came_from for every explored tile

        return came_from, start_tile, board.get_tile(goal[0], goal[1])
        # ... existing code ...
        # ... existing code ...

    def retreat(self, board) -> Action:
        if not self.can_move():
            return IdleAction(self)

        # Move away from the closest enemy
        enemies = self.enemies_in_sight(board)
        if len(enemies) > 0:
            farthest_enemy = max(enemies, key=lambda enemy: self.distance_to(enemy))
            came_from, start, goal = self.astar_path(
                (self.x, self.y), (farthest_enemy.x, farthest_enemy.y), board
            )
            path = self.reconstruct_path(came_from, start, goal)
            if path and len(path) > 1:
                if path[1].is_occupied():
                    return IdleAction(self)
                return MoveAction(self, path[1])

        movable_tiles = self.adjacent_tiles(board)
        random.shuffle(movable_tiles)
        for tile in movable_tiles:
            if not tile.is_occupied():
                return MoveAction(self, tile)

        return IdleAction(self)
        
    # ... rest of the code ...


class Soldier3(Soldier):
    def act(self, board) -> Action:
        enemies = self.enemies_in_action_range(board)
        if enemies:
            target = random.choice(enemies)
            return AttackAction(self, target)
        else:
            return IdleAction(self)

    def move(self, board) -> Action:
        enemies = self.enemies_in_sight(board)
        if enemies:
            target = random.choice(enemies)
            tiles_next_to_target = board.tiles_in_radius(target.x, target.y, 1.5)
            movable_tiles = [
                tile
                for tile in tiles_next_to_target
                if not tile.is_occupied() and self.is_adjacent(tile)
            ]
            if movable_tiles:
                destination = random.choice(movable_tiles)
                return MoveAction(self, destination)

        adjacent_tiles = self.adjacent_tiles(board)
        movable_tiles = [tile for tile in adjacent_tiles if not tile.is_occupied()]
        if movable_tiles:
            destination = random.choice(movable_tiles)
            return MoveAction(self, destination)

        return IdleAction(self)

    def is_adjacent(self, tile) -> bool:
        # Check whether a tile is directly adjacent (up, down, left, right, or diagonally)
        dx = abs(self.x - tile.x)
        dy = abs(self.y - tile.y)
        return dx in [0, 1] and dy in [0, 1]


import math


class Soldier31(Soldier3):
    def act(self, board) -> Action:
        enemies = self.enemies_in_action_range(board)
        if enemies:
            # Prioritize the enemy closest to the spawn location.
            target = min(enemies, key=self.distance_to_spawn)
            return AttackAction(self, target)
        else:
            return IdleAction(self)

    def move(self, board) -> Action:
        enemies = self.enemies_in_sight(board)
        if enemies:
            target = min(enemies, key=self.distance_to_spawn)
            tiles_next_to_target = board.tiles_in_radius(target.x, target.y, 1.5)
            movable_tiles = [
                tile
                for tile in tiles_next_to_target
                if not tile.is_occupied()
                and self.is_adjacent(tile)
                and not tile.rubble > 2
            ]
            if movable_tiles:
                # Select the tile with the least amount of rubble.
                destination = min(movable_tiles, key=lambda tile: tile.rubble)
                return MoveAction(self, destination)

        adjacent_tiles = self.adjacent_tiles(board)
        movable_tiles = [
            tile
            for tile in adjacent_tiles
            if not tile.is_occupied() and not tile.rubble > 2
        ]
        if movable_tiles:
            destination = min(movable_tiles, key=lambda tile: tile.rubble)
            return MoveAction(self, destination)

        return IdleAction(self)

    def is_adjacent(self, tile) -> bool:
        dx = abs(self.x - tile.x)
        dy = abs(self.y - tile.y)
        return dx in [0, 1] and dy in [0, 1]

    def distance_to_spawn(self, unit) -> float:
        spawn_x, spawn_y = 0, 0  # Assuming the spawn location is at (0, 0).
        return math.sqrt((unit.x - spawn_x) ** 2 + (unit.y - spawn_y) ** 2)


class Soldier32(Soldier3):

    def act(self, board) -> Action:
        enemies = self.enemies_in_action_range(board)
        if enemies:
            # Change random choice to target based on highest threat level
            target = max(enemies, key=self.threat_level)
            return AttackAction(self, target)
        else:
            return IdleAction(self)

    def move(self, board) -> Action:
        enemies = self.enemies_in_sight(board)
        if enemies:
            target = max(enemies, key=self.threat_level)
            # Implement pathfinding to calculate best path to target
            path = self.calculate_path(board, target)
            if path:
                destination = path[0]  # Take the first step along the path
                if not destination.is_occupied():
                    return MoveAction(self, destination)
                

        adjacent_tiles = self.adjacent_tiles(board)
        movable_tiles = [tile for tile in adjacent_tiles if not tile.is_occupied()]
        if movable_tiles:
            destination = random.choice(movable_tiles)
            return MoveAction(self, destination)

        return IdleAction(self)

    def is_adjacent(self, tile) -> bool:
        # Check whether a tile is directly adjacent (up, down, left, right, or diagonally)
        dx = abs(self.x - tile.x)
        dy = abs(self.y - tile.y)
        return dx in [0, 1] and dy in [0, 1]

    def threat_level(self, enemy) -> float:
        # Calculate a "threat level" for an enemy based on factors like proximity, their strength, etc.
        # For now, let's just base it on inverse of distance (i.e., enemies closer to us are more threatening)
        dx = abs(self.x - enemy.x)
        dy = abs(self.y - enemy.y)
        return 1.0 / (dx + dy)

    def calculate_path(self, board, target) -> list:
        # Implement simple A* pathfinding to calculate path to target
        frontier = PriorityQueue()
        frontier.put((0, self))
        came_from = {self: None}
        cost_so_far = {self: 0}

        while not frontier.empty():
            current = frontier.get()[1]

            if current == target:
                break

            for next_tile in board.adjacent_tiles(current.x, current.y):
                new_cost = cost_so_far[current] + self.cost(board, next_tile)
                if next_tile not in cost_so_far or new_cost < cost_so_far[next_tile]:
                    cost_so_far[next_tile] = new_cost
                    priority = new_cost + self.heuristic(target, next_tile)
                    item = QueueItem(priority, next_tile)
                    frontier.put((item, next_tile))
                    came_from[next_tile] = current

        path = []
        while current != self:
            path.append(current)
            current = came_from[current]
        path.reverse()  # Path from self to target
        return path

    def cost(self, board, tile) -> int:
        # Cost of moving to a tile (higher if it's filled with rubble)
        return 1 + (10 if tile.rubble > 1 else 0)

    def heuristic(self, target, tile) -> int:
        # Heuristic function (Manhattan distance in this case)
        return abs(tile.x - target.x) + abs(tile.y - target.y)

class Soldier4(Soldier):
    def move(self, board) -> Action:
        if not self.can_move():
            return IdleAction(self)

        enemies = self.enemies_in_sight(board)
        if len(enemies) > 0:
            closest_enemy = min(enemies, key=lambda enemy: self.distance_to(enemy))
            came_from, start, goal = self.astar_path(
                (self.x, self.y), (closest_enemy.x, closest_enemy.y), board
            )
            path = self.reconstruct_path(came_from, start, goal)
            if path and len(path) > 1:
                if path[1].is_occupied():
                    movable_tiles = self.adjacent_tiles(board)
                    for tile in movable_tiles:
                        if not tile.is_occupied():
                            return MoveAction(self, tile)
                else:
                    return MoveAction(
                        self, path[1]
                    )  # Moving to the second tile in the path, as the first one is the current location of the unit

        movable_tiles = self.adjacent_tiles(board)
        random.shuffle(movable_tiles)
        for tile in movable_tiles:
            if not tile.is_occupied():
                return MoveAction(self, tile)

        return IdleAction(self)

    def astar_path(self, start, goal, board):
        frontier = PriorityQueue()
        start_tile = board.get_tile(start[0], start[1])
        frontier.put(QueueItem(0, start_tile))
        came_from = {start_tile: None}
        cost_so_far = {start_tile: 0}

        while not frontier.empty():
            current = frontier.get().tile

            if (current.x, current.y) == goal:
                if current not in came_from:
                    came_from[
                        current
                    ] = current  # Add the goal tile to the came_from dictionary
                break

            for next_tile in board.tiles_in_radius(current.x, current.y, 1.5):
                new_cost = cost_so_far[current] + next_tile.rubble + 1
                if next_tile not in cost_so_far or new_cost < cost_so_far[next_tile]:
                    cost_so_far[next_tile] = new_cost
                    priority = new_cost + self.heuristic(goal, next_tile)
                    frontier.put(QueueItem(priority, next_tile))
                    came_from[
                        next_tile
                    ] = current  # this line updates came_from for every explored tile

        return came_from, start_tile, board.get_tile(goal[0], goal[1])

    def reconstruct_path(self, came_from, start, goal):
        current = goal
        path = []
        while current != start:
            if current not in came_from:
                # If the current tile is not in came_from, a path could not be found.
                return None
            path.append(current)
            try:
                current = came_from[current]
            except KeyError:
                # If the current tile is not in came_from, a path could not be found.
                return None
        path.append(start)  # optional
        path.reverse()  # optional
        return path

    def heuristic(self, goal, next):
        # Chebyshev distance
        dx = abs(goal[0] - next.x)
        dy = abs(goal[1] - next.y)
        return max(dx, dy)

    def distance_to(self, unit):
        return abs(self.x - unit.x) + abs(self.y - unit.y)


class Soldier41(Soldier4):
    def __init__(self) -> None:
        super().__init__()
        self.spawn_point = None

    def move(self, board) -> Action:
        if self.spawn_point is None:
            self.spawn_point = board.get_tile(self.x, self.y)

        if not self.can_move():
            return IdleAction(self)

        enemies = self.enemies_in_sight(board)
        if len(enemies) > 0:
            closest_enemy = min(enemies, key=lambda enemy: self.distance_to(enemy))
            if self.distance_to(self.spawn_point) < self.distance_to(closest_enemy):
                return IdleAction(self)
            else:
                came_from, start, goal = self.astar_path(
                    (self.x, self.y), (closest_enemy.x, closest_enemy.y), board
                )
                path = self.reconstruct_path(came_from, start, goal)
                if path and len(path) > 1:
                    if path[1].is_occupied():
                        movable_tiles = self.adjacent_tiles(board)
                        for tile in movable_tiles:
                            if not tile.is_occupied():
                                return MoveAction(self, tile)
                    else:
                        return MoveAction(self, path[1])

        movable_tiles = self.adjacent_tiles(board)
        random.shuffle(movable_tiles)
        for tile in movable_tiles:
            if not tile.is_occupied():
                return MoveAction(self, tile)

        return IdleAction(self)

    def act(self, board):
        if not self.can_act():
            return IdleAction(self)

        enemies = self.enemies_in_sight(board)
        if enemies:
            closest_enemy = min(enemies, key=lambda enemy: self.distance_to(enemy))
            in_attack_range = self.in_action_range(
                board.get_tile(closest_enemy.x, closest_enemy.y)
            )
            if in_attack_range:
                return AttackAction(self, closest_enemy)

        return IdleAction(self)

    def astar_path(self, start, goal, board):
        frontier = PriorityQueue()
        start_tile = board.get_tile(start[0], start[1])
        frontier.put(QueueItem(0, start_tile))
        came_from = {start_tile: None}
        cost_so_far = {start_tile: 0}

        while not frontier.empty():
            current = frontier.get().tile

            if (current.x, current.y) == goal:
                if current not in came_from:
                    came_from[current] = current
                break

            for next_tile in board.tiles_in_radius(current.x, current.y, 1.5):
                new_cost = (
                    cost_so_far[current] + next_tile.rubble * self.rubble_cost + 1
                )
                if next_tile not in cost_so_far or new_cost < cost_so_far[next_tile]:
                    cost_so_far[next_tile] = new_cost
                    priority = new_cost + self.heuristic(goal, next_tile)
                    frontier.put(QueueItem(priority, next_tile))
                    came_from[next_tile] = current

        return came_from, start_tile, board.get_tile(goal[0], goal[1])

    def reconstruct_path(self, came_from, start, goal):
        current = goal
        path = []
        while current != start:
            if current not in came_from:
                return None
            path.append(current)
            try:
                current = came_from[current]
            except KeyError:
                return None
        path.append(start)
        path.reverse()
        return path

    def heuristic(self, goal, next):
        dx = abs(goal[0] - next.x)
        dy = abs(goal[1] - next.y)
        return max(dx, dy)

    def distance_to(self, unit):
        return abs(self.x - unit.x) + abs(self.y - unit.y)

    @property
    def rubble_cost(self):
        return 10  # modify this value to change how much the AI avoids rubble


class Soldier5(Soldier):
    def move(self, board) -> Action:
        if not self.can_move():
            return IdleAction(self)

        enemies = self.enemies_in_sight(board)
        if len(enemies) > 0:
            closest_enemy = min(enemies, key=lambda enemy: self.distance_to(enemy))
            came_from, start, goal = self.astar_path(
                (self.x, self.y), (closest_enemy.x, closest_enemy.y), board
            )
            path = self.reconstruct_path(came_from, start, goal)
            if path and len(path) > 1:
                if path[1].is_occupied():
                    movable_tiles = self.adjacent_tiles(board)
                    for tile in movable_tiles:
                        if not tile.is_occupied():
                            return MoveAction(self, tile)
                else:
                    return MoveAction(
                        self, path[1]
                    )  # Moving to the second tile in the path, as the first one is the current location of the unit

        movable_tiles = self.adjacent_tiles(board)
        random.shuffle(movable_tiles)
        for tile in movable_tiles:
            if not tile.is_occupied():
                return MoveAction(self, tile)

        return IdleAction(self)

        return IdleAction(self)

    def astar_path(self, start, goal, board):
        frontier = PriorityQueue()
        start_tile = board.get_tile(start[0], start[1])
        frontier.put(QueueItem(0, start_tile))
        came_from = {start_tile: None}
        cost_so_far = {start_tile: 0}

        while not frontier.empty():
            current = frontier.get().tile

            if (current.x, current.y) == goal:
                if current not in came_from:
                    came_from[
                        current
                    ] = current  # Add the goal tile to the came_from dictionary
                break

            for next_tile in board.tiles_in_radius(current.x, current.y, 1):
                new_cost = cost_so_far[current] + next_tile.rubble + 1
                if next_tile not in cost_so_far or new_cost < cost_so_far[next_tile]:
                    cost_so_far[next_tile] = new_cost
                    priority = new_cost + self.heuristic(goal, next_tile)
                    frontier.put(QueueItem(priority, next_tile))
                    came_from[
                        next_tile
                    ] = current  # this line updates came_from for every explored tile

        return came_from, start_tile, board.get_tile(goal[0], goal[1])

    # ... existing code ...

    def reconstruct_path(self, came_from, start, goal):
        current = goal
        path = []
        while current != start:
            if current not in came_from:
                # If the current tile is not in came_from, a path could not be found.
                return None
            path.append(current)
            try:
                current = came_from[current]
            except KeyError:
                # If the current tile is not in came_from, a path could not be found.
                return None
        path.append(start)  # optional
        path.reverse()  # optional
        return path

    def heuristic(self, goal, next):
        # Chebyshev distance
        dx = abs(goal[0] - next.x)
        dy = abs(goal[1] - next.y)
        return max(dx, dy)

    def distance_to(self, unit):
        return abs(self.x - unit.x) + abs(self.y - unit.y)


class Soldier51(Soldier5):
    def move(self, board) -> Action:
        if not self.can_move():
            return IdleAction(self)

        enemies = self.enemies_in_sight(board)
        if len(enemies) > 0:
            enemies.sort(key=lambda enemy: self.threat_level(enemy))
            target = enemies[0]
            came_from, start, goal = self.astar_path(
                (self.x, self.y), (target.x, target.y), board
            )
            path = self.reconstruct_path(came_from, start, goal)
            if path and len(path) > 1:
                if path[1].is_occupied():
                    movable_tiles = self.adjacent_tiles(board)
                    for tile in movable_tiles:
                        if not tile.is_occupied():
                            return MoveAction(self, tile)
                else:
                    return MoveAction(
                        self, path[1]
                    )  # Moving to the second tile in the path, as the first one is the current location of the unit

        movable_tiles = self.adjacent_tiles(board)
        random.shuffle(movable_tiles)
        for tile in movable_tiles:
            if not tile.is_occupied():
                return MoveAction(self, tile)

        return IdleAction(self)

        return IdleAction(self)

    def threat_level(self, enemy):
        # This is just a simple example. The exact formula would depend on the game's mechanics.
        enemy_strength = enemy.attack_damage / enemy.health
        if enemy_strength == 0:
            return 0
        return self.distance_to(enemy) / enemy_strength

    def astar_path(self, start, goal, board):
        frontier = PriorityQueue()
        start_tile = board.get_tile(start[0], start[1])
        frontier.put(QueueItem(0, start_tile))
        came_from = {start_tile: None}
        cost_so_far = {start_tile: 0}

        while not frontier.empty():
            current = frontier.get().tile

            if (current.x, current.y) == goal:
                if current not in came_from:
                    came_from[
                        current
                    ] = current  # Add the goal tile to the came_from dictionary
                break

            for next_tile in board.tiles_in_radius(current.x, current.y, 1):
                new_cost = cost_so_far[current] + next_tile.rubble + 1
                if next_tile not in cost_so_far or new_cost < cost_so_far[next_tile]:
                    cost_so_far[next_tile] = new_cost
                    priority = new_cost + self.heuristic(goal, next_tile)
                    frontier.put(QueueItem(priority, next_tile))
                    came_from[
                        next_tile
                    ] = current  # this line updates came_from for every explored tile

        return came_from, start_tile, board.get_tile(goal[0], goal[1])

    # ... existing code ...

    def reconstruct_path(self, came_from, start, goal):
        current = goal
        path = []
        while current != start:
            if current not in came_from:
                # If the current tile is not in came_from, a path could not be found.
                return None
            path.append(current)
            try:
                current = came_from[current]
            except KeyError:
                # If the current tile is not in came_from, a path could not be found.
                return None
        path.append(start)  # optional
        path.reverse()  # optional
        return path

    def heuristic(self, goal, next):
        # Chebyshev distance
        dx = abs(goal[0] - next.x)
        dy = abs(goal[1] - next.y)
        return max(dx, dy)

    def distance_to(self, unit):
        return abs(self.x - unit.x) + abs(self.y - unit.y)


class Soldier52(Soldier5):
    def move(self, board) -> Action:
        if not self.can_move():
            return IdleAction(self)

        enemies = self.enemies_in_sight(board)
        allies = self.allies_in_sight(board)

        if len(enemies) > 0:
            if len(allies) < len(enemies):  # Outnumbered, try to retreat
                retreat_tile = self.find_retreat_tile(board)
                if retreat_tile:
                    return MoveAction(self, retreat_tile)
            else:  # Not outnumbered, proceed as before
                closest_enemy = min(enemies, key=lambda enemy: self.distance_to(enemy))
                came_from, start, goal = self.astar_path(
                    (self.x, self.y), (closest_enemy.x, closest_enemy.y), board
                )
                path = self.reconstruct_path(came_from, start, goal)
                if path and len(path) > 1:
                    if path[1].is_occupied():
                        movable_tiles = self.adjacent_tiles(board)
                        for tile in movable_tiles:
                            if not tile.is_occupied():
                                return MoveAction(self, tile)
                    else:
                        return MoveAction(self, path[1])

        movable_tiles = self.adjacent_tiles(board)
        random.shuffle(movable_tiles)
        for tile in movable_tiles:
            if not tile.is_occupied():
                return MoveAction(self, tile)

        return IdleAction(self)

    def find_retreat_tile(self, board):
        # Find a tile to retreat to
        # Consider safety in terms of distance from enemies and proximity to allies
        movable_tiles = self.adjacent_tiles(board)
        enemies = self.enemies_in_sight(board)
        allies = self.allies_in_sight(board)

        # If there are no movable tiles or no allies, return None
        if not movable_tiles or not allies:
            return None

        safe_tiles = []
        for tile in movable_tiles:
            if not tile.is_occupied() and all(
                self.distance_between(tile, enemy) > 1 for enemy in enemies
            ):
                safe_tiles.append(tile)

        # If there are no safe tiles, return None
        if not safe_tiles:
            return None

        # Find the safe tile closest to an ally
        retreat_tile = min(
            safe_tiles,
            key=lambda tile: min(self.distance_between(tile, ally) for ally in allies),
        )

        return retreat_tile

    def distance_between(self, tile1, tile2):
        # Returns the Chebyshev distance between two tiles
        dx = abs(tile1.x - tile2.x)
        dy = abs(tile1.y - tile2.y)
        return max(dx, dy)

    def threat_level(self, enemy):
        # This is just a simple example. The exact formula would depend on the game's mechanics.
        enemy_strength = enemy.attack_damage / enemy.health
        if enemy_strength == 0:
            return 0
        return self.distance_to(enemy) / enemy_strength

    def astar_path(self, start, goal, board):
        frontier = PriorityQueue()
        start_tile = board.get_tile(start[0], start[1])
        frontier.put(QueueItem(0, start_tile))
        came_from = {start_tile: None}
        cost_so_far = {start_tile: 0}

        while not frontier.empty():
            current = frontier.get().tile

            if (current.x, current.y) == goal:
                if current not in came_from:
                    came_from[
                        current
                    ] = current  # Add the goal tile to the came_from dictionary
                break

            for next_tile in board.tiles_in_radius(current.x, current.y, 1):
                new_cost = cost_so_far[current] + next_tile.rubble + 1
                if next_tile not in cost_so_far or new_cost < cost_so_far[next_tile]:
                    cost_so_far[next_tile] = new_cost
                    priority = new_cost + self.heuristic(goal, next_tile)
                    frontier.put(QueueItem(priority, next_tile))
                    came_from[
                        next_tile
                    ] = current  # this line updates came_from for every explored tile

        return came_from, start_tile, board.get_tile(goal[0], goal[1])

    # ... existing code ...

    def reconstruct_path(self, came_from, start, goal):
        current = goal
        path = []
        while current != start:
            if current not in came_from:
                # If the current tile is not in came_from, a path could not be found.
                return None
            path.append(current)
            try:
                current = came_from[current]
            except KeyError:
                # If the current tile is not in came_from, a path could not be found.
                return None
        path.append(start)  # optional
        path.reverse()  # optional
        return path

    def heuristic(self, goal, next):
        # Chebyshev distance
        dx = abs(goal[0] - next.x)
        dy = abs(goal[1] - next.y)
        return max(dx, dy)

    def distance_to(self, unit):
        return abs(self.x - unit.x) + abs(self.y - unit.y)


class Soldier54(Soldier5):
    def move(self, board) -> Action:
        if not hasattr(self, "base"):
            self.base = (self.x, self.y)
            max_x, max_y = board.width(), board.height()
            self.enemy_base = (max_x - self.base[0], max_y - self.base[1])

        if not self.can_move():
            return IdleAction(self)

        HEALTH_THRESHOLD = 2
        if (
            self.health < HEALTH_THRESHOLD
        ):  # Check if health is below a certain threshold
            return self.retreat(board)  # Retreat to heal

        enemies = self.enemies_in_sight(board)
        if len(enemies) > 0:
            # Sort enemies by health and distance to prioritize lower health and closer enemies
            enemies.sort(key=lambda enemy: (enemy.health, self.distance_to(enemy)))
            for enemy in enemies:
                path = self.get_path_to(enemy, board)
                if path and len(path) > 1 and not path[1].is_occupied():
                    return MoveAction(self, path[1])

        # If no enemies or no accessible path to enemies, move towards a strategic location or spawn point
        path = self.get_path_to(self.strategic_location(), board)
        if path and len(path) > 1 and not path[1].is_occupied():
            return MoveAction(self, path[1])

        adjacent_tiles = self.adjacent_tiles(board)
        for t in adjacent_tiles:
            if not t.is_occupied():
                return MoveAction(self, t)
        return IdleAction(self)

    def attack(self, board) -> Action:
        if not self.can_attack():
            return IdleAction(self)

        enemies = self.enemies_in_sight(board)
        if len(enemies) > 0:
            # Sort enemies by health and distance to prioritize lower health and closer enemies
            enemies.sort(key=lambda enemy: (enemy.health, self.distance_to(enemy)))
            return AttackAction(
                self, enemies[0]
            )  # Attack the first (best) enemy in the sorted list

        return IdleAction(self)

    def retreat(self, board) -> Action:
        # Find a safe retreat location
        retreat_location = self.find_retreat_location(board)
        path = self.get_path_to(retreat_location, board)
        if path and len(path) > 1 and not path[1].is_occupied():
            return MoveAction(self, path[1])

        return IdleAction(self)

    def strategic_location(self) -> tuple[int, int]:
        # Return the enemy base to move towards when there are no visible enemies
        return self.enemy_base

    def find_retreat_location(self, board) -> tuple[int, int]:
        # Retreat to the friendly base
        return self.base

    def get_path_to(self, target, board):
        start = (self.x, self.y)
        if isinstance(target, Unit):
            goal = (target.x, target.y)
        else:  # If the target is a location
            goal = target

        came_from, start, goal = self.astar_path(start, goal, board)
        return self.reconstruct_path(came_from, start, goal)


class Soldier6(Soldier):

    def __init__(self) -> None:
        super().__init__()
        self.spawn_location = None

    def act(self, board) -> Action:
        if self.spawn_location is None:
            self.spawn_location = board.get_tile(self.x, self.y)

        enemies = self.enemies_in_action_range(board)
        if len(enemies) > 0:
            weakest_enemy = min(enemies, key=lambda enemy: enemy.health)
            return AttackAction(self, weakest_enemy)
        return IdleAction(self)

    def move(self, board) -> Action:
        # If health is critically low, try to move towards the spawn location
        if self.health <= self.max_health / 3:
            return self.move_towards_spawn(board)

        enemies_in_sight = self.enemies_in_sight(board)
        if enemies_in_sight:
            closest_enemy = min(enemies_in_sight, key=lambda enemy: self.distance_to(enemy))
            return self.move_towards_enemy(board, closest_enemy)

        movable_tiles = self.adjacent_tiles(board)
        movable_tiles_without_rubble = [tile for tile in movable_tiles if not tile.rubble > 1]
        if movable_tiles_without_rubble:
            random.shuffle(movable_tiles_without_rubble)
            if not movable_tiles_without_rubble[0].is_occupied():
                return MoveAction(self, movable_tiles_without_rubble[0])
        else:
            # If all movable tiles have rubble, select one at random
            for tile in movable_tiles:
                if not tile.is_occupied():
                    return MoveAction(self, tile)

        return IdleAction(self)

    def move_towards_spawn(self, board) -> Action:
        # Directly move towards the spawn location by choosing the tile that minimizes distance
        return self.move_in_direction(board, self.spawn_location)

    def move_towards_enemy(self, board, enemy) -> Action:
        # Directly move towards the enemy by choosing the tile that minimizes distance
        return self.move_in_direction(board, enemy.tile)
    
    def move_in_direction(self, board, location) -> Action:
        movable_tiles = self.adjacent_tiles(board)
        if not movable_tiles:
            return IdleAction(self)
        
        # Avoid rubble if possible
        movable_tiles_without_rubble = [tile for tile in movable_tiles if not tile.rubble > 1]
        if movable_tiles_without_rubble:
            best_tile = min(movable_tiles_without_rubble, key=lambda tile: tile.distance_to(location))
            if not best_tile.is_occupied():
                return MoveAction(self, best_tile)
            # return MoveAction(self, best_tile)
        
        # If all tiles contain rubble, select the one that minimizes distance to the target location
        best_tile = min(movable_tiles, key=lambda tile: tile.distance_to(location))
        if not best_tile.is_occupied():
            return MoveAction(self, best_tile)
        return IdleAction(self)
    
    def distance_to(self, enemy):
        return abs(self.x - enemy.x) + abs(self.y - enemy.y)


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
        self.spawn_unit = None

    def act(self, board) -> Action:
        for tile in self.adjacent_tiles(board):
            if tile.is_occupied():
                unit = tile.occupant
                if unit.player == self.player:
                    if unit.health < unit.max_health:
                        # TODO heal action
                        unit.health += 1

        if self.can_act():
            adjacent_tiles = self.adjacent_tiles(board)
            random.shuffle(adjacent_tiles)
            for tile in adjacent_tiles:
                if not tile.is_occupied():
                    if self.spawn_unit is None:
                        raise Exception("Spawner.spawn_unit is None")
                    unit = self.spawn_unit()
                    unit.player = self.player
                    return SpawnAction(self, unit, tile)
        return IdleAction(self)

    def move(self, board) -> Action:
        return IdleAction(self)
