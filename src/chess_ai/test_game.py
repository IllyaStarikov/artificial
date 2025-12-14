"""Tests for chess game logic."""

from __future__ import annotations

import unittest

from chess_client.game import ChessGame


class TestCastlingValidation(unittest.TestCase):
    """Tests for castling move generation."""

    def test_castling_requires_king_on_e_file(self) -> None:
        """King not on e-file should not be able to castle."""
        # King on f1 (file 5) with castling rights - should NOT castle
        # We use f1 so that g1 is a one-square move but c1 would require castling
        game = ChessGame()
        game.from_fen("r3k2r/8/8/8/8/8/8/R4K1R w KQkq - 0 1")
        # White king is on f1 (file 5), not e1 (file 4)
        moves = game.get_legal_moves(5, 0)  # f1
        # King can move to e1, g1 (one square) but NOT castle to c1 (4 squares away)
        # Castling would require 2-square jump which isn't valid from f1
        # The key is no TWO-square moves should exist
        two_square_moves = [(f, r) for f, r in moves if abs(f - 5) == 2]
        self.assertEqual(two_square_moves, [])

    def test_castling_requires_rook_present_kingside(self) -> None:
        """Missing kingside rook should prevent kingside castling."""
        # King on e1 with rights but no h1 rook
        game = ChessGame()
        game.from_fen("r3k2r/8/8/8/8/8/8/R3K3 w Qkq - 0 1")
        moves = game.get_legal_moves(4, 0)  # e1
        # Should not include kingside castle (g1=6,0)
        self.assertNotIn((6, 0), moves)
        # Should include queenside castle (c1=2,0)
        self.assertIn((2, 0), moves)

    def test_castling_requires_rook_present_queenside(self) -> None:
        """Missing queenside rook should prevent queenside castling."""
        # King on e1 with rights but no a1 rook
        game = ChessGame()
        game.from_fen("r3k2r/8/8/8/8/8/8/4K2R w Kkq - 0 1")
        moves = game.get_legal_moves(4, 0)  # e1
        # Should include kingside castle (g1=6,0)
        self.assertIn((6, 0), moves)
        # Should not include queenside castle (c1=2,0)
        self.assertNotIn((2, 0), moves)

    def test_castling_kingside_white(self) -> None:
        """Valid white kingside castling works."""
        game = ChessGame()
        game.from_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
        moves = game.get_legal_moves(4, 0)  # e1
        self.assertIn((6, 0), moves)  # g1

    def test_castling_queenside_white(self) -> None:
        """Valid white queenside castling works."""
        game = ChessGame()
        game.from_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
        moves = game.get_legal_moves(4, 0)  # e1
        self.assertIn((2, 0), moves)  # c1

    def test_castling_kingside_black(self) -> None:
        """Valid black kingside castling works."""
        game = ChessGame()
        game.from_fen("r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1")
        moves = game.get_legal_moves(4, 7)  # e8
        self.assertIn((6, 7), moves)  # g8

    def test_castling_queenside_black(self) -> None:
        """Valid black queenside castling works."""
        game = ChessGame()
        game.from_fen("r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1")
        moves = game.get_legal_moves(4, 7)  # e8
        self.assertIn((2, 7), moves)  # c8

    def test_castling_blocked_by_pieces(self) -> None:
        """Pieces between king and rook block castling."""
        game = ChessGame()
        # Bishop on f1 blocks kingside, knight on b1 blocks queenside
        game.from_fen("r3k2r/8/8/8/8/8/8/RN2KB1R w KQkq - 0 1")
        moves = game.get_legal_moves(4, 0)  # e1
        self.assertNotIn((6, 0), moves)  # g1 blocked
        self.assertNotIn((2, 0), moves)  # c1 blocked


