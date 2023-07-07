from tile import Tile
from action import Action, AttackAction, MoveAction, DieAction, IdleAction, SpawnAction
import random
from math import sqrt
from queue import PriorityQueue


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
            if tile.occupant.player != self.player
            and tile.occupant.is_alive()
        ]

    def enemies_in_action_range(self, board) -> list:
        return [
            tile.occupant
            for tile in board.occupied_tiles_in_radius(
                self.x, self.y, self.action_range
            )
            if tile.occupant.player != self.player
            and tile.occupant.is_alive()
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
        self.vision_range = 50
        self.move_cooldown = 2
        self.action_cooldown = 2
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
            came_from, start, goal = self.astar_path((self.x, self.y), (closest_enemy.x, closest_enemy.y), board)
            path = self.reconstruct_path(came_from, start, goal)
            if path and len(path) > 1:
                if path[1].is_occupied():
                    return IdleAction(self)
                return MoveAction(self, path[1])  # Moving to the second tile in the path, as the first one is the current location of the unit

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
                    came_from[current] = current  # Add the goal tile to the came_from dictionary
                break

            for next_tile in board.tiles_in_radius(current.x, current.y, 1):
                if next_tile.is_occupied() and (next_tile.x, next_tile.y) != goal:
                    continue
                
                new_cost = cost_so_far[current] + next_tile.rubble + 1
                if next_tile not in cost_so_far or new_cost < cost_so_far[next_tile]:
                    cost_so_far[next_tile] = new_cost
                    priority = new_cost + self.heuristic(goal, next_tile)
                    frontier.put(QueueItem(priority, next_tile))
                    came_from[next_tile] = current  # this line updates came_from for every explored tile

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
            came_from, start, goal = self.astar_path((self.x, self.y), (closest_enemy.x, closest_enemy.y), board)
            path = self.reconstruct_path(came_from, start, goal)
            if path and len(path) > 1:
                if path[1].is_occupied():
                    return IdleAction(self)
                return MoveAction(self, path[1])  # Moving to the second tile in the path, as the first one is the current location of the unit

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
                    came_from[current] = current  # Add the goal tile to the came_from dictionary
                break

            for next_tile in board.tiles_in_radius(current.x, current.y, 1):
                if next_tile.is_occupied() and (next_tile.x, next_tile.y) != goal:
                    continue
                
                new_cost = cost_so_far[current] + next_tile.rubble + 1
                if next_tile not in cost_so_far or new_cost < cost_so_far[next_tile]:
                    cost_so_far[next_tile] = new_cost
                    priority = new_cost + self.heuristic(goal, next_tile)
                    frontier.put(QueueItem(priority, next_tile))
                    came_from[next_tile] = current  # this line updates came_from for every explored tile

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
            movable_tiles = [tile for tile in tiles_next_to_target if not tile.is_occupied() and self.is_adjacent(tile)]
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


class Soldier4(Soldier):
    def move(self, board) -> Action:
        if not self.can_move():
            return IdleAction(self)

        enemies = self.enemies_in_sight(board)
        if len(enemies) > 0:
            closest_enemy = min(enemies, key=lambda enemy: self.distance_to(enemy))
            came_from, start, goal = self.astar_path((self.x, self.y), (closest_enemy.x, closest_enemy.y), board)
            path = self.reconstruct_path(came_from, start, goal)
            if path and len(path) > 1:
                if path[1].is_occupied():
                    movable_tiles = self.adjacent_tiles(board)
                    for tile in movable_tiles:
                        if not tile.is_occupied():
                            return MoveAction(self, tile)
                else:
                    return MoveAction(self, path[1])  # Moving to the second tile in the path, as the first one is the current location of the unit

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
                    came_from[current] = current  # Add the goal tile to the came_from dictionary
                break

            for next_tile in board.tiles_in_radius(current.x, current.y, 1.5):
                new_cost = cost_so_far[current] + next_tile.rubble + 1
                if next_tile not in cost_so_far or new_cost < cost_so_far[next_tile]:
                    cost_so_far[next_tile] = new_cost
                    priority = new_cost + self.heuristic(goal, next_tile)
                    frontier.put(QueueItem(priority, next_tile))
                    came_from[next_tile] = current  # this line updates came_from for every explored tile

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

class Soldier5(Soldier):
    def move(self, board) -> Action:
        if not self.can_move():
            return IdleAction(self)

        enemies = self.enemies_in_sight(board)
        if len(enemies) > 0:
            closest_enemy = min(enemies, key=lambda enemy: self.distance_to(enemy))
            came_from, start, goal = self.astar_path((self.x, self.y), (closest_enemy.x, closest_enemy.y), board)
            path = self.reconstruct_path(came_from, start, goal)
            if path and len(path) > 1:
                if path[1].is_occupied():
                    movable_tiles = self.adjacent_tiles(board)
                    for tile in movable_tiles:
                        if not tile.is_occupied():
                            return MoveAction(self, tile)
                else:
                    return MoveAction(self, path[1])  # Moving to the second tile in the path, as the first one is the current location of the unit

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
                    came_from[current] = current  # Add the goal tile to the came_from dictionary
                break

            for next_tile in board.tiles_in_radius(current.x, current.y, 1):
                new_cost = cost_so_far[current] + next_tile.rubble + 1
                if next_tile not in cost_so_far or new_cost < cost_so_far[next_tile]:
                    cost_so_far[next_tile] = new_cost
                    priority = new_cost + self.heuristic(goal, next_tile)
                    frontier.put(QueueItem(priority, next_tile))
                    came_from[next_tile] = current  # this line updates came_from for every explored tile

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