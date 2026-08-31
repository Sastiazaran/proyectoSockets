"""Pure Tic-Tac-Toe rules. No pygame dependency so this can be unit tested."""

EMPTY = None
PLAYER_X = "X"
PLAYER_O = "O"

WIN_LINES = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


class Board:
    """3x3 board stored as a flat list of 9 cells."""

    def __init__(self, starting_player=PLAYER_X):
        if starting_player not in (PLAYER_X, PLAYER_O):
            raise ValueError("starting_player must be 'X' or 'O'")
        self.cells = [EMPTY] * 9
        self.turn = starting_player
        self.winner = None
        self.winning_line = None

    def reset(self, starting_player=PLAYER_X):
        self.__init__(starting_player)

    def occupied(self, index):
        return 0 <= index < 9 and self.cells[index] is not EMPTY

    def is_full(self):
        return EMPTY not in self.cells

    @property
    def is_tie(self):
        return self.winner is None and self.is_full()

    @property
    def is_over(self):
        return self.winner is not None or self.is_tie

    def move(self, index):
        """Place the current player's mark. Returns True if the move was applied."""
        if self.winner is not None:
            return False
        if not isinstance(index, int) or index < 0 or index > 8:
            return False
        if self.cells[index] is not EMPTY:
            return False

        self.cells[index] = self.turn
        self._refresh_winner()
        if self.winner is None and not self.is_full():
            self.turn = PLAYER_O if self.turn == PLAYER_X else PLAYER_X
        return True

    def _refresh_winner(self):
        for line in WIN_LINES:
            a, b, c = (self.cells[i] for i in line)
            if a is not EMPTY and a == b == c:
                self.winner = a
                self.winning_line = line
                return
        self.winner = None
        self.winning_line = None

    def row_col_to_index(self, row, col):
        if row < 0 or row > 2 or col < 0 or col > 2:
            return None
        return row * 3 + col
