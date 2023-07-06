class Action:
    def __init__(self) -> None:
        pass


class IdleAction(Action):
    def __init__(self, unit) -> None:
        self.unit = unit


class AttackAction(Action):
    def __init__(self, unit, tile) -> None:
        self.unit = unit
        self.tile = tile


class MoveAction(Action):
    def __init__(self, unit, tile) -> None:
        self.unit = unit
        self.tile = tile
