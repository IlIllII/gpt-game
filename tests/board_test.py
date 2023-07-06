import pytest
from gptgame import Board, Unit


def test_tiles_in_radius():
    board_data = [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ]

    board = Board(board_data, board_data)

    x, y, radius = 2, 2, 1

    tiles = board.tiles_in_radius(x, y, radius)

    expected_tiles = [
        board.get_tile(1, 2),
        board.get_tile(2, 1),
        board.get_tile(3, 2),
        board.get_tile(2, 3),
    ]

    assert set(tiles) == set(
        expected_tiles
    ), "Tiles in radius did not match expected tiles"
