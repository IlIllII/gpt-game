from game import Game
from player import Player
from board import Board
from unit import Unit, Spawner, Soldier
from tile import Tile
from action import Action, AttackAction, MoveAction, DieAction, IdleAction
from statechange import StateChange
from render import Renderer
import time
# from gptgame.state import State


def main():
    player1 = Player(1)
    player2 = Player(2)
    rubble = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [2, 0, 0, 0, 0, 0, 0, 0, 0, 2],
        [2, 0, 0, 0, 0, 0, 0, 0, 0, 2],
        [2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [3, 3, 0, 0, 0, 0, 0, 0, 0, 0]
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
    spawner1 = Spawner()
    spawner1.player = player1
    spawner2 = Spawner()
    spawner2.player = player2
    spawner1.x = 0
    spawner1.y = 0
    spawner2.x = 9
    spawner2.y = 8
    board.get_tile(0, 0).occupant = spawner1
    board.get_tile(9, 8).occupant = spawner2
    player1.add_unit(spawner1)
    player2.add_unit(spawner2)
    renderer = Renderer(game)
    renderer.debug = False
    for _ in range(1000):
        time.sleep(0.05)
        state_changes = game.update()
        renderer.render(state_changes)


if __name__ == "__main__":
    main()
