"""Chess game logic and AI communication."""

from __future__ import annotations

import os
import re
import subprocess
import typing


# Starting position FEN
STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


class ChessGame:
    """Manages chess game state and AI communication."""

    def __init__(
        self,
        mode: str = "human-ai",
        human_color: str = "white",
        ai_time: float = 5.0,
        fen: typing.Optional[str] = None,
        ai_path: typing.Optional[str] = None,
        worst_mode: bool = False,
    ) -> None:
        """Initialize the chess game.

        Args:
            mode: Game mode ("human-ai" or "ai-ai").
            human_color: Human's color in human-ai mode.
            ai_time: Time limit for AI moves in seconds.
            fen: Starting position FEN string.
            ai_path: Path to chess_ai binary.
            worst_mode: If True, AI picks worst possible moves.
        """
        self.mode = mode
        self.human_color = human_color
        self.ai_time = ai_time
        self.worst_mode = worst_mode

        # Find AI binary
        if ai_path:
            self.ai_path = ai_path
        else:
            # Look for binary in same directory as this file
            parent_dir = os.path.dirname(os.path.abspath(__file__))
            script_dir = os.path.dirname(parent_dir)
            self.ai_path = os.path.join(script_dir, "chess_ai")

        # Game state
        self.board: typing.List[typing.List[str]] = [[""]*8 for _ in range(8)]
        self.turn: str = "white"
        self.move_number: int = 1
        self.halfmove_clock: int = 0
        self.castling_rights: str = "KQkq"
        self.en_passant: str = "-"
        self.move_history: typing.List[str] = []
        self.position_history: typing.List[str] = []
        self.captured_white: typing.List[str] = []  # Pieces white has captured
        self.captured_black: typing.List[str] = []  # Pieces black has captured
        self.last_move: typing.Optional[
            typing.Tuple[typing.Tuple[int, int], typing.Tuple[int, int]]
        ] = None
        self.game_over: bool = False
        self.game_result: str = ""

        # Initialize from FEN
        self.from_fen(fen or STARTING_FEN)

    def from_fen(self, fen: str) -> None:
        """Load position from FEN string.

        Args:
            fen: FEN string.
        """
        parts = fen.split()

        # Board position
        rows = parts[0].split("/")
        for rank in range(8):
            file = 0
            for char in rows[7 - rank]:  # FEN starts from rank 8
                if char.isdigit():
                    for _ in range(int(char)):
                        self.board[rank][file] = ""
                        file += 1
                else:
                    self.board[rank][file] = char
                    file += 1

        # Active color
        self.turn = "white" if parts[1] == "w" else "black"

        # Castling rights
        self.castling_rights = parts[2] if len(parts) > 2 else "-"

        # En passant
        self.en_passant = parts[3] if len(parts) > 3 else "-"

        # Halfmove clock
        self.halfmove_clock = int(parts[4]) if len(parts) > 4 else 0

        # Fullmove number
        self.move_number = int(parts[5]) if len(parts) > 5 else 1

    def to_fen(self) -> str:
        """Convert current position to FEN string.

        Returns:
            FEN string.
        """
        # Board position
        rows = []
        for rank in range(7, -1, -1):  # FEN starts from rank 8
            row = ""
            empty = 0
            for file in range(8):
                piece = self.board[rank][file]
                if piece:
                    if empty > 0:
                        row += str(empty)
                        empty = 0
                    row += piece
                else:
                    empty += 1
            if empty > 0:
                row += str(empty)
            rows.append(row)

        position = "/".join(rows)
        color = "w" if self.turn == "white" else "b"

        return (
            f"{position} {color} {self.castling_rights} "
            f"{self.en_passant} {self.halfmove_clock} {self.move_number}"
        )

    def get_piece_at(self, file: int, rank: int) -> str:
        """Get piece at given square.

        Args:
            file: File index (0-7).
            rank: Rank index (0-7).

        Returns:
            Piece character or empty string.
        """
        if 0 <= file < 8 and 0 <= rank < 8:
            return self.board[rank][file]
        return ""

    def is_own_piece(self, file: int, rank: int) -> bool:
        """Check if square has a piece belonging to current player.

        Args:
            file: File index.
            rank: Rank index.

        Returns:
            True if square has own piece.
        """
        piece = self.get_piece_at(file, rank)
        if not piece:
            return False
        is_white_piece = piece.isupper()
        is_white_turn = self.turn == "white"
        return is_white_turn == is_white_piece

    def get_legal_moves(
        self, file: int, rank: int
    ) -> typing.List[typing.Tuple[int, int]]:
        """Get legal moves for piece at given square.

        This is a simplified implementation. For complete legality checking,
        we rely on the AI engine.

        Args:
            file: File index.
            rank: Rank index.

        Returns:
            List of (file, rank) tuples for legal destinations.
        """
        piece = self.get_piece_at(file, rank)
        if not piece:
            return []

        moves = []
        piece_type = piece.upper()
        is_white = piece.isupper()

        # Generate pseudo-legal moves based on piece type
        if piece_type == "P":
            moves = self._get_pawn_moves(file, rank, is_white)
        elif piece_type == "N":
            moves = self._get_knight_moves(file, rank, is_white)
        elif piece_type == "B":
            moves = self._get_bishop_moves(file, rank, is_white)
        elif piece_type == "R":
            moves = self._get_rook_moves(file, rank, is_white)
        elif piece_type == "Q":
            moves = self._get_queen_moves(file, rank, is_white)
        elif piece_type == "K":
            moves = self._get_king_moves(file, rank, is_white)

        return moves

    def _get_pawn_moves(
        self, file: int, rank: int, is_white: bool
    ) -> typing.List[typing.Tuple[int, int]]:
        """Get pawn moves."""
        moves = []
        direction = 1 if is_white else -1
        start_rank = 1 if is_white else 6

        # Forward one
        new_rank = rank + direction
        if 0 <= new_rank < 8 and not self.board[new_rank][file]:
            moves.append((file, new_rank))
            # Forward two from starting position
            if rank == start_rank:
                new_rank2 = rank + 2 * direction
                if not self.board[new_rank2][file]:
                    moves.append((file, new_rank2))

        # Captures
        for df in [-1, 1]:
            new_file = file + df
            new_rank = rank + direction
            if 0 <= new_file < 8 and 0 <= new_rank < 8:
                target = self.board[new_rank][new_file]
                if target and target.isupper() != is_white:
                    moves.append((new_file, new_rank))
                # En passant
                ep_square = self._parse_square(self.en_passant)
                if ep_square and ep_square == (new_file, new_rank):
                    moves.append((new_file, new_rank))

        return moves

    def _get_knight_moves(
        self, file: int, rank: int, is_white: bool
    ) -> typing.List[typing.Tuple[int, int]]:
        """Get knight moves."""
        moves = []
        deltas = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        for df, dr in deltas:
            nf, nr = file + df, rank + dr
            if 0 <= nf < 8 and 0 <= nr < 8:
                target = self.board[nr][nf]
                if not target or target.isupper() != is_white:
                    moves.append((nf, nr))
        return moves

    def _get_sliding_moves(
        self,
        file: int,
        rank: int,
        is_white: bool,
        directions: typing.List[typing.Tuple[int, int]],
    ) -> typing.List[typing.Tuple[int, int]]:
        """Get moves for sliding pieces (bishop, rook, queen)."""
        moves = []
        for df, dr in directions:
            nf, nr = file + df, rank + dr
            while 0 <= nf < 8 and 0 <= nr < 8:
                target = self.board[nr][nf]
                if not target:
                    moves.append((nf, nr))
                elif target.isupper() != is_white:
                    moves.append((nf, nr))
                    break
                else:
                    break
                nf += df
                nr += dr
        return moves

    def _get_bishop_moves(
        self, file: int, rank: int, is_white: bool
    ) -> typing.List[typing.Tuple[int, int]]:
        """Get bishop moves."""
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        return self._get_sliding_moves(file, rank, is_white, directions)

    def _get_rook_moves(
        self, file: int, rank: int, is_white: bool
    ) -> typing.List[typing.Tuple[int, int]]:
        """Get rook moves."""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        return self._get_sliding_moves(file, rank, is_white, directions)

    def _get_queen_moves(
        self, file: int, rank: int, is_white: bool
    ) -> typing.List[typing.Tuple[int, int]]:
        """Get queen moves."""
        bishop_moves = self._get_bishop_moves(file, rank, is_white)
        rook_moves = self._get_rook_moves(file, rank, is_white)
        return bishop_moves + rook_moves

    def _get_king_moves(
        self, file: int, rank: int, is_white: bool
    ) -> typing.List[typing.Tuple[int, int]]:
        """Get king moves including castling."""
        moves = []
        for df in [-1, 0, 1]:
            for dr in [-1, 0, 1]:
                if df == 0 and dr == 0:
                    continue
                nf, nr = file + df, rank + dr
                if 0 <= nf < 8 and 0 <= nr < 8:
                    target = self.board[nr][nf]
                    if not target or target.isupper() != is_white:
                        moves.append((nf, nr))

        # Castling (simplified - doesn't check for attacks through squares)
        if is_white and rank == 0 and file == 4:
            kingside_clear = not self.board[0][5] and not self.board[0][6]
            kingside_rook = self.board[0][7] == "R"
            if "K" in self.castling_rights and kingside_clear and kingside_rook:
                moves.append((6, 0))  # Kingside
            queenside_clear = (
                not self.board[0][1]
                and not self.board[0][2]
                and not self.board[0][3]
            )
            queenside_rook = self.board[0][0] == "R"
            if "Q" in self.castling_rights and queenside_clear and queenside_rook:
                moves.append((2, 0))  # Queenside
        elif not is_white and rank == 7 and file == 4:
            kingside_clear = not self.board[7][5] and not self.board[7][6]
            kingside_rook = self.board[7][7] == "r"
            if "k" in self.castling_rights and kingside_clear and kingside_rook:
                moves.append((6, 7))  # Kingside
            queenside_clear = (
                not self.board[7][1]
                and not self.board[7][2]
                and not self.board[7][3]
            )
            queenside_rook = self.board[7][0] == "r"
            if "q" in self.castling_rights and queenside_clear and queenside_rook:
                moves.append((2, 7))  # Queenside

        return moves

    def _parse_square(
        self, square: str
    ) -> typing.Optional[typing.Tuple[int, int]]:
        """Parse algebraic notation to (file, rank)."""
        if not square or square == "-" or len(square) < 2:
            return None
        file = ord(square[0].lower()) - ord('a')
        rank = int(square[1]) - 1
        if 0 <= file < 8 and 0 <= rank < 8:
            return (file, rank)
        return None

    def _square_to_notation(self, file: int, rank: int) -> str:
        """Convert (file, rank) to algebraic notation."""
        return f"{chr(ord('a') + file)}{rank + 1}"

    def make_move(
        self,
        from_pos: typing.Tuple[int, int],
        to_pos: typing.Tuple[int, int],
        promotion: typing.Optional[str] = "Q",
    ) -> bool:
        """Make a move on the board.

        Args:
            from_pos: Source square (file, rank).
            to_pos: Destination square (file, rank).
            promotion: Piece to promote to (default Queen).

        Returns:
            True if move was made successfully.
        """
        from_file, from_rank = from_pos
        to_file, to_rank = to_pos

        piece = self.board[from_rank][from_file]
        if not piece:
            return False

        captured = self.board[to_rank][to_file]
        is_white = piece.isupper()

        # Record captured piece
        if captured:
            if is_white:
                self.captured_white.append(captured)
            else:
                self.captured_black.append(captured)
            # Update castling rights if a rook was captured
            if to_pos == (7, 0):  # h1 - white kingside rook
                self.castling_rights = self.castling_rights.replace("K", "")
            elif to_pos == (0, 0):  # a1 - white queenside rook
                self.castling_rights = self.castling_rights.replace("Q", "")
            elif to_pos == (7, 7):  # h8 - black kingside rook
                self.castling_rights = self.castling_rights.replace("k", "")
            elif to_pos == (0, 7):  # a8 - black queenside rook
                self.castling_rights = self.castling_rights.replace("q", "")

        # Handle special moves
        piece_type = piece.upper()

        # En passant capture
        ep_square = self._parse_square(self.en_passant)
        if piece_type == "P" and (to_file, to_rank) == ep_square:
            ep_rank = to_rank - 1 if is_white else to_rank + 1
            captured_pawn = self.board[ep_rank][to_file]
            if is_white:
                self.captured_white.append(captured_pawn)
            else:
                self.captured_black.append(captured_pawn)
            self.board[ep_rank][to_file] = ""

        # Castling
        if piece_type == "K" and abs(to_file - from_file) == 2:
            if to_file > from_file:  # Kingside
                self.board[from_rank][5] = self.board[from_rank][7]
                self.board[from_rank][7] = ""
            else:  # Queenside
                self.board[from_rank][3] = self.board[from_rank][0]
                self.board[from_rank][0] = ""

        # Update en passant square
        if piece_type == "P" and abs(to_rank - from_rank) == 2:
            ep_rank = (from_rank + to_rank) // 2
            self.en_passant = self._square_to_notation(to_file, ep_rank)
        else:
            self.en_passant = "-"

        # Update castling rights
        if piece_type == "K":
            if is_white:
                rights = self.castling_rights.replace("K", "").replace("Q", "")
            else:
                rights = self.castling_rights.replace("k", "").replace("q", "")
            self.castling_rights = rights
        if piece_type == "R":
            if from_pos == (0, 0):
                self.castling_rights = self.castling_rights.replace("Q", "")
            elif from_pos == (7, 0):
                self.castling_rights = self.castling_rights.replace("K", "")
            elif from_pos == (0, 7):
                self.castling_rights = self.castling_rights.replace("q", "")
            elif from_pos == (7, 7):
                self.castling_rights = self.castling_rights.replace("k", "")
        if not self.castling_rights:
            self.castling_rights = "-"

        # Move the piece
        self.board[to_rank][to_file] = piece
        self.board[from_rank][from_file] = ""

        # Pawn promotion
        if piece_type == "P" and (to_rank == 7 or to_rank == 0):
            # Validate promotion piece
            valid_promotions = {"Q", "R", "B", "N"}
            promo_piece = promotion.upper() if promotion else "Q"
            if promo_piece not in valid_promotions:
                promo_piece = "Q"
            promoted = promo_piece if is_white else promo_piece.lower()
            self.board[to_rank][to_file] = promoted

        # Record move
        from_notation = self._square_to_notation(from_file, from_rank)
        to_notation = self._square_to_notation(to_file, to_rank)
        move_str = f"{from_notation}{to_notation}"
        self.move_history.append(move_str)
        self.last_move = (from_pos, to_pos)

        # Update halfmove clock
        if piece_type == "P" or captured:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        # Switch turn
        if self.turn == "black":
            self.move_number += 1
        self.turn = "black" if self.turn == "white" else "white"

        # Record position for repetition detection
        self.position_history.append(self.to_fen().split()[0])

        return True

    def get_ai_move(
        self,
    ) -> typing.Optional[
        typing.Tuple[
            typing.Tuple[int, int], typing.Tuple[int, int], typing.Optional[str]
        ]
    ]:
        """Get move from AI engine.

        Returns:
            Tuple of (from_pos, to_pos, promotion) or None if error.
            promotion is the piece to promote to (Q, R, B, N) or None.
        """
        fen = self.to_fen()

        try:
            # Build command with optional --worst flag.
            cmd = [self.ai_path]
            if self.worst_mode:
                cmd.append("--worst")
            cmd.append(fen)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.ai_time + 10
            )

            # Parse output to find move
            # Expected format: "e2 -> e4" or "e7 -> e8=Q" for promotion
            output = result.stdout

            # Try different patterns
            patterns = [
                # e2 -> e4 or e7 -> e8=Q (with optional promotion)
                r'([a-h][1-8])\s*->\s*([a-h][1-8])(?:=([QRBN]))?',
                # e2e4 or e7e8q (UCI format with optional promotion)
                r'([a-h][1-8])([a-h][1-8])([qrbn])?',
            ]

            for pattern in patterns:
                match = re.search(pattern, output, re.IGNORECASE)
                if match:
                    from_sq = match.group(1).lower()
                    to_sq = match.group(2).lower()
                    promotion = None
                    if len(match.groups()) >= 3 and match.group(3):
                        promotion = match.group(3).upper()

                    from_pos = self._parse_square(from_sq)
                    to_pos = self._parse_square(to_sq)

                    if from_pos and to_pos:
                        # Auto-detect promotion if pawn reaches back rank
                        if promotion is None:
                            piece = self.board[from_pos[1]][from_pos[0]]
                            if piece and piece.lower() == "p":
                                if (piece == "P" and to_pos[1] == 7) or \
                                   (piece == "p" and to_pos[1] == 0):
                                    promotion = "Q"  # Default to queen

                        return (from_pos, to_pos, promotion)

            return None

        except subprocess.TimeoutExpired:
            return None
        except Exception:
            return None

    def find_king(
        self, is_white: bool
    ) -> typing.Optional[typing.Tuple[int, int]]:
        """Find the king's position.

        Args:
            is_white: True to find white king, False for black.

        Returns:
            King position (file, rank) or None.
        """
        king = "K" if is_white else "k"
        for rank in range(8):
            for file in range(8):
                if self.board[rank][file] == king:
                    return (file, rank)
        return None

    def _get_attack_squares(
        self, file: int, rank: int
    ) -> typing.List[typing.Tuple[int, int]]:
        """Get squares attacked by piece (excludes castling and en passant).

        This is used for check detection where we only care about actual
        attack squares, not special moves.

        Args:
            file: File index (0-7).
            rank: Rank index (0-7).

        Returns:
            List of (file, rank) tuples for attacked squares.
        """
        piece = self.get_piece_at(file, rank)
        if not piece:
            return []

        piece_type = piece.upper()
        is_white = piece.isupper()

        if piece_type == "P":
            # Pawns attack diagonally only
            attacks = []
            direction = 1 if is_white else -1
            for df in [-1, 1]:
                nf, nr = file + df, rank + direction
                if 0 <= nf < 8 and 0 <= nr < 8:
                    attacks.append((nf, nr))
            return attacks
        elif piece_type == "N":
            return self._get_knight_moves(file, rank, is_white)
        elif piece_type == "B":
            return self._get_bishop_moves(file, rank, is_white)
        elif piece_type == "R":
            return self._get_rook_moves(file, rank, is_white)
        elif piece_type == "Q":
            return self._get_queen_moves(file, rank, is_white)
        elif piece_type == "K":
            # King attacks adjacent squares only (no castling)
            attacks = []
            for df in [-1, 0, 1]:
                for dr in [-1, 0, 1]:
                    if df == 0 and dr == 0:
                        continue
                    nf, nr = file + df, rank + dr
                    if 0 <= nf < 8 and 0 <= nr < 8:
                        attacks.append((nf, nr))
            return attacks
        return []

    def is_in_check(self, is_white: bool) -> bool:
        """Check if the given side's king is in check.

        Args:
            is_white: True to check if white is in check.

        Returns:
            True if king is in check.
        """
        king_pos = self.find_king(is_white)
        if not king_pos:
            return False

        # Check if any enemy piece attacks the king
        for rank in range(8):
            for file in range(8):
                piece = self.board[rank][file]
                if piece and piece.isupper() != is_white:
                    attacks = self._get_attack_squares(file, rank)
                    if king_pos in attacks:
                        return True
        return False

    def get_last_move_notation(self) -> str:
        """Get the last move in algebraic notation.

        Returns:
            Move string like "e2 -> e4".
        """
        if self.last_move:
            from_pos, to_pos = self.last_move
            from_str = self._square_to_notation(from_pos[0], from_pos[1])
            to_str = self._square_to_notation(to_pos[0], to_pos[1])
            return f"{from_str} -> {to_str}"
        return ""

    @property
    def last_move_str(self) -> str:
        """Get the last move in algebraic notation.

        Returns:
            Move string like "e2 -> e4".
        """
        return self.get_last_move_notation()

    @property
    def in_check(self) -> bool:
        """Check if the current player's king is in check.

        Returns:
            True if current player's king is in check.
        """
        is_white = self.turn == "white"
        return self.is_in_check(is_white)

    @property
    def captured_by_white(self) -> typing.List[str]:
        """Get pieces captured by white.

        Returns:
            List of piece characters captured by white.
        """
        return self.captured_white

    @property
    def captured_by_black(self) -> typing.List[str]:
        """Get pieces captured by black.

        Returns:
            List of piece characters captured by black.
        """
        return self.captured_black

    def is_human_turn(self) -> bool:
        """Check if it's the human's turn.

        Returns:
            True if human should move.
        """
        if self.mode == "ai-ai":
            return False
        return self.turn == self.human_color
