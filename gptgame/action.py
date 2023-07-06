class Action:
    def __init__(self) -> None:
        pass

    def execute(self, board) -> None:
        raise NotImplementedError


class IdleAction(Action):
    def __init__(self, unit) -> None:
        self.unit = unit

    def execute(self, board) -> None:
        pass


class AttackAction(Action):
    def __init__(self, attacker, target) -> None:
        self.attacker = attacker
        self.target = target

    def execute(self, board) -> None:
        tile = board.get_tile(self.target.x, self.target.y)
        if not self.attacker.in_attack_range(tile):
            raise Exception("Tile not in range")
        if not tile.is_occupied():
            raise Exception("Tile not occupied")
        if not self.attacker.can_attack():
            raise Exception("Unit on cooldown")
        if not self.attacker.is_alive():
            raise Exception("Unit dead")
        
        self.target.health -= self.attacker.attack_damage
        cooldown = self.attacker.attack_cooldown
        cooldown *= board.get_rubble(self.attacker.x, self.attacker.y)
        self.attacker.attack_cooldown = cooldown

        if self.target.health <= 0:
            self.target.alive = False

        


class MoveAction(Action):
    def __init__(self, unit, tile) -> None:
        self.unit = unit
        self.tile = tile

    def execute(self, board) -> None:
        if not self.unit.in_range(self.tile, 1):
            raise Exception("Tile not in range")
        if self.tile.is_occupied():
            raise Exception("Tile occupied")
        if not self.unit.can_move():
            raise Exception("Unit on cooldown")
        if not self.unit.is_alive():
            raise Exception("Unit dead")
        
        cooldown = self.unit.move_cooldown
        cooldown *= board.get_rubble(self.unit.x, self.unit.y)
        self.unit.x = self.tile.x
        self.unit.y = self.tile.y
        board.remove_occupant(self.unit.x, self.unit.y)
        board.set_occupant(self.tile.x, self.tile.y, self.unit)
        self.unit.move_cooldown = cooldown



class DieAction(Action):
    def __init__(self, unit) -> None:
        self.unit = unit

    def execute(self, board) -> None:
        self.unit.alive = False
        board.remove_occupant(self.unit.x, self.unit.y)
        existing_resource = board.get_resource(self.unit.x, self.unit.y)
        new_resource = existing_resource + self.unit.bounty
        board.set_resource(self.unit.x, self.unit.y, new_resource)
        self.unit.player.remove_unit(self.unit)

class CreateUnit(Action):
    def __init__(self, unit, tile) -> None:
        self.unit = unit
        self.tile = tile
    
    def execute(self, board) -> None:
        if self.tile.is_occupied():
            raise Exception("Tile occupied")
        board.set_occupant(self.tile.x, self.tile.y, self.unit)