class TestCastlingRights(unittest.TestCase):
    """Tests for castling rights management."""

    def test_rook_capture_removes_castling_rights_white_kingside(self) -> None:
        """Capturing white's h1 rook removes white kingside castling."""
        game = ChessGame()
        game.from_fen("r3k2r/8/8/8/8/7q/8/R3K2R b KQkq - 0 1")
        # Black queen captures h1 rook
        game.make_move((7, 2), (7, 0))  # Qh3xh1
        self.assertNotIn("K", game.castling_rights)
        self.assertIn("Q", game.castling_rights)

    def test_rook_capture_removes_castling_rights_white_queenside(self) -> None:
        """Capturing white's a1 rook removes white queenside castling."""
        game = ChessGame()
        game.from_fen("r3k2r/8/8/8/8/q7/8/R3K2R b KQkq - 0 1")
        # Black queen captures a1 rook
        game.make_move((0, 2), (0, 0))  # Qa3xa1
        self.assertNotIn("Q", game.castling_rights)
        self.assertIn("K", game.castling_rights)

    def test_rook_capture_removes_castling_rights_black_kingside(self) -> None:
        """Capturing black's h8 rook removes black kingside castling."""
        game = ChessGame()
        game.from_fen("r3k2r/8/7Q/8/8/8/8/R3K2R w KQkq - 0 1")
        # White queen captures h8 rook
        game.make_move((7, 5), (7, 7))  # Qh6xh8
        self.assertNotIn("k", game.castling_rights)
        self.assertIn("q", game.castling_rights)

    def test_rook_capture_removes_castling_rights_black_queenside(self) -> None:
        """Capturing black's a8 rook removes black queenside castling."""
        game = ChessGame()
        game.from_fen("r3k2r/8/Q7/8/8/8/8/R3K2R w KQkq - 0 1")
        # White queen captures a8 rook
        game.make_move((0, 5), (0, 7))  # Qa6xa8
        self.assertNotIn("q", game.castling_rights)
        self.assertIn("k", game.castling_rights)

    def test_king_move_removes_both_castling_rights(self) -> None:
        """Moving king removes both castling rights for that side."""
        game = ChessGame()
        game.from_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
        game.make_move((4, 0), (4, 1))  # Ke1-e2
        self.assertNotIn("K", game.castling_rights)
        self.assertNotIn("Q", game.castling_rights)
        self.assertIn("k", game.castling_rights)
        self.assertIn("q", game.castling_rights)

    def test_rook_move_removes_one_castling_right(self) -> None:
        """Moving a rook removes only that side's castling rights."""
        game = ChessGame()
        game.from_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
        game.make_move((7, 0), (7, 1))  # Rh1-h2
        self.assertNotIn("K", game.castling_rights)
        self.assertIn("Q", game.castling_rights)


class TestCheckDetection(unittest.TestCase):
    """Tests for check detection."""

    def test_pawn_check(self) -> None:
        """Pawn gives check diagonally."""
        game = ChessGame()
        game.from_fen("8/8/8/8/3k4/4P3/8/4K3 b - - 0 1")
        # Black king on d4, white pawn on e3 - pawn attacks d4
        self.assertTrue(game.is_in_check(is_white=False))

    def test_knight_check(self) -> None:
        """Knight gives check."""
        game = ChessGame()
        game.from_fen("8/8/8/8/3k4/5N2/8/4K3 b - - 0 1")
        # Black king on d4, white knight on f3 - knight attacks d4
        self.assertTrue(game.is_in_check(is_white=False))

    def test_bishop_check(self) -> None:
        """Bishop gives check."""
        game = ChessGame()
        game.from_fen("8/8/8/8/3k4/8/5B2/4K3 b - - 0 1")
        # Black king on d4, white bishop on f2 - bishop attacks d4
        self.assertTrue(game.is_in_check(is_white=False))

    def test_rook_check(self) -> None:
        """Rook gives check."""
        game = ChessGame()
        game.from_fen("8/8/8/8/R2k4/8/8/4K3 b - - 0 1")
        # Black king on d4, white rook on a4 - rook attacks d4
        self.assertTrue(game.is_in_check(is_white=False))

    def test_queen_check(self) -> None:
        """Queen gives check."""
        game = ChessGame()
        game.from_fen("8/8/8/8/3k4/8/8/3QK3 b - - 0 1")
        # Black king on d4, white queen on d1 - queen attacks d4
        self.assertTrue(game.is_in_check(is_white=False))

    def test_no_check_from_castling_square(self) -> None:
        """King cannot give 'check' via castling move squares."""
        game = ChessGame()
        # White king on e1 can castle but black king on g1 is NOT in check
        # (this is a weird position but tests the attack detection)
        game.from_fen("8/8/8/8/8/8/8/4K1k1 b KQ - 0 1")
        # Black king on g1 should NOT be in check from white king on e1
        # (even though castling would land on g1)
        self.assertFalse(game.is_in_check(is_white=False))

    def test_no_check_when_safe(self) -> None:
        """No false positives for check detection."""
        game = ChessGame()
        game.from_fen("8/8/8/8/3k4/8/8/4K3 b - - 0 1")
        # Just two kings, no check
        self.assertFalse(game.is_in_check(is_white=False))
        self.assertFalse(game.is_in_check(is_white=True))


