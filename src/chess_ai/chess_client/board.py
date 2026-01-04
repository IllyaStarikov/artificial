"""Chess board rendering with rich library."""

from __future__ import annotations

import typing

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


# Unicode chess pieces
WHITE_PIECES = {
    "K": "♔", "Q": "♕", "R": "♖", "B": "♗", "N": "♘", "P": "♙"
}
BLACK_PIECES = {
    "k": "♚", "q": "♛", "r": "♜", "b": "♝", "n": "♞", "p": "♟"
}

# All pieces combined
PIECE_SYMBOLS = {**WHITE_PIECES, **BLACK_PIECES}

# Square colors
LIGHT_SQUARE = "on grey85"
DARK_SQUARE = "on grey37"
CURSOR_STYLE = "bold reverse"
SELECTED_STYLE = "bold black on bright_yellow"
VALID_MOVE_STYLE = "bold green"
LAST_MOVE_STYLE = "on dark_goldenrod"
CHECK_STYLE = "bold white on red"


class ChessBoard:
    """Renders a chess board using the rich library."""

    def __init__(self) -> None:
        """Initialize the chess board renderer."""
        self.console = Console()

    def _get_square_color(self, file: int, rank: int) -> str:
        """Get the background color for a square.

        Args:
            file: File index (0-7, a-h).
            rank: Rank index (0-7, 1-8).

        Returns:
            Rich style string for the square background.
        """
        is_light = (file + rank) % 2 == 1
        return LIGHT_SQUARE if is_light else DARK_SQUARE

    def _render_square(
        self,
        piece: str,
        file: int,
        rank: int,
        is_cursor: bool = False,
        is_selected: bool = False,
        is_valid_move: bool = False,
        is_last_move: bool = False,
        is_check: bool = False,
    ) -> Text:
        """Render a single square.

        Args:
            piece: Piece character (or empty string).
            file: File index (0-7).
            rank: Rank index (0-7).
            is_cursor: Whether cursor is on this square.
            is_selected: Whether this piece is selected.
            is_valid_move: Whether this is a valid move destination.
            is_last_move: Whether this square was part of the last move.
            is_check: Whether the king on this square is in check.

        Returns:
            Rich Text object for the square.
        """
        base_color = self._get_square_color(file, rank)

        # Determine piece display
        if piece:
            symbol = PIECE_SYMBOLS.get(piece, piece)
            is_white_piece = piece.isupper()
            piece_color = "white" if is_white_piece else "black"
        else:
            symbol = " "
            piece_color = ""

        # Build style based on state
        if is_check:
            style = CHECK_STYLE
        elif is_selected:
            style = SELECTED_STYLE
        elif is_cursor:
            if piece_color:
                style = f"bold {piece_color} {CURSOR_STYLE}"
            else:
                style = CURSOR_STYLE
        elif is_last_move:
            if piece_color:
                style = f"{piece_color} {LAST_MOVE_STYLE}"
            else:
                style = LAST_MOVE_STYLE
        elif is_valid_move:
            if piece:
                # Capture available
                style = f"bold {piece_color} on red"
            else:
                # Empty square - show dot
                symbol = "·"
                style = f"{VALID_MOVE_STYLE} {base_color}"
        else:
            style = f"{piece_color} {base_color}" if piece_color else base_color

        return Text(f" {symbol} ", style=style)

    def render(
        self,
        board: typing.List[typing.List[str]],
        cursor: typing.Optional[typing.Tuple[int, int]] = None,
        selected: typing.Optional[typing.Tuple[int, int]] = None,
        valid_moves: typing.Optional[
            typing.List[typing.Tuple[int, int]]
        ] = None,
        last_move: typing.Optional[
            typing.Tuple[typing.Tuple[int, int], typing.Tuple[int, int]]
        ] = None,
        king_in_check: typing.Optional[typing.Tuple[int, int]] = None,
        flipped: bool = False,
    ) -> Text:
        """Render the chess board.

        Args:
            board: 8x8 list of piece characters (index [rank][file]).
            cursor: Current cursor position (file, rank).
            selected: Currently selected piece position (file, rank).
            valid_moves: List of valid move destinations (file, rank).
            last_move: Tuple of (from_pos, to_pos) for last move highlighting.
            king_in_check: Position of king in check (file, rank).
            flipped: If True, render from black's perspective.

        Returns:
            Rich Text representing the board.
        """
        valid_moves = valid_moves or []
        valid_moves_set = set(valid_moves)

        last_move_squares = set()
        if last_move:
            last_move_squares.add(last_move[0])
            last_move_squares.add(last_move[1])

        # Determine rank/file order based on perspective
        ranks = range(7, -1, -1) if not flipped else range(8)
        files = range(8) if not flipped else range(7, -1, -1)

        result = Text()

        for rank in ranks:
            # Rank label
            result.append(f" {rank + 1} ", style="bold cyan")

            for file in files:
                piece = board[rank][file] if board[rank][file] else ""

                is_cursor = cursor == (file, rank)
                is_selected = selected == (file, rank)
                is_valid_move = (file, rank) in valid_moves_set
                is_last_move = (file, rank) in last_move_squares
                is_check = king_in_check == (file, rank)

                square = self._render_square(
                    piece,
                    file,
                    rank,
                    is_cursor,
                    is_selected,
                    is_valid_move,
                    is_last_move,
                    is_check,
                )
                result.append_text(square)

            result.append("\n")

        # File labels
        result.append("   ")  # Align with rank labels
        file_chars = "abcdefgh" if not flipped else "hgfedcba"
        for char in file_chars:
            result.append(f" {char} ", style="bold cyan")
        result.append("\n")

        return result

    def render_status(
        self,
        turn: str,
        move_number: int,
        mode: str,
        human_color: str,
        last_move_str: str = "",
        status: str = "",
        captured_white: typing.Optional[typing.List[str]] = None,
        captured_black: typing.Optional[typing.List[str]] = None,
        show_controls: bool = True,
    ) -> Panel:
        """Render the status panel.

        Args:
            turn: Current turn ("white" or "black").
            move_number: Current move number.
            mode: Game mode ("human-ai" or "ai-ai").
            human_color: Human's color in human-ai mode.
            last_move_str: String representation of last move.
            status: Current game status (e.g., "Check!", "Checkmate").
            captured_white: Pieces captured by white.
            captured_black: Pieces captured by black.
            show_controls: Whether to show control hints.

        Returns:
            Rich Panel with status information.
        """
        captured_white = captured_white or []
        captured_black = captured_black or []

        status_text = Text()

        # Turn indicator
        turn_symbol = "♔" if turn == "white" else "♚"
        turn_style = "bold white" if turn == "white" else "bold"
        status_text.append(f"{turn_symbol} ", style=turn_style)
        status_text.append(f"{turn.capitalize()} to move", style="bold")

        # Move number
        status_text.append(f"  │  Move: {move_number}", style="dim")

        # Mode indicator
        if mode == "human-ai":
            is_human_turn = turn == human_color
            player = "[Human]" if is_human_turn else "[AI]"
            player_style = "bold cyan" if is_human_turn else "bold magenta"
            status_text.append(f"  |  {player}", style=player_style)

        status_text.append("\n")

        # Last move
        if last_move_str:
            status_text.append(f"Last: {last_move_str}", style="italic")
            status_text.append("\n")

        # Game status
        if status:
            if "checkmate" in status.lower():
                status_text.append(status, style="bold red")
            elif "check" in status.lower():
                status_text.append(status, style="bold yellow")
            elif "draw" in status.lower() or "stalemate" in status.lower():
                status_text.append(status, style="bold blue")
            else:
                status_text.append(status, style="italic cyan")
            status_text.append("\n")

        # Captured pieces
        if captured_white or captured_black:
            status_text.append("─" * 50, style="dim")
            status_text.append("\n")
            if captured_white:
                white_caps = " ".join(
                    PIECE_SYMBOLS.get(p, p) for p in captured_white
                )
                status_text.append(
                    f"White captured: {white_caps}\n", style="dim"
                )
            if captured_black:
                black_caps = " ".join(
                    PIECE_SYMBOLS.get(p, p) for p in captured_black
                )
                status_text.append(
                    f"Black captured: {black_caps}\n", style="dim"
                )

        # Controls
        if show_controls:
            status_text.append("─" * 50, style="dim")
            status_text.append("\n")
            controls = "[arrows]=move  [Enter]=select  [Esc]=cancel  [q]=quit"
            status_text.append(controls, style="dim")

        return Panel(
            status_text,
            title="Status",
            border_style="blue",
            padding=(0, 2),
        )

    def render_display(
        self,
        board: typing.List[typing.List[str]],
        turn: str,
        move_number: int,
        mode: str = "human-ai",
        human_color: str = "white",
        cursor: typing.Optional[typing.Tuple[int, int]] = None,
        selected: typing.Optional[typing.Tuple[int, int]] = None,
        valid_moves: typing.Optional[
            typing.List[typing.Tuple[int, int]]
        ] = None,
        last_move: typing.Optional[
            typing.Tuple[typing.Tuple[int, int], typing.Tuple[int, int]]
        ] = None,
        last_move_str: str = "",
        king_in_check: typing.Optional[typing.Tuple[int, int]] = None,
        status: str = "",
        captured_white: typing.Optional[typing.List[str]] = None,
        captured_black: typing.Optional[typing.List[str]] = None,
        show_controls: bool = True,
        flipped: bool = False,
    ) -> Panel:
        """Render the complete display with board and status.

        Args:
            board: 8x8 board state.
            turn: Current turn.
            move_number: Current move number.
            mode: Game mode.
            human_color: Human's color.
            cursor: Cursor position.
            selected: Selected piece position.
            valid_moves: Valid move destinations.
            last_move: Last move positions.
            last_move_str: Last move string.
            king_in_check: King in check position.
            status: Game status message.
            captured_white: Pieces captured by white.
            captured_black: Pieces captured by black.
            show_controls: Show control hints.
            flipped: Flip board perspective.

        Returns:
            Rich Panel with complete display.
        """
        board_table = self.render(
            board,
            cursor,
            selected,
            valid_moves,
            last_move,
            king_in_check,
            flipped,
        )
        status_panel = self.render_status(
            turn,
            move_number,
            mode,
            human_color,
            last_move_str,
            status,
            captured_white,
            captured_black,
            show_controls,
        )

        layout = Layout()
        board_panel = Panel(
            board_table,
            title="Chess Board",
            border_style="green",
            padding=(1, 2),
        )
        layout.split_column(
            Layout(board_panel, name="board"),
            Layout(status_panel, name="status", size=11),
        )

        return Panel(
            layout,
            title="[bold magenta]♔ Chess Client ♚[/bold magenta]",
            border_style="magenta",
            padding=(1, 2),
        )
