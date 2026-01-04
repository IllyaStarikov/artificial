"""Entry point for shape packer module.

Usage:
    python -m shape_packer --input shapes.txt --mu 100 --lambda 50

Run with --help for full options.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from sat_solver.termination import (
    NoChangeInBestFitness,
    NumberOfFitnessEvaluations,
    TerminationCondition,
)

from shape_packer.config import ShapePackerConfig
from shape_packer.ea import ShapePackerEA
from shape_packer.io import format_solution, parse_input_file, write_solution


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments.

    Args:
        argv: Command line arguments. Defaults to sys.argv[1:].

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Shape packer using evolutionary algorithm",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--input", "-i",
        type=Path,
        required=True,
        help="Input file with shapes",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output file for solution",
    )
    parser.add_argument(
        "--mu",
        type=int,
        default=100,
        help="Parent population size",
    )
    parser.add_argument(
        "--lambda",
        dest="lambda_",
        type=int,
        default=50,
        help="Offspring per generation",
    )
    parser.add_argument(
        "--mutation-rate",
        type=float,
        default=0.05,
        help="Mutation probability (0.0 to 1.0)",
    )
    parser.add_argument(
        "--tournament-size",
        type=int,
        default=5,
        help="Tournament size for parent selection",
    )
    parser.add_argument(
        "--max-evals",
        type=int,
        default=10000,
        help="Maximum fitness evaluations",
    )
    parser.add_argument(
        "--stagnation",
        type=int,
        default=250,
        help="Generations without improvement to terminate",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress output",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Main entry point.

    Args:
        argv: Command line arguments.

    Returns:
        Exit code (0 for success).
    """
    args = parse_args(argv)

    # Parse input
    if not args.quiet:
        print(f"Loading shapes from {args.input}...")

    try:
        shapes, board_dims = parse_input_file(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"  Board: {board_dims[0]}x{board_dims[1]}")
        print(f"  Shapes: {len(shapes)}")

    # Create config
    config = ShapePackerConfig(
        mu=args.mu,
        lambda_=args.lambda_,
        mutation_rate=args.mutation_rate,
        tournament_size=args.tournament_size,
        max_evaluations=args.max_evals,
        stagnation_generations=args.stagnation,
        seed=args.seed,
    )

    # Set up termination conditions
    conditions: list[TerminationCondition] = [
        NumberOfFitnessEvaluations(config.max_evaluations),
        NoChangeInBestFitness(config.stagnation_generations),
    ]

    # Run EA
    if not args.quiet:
        print("\nRunning evolutionary algorithm...")
        print(f"  mu={config.mu}, lambda={config.lambda_}")
        print(f"  mutation_rate={config.mutation_rate}")
        print(f"  max_evals={config.max_evaluations}")

    ea = ShapePackerEA(shapes, board_dims, config)
    start_time = time.time()
    best = ea.search(conditions)
    elapsed = time.time() - start_time

    # Output results
    if not args.quiet:
        print(f"\nCompleted in {elapsed:.2f}s")
        print(f"Generations: {ea.generation}")
        print()
        print(format_solution(best))

    # Write output file if specified
    if args.output:
        write_solution(args.output, best, elapsed)
        if not args.quiet:
            print(f"\nSolution written to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
