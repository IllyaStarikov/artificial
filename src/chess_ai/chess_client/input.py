"""Interactive keyboard input handling for chess client."""

from __future__ import annotations

import sys
import typing

import readchar


# Key mappings
KEY_UP = readchar.key.UP
KEY_DOWN = readchar.key.DOWN
KEY_LEFT = readchar.key.LEFT
KEY_RIGHT = readchar.key.RIGHT
KEY_ENTER = readchar.key.ENTER
KEY_ESCAPE = readchar.key.ESC


class InteractiveInput:
    """Handles interactive keyboard input for chess piece selection.

    Manages cursor position, piece selection state, and valid move tracking.
    Provides arrow key navigation and Enter/Escape for selection/cancellation.
    """

    def __init__(self, start_file: int = 4, start_rank: int = 0) -> None:
        """Initialize the input handler.

        Args:
            start_file: Starting cursor file position (0-7, default e1).
            start_rank: Starting cursor rank position (0-7, default rank 1).
        """
        self.cursor_file = start_file
        self.cursor_rank = start_rank
        self.selected_piece: typing.Optional[typing.Tuple[int, int]] = None
        self.valid_moves: typing.List[typing.Tuple[int, int]] = []
        self.flipped = False

    @property
    def cursor_pos(self) -> typing.Tuple[int, int]:
        """Get current cursor position.

        Returns:
            Tuple of (file, rank) for cursor position.
        """
        return (self.cursor_file, self.cursor_rank)

    def set_flipped(self, flipped: bool) -> None:
        """Set board orientation for correct key mapping.

        Args:
            flipped: True if playing as black (board flipped).
        """
        self.flipped = flipped

    def set_valid_moves(
        self, moves: typing.List[typing.Tuple[int, int]]
    ) -> None:
        """Set the list of valid moves for the selected piece.

        Args:
            moves: List of valid destination squares (file, rank).
        """
        self.valid_moves = moves

    def clear_selection(self) -> None:
        """Clear the current piece selection and valid moves."""
        self.selected_piece = None
        self.valid_moves = []

    def select_piece(self) -> None:
        """Select the piece at the current cursor position."""
        self.selected_piece = self.cursor_pos

    def read_key(self) -> str:
        """Read a single keypress.

        Returns:
            The key that was pressed.
        """
        return readchar.readkey()

    def _move_cursor(self, d_file: int, d_rank: int) -> None:
        """Move cursor by the given delta, clamping to board bounds.

        Args:
            d_file: File delta (-1, 0, or 1).
            d_rank: Rank delta (-1, 0, or 1).
        """
        # When flipped, reverse the direction
        if self.flipped:
            d_file = -d_file
            d_rank = -d_rank

        new_file = self.cursor_file + d_file
        new_rank = self.cursor_rank + d_rank

        # Clamp to board bounds
        self.cursor_file = max(0, min(7, new_file))
        self.cursor_rank = max(0, min(7, new_rank))

    def handle_key(
        self, key: str
    ) -> typing.Tuple[
        str,
        typing.Optional[
            typing.Tuple[typing.Tuple[int, int], typing.Tuple[int, int]]
        ],
    ]:
        """Handle a keypress and return the resulting action.

        Args:
            key: The key that was pressed.

        Returns:
            Tuple of (action, move_data) where:
            - action: "move_cursor", "select", "deselect", "make_move",
                      "quit", "flip", "undo", "new_game", "none"
            - move_data: For "make_move", tuple of ((from_file, from_rank),
                         (to_file, to_rank)), otherwise None.
        """
        if key == KEY_UP:
            self._move_cursor(0, 1)
            return ("move_cursor", None)

        if key == KEY_DOWN:
            self._move_cursor(0, -1)
            return ("move_cursor", None)

        if key == KEY_LEFT:
            self._move_cursor(-1, 0)
            return ("move_cursor", None)

        if key == KEY_RIGHT:
            self._move_cursor(1, 0)
            return ("move_cursor", None)

        if key == KEY_ENTER or key == " ":
            if self.selected_piece is None:
                # Selecting a piece
                return ("select", None)

            # Making a move
            if self.cursor_pos in self.valid_moves:
                move = (self.selected_piece, self.cursor_pos)
                return ("make_move", move)

            # Clicking on same square deselects
            if self.cursor_pos == self.selected_piece:
                return ("deselect", None)

            # Clicking on invalid square - try to select new piece
            return ("select", None)

        if key == KEY_ESCAPE:
            if self.selected_piece is not None:
                return ("deselect", None)
            return ("none", None)

        if key.lower() == "q":
            return ("quit", None)

        if key.lower() == "f":
            return ("flip", None)

        if key.lower() == "u":
            return ("undo", None)

        if key.lower() == "n":
            return ("new_game", None)

        if key.lower() == "h":
            return ("help", None)

        return ("none", None)

    def get_square_notation(
        self, pos: typing.Optional[typing.Tuple[int, int]] = None
    ) -> str:
        """Convert position to algebraic notation.

        Args:
            pos: Position tuple (file, rank), or None to use cursor position.

        Returns:
            Algebraic notation string (e.g., "e4").
        """
        if pos is None:
            pos = self.cursor_pos
        file, rank = pos
        return f"{chr(ord('a') + file)}{rank + 1}"


class PromotionSelector:
    """Handles pawn promotion piece selection."""

    PIECES = ["q", "r", "b", "n"]
    PIECE_NAMES = ["Queen", "Rook", "Bishop", "Knight"]

    def __init__(self, is_white: bool = True) -> None:
        """Initialize the promotion selector.

        Args:
            is_white: True if promoting white pawn, False for black.
        """
        self.is_white = is_white
        self.selected_index = 0

    def handle_key(self, key: str) -> typing.Optional[str]:
        """Handle key press for promotion selection.

        Args:
            key: The key that was pressed.

        Returns:
            Selected piece character if Enter pressed, None otherwise.
            Returns "cancel" if Escape pressed.
        """
        if key == KEY_UP or key == KEY_LEFT:
            self.selected_index = (self.selected_index - 1) % 4
            return None

        if key == KEY_DOWN or key == KEY_RIGHT:
            self.selected_index = (self.selected_index + 1) % 4
            return None

        if key == KEY_ENTER or key == " ":
            piece = self.PIECES[self.selected_index]
            return piece.upper() if self.is_white else piece

        if key in "1234":
            idx = int(key) - 1
            piece = self.PIECES[idx]
            return piece.upper() if self.is_white else piece

        if key.lower() in "qrbn":
            piece = key.lower()
            return piece.upper() if self.is_white else piece

        if key == KEY_ESCAPE:
            return "cancel"

        return None

    def get_selected_piece(self) -> str:
        """Get the currently highlighted piece.

        Returns:
            Piece character for the selected promotion option.
        """
        piece = self.PIECES[self.selected_index]
        return piece.upper() if self.is_white else piece

    def get_selected_name(self) -> str:
        """Get the name of the currently highlighted piece.

        Returns:
            Human-readable name of the selected piece.
        """
        return self.PIECE_NAMES[self.selected_index]
