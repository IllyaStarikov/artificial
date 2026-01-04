#!/usr/bin/env python3
"""Benchmark script for shape packer evolutionary algorithm.

Tests all combinations of mu, lambda, and generations parameters.
Runs 30 trials per configuration and saves the best GIF for each.

Usage:
    python benchmark.py
    python benchmark.py --runs 10  # Fewer runs for quick test
"""

import argparse
import os
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

# Parameter grids to test
MU_VALUES = [10, 25, 50, 100, 250]
LAMBDA_VALUES = [10, 25, 50, 100, 250]
GENERATION_VALUES = [10, 25, 50, 100, 250, 500, 1000]
INPUT_FILES = ["input-1.txt", "input-2.txt", "input-3.txt"]
OUTPUT_DIR = Path("../../assets/shape_packer")
TEMP_DIR = Path("/tmp/shape_packer_benchmark")
SRC_DIR = Path(__file__).parent.parent  # src/ directory


def run_single(input_file: str, mu: int, lambda_: int, generations: int, output_path: Path) -> tuple[float, float]:
    """Run a single benchmark and return (fitness, elapsed_seconds)."""
    import time
    input_path = SRC_DIR / "shape_packer" / "input" / input_file
    cmd = [
        sys.executable, str(SRC_DIR / "run.py"), "shape-pack",
        "-i", str(input_path),
        "--mu", str(mu),
        "--lambda", str(lambda_),
        "--generations", str(generations),
        "--interval", "1",
        "--save", str(output_path),
    ]

    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - start
    output = result.stdout + result.stderr

    # Parse fitness from output
    for line in output.split("\n"):
        if "Best fitness:" in line:
            try:
                fitness = float(line.split("Best fitness:")[1].strip())
                return fitness, elapsed
            except (ValueError, IndexError):
                pass
    return 0.0, elapsed


def run_benchmark(runs: int = 30):
    """Run the full benchmark suite."""
    # Create output directories
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    # Results storage: {input_file: {(mu, lambda, gens): [(fitness, time), ...]}}
    all_results = {f: defaultdict(list) for f in INPUT_FILES}
    all_best_gifs = {f: {} for f in INPUT_FILES}

    # Calculate total runs
    total_configs = len(INPUT_FILES) * len(MU_VALUES) * len(LAMBDA_VALUES) * len(GENERATION_VALUES)
    total_runs = total_configs * runs
    current_run = 0

    print(f"Shape Packer Benchmark")
    print(f"=" * 60)
    print(f"Input files: {len(INPUT_FILES)}")
    print(f"Configurations per input: {len(MU_VALUES) * len(LAMBDA_VALUES) * len(GENERATION_VALUES)}")
    print(f"Runs per config: {runs}")
    print(f"Total runs: {total_runs}")
    print(f"=" * 60)
    print()

    for input_file in INPUT_FILES:
        input_name = input_file.replace(".txt", "")
        input_dir = OUTPUT_DIR / input_name
        input_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{'='*60}")
        print(f"INPUT: {input_file}")
        print(f"{'='*60}")

        results = all_results[input_file]
        best_gifs = all_best_gifs[input_file]

        for gens in GENERATION_VALUES:
            for mu in MU_VALUES:
                for lambda_ in LAMBDA_VALUES:
                    config_key = (mu, lambda_, gens)
                    config_name = f"mu{mu}_lambda{lambda_}_gen{gens}"

                    print(f"\n[{input_name}/{config_name}]")

                    best_fitness = 0
                    best_path = None

                    for run_idx in range(runs):
                        current_run += 1
                        temp_path = TEMP_DIR / f"{input_name}_{config_name}_run{run_idx}.gif"

                        fitness, elapsed = run_single(input_file, mu, lambda_, gens, temp_path)
                        results[config_key].append((fitness, elapsed))

                        # Track best
                        if fitness > best_fitness:
                            best_fitness = fitness
                            if best_path and best_path.exists():
                                best_path.unlink()
                            best_path = temp_path
                        else:
                            # Remove non-best GIF to save space
                            if temp_path.exists():
                                temp_path.unlink()

                        fitnesses = [r[0] for r in results[config_key]]
                        avg_so_far = sum(fitnesses) / len(fitnesses)
                        print(f"  Run {run_idx + 1}/{runs}: {fitness:.0f} in {elapsed:.1f}s (best: {best_fitness:.0f}, avg: {avg_so_far:.1f}) [{current_run}/{total_runs}]")

                    # Save best GIF to output directory
                    if best_path and best_path.exists():
                        final_path = input_dir / f"{config_name}.gif"
                        shutil.move(str(best_path), str(final_path))
                        best_gifs[config_key] = (best_fitness, final_path)
                        print(f"  -> Saved best ({best_fitness:.0f}) to {final_path}")

    # Clean up temp directory
    shutil.rmtree(TEMP_DIR, ignore_errors=True)

    # Generate markdown tables
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    # Table by generations (one table per input file)
    for input_file in INPUT_FILES:
        input_name = input_file.replace(".txt", "")
        results = all_results[input_file]

        print(f"\n## {input_name}: Results by Generations\n")
        print("| Generations | Best | Average | Avg Time (s) |")
        print("|-------------|------|---------|--------------|")

        for gens in GENERATION_VALUES:
            all_fitness = []
            all_times = []
            for mu in MU_VALUES:
                for lambda_ in LAMBDA_VALUES:
                    key = (mu, lambda_, gens)
                    if key in results:
                        for fitness, elapsed in results[key]:
                            all_fitness.append(fitness)
                            all_times.append(elapsed)

            if all_fitness:
                best = max(all_fitness)
                avg = sum(all_fitness) / len(all_fitness)
                avg_time = sum(all_times) / len(all_times)
                print(f"| {gens} | {best:.0f} | {avg:.1f} | {avg_time:.1f} |")

    # Table by input file (aggregated across all configs)
    print(f"\n## Results by Input File\n")
    print("| Input | Best | Average | Avg Time (s) |")
    print("|-------|------|---------|--------------|")

    for input_file in INPUT_FILES:
        input_name = input_file.replace(".txt", "")
        results = all_results[input_file]

        all_fitness = []
        all_times = []
        for key, runs_data in results.items():
            for fitness, elapsed in runs_data:
                all_fitness.append(fitness)
                all_times.append(elapsed)

        if all_fitness:
            best = max(all_fitness)
            avg = sum(all_fitness) / len(all_fitness)
            avg_time = sum(all_times) / len(all_times)
            print(f"| {input_name} | {best:.0f} | {avg:.1f} | {avg_time:.1f} |")

    # Best configuration per input
    print(f"\n## Best Configuration per Input\n")
    for input_file in INPUT_FILES:
        input_name = input_file.replace(".txt", "")
        best_gifs = all_best_gifs[input_file]

        if best_gifs:
            overall_best = max(best_gifs.items(), key=lambda x: x[1][0])
            config, (fitness, path) = overall_best
            print(f"**{input_name}:** mu={config[0]}, lambda={config[1]}, gen={config[2]} → fitness={fitness:.0f}")
            print(f"  GIF: {path}\n")


def main():
    parser = argparse.ArgumentParser(description="Benchmark shape packer")
    parser.add_argument("--runs", type=int, default=30, help="Runs per configuration")
    args = parser.parse_args()

    # Resolve OUTPUT_DIR relative to script location
    global OUTPUT_DIR
    OUTPUT_DIR = (Path(__file__).parent / OUTPUT_DIR).resolve()

    run_benchmark(runs=args.runs)


if __name__ == "__main__":
    main()
