#!/usr/bin/env python3
"""Entry point for match-3 puzzle visualizer."""

from __future__ import annotations

import argparse
import sys

import heuristic
import solver
import utils
import visualizer


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Namespace with puzzle_path, delay, and step options.
    """
    parser = argparse.ArgumentParser(
        description="Visualize a match-3 puzzle solution"
    )
    parser.add_argument(
        "puzzle_path",
        metavar="puzzle-path",
        type=str,
        help="Path to the puzzle input file",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Delay between animation frames in seconds (default: 0.5)",
    )
    parser.add_argument(
        "--step",
        action="store_true",
        help="Step through moves manually (press Enter between moves)",
    )
    parser.add_argument(
        "--no-emoji",
        action="store_true",
        help="Use colored numbers instead of emoji tiles",
    )

    return parser.parse_args()


def main() -> None:
    """Run the match-3 visualizer."""
    args = parse_arguments()

    print(f"Loading puzzle from {args.puzzle_path}...")

    file_contents = utils.get_file_contents(args.puzzle_path)
    game_params = utils.parse_game_parameters(file_contents)
    game = utils.create_game_from_params(game_params)

    print(f"Puzzle loaded: {game.row_max}x{game.column_max} grid")
    print(f"Target: {game.quota} points in {game.swaps_allowed} swaps")
    print("Solving puzzle...")

    puzzle_solver = solver.Solver(game)
    solution = puzzle_solver.a_star(heuristic.HeuristicType.SCORE_PER_NODE)

    if solution is None:
        print("No solution found!")
        sys.exit(1)

    print("Solution found! Starting visualization...\n")

    viz = visualizer.Match3Visualizer(
        game,
        delay=args.delay,
        step_mode=args.step,
        use_emoji=not args.no_emoji,
    )
    viz.play_solution(solution)


if __name__ == "__main__":
    main()
