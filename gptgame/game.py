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
        actions = []
        movements = []
        units = self.all_units()
        random.shuffle(units)
        for unit in units:
            action = unit.act(self.board)
            actions.append(action)
            movement = unit.move(self.board)
            movements.append(movement)
        return StateChange(movements, actions)

    def all_units(self):
        return self.player1.units + self.player2.units
