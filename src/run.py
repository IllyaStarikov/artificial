#!/usr/bin/env python3
"""Unified CLI runner for AI algorithms.

Usage:
    python -m run sat --input input.cnf --mu 100 --lambda 50
    python -m run shape-pack --input shapes.txt --mu 100 --lambda 50
    python -m run hill-climb --function quadratic

Run with --help for full options.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser with subcommands.

    Returns:
        Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        description="Artificial Intelligence Algorithm Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python -m run sat --input input.cnf
    python -m run shape-pack --input shapes.txt --mu 100
    python -m run hill-climb --function sphere
        """,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # SAT Solver subcommand
    sat_parser = subparsers.add_parser(
        "sat",
        help="SAT solver using evolutionary algorithm",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    sat_parser.add_argument(
        "--input", "-i",
        type=Path,
        required=True,
        help="CNF file",
    )
    sat_parser.add_argument(
        "--mu",
        type=int,
        default=100,
        help="Parent population size",
    )
    sat_parser.add_argument(
        "--lambda",
        dest="lambda_",
        type=int,
        default=50,
        help="Offspring per generation",
    )
    sat_parser.add_argument(
        "--target-fitness",
        type=float,
        default=100.0,
        help="Target fitness (100 = all clauses satisfied)",
    )
    sat_parser.add_argument(
        "--max-evals",
        type=int,
        default=100000,
        help="Maximum fitness evaluations",
    )
    sat_parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed",
    )

    # Shape Packer subcommand
    pack_parser = subparsers.add_parser(
        "shape-pack",
        help="Shape packing using evolutionary algorithm",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    pack_parser.add_argument(
        "--input", "-i",
        type=Path,
        required=True,
        help="Shapes file",
    )
    pack_parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output file for solution",
    )
    pack_parser.add_argument(
        "--mu",
        type=int,
        default=100,
        help="Parent population size",
    )
    pack_parser.add_argument(
        "--lambda",
        dest="lambda_",
        type=int,
        default=50,
        help="Offspring per generation",
    )
    pack_parser.add_argument(
        "--mutation-rate",
        type=float,
        default=0.05,
        help="Mutation probability",
    )
    pack_parser.add_argument(
        "--max-evals",
        type=int,
        default=10000,
        help="Maximum fitness evaluations",
    )
    pack_parser.add_argument(
        "--stagnation",
        type=int,
        default=250,
        help="Generations without improvement to terminate",
    )
    pack_parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed",
    )
    pack_parser.add_argument(
        "--visualize", "-v",
        action="store_true",
        help="Show real-time visualization",
    )
    pack_parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Update visualization every N generations (with --visualize)",
    )
    pack_parser.add_argument(
        "--save",
        type=Path,
        default=None,
        help="Save animation as GIF (e.g., --save=run.gif). Implies --visualize",
    )
    pack_parser.add_argument(
        "--duration",
        type=int,
        default=15,
        help="Duration in seconds for GIF recording (with --save)",
    )

    # Hill Climber subcommand
    hill_parser = subparsers.add_parser(
        "hill-climb",
        help="Hill climbing local search",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    hill_parser.add_argument(
        "--function", "-f",
        type=str,
        default="sphere",
        choices=["sphere", "rastrigin", "ackley"],
        help="Objective function",
    )
    hill_parser.add_argument(
        "--strategy",
        type=str,
        default="steepest",
        choices=["steepest", "stochastic"],
        help="Search strategy",
    )
    hill_parser.add_argument(
        "--restarts",
        type=int,
        default=10,
        help="Number of random restarts",
    )
    hill_parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed",
    )

    return parser


def run_sat(args: argparse.Namespace) -> int:
    """Run SAT solver.

    Args:
        args: Parsed arguments.

    Returns:
        Exit code.
    """
    import random

    from evolutionary import EA, Individual, Population, SAT
    from evolutionary.termination import (
        FitnessTarget,
        NumberOfFitnessEvaluations,
    )

    if args.seed is not None:
        random.seed(args.seed)

    print(f"Loading CNF from {args.input}...")
    Individual.cnf_filename = str(args.input)
    sat = SAT(str(args.input))
    print(f"  Variables: {len(sat.variables)}")
    print(f"  Clauses: {sat.total_clauses}")

    conditions = [
        FitnessTarget(args.target_fitness),
        NumberOfFitnessEvaluations(args.max_evals),
    ]

    print(f"\nRunning EA (mu={args.mu}, lambda={args.lambda_})...")
    start_time = time.time()

    ea = EA(args.mu, args.lambda_)
    best = ea.search(conditions)

    elapsed = time.time() - start_time
    print(f"\nCompleted in {elapsed:.2f}s")
    print(f"Best fitness: {best.fitness:.2f}%")

    if best.fitness >= 100.0:
        print("\nSATISFIABLE")
    else:
        print(f"\nBest found satisfies {best.fitness:.2f}% of clauses")

    return 0