class TestPromotion(unittest.TestCase):
    """Tests for pawn promotion."""

    def test_pawn_promotion_to_queen(self) -> None:
        """Default promotion to queen works."""
        game = ChessGame()
        game.from_fen("8/4P3/8/8/8/8/8/4K2k w - - 0 1")
        game.make_move((4, 6), (4, 7))  # e7-e8
        self.assertEqual(game.board[7][4], "Q")

    def test_pawn_promotion_to_knight(self) -> None:
        """Promotion to knight works."""
        game = ChessGame()
        game.from_fen("8/4P3/8/8/8/8/8/4K2k w - - 0 1")
        game.make_move((4, 6), (4, 7), promotion="N")  # e7-e8=N
        self.assertEqual(game.board[7][4], "N")

    def test_pawn_promotion_to_rook(self) -> None:
        """Promotion to rook works."""
        game = ChessGame()
        game.from_fen("8/4P3/8/8/8/8/8/4K2k w - - 0 1")
        game.make_move((4, 6), (4, 7), promotion="R")  # e7-e8=R
        self.assertEqual(game.board[7][4], "R")

    def test_pawn_promotion_to_bishop(self) -> None:
        """Promotion to bishop works."""
        game = ChessGame()
        game.from_fen("8/4P3/8/8/8/8/8/4K2k w - - 0 1")
        game.make_move((4, 6), (4, 7), promotion="B")  # e7-e8=B
        self.assertEqual(game.board[7][4], "B")

    def test_invalid_promotion_defaults_to_queen(self) -> None:
        """Invalid promotion piece defaults to queen."""
        game = ChessGame()
        game.from_fen("8/4P3/8/8/8/8/8/4K2k w - - 0 1")
        game.make_move((4, 6), (4, 7), promotion="X")  # Invalid piece
        self.assertEqual(game.board[7][4], "Q")

    def test_promotion_none_defaults_to_queen(self) -> None:
        """None promotion defaults to queen."""
        game = ChessGame()
        game.from_fen("8/4P3/8/8/8/8/8/4K2k w - - 0 1")
        game.make_move((4, 6), (4, 7), promotion=None)
        self.assertEqual(game.board[7][4], "Q")

    def test_black_pawn_promotion(self) -> None:
        """Black pawn promotion uses lowercase."""
        game = ChessGame()
        game.from_fen("4K2k/8/8/8/8/8/4p3/8 b - - 0 1")
        game.make_move((4, 1), (4, 0))  # e2-e1
        self.assertEqual(game.board[0][4], "q")


class TestEnPassant(unittest.TestCase):
    """Tests for en passant."""

    def test_en_passant_capture(self) -> None:
        """En passant capture works correctly."""
        game = ChessGame()
        # White pawn on e5, black just played d7-d5
        game.from_fen("4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1")
        moves = game.get_legal_moves(4, 4)  # e5
        self.assertIn((3, 5), moves)  # d6 en passant
        game.make_move((4, 4), (3, 5))  # exd6 e.p.
        self.assertEqual(game.board[5][3], "P")  # Pawn on d6
        self.assertEqual(game.board[4][3], "")  # d5 empty (captured pawn)

    def test_en_passant_only_immediate(self) -> None:
        """En passant only available immediately after pawn move."""
        game = ChessGame()
        game.from_fen("4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1")
        # Make a different move
        game.make_move((4, 0), (4, 1))  # Ke1-e2
        # Now en passant should be gone
        self.assertEqual(game.en_passant, "-")
        # Black moves
        game.make_move((4, 7), (4, 6))  # Ke8-e7
        # White pawn can no longer take en passant
        moves = game.get_legal_moves(4, 4)  # e5
        self.assertNotIn((3, 5), moves)


