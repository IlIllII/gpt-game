import pytest
from gptgame.board import Board, Unit


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
    ), f"Tiles around ({x}, {y}) in radius={radius} did not match expected tiles"

    x, y, radius = 2, 2, 2

    tiles = board.tiles_in_radius(x, y, radius)

    expected_tiles = [
        board.get_tile(0, 2),
        board.get_tile(1, 1),
        board.get_tile(1, 2),
        board.get_tile(1, 3),
        board.get_tile(2, 0),
        board.get_tile(2, 1),
        board.get_tile(2, 3),
        board.get_tile(2, 4),
        board.get_tile(3, 1),
        board.get_tile(3, 2),
        board.get_tile(3, 3),
        board.get_tile(4, 2),
    ]

    assert set(tiles) == set(
        expected_tiles
    ), f"Tiles around ({x}, {y}) in radius={radius} did not match expected tiles"

    x, y, radius = 0, 0, 1

    tiles = board.tiles_in_radius(x, y, radius)

    expected_tiles = [
        board.get_tile(0, 1),
        board.get_tile(1, 0),
    ]

    assert set(tiles) == set(
        expected_tiles
    ), f"Tiles around ({x}, {y}) in radius={radius} did not match expected tiles"

    x, y, radius = 0, 0, 0

    tiles = board.tiles_in_radius(x, y, radius)

    expected_tiles = []

    assert set(tiles) == set(
        expected_tiles
    ), f"Tiles around ({x}, {y}) in radius={radius} did not match expected tiles"

    x, y, radius = 2, 2, 10

    tiles = board.tiles_in_radius(x, y, radius)

    expected_tiles = [
        board.get_tile(i, j)
        for i in range(len(board_data))
        for j in range(len(board_data[0]))
        if not (i, j) == (2, 2)
    ]

    assert set(tiles) == set(
        expected_tiles
    ), f"Tiles around ({x}, {y}) in radius={radius} did not match expected tiles"
