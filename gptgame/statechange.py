from action import Action


class StateChange:
    def __init__(self, state_chnages: list[tuple[Action, Action]]) -> None:
        self.state_changes = state_chnages
