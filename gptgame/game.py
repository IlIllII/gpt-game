class Game:
    def __init__(self, player1, player2, gameboard) -> None:
        self.player1 = player1
        self.player2 = player2
        self.turn = 1
        self.board = gameboard
        self.winner = None

    def run_turn(self):
        pass
