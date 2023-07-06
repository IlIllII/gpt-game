from game import Game
from player import Player
from board import Board
from unit import Unit
from tile import Tile
from action import Action, AttackAction, MoveAction, DieAction, IdleAction
from statechange import StateChange
from render import Renderer
# from gptgame.state import State


def main():
    player1 = Player(1)
    player2 = Player(2)
    rubble = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [2, 0, 0, 0, 0, 0, 0, 0, 0, 2],
        [2, 0, 0, 0, 0, 0, 0, 0, 0, 2],
        [2, 0, 0, 0, 0, 0, 0, 0, 0, 2],
        [2, 0, 0, 0, 0, 0, 0, 0, 0, 2],
        [2, 0, 0, 0, 0, 0, 0, 0, 0, 2],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [3, 3, 0, 0, 0, 0, 0, 0, 3, 3]
    ]
    resources = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
        [10, 0, 0, 0, 0, 0, 0, 0, 0, 10],
        [10, 0, 0, 0, 0, 0, 0, 0, 0, 10],
        [10, 0, 0, 0, 0, 0, 0, 0, 0, 10],
        [10, 0, 0, 0, 0, 0, 0, 0, 0, 10],
        [10, 0, 0, 0, 0, 0, 0, 0, 0, 10],
        [10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
        [10, 10, 0, 0, 0, 0, 0, 0, 10, 10]
    ]
    board = Board(rubble, resources)
    game = Game(player1, player2, board)
    renderer = Renderer(game)
    renderer.debug = False
    for _ in range(10000):
        renderer.render(game.update())


if __name__ == "__main__":
    main()
