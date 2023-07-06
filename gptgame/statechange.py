from action import Action

class StateChange:
    def __init__(self, movements: list[Action], actions: list[Action]) -> None:
        self.movements = movements
        self.actions = actions