class Unit:
    def __init__(self) -> None:
        self.alive = True

    def act(self, board) -> None:
        pass

    def is_alive(self) -> bool:
        return self.alive