def run_shape_pack(args: argparse.Namespace) -> int:
    """Run shape packer.

    Args:
        args: Parsed arguments.

    Returns:
        Exit code.
    """
    from evolutionary.termination import (
        NoChangeInBestFitness,
        NumberOfFitnessEvaluations,
    )

    from shape_packer import (
        ShapePackerConfig,
        ShapePackerEA,
        format_solution,
        parse_input_file,
        write_solution,
    )

    print(f"Loading shapes from {args.input}...")
    try:
        shapes, board_dims = parse_input_file(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(f"  Board: {board_dims[0]}x{board_dims[1]}")
    print(f"  Shapes: {len(shapes)}")

    config = ShapePackerConfig(
        mu=args.mu,
        lambda_=args.lambda_,
        mutation_rate=args.mutation_rate,
        max_evaluations=args.max_evals,
        stagnation_generations=args.stagnation,
        seed=args.seed,
    )

    # Use visualizer if requested (--visualize or --save implies visualize)
    if args.visualize or args.save:
        from shape_packer import ShapePackerVisualizer, VisualShapePackerEA

        print(f"\nStarting visualization...")
        print(f"  mu={config.mu}, lambda={config.lambda_}")
        print(f"  update_interval={args.interval}")

        # When saving, use duration; otherwise run indefinitely
        if args.save:
            max_gens = 1000000  # High limit, duration controls stopping
            print(f"  saving to: {args.save} ({args.duration}s)")
        else:
            max_gens = 1000000  # Effectively infinite
            print("\nClose the window to stop (runs indefinitely).")

        ea = VisualShapePackerEA(shapes, board_dims, config)
        visualizer = ShapePackerVisualizer(
            ea,
            update_interval=args.interval,
            max_generations=max_gens,
            save_path=args.save,
            duration_seconds=args.duration if args.save else None,
        )

        start_time = time.time()
        best = visualizer.run()
        elapsed = time.time() - start_time

        print(f"\nCompleted in {elapsed:.2f}s")
        print(f"Final generation: {ea.generation}")
        print(f"Best fitness: {best.fitness:.2f}")
    else:
        conditions = [
            NumberOfFitnessEvaluations(config.max_evaluations),
            NoChangeInBestFitness(config.stagnation_generations),
        ]

        print(f"\nRunning EA (mu={config.mu}, lambda={config.lambda_})...")
        start_time = time.time()

        ea = ShapePackerEA(shapes, board_dims, config)
        best = ea.search(conditions)

        elapsed = time.time() - start_time
        print(f"\nCompleted in {elapsed:.2f}s")
        print(f"Generations: {ea.generation}")
        print()
        print(format_solution(best))

    if args.output:
        write_solution(args.output, best, elapsed)
        print(f"\nSolution written to {args.output}")

    return 0


def run_hill_climb(args: argparse.Namespace) -> int:
    """Run hill climber.

    Args:
        args: Parsed arguments.

    Returns:
        Exit code.
    """
    import random

    import numpy as np

    from hill_climber import Function, HillClimber, Node

    if args.seed is not None:
        random.seed(args.seed)
        np.random.seed(args.seed)

    # Define objective functions
    functions = {
        "sphere": (
            lambda x, y: -(x**2 + y**2),
            (-5.0, 5.0),
            (-5.0, 5.0),
        ),
        "rastrigin": (
            lambda x, y: -(20 + x**2 - 10 * np.cos(2 * np.pi * x)
                          + y**2 - 10 * np.cos(2 * np.pi * y)),
            (-5.12, 5.12),
            (-5.12, 5.12),
        ),
        "ackley": (
            lambda x, y: -(-20 * np.exp(-0.2 * np.sqrt(0.5 * (x**2 + y**2)))
                          - np.exp(0.5 * (np.cos(2 * np.pi * x)
                                          + np.cos(2 * np.pi * y)))
                          + np.e + 20),
            (-5.0, 5.0),
            (-5.0, 5.0),
        ),
    }

    func, x_bounds, y_bounds = functions[args.function]
    objective = Function(func, x_bounds, y_bounds)

    print(f"Function: {args.function}")
    print(f"Strategy: {args.strategy}")
    print(f"Restarts: {args.restarts}")

    start_time = time.time()

    climber = HillClimber(
        objective,
        stochastic=(args.strategy == "stochastic"),
    )
    best = climber.climb(restarts=args.restarts)

    elapsed = time.time() - start_time

    print(f"\nCompleted in {elapsed:.2f}s")
    print(f"Best position: ({best.x:.6f}, {best.y:.6f})")
    print(f"Best value: {objective(best):.6f}")

    return 0


def main(argv: list[str] | None = None) -> int:
    """Main entry point.

    Args:
        argv: Command line arguments.

    Returns:
        Exit code.
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "sat":
            return run_sat(args)
        elif args.command == "shape-pack":
            return run_shape_pack(args)
        elif args.command == "hill-climb":
            return run_hill_climb(args)
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
