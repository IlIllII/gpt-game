from unit import Unit

class Action:
    def __init__(self) -> None:
        pass

    def execute(self, board) -> None:
        raise NotImplementedError


class IdleAction(Action):
    def __init__(self, unit) -> None:
        self.unit = unit


class AttackAction(Action):
    def __init__(self, attacker: Unit, target: Unit) -> None:
        self.attacker = attacker
        self.target = target
    
    def execute(self, board) -> None:
        if not self.unit.in_range(self.tile):
            raise Exception("Tile not in range")
        if not self.tile.is_occupied():
            raise Exception("Tile not occupied")
        if self.tile.occupant.player == self.player:
            # TODO: friendly fire?
            raise Exception("Tile occupied by friendly unit")
        self.tile.occupant.health -= self.unit.attack_damage


class MoveAction(Action):
    def __init__(self, unit, tile) -> None:
        self.unit = unit
        self.tile = tile
