import random

from action import Action
from statechange import StateChange


class Game:
    def __init__(self, player1, player2, gameboard) -> None:
        self.player1 = player1
        self.player2 = player2
        self.turn = 1
        self.board = gameboard
        self.winner = None

    def update(self) -> StateChange:
        state_changes = []
        units = self.all_units()
        random.shuffle(units)
        for unit in units:
            state_change = unit.take_turn(self.board)
            for action in state_change:
                action.execute(self.board)
            state_changes.append(state_change)

        # Purge dead units
        units = self.all_units()
        for unit in units:
            if not unit.is_alive():
                state_change = unit.die()
                for action in state_change:
                    action.execute(self.board)
                state_changes.append(state_change)

        return StateChange(state_changes)

    def all_units(self):
        return self.player1.units + self.player2.units
