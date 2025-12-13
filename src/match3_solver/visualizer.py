"""Terminal-based match-3 game visualizer using rich library."""

from __future__ import annotations

import copy
import sys
import time
import typing

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn
from rich.progress import Progress
from rich.progress import TextColumn
from rich.table import Table
from rich.text import Text

import action as action_module
import match3
import search_node as search_node_module
import state as state_module


class Match3Visualizer:
    """Terminal-based match-3 game visualizer with animations."""

    # Emoji tiles for each device type (1-7)
    TILE_EMOJIS = ["🟥", "🟩", "🟦", "🟨", "🟪", "🟫", "⬜"]

    # Fallback colored number display
    TILE_COLORS = [
        "bright_red",
        "bright_green",
        "bright_blue",
        "bright_yellow",
        "bright_magenta",
        "rgb(139,69,19)",  # brown
        "bright_white",
    ]

    def __init__(
        self,
        game: match3.Match3Game,
        delay: float = 0.5,
        step_mode: bool = False,
        use_emoji: bool = True,
    ) -> None:
        """Initialize the visualizer.

        Args:
            game: The Match3Game instance to visualize.
            delay: Seconds between animation frames.
            step_mode: If True, wait for input between moves.
            use_emoji: If True, use emoji tiles instead of numbers.
        """
        self.game = game
        self.delay = delay
        self.step_mode = step_mode
        self.use_emoji = use_emoji
        self.console = Console()
        self.combo_count = 0
        self.last_points_earned = 0

    def _render_tile(
        self,
        tile_value: int,
        is_highlight: bool = False,
        is_match: bool = False,
        is_pool: bool = False,
        flash_on: bool = True,
    ) -> Text:
        """Render a single tile.

        Args:
            tile_value: The tile type (1-7).
            is_highlight: Whether this tile is being swapped.
            is_match: Whether this tile is part of a match.
            is_pool: Whether this tile is in the pool.
            flash_on: For flashing effect, whether tile is visible.

        Returns:
            Rich Text object for the tile.
        """
        if tile_value < 1 or tile_value > len(self.TILE_EMOJIS):
            if self.use_emoji:
                return Text("  ⬛  ", style="dim")
            return Text(" ? ", style="dim")

        color = self.TILE_COLORS[tile_value - 1]

        if self.use_emoji:
            emoji = self.TILE_EMOJIS[tile_value - 1]
            if is_match and not flash_on:
                return Text("  ✨  ", style="bold")
            if is_match:
                return Text(f" [{emoji}]", style="bold reverse")
            if is_highlight:
                return Text(f" ➤{emoji}", style="bold")
            if is_pool:
                return Text(f"  {emoji} ", style="dim")
            return Text(f"  {emoji} ", style="bold")
        else:
            symbol = str(tile_value)
            if is_match and not flash_on:
                return Text(" ★ ", style="bold white")
            if is_match:
                return Text(f" {symbol} ", style=f"bold black on {color}")
            if is_highlight:
                return Text(f">{symbol}<", style=f"bold {color} reverse")
            if is_pool:
                return Text(f" {symbol} ", style=f"dim {color}")
            return Text(f" {symbol} ", style=f"bold {color}")

    def render_grid(
        self,
        state: state_module.State,
        swap_highlights: typing.Optional[typing.Set[typing.Tuple[int, int]]] = None,
        match_highlights: typing.Optional[typing.Set[typing.Tuple[int, int]]] = None,
        show_pool: bool = True,
        flash_on: bool = True,
    ) -> Table:
        """Render the game grid as a rich Table.

        Args:
            state: Current game state.
            swap_highlights: Set of (row, col) positions being swapped.
            match_highlights: Set of (row, col) positions that matched.
            show_pool: Whether to show the pool above the grid.
            flash_on: For match flashing effect.

        Returns:
            Rich Table representing the grid.
        """
        swap_highlights = swap_highlights or set()
        match_highlights = match_highlights or set()

        row_max, column_max = match3.Match3Game.grid_size(state.grid)

        table = Table(
            show_header=True,
            header_style="bold cyan",
            box=None,
            padding=(0, 0),
        )

        col_width = 5 if self.use_emoji else 3
        table.add_column("", style="dim", width=3)
        for col in range(column_max):
            table.add_column(str(col), justify="center", width=col_width)

        if show_pool:
            pool_row_max = len(state.pool)
            for pool_row in range(pool_row_max):
                row_cells = [Text("·", style="dim")]
                for col in range(column_max):
                    tile = state.pool[pool_row][col]
                    row_cells.append(self._render_tile(tile, is_pool=True))
                table.add_row(*row_cells)

            separator = "─────" if self.use_emoji else "───"
            separator_cells = [Text("", style="dim")]
            for _ in range(column_max):
                separator_cells.append(Text(separator, style="dim cyan"))
            table.add_row(*separator_cells)

        for row in range(row_max):
            row_cells = [Text(str(row), style="bold cyan")]
            for col in range(column_max):
                tile = state.grid[row][col]
                is_swap = (row, col) in swap_highlights
                is_match = (row, col) in match_highlights
                row_cells.append(self._render_tile(
                    tile, is_swap, is_match, flash_on=flash_on
                ))
            table.add_row(*row_cells)

        return table

    def render_status(
        self,
        state: state_module.State,
        swap_num: int,
        total_swaps: int,
        move_description: str = "",
        points_earned: int = 0,
        combo: int = 0,
    ) -> Panel:
        """Render the status panel.

        Args:
            state: Current game state.
            swap_num: Current swap number.
            total_swaps: Total number of swaps in solution.
            move_description: Description of current move.
            points_earned: Points earned on this move.
            combo: Current combo count.

        Returns:
            Rich Panel with status information.
        """
        progress = Progress(
            TextColumn("[bold blue]Score:"),
            BarColumn(bar_width=20, complete_style="green", finished_style="green"),
            TextColumn("[bold]{task.completed}/{task.total}"),
            expand=False,
        )
        progress.add_task("score", total=self.game.quota, completed=min(state.points, self.game.quota))

        status_text = Text()
        status_text.append(f"Swaps: {state.swaps}/{state.max_swaps}", style="bold")
        status_text.append(f"  │  ", style="dim")
        status_text.append(f"Move: {swap_num}/{total_swaps}", style="bold cyan")

        if points_earned > 0:
            status_text.append(f"  │  ", style="dim")
            status_text.append(f"+{points_earned} pts", style="bold green")

        if combo > 1:
            status_text.append(f"  │  ", style="dim")
            combo_style = "bold yellow" if combo == 2 else "bold magenta" if combo == 3 else "bold red"
            status_text.append(f"{combo}x COMBO!", style=combo_style)

        status_text.append("\n")

        if move_description:
            if "SOLVED" in move_description:
                status_text.append(move_description, style="bold green")
            elif "FAILED" in move_description:
                status_text.append(move_description, style="bold red")
            else:
                status_text.append(move_description, style="italic cyan")

        if self.step_mode:
            status_text.append("\n")
            status_text.append("[Enter]=next  [q]=quit  [+/-]=speed", style="dim")

        layout = Layout()
        layout.split_column(
            Layout(progress, size=1),
            Layout(status_text, size=3 if self.step_mode else 2),
        )

        return Panel(layout, title="Status", border_style="blue")

    def render_display(
        self,
        state: state_module.State,
        swap_num: int,
        total_swaps: int,
        move_description: str = "",
        swap_highlights: typing.Optional[typing.Set[typing.Tuple[int, int]]] = None,
        match_highlights: typing.Optional[typing.Set[typing.Tuple[int, int]]] = None,
        flash_on: bool = True,
        points_earned: int = 0,
        combo: int = 0,
    ) -> Panel:
        """Render the complete display."""
        grid = self.render_grid(
            state, swap_highlights, match_highlights, flash_on=flash_on
        )
        status = self.render_status(
            state, swap_num, total_swaps, move_description,
            points_earned, combo
        )

        layout = Layout()
        layout.split_column(
            Layout(Panel(grid, title="Grid", border_style="green"), name="grid"),
            Layout(status, name="status", size=7 if self.step_mode else 6),
        )

        return Panel(
            layout,
            title="[bold magenta]🎮 Match-3 Puzzle Visualizer 🎮[/bold magenta]",
            border_style="magenta",
        )

    def extract_solution_path(
        self,
        solution_node: search_node_module.SearchNode,
    ) -> typing.List[typing.Tuple[state_module.State, typing.Optional[action_module.Action]]]:
        """Extract the sequence of states and actions from solution."""
        path: typing.List[typing.Tuple[
            state_module.State, typing.Optional[action_module.Action]
        ]] = []

        runner: typing.Optional[search_node_module.SearchNode] = solution_node
        while runner is not None:
            path.append((runner.state, runner.action))
            runner = runner.parent

        return list(reversed(path))

    def get_swap_positions(
        self,
        action: action_module.Action,
    ) -> typing.Set[typing.Tuple[int, int]]:
        """Get the two positions involved in a swap action."""
        row, col = action.row_column_pair
        unit = action.direction.unit_vector
        new_row, new_col = row + unit[0], col + unit[1]
        return {(row, col), (new_row, new_col)}

    def flash_matches(
        self,
        state: state_module.State,
        matches: typing.Set[typing.Tuple[int, int]],
        swap_num: int,
        total_swaps: int,
        move_desc: str,
        live: Live,
        flash_count: int = 3,
    ) -> None:
        """Flash matched tiles before removing them.

        Args:
            state: Current game state.
            matches: Set of matched positions.
            swap_num: Current swap number.
            total_swaps: Total swaps.
            move_desc: Move description.
            live: Rich Live context.
            flash_count: Number of flashes.
        """
        for i in range(flash_count * 2):
            flash_on = (i % 2 == 0)
            live.update(self.render_display(
                state, swap_num, total_swaps,
                f"{move_desc} - {len(matches)} tiles matched!",
                match_highlights=matches,
                flash_on=flash_on,
            ))
            time.sleep(self.delay / 4)

    def animate_cascade(
        self,
        grid_before: typing.List[typing.List[int]],
        pool_before: typing.List[typing.List[int]],
        state_after: state_module.State,
        swap_num: int,
        total_swaps: int,
        move_desc: str,
        points_before: int,
        live: Live,
    ) -> int:
        """Animate the cascade with tiles falling and chain combos.

        Returns:
            Total combo count for this move.
        """
        temp_grid = copy.deepcopy(grid_before)
        temp_pool = copy.deepcopy(pool_before)
        current_points = points_before
        combo = 0

        while match3.Match3Game.match_exists(temp_grid):
            combo += 1
            matches = match3.Match3Game.find_all_points_of_matches(temp_grid)
            points_from_match = len(matches)
            current_points += points_from_match

            temp_state = state_module.State(
                temp_grid, temp_pool,
                state_after.swaps, state_after.max_swaps,
                current_points, state_after.number_of_device_types
            )

            self.flash_matches(
                temp_state, matches, swap_num, total_swaps, move_desc, live
            )

            combo_text = f" ({combo}x combo!)" if combo > 1 else ""
            live.update(self.render_display(
                temp_state, swap_num, total_swaps,
                f"{move_desc} - removing tiles...{combo_text}",
                match_highlights=matches,
                points_earned=points_from_match,
                combo=combo,
            ))
            time.sleep(self.delay / 2)

            match3.Match3Game.reduce(
                temp_grid, temp_pool, state_after.number_of_device_types
            )

            temp_state = state_module.State(
                temp_grid, temp_pool,
                state_after.swaps, state_after.max_swaps,
                current_points, state_after.number_of_device_types
            )

            cascade_msg = "tiles falling..." if combo == 1 else f"chain reaction! ({combo}x)"
            live.update(self.render_display(
                temp_state, swap_num, total_swaps,
                f"{move_desc} - {cascade_msg}",
                points_earned=points_from_match,
                combo=combo,
            ))
            time.sleep(self.delay / 2)

        return combo

    def animate_move(
        self,
        before_state: state_module.State,
        action: action_module.Action,
        after_state: state_module.State,
        swap_num: int,
        total_swaps: int,
        live: Live,
    ) -> None:
        """Animate a single move with swap, flash, and cascade phases."""
        row, col = action.row_column_pair
        unit = action.direction.unit_vector
        new_row, new_col = row + unit[0], col + unit[1]

        move_desc = f"Swap ({row},{col}) ↔ ({new_row},{new_col})"
        swap_positions = self.get_swap_positions(action)

        live.update(self.render_display(
            before_state, swap_num, total_swaps,
            f"{move_desc} - selecting tiles...",
            swap_highlights=swap_positions,
        ))
        time.sleep(self.delay)

        temp_grid = copy.deepcopy(before_state.grid)
        match3.Match3Game.swap(temp_grid, action.row_column_pair, action.direction)

        temp_state = state_module.State(
            temp_grid, before_state.pool,
            before_state.swaps, before_state.max_swaps,
            before_state.points, before_state.number_of_device_types
        )

        live.update(self.render_display(
            temp_state, swap_num, total_swaps,
            f"{move_desc} - swapped!",
        ))
        time.sleep(self.delay / 2)

        combo = self.animate_cascade(
            temp_grid, copy.deepcopy(before_state.pool),
            after_state, swap_num, total_swaps, move_desc,
            before_state.points, live
        )

        points_earned = after_state.points - before_state.points
        self.last_points_earned = points_earned
        self.combo_count = combo

        live.update(self.render_display(
            after_state, swap_num, total_swaps,
            f"{move_desc} - complete!",
            points_earned=points_earned,
            combo=combo,
        ))
        time.sleep(self.delay / 2)

    def handle_input(self) -> str:
        """Handle user input in step mode.

        Returns:
            Command string: 'next', 'quit', 'faster', 'slower'
        """
        try:
            user_input = input().strip().lower()
            if user_input == 'q':
                return 'quit'
            elif user_input == '+':
                self.delay = max(0.1, self.delay - 0.1)
                return 'faster'
            elif user_input == '-':
                self.delay = min(2.0, self.delay + 0.1)
                return 'slower'
            else:
                return 'next'
        except EOFError:
            return 'quit'

    def play_solution(
        self,
        solution_node: search_node_module.SearchNode,
    ) -> None:
        """Play through the complete solution with animation."""
        path = self.extract_solution_path(solution_node)
        total_swaps = len(path) - 1

        with Live(console=self.console, refresh_per_second=20) as live:
            initial_state = path[0][0]
            start_msg = "Press Enter to start..." if self.step_mode else "Starting..."
            live.update(self.render_display(
                initial_state, 0, total_swaps, start_msg
            ))

            if self.step_mode:
                cmd = self.handle_input()
                if cmd == 'quit':
                    return
            else:
                time.sleep(self.delay * 2)

            for i in range(1, len(path)):
                before_state = path[i - 1][0]
                after_state, action = path[i]

                if action is not None:
                    self.animate_move(
                        before_state, action, after_state, i, total_swaps, live
                    )

                    if self.step_mode and i < len(path) - 1:
                        live.update(self.render_display(
                            after_state, i, total_swaps,
                            f"Move {i} complete. Press Enter...",
                            points_earned=self.last_points_earned,
                            combo=self.combo_count,
                        ))
                        cmd = self.handle_input()
                        if cmd == 'quit':
                            return

            final_state = path[-1][0]
            won = final_state.points >= self.game.quota

            result_msg = (
                f"🎉 SOLVED! Final score: {final_state.points}/{self.game.quota} 🎉"
                if won else
                f"❌ FAILED! Final score: {final_state.points}/{self.game.quota}"
            )

            live.update(self.render_display(
                final_state, total_swaps, total_swaps, result_msg,
            ))
            time.sleep(self.delay * 3)

        self.console.print()
        if won:
            self.console.print(
                f"[bold green]✓ Puzzle solved in {total_swaps} moves![/bold green]"
            )
        else:
            self.console.print(
                f"[bold red]✗ Puzzle not solved. Score: {final_state.points}/{self.game.quota}[/bold red]"
            )
