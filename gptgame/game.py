import random

from action import Action


class Game:
    def __init__(self, player1, player2, gameboard) -> None:
        self.player1 = player1
        self.player2 = player2
        self.turn = 1
        self.board = gameboard
        self.winner = None

    def run_step(self) -> Action:
        actions = []
        for unit in self.shuffled_units():
            action = unit.act(self.board)
            actions.append(action)
        return actions

    def shuffled_units(self):
        units = self.player1.units + self.player2.units
        random.shuffle(units)
        return units
