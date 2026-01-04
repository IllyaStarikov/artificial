#!/usr/bin/env python3
"""Chess client for playing against chess AI."""

from __future__ import annotations

import argparse
import os
import sys
import time
import typing

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

import chess_client
from chess_client.board import PIECE_SYMBOLS
from chess_client.input import PromotionSelector


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Namespace with game configuration options.
    """
    parser = argparse.ArgumentParser(
        description="Chess Client - Play against the Chess AI"
    )
    parser.add_argument(
        "--mode",
        choices=["human-ai", "ai-ai"],
        default="human-ai",
        help="Game mode (default: human-ai)",
    )
    parser.add_argument(
        "--color",
        choices=["white", "black"],
        default="white",
        help="Human's color in human-ai mode (default: white)",
    )
    parser.add_argument(
        "--ai-time",
        type=float,
        default=5.0,
        help="AI thinking time in seconds (default: 5.0)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.5,
        help="Delay between moves in ai-ai mode (default: 1.5)",
    )
    parser.add_argument(
        "--fen",
        type=str,
        help="Starting position in FEN notation",
    )
    parser.add_argument(
        "--ai-path",
        type=str,
        default="./chess_ai",
        help="Path to chess AI binary (default: ./chess_ai)",
    )
    parser.add_argument(
        "--worst",
        action="store_true",
        help="Enable worst mode (AI picks worst possible moves)",
    )

    return parser.parse_args()


class ChessClient:
    """Main chess client for interactive play."""

    def __init__(self, args: argparse.Namespace) -> None:
        """Initialize the chess client.

        Args:
            args: Parsed command line arguments.
        """
        self.mode = args.mode
        self.human_color = args.color
        self.ai_time = args.ai_time
        self.delay = args.delay
        self.worst_mode = args.worst

        self.console = Console()
        self.board_renderer = chess_client.ChessBoard()
        self.input_handler = chess_client.InteractiveInput()
        self.game = chess_client.ChessGame(
            ai_path=args.ai_path,
            ai_time=args.ai_time,
            worst_mode=args.worst,
        )

        # Set starting position
        if args.fen:
            self.game.from_fen(args.fen)

        # Set board orientation for black player
        self.flipped = self.human_color == "black"
        self.input_handler.set_flipped(self.flipped)

        # Set starting cursor position
        if self.flipped:
            self.input_handler.cursor_file = 4
            self.input_handler.cursor_rank = 7
        else:
            self.input_handler.cursor_file = 4
            self.input_handler.cursor_rank = 0

        self.running = True
        self.status_message = ""
        self.show_help = False

    def _get_king_in_check(self) -> typing.Optional[typing.Tuple[int, int]]:
        """Find the position of king in check.

        Returns:
            Position of king in check, or None if not in check.
        """
        if not self.game.in_check:
            return None

        # Find the current player's king
        king_char = "K" if self.game.turn == "white" else "k"
        for rank in range(8):
            for file in range(8):
                if self.game.board[rank][file] == king_char:
                    return (file, rank)
        return None

    def _render_display(self, thinking: bool = False) -> Panel:
        """Render the complete game display.

        Args:
            thinking: Whether AI is currently thinking.

        Returns:
            Rich Panel with complete game display.
        """
        status = self.status_message
        if thinking:
            status = "AI thinking..."
        elif self.game.game_over:
            status = self.game.game_result
        elif self.game.in_check:
            status = "Check!"

        return self.board_renderer.render_display(
            board=self.game.board,
            turn=self.game.turn,
            move_number=self.game.move_number,
            mode=self.mode,
            human_color=self.human_color,
            cursor=self.input_handler.cursor_pos,
            selected=self.input_handler.selected_piece,
            valid_moves=self.input_handler.valid_moves,
            last_move=self.game.last_move,
            last_move_str=self.game.last_move_str,
            king_in_check=self._get_king_in_check(),
            status=status,
            captured_white=self.game.captured_by_white,
            captured_black=self.game.captured_by_black,
            show_controls=self.mode == "human-ai",
            flipped=self.flipped,
        )

    def _render_promotion_dialog(
        self, selector: PromotionSelector
    ) -> Panel:
        """Render pawn promotion selection dialog.

        Args:
            selector: The promotion selector state.

        Returns:
            Rich Panel with promotion options.
        """
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("", width=3)
        table.add_column("", width=10)

        if selector.is_white:
            pieces = ["Q", "R", "B", "N"]
        else:
            pieces = ["q", "r", "b", "n"]
        names = ["Queen", "Rook", "Bishop", "Knight"]

        for i, (piece, name) in enumerate(zip(pieces, names)):
            symbol = PIECE_SYMBOLS.get(piece, piece)
            if i == selector.selected_index:
                style = "bold reverse"
            else:
                style = ""
            table.add_row(
                Text(f" {symbol} ", style=style),
                Text(f"[{i+1}] {name}", style=style),
            )

        return Panel(
            table,
            title="Promote to:",
            border_style="yellow",
        )

    def _handle_human_turn(self, live: Live) -> bool:
        """Handle human player's turn.

        Args:
            live: Rich Live context for display updates.

        Returns:
            True if game should continue, False to exit.
        """
        while True:
            live.update(self._render_display())

            key = self.input_handler.read_key()
            action, move_data = self.input_handler.handle_key(key)

            if action == "quit":
                return False

            if action == "flip":
                self.flipped = not self.flipped
                self.input_handler.set_flipped(self.flipped)
                continue

            if action == "help":
                self.show_help = not self.show_help
                continue

            if action == "move_cursor":
                continue

            if action == "select":
                pos = self.input_handler.cursor_pos
                piece = self.game.board[pos[1]][pos[0]]

                # Check if selecting own piece
                if piece:
                    is_white_piece = piece.isupper()
                    is_own_piece = (
                        (self.game.turn == "white" and is_white_piece) or
                        (self.game.turn == "black" and not is_white_piece)
                    )
                    if is_own_piece:
                        self.input_handler.select_piece()
                        moves = self.game.get_legal_moves(pos)
                        self.input_handler.set_valid_moves(moves)
                continue

            if action == "deselect":
                self.input_handler.clear_selection()
                continue

            if action == "make_move":
                from_pos, to_pos = move_data

                # Check for pawn promotion
                piece = self.game.board[from_pos[1]][from_pos[0]]
                is_pawn = piece and piece.lower() == "p"
                is_promotion_rank = (
                    (piece == "P" and to_pos[1] == 7) or
                    (piece == "p" and to_pos[1] == 0)
                )

                promotion_piece = None
                if is_pawn and is_promotion_rank:
                    promotion_piece = self._handle_promotion(
                        live, piece.isupper()
                    )
                    if promotion_piece == "cancel":
                        self.input_handler.clear_selection()
                        continue

                # Make the move
                success = self.game.make_move(from_pos, to_pos, promotion_piece)
                self.input_handler.clear_selection()

                if success:
                    return True

                self.status_message = "Invalid move!"
                continue

        return True

    def _handle_promotion(self, live: Live, is_white: bool) -> str:
        """Handle pawn promotion selection.

        Args:
            live: Rich Live context for display updates.
            is_white: True if promoting white pawn.

        Returns:
            Selected piece character, or "cancel" if cancelled.
        """
        selector = PromotionSelector(is_white)

        while True:
            # Render board with promotion dialog overlay
            display = self._render_display()
            dialog = self._render_promotion_dialog(selector)

            # Create combined layout
            layout = Layout()
            layout.split_column(
                Layout(display, name="board"),
                Layout(dialog, name="dialog", size=8),
            )
            live.update(layout)

            key = self.input_handler.read_key()
            result = selector.handle_key(key)

            if result is not None:
                return result

    def _handle_ai_turn(self, live: Live) -> bool:
        """Handle AI player's turn.

        Args:
            live: Rich Live context for display updates.

        Returns:
            True if game should continue, False on error.
        """
        # Show thinking status
        live.update(self._render_display(thinking=True))

        # Get AI move
        move = self.game.get_ai_move()

        if move is None:
            self.status_message = "AI failed to find a move!"
            live.update(self._render_display())
            time.sleep(2)
            return False

        from_pos, to_pos, promotion = move

        # Make the move
        success = self.game.make_move(from_pos, to_pos, promotion)

        if not success:
            self.status_message = "AI made invalid move!"
            live.update(self._render_display())
            time.sleep(2)
            return False

        self.status_message = ""
        return True

    def _run_human_ai_mode(self) -> None:
        """Run human vs AI game mode."""
        with Live(
            self._render_display(),
            console=self.console,
            refresh_per_second=10,
            screen=True,
        ) as live:
            while self.running and not self.game.game_over:
                is_human_turn = self.game.turn == self.human_color

                if is_human_turn:
                    if not self._handle_human_turn(live):
                        break
                else:
                    if not self._handle_ai_turn(live):
                        break

                # Update display after move
                live.update(self._render_display())

            # Game over - show final state
            if self.game.game_over:
                live.update(self._render_display())
                self.input_handler.read_key()  # Wait for keypress

    def _run_ai_ai_mode(self) -> None:
        """Run AI vs AI game mode."""
        with Live(
            self._render_display(),
            console=self.console,
            refresh_per_second=10,
            screen=True,
        ) as live:
            while self.running and not self.game.game_over:
                # Show thinking
                live.update(self._render_display(thinking=True))

                if not self._handle_ai_turn(live):
                    break

                # Update display
                live.update(self._render_display())

                # Delay for viewing
                time.sleep(self.delay)

            # Game over - show final state
            if self.game.game_over:
                live.update(self._render_display())
                self.console.print("\nPress any key to exit...")
                self.input_handler.read_key()

    def run(self) -> None:
        """Run the chess client."""
        try:
            if self.mode == "human-ai":
                self._run_human_ai_mode()
            else:
                self._run_ai_ai_mode()
        except KeyboardInterrupt:
            pass
        finally:
            self.console.print("\nThanks for playing!")


def main() -> None:
    """Entry point for the chess client."""
    args = parse_arguments()

    # Check if AI binary exists
    if not os.path.exists(args.ai_path):
        print(f"Error: Chess AI binary not found at '{args.ai_path}'")
        print("Please compile the chess AI first with 'make'")
        sys.exit(1)

    client = ChessClient(args)
    client.run()


if __name__ == "__main__":
    main()
