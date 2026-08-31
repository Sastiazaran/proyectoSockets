import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "client"))

from game_logic import EMPTY, PLAYER_O, PLAYER_X, Board  # noqa: E402
import users  # noqa: E402


class BoardTests(unittest.TestCase):
    def test_rejects_out_of_range_and_occupied_cells(self):
        board = Board()
        self.assertFalse(board.move(-1))
        self.assertFalse(board.move(9))
        self.assertTrue(board.move(0))
        self.assertFalse(board.move(0))
        self.assertEqual(board.cells[0], PLAYER_X)

    def test_alternates_turns(self):
        board = Board()
        board.move(0)
        self.assertEqual(board.turn, PLAYER_O)
        board.move(1)
        self.assertEqual(board.turn, PLAYER_X)

    def test_row_win(self):
        board = Board()
        for index in (0, 3, 1, 4, 2):
            board.move(index)
        self.assertEqual(board.winner, PLAYER_X)
        self.assertEqual(board.winning_line, (0, 1, 2))
        self.assertFalse(board.move(8), "no moves after a win")

    def test_column_and_diagonal_wins(self):
        col = Board()
        for index in (0, 1, 3, 2, 6):
            col.move(index)
        self.assertEqual(col.winner, PLAYER_X)
        self.assertEqual(col.winning_line, (0, 3, 6))

        diag = Board()
        for index in (0, 1, 4, 2, 8):
            diag.move(index)
        self.assertEqual(diag.winner, PLAYER_X)
        self.assertEqual(diag.winning_line, (0, 4, 8))

        anti = Board(starting_player=PLAYER_O)
        for index in (2, 0, 4, 1, 6):
            anti.move(index)
        self.assertEqual(anti.winner, PLAYER_O)
        self.assertEqual(anti.winning_line, (2, 4, 6))

    def test_tie_when_board_is_full_without_winner(self):
        board = Board()
        # X O X
        # X X O
        # O X O
        for index in (0, 1, 2, 5, 3, 6, 4, 8, 7):
            self.assertTrue(board.move(index))
        self.assertIsNone(board.winner)
        self.assertTrue(board.is_tie)
        self.assertTrue(board.is_over)

    def test_row_col_to_index_bounds(self):
        board = Board()
        self.assertEqual(board.row_col_to_index(2, 2), 8)
        self.assertIsNone(board.row_col_to_index(3, 0))
        self.assertIsNone(board.row_col_to_index(0, -1))
        self.assertEqual(board.cells, [EMPTY] * 9)

    def test_reset_clears_state(self):
        board = Board()
        board.move(0)
        board.reset()
        self.assertEqual(board.cells, [EMPTY] * 9)
        self.assertEqual(board.turn, PLAYER_X)
        self.assertIsNone(board.winner)


class UsersTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        self.tmp.close()
        users.USERS_FILE = Path(self.tmp.name)
        Path(self.tmp.name).write_text("", encoding="utf-8")

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_register_and_authenticate(self):
        self.assertIsNone(users.register("alice", "secret"))
        self.assertTrue(users.authenticate("Alice", "secret"))
        self.assertFalse(users.authenticate("alice", "wrong"))
        self.assertEqual(users.register("alice", "secret"), "That username is already taken.")

    def test_rejects_bad_usernames_and_short_passwords(self):
        self.assertIsNotNone(users.register("ab", "secret"))
        self.assertIsNotNone(users.register("bad name", "secret"))
        self.assertIsNotNone(users.register("okname", "ab"))


if __name__ == "__main__":
    unittest.main()
