"""Utility functions for match-3 puzzle solver."""

from __future__ import annotations

import argparse
import os
import sys
import typing

import direction as direction_module
import match3
import search_node as search_node_module


def parse_arguments() -> tuple[str, typing.Optional[str]]:
    """Parses command line arguments.

    Returns:
        Tuple of (puzzle_path, solution_path or None).
    """
    parser = argparse.ArgumentParser(
        description="An AI to solve match-3 puzzles"
    )
    parser.add_argument(
        "puzzle_path",
        metavar="puzzle-path",
        type=str,
        help="The input puzzle file",
    )
    parser.add_argument(
        "--solution_path",
        metavar="solution-path",
        type=str,
        help="Output path for the solution",
    )

    arguments = parser.parse_args()
    return arguments.puzzle_path, arguments.solution_path


def get_file_contents(filename: str) -> str:
    """Reads and returns file contents.

    Args:
        filename: Path to the file.

    Returns:
        File contents as a string.
    """
    if not (os.path.exists(filename) and os.path.isfile(filename)):
        print(f"{filename} does not exist. Terminating.")
        sys.exit(1)

    with open(filename, encoding="utf-8") as f:
        return f.read()


def parse_game_parameters(file_contents: str) -> argparse.Namespace:
    """Parses game parameters from puzzle file contents.

    Args:
        file_contents: Raw puzzle file text.

    Returns:
        Namespace with game configuration.
    """
    lines = file_contents.split("\n")

    (
        quota,
        swaps_allowed,
        device_types,
        column_max,
        row_max,
        pool_height,
        bonuses_being_used,
    ) = [int(x) for x in lines[:7]]

    pool = [
        [int(x) for x in line.split(" ")]
        for line in lines[7 : 7 + pool_height]
    ]

    grid_start = 7 + pool_height
    grid_end = grid_start + row_max
    grid = [
        [int(x) for x in line.split(" ")]
        for line in lines[grid_start:grid_end]
    ]

    return argparse.Namespace(
        quota=quota,
        swaps_allowed=swaps_allowed,
        device_types=device_types,
        column_max=column_max,
        row_max=row_max,
        pool_height=pool_height,
        bonuses_being_used=bonuses_being_used,
        pool=pool,
        grid=grid,
    )


def create_game_from_params(params: argparse.Namespace) -> match3.Match3Game:
    """Creates a Match3Game from parsed parameters.

    Args:
        params: Namespace with game configuration.

    Returns:
        Configured Match3Game instance.
    """
    return match3.Match3Game(
        quota=params.quota,
        swaps_allowed=params.swaps_allowed,
        device_types=params.device_types,
        column_max=params.column_max,
        row_max=params.row_max,
        pool_height=params.pool_height,
        bonuses_being_used=params.bonuses_being_used,
        pool=params.pool,
        grid=params.grid,
    )


def calculate_new_position(
    row_column_pair: tuple[int, int],
    direction: direction_module.Direction,
) -> tuple[int, int]:
    """Calculates the position after moving in a direction.

    Args:
        row_column_pair: Starting (row, column).
        direction: Direction to move.

    Returns:
        New (row, column) position.
    """
    unit_vector = direction.unit_vector
    return (
        row_column_pair[0] + unit_vector[0],
        row_column_pair[1] + unit_vector[1],
    )


def extract_swaps(
    node: search_node_module.SearchNode,
    game: match3.Match3Game,
) -> typing.List[typing.Tuple[typing.Tuple[int, int], typing.Tuple[int, int]]]:
    """Extracts the sequence of swaps from a solution node.

    Args:
        node: The solution SearchNode.
        game: The game instance.

    Returns:
        List of ((old_x, old_y), (new_x, new_y)) swap tuples.
    """
    runner: typing.Optional[search_node_module.SearchNode] = node
    swaps: typing.List[
        typing.Tuple[typing.Tuple[int, int], typing.Tuple[int, int]]
    ] = []

    while runner is not None and runner.parent is not None:
        before = runner.action.row_column_pair
        after = calculate_new_position(
            runner.action.row_column_pair,
            runner.action.direction,
        )

        # Convert to output format
        before = (before[1], before[0] + game.pool_height)
        after = (after[1], after[0] + game.pool_height)

        swaps.append((before, after))
        runner = runner.parent

    return list(reversed(swaps))


def format_swaps(
    swaps: typing.List[
        typing.Tuple[typing.Tuple[int, int], typing.Tuple[int, int]]
    ],
) -> str:
    """Formats swaps as a string.

    Args:
        swaps: List of swap tuples.

    Returns:
        Formatted string with newlines.
    """
    lines = []
    for before, after in swaps:
        lines.append(f"{before}, {after}")
    return "\n".join(lines)


def output_to_file(filename: str, content: str) -> None:
    """Writes content to a file.

    Args:
        filename: Output path.
        content: Content to write.
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)


def output_solution(
    output_path: typing.Optional[str],
    input_path: str,
    elapsed_time: float,
    solution_node: search_node_module.SearchNode,
    game: match3.Match3Game,
) -> None:
    """Outputs the solution to stdout and optionally to a file.

    Args:
        output_path: Optional file path for output.
        input_path: Original puzzle file path.
        elapsed_time: Time taken to solve.
        solution_node: The solution SearchNode.
        game: The game instance.
    """
    file_contents = get_file_contents(input_path)
    swap_string = format_swaps(extract_swaps(solution_node, game))

    print(file_contents)
    print(swap_string)
    print(elapsed_time)

    if output_path:
        output_to_file(
            output_path,
            f"{file_contents}\n{swap_string}\n{elapsed_time}\n",
        )