class TestMoveGeneration(unittest.TestCase):
    """Tests for basic move generation."""

    def test_pawn_moves_from_start(self) -> None:
        """Pawn can move 1 or 2 squares from starting position."""
        game = ChessGame()
        moves = game.get_legal_moves(4, 1)  # e2
        self.assertIn((4, 2), moves)  # e3
        self.assertIn((4, 3), moves)  # e4

    def test_pawn_blocked(self) -> None:
        """Pawn cannot move forward if blocked."""
        game = ChessGame()
        game.from_fen("4k3/8/8/8/4p3/4P3/8/4K3 w - - 0 1")
        moves = game.get_legal_moves(4, 2)  # e3
        self.assertNotIn((4, 3), moves)  # e4 blocked

    def test_pawn_double_move_blocked(self) -> None:
        """Pawn cannot double move if first square blocked."""
        game = ChessGame()
        game.from_fen("4k3/8/8/8/8/4p3/4P3/4K3 w - - 0 1")
        moves = game.get_legal_moves(4, 1)  # e2
        self.assertNotIn((4, 2), moves)  # e3 blocked
        self.assertNotIn((4, 3), moves)  # e4 not reachable

    def test_knight_moves_all_eight(self) -> None:
        """Knight can move to all 8 squares when in center."""
        game = ChessGame()
        game.from_fen("4k3/8/8/8/3N4/8/8/4K3 w - - 0 1")
        moves = game.get_legal_moves(3, 3)  # d4
        expected = [
            (1, 2), (1, 4),  # b3, b5
            (2, 1), (2, 5),  # c2, c6
            (4, 1), (4, 5),  # e2, e6
            (5, 2), (5, 4),  # f3, f5
        ]
        for square in expected:
            self.assertIn(square, moves)

    def test_knight_moves_corner(self) -> None:
        """Knight on corner has limited moves."""
        game = ChessGame()
        game.from_fen("4k3/8/8/8/8/8/8/N3K3 w - - 0 1")
        moves = game.get_legal_moves(0, 0)  # a1
        expected = [(1, 2), (2, 1)]  # b3, c2
        self.assertEqual(sorted(moves), sorted(expected))

    def test_sliding_pieces_blocked_by_own(self) -> None:
        """Sliding pieces stop at own pieces."""
        game = ChessGame()
        game.from_fen("4k3/8/8/8/8/8/4P3/4RK2 w - - 0 1")
        moves = game.get_legal_moves(4, 0)  # e1 rook
        # Rook should not be able to reach e2 (own pawn)
        self.assertNotIn((4, 1), moves)

    def test_sliding_pieces_capture_enemy(self) -> None:
        """Sliding pieces can capture enemy pieces."""
        game = ChessGame()
        game.from_fen("4k3/8/8/8/8/8/4p3/4RK2 w - - 0 1")
        moves = game.get_legal_moves(4, 0)  # e1 rook
        # Rook can capture pawn on e2
        self.assertIn((4, 1), moves)
        # But cannot go past it
        self.assertNotIn((4, 2), moves)


class TestFEN(unittest.TestCase):
    """Tests for FEN parsing and generation."""

    def test_starting_position(self) -> None:
        """Starting position FEN is correct."""
        game = ChessGame()
        fen = game.to_fen()
        self.assertTrue(fen.startswith(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
        ))

    def test_round_trip(self) -> None:
        """FEN round-trip preserves position."""
        fen = "r3k2r/pp1b1ppp/2n1pn2/q1pp4/3P1B2/2PBPN2/PP1N1PPP/R2QK2R w KQkq - 0 1"
        game = ChessGame()
        game.from_fen(fen)
        result = game.to_fen()
        self.assertEqual(fen, result)


if __name__ == "__main__":
    unittest.main()
