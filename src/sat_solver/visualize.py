#!/usr/bin/env python3
"""Matplotlib visualization for evolutionary algorithm solving SAT.

Shows variables and clauses as simple green/red pass/fail indicators.

Usage:
    python visualize.py input.cnf
    python visualize.py easy.cnf --max-gens 50
    python visualize.py easy.cnf --save evolution.gif
"""

from __future__ import annotations

import argparse
import os
import sys
import typing

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
import numpy as np

import individual
import population
import termination


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Visualize evolutionary algorithm solving SAT"
    )
    parser.add_argument(
        "cnf_file",
        nargs="?",
        default="input.cnf",
        help="Path to CNF file (default: input.cnf)",
    )
    parser.add_argument(
        "--mu",
        type=int,
        default=100,
        help="Population size (default: 100)",
    )
    parser.add_argument(
        "--lambda",
        dest="lambda_",
        type=int,
        default=50,
        help="Offspring size (default: 50)",
    )
    parser.add_argument(
        "--target",
        type=float,
        default=95.0,
        help="Target fitness percentage (default: 95.0)",
    )
    parser.add_argument(
        "--max-gens",
        type=int,
        default=200,
        help="Maximum generations (default: 200)",
    )
    parser.add_argument(
        "--save",
        type=str,
        help="Save animation to file (e.g., output.gif)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=200,
        help="Animation interval in ms (default: 200)",
    )
    return parser.parse_args()


class SATVisualizer:
    """Visualizes SAT problem with simple pass/fail indicators."""

    def __init__(
        self,
        cnf_file: str,
        mu: int = 100,
        lambda_: int = 50,
        target_fitness: float = 95.0,
        max_generations: int = 200,
    ) -> None:
        """Initialize the visualizer."""
        self.cnf_file = cnf_file
        self.mu = mu
        self.lambda_ = lambda_
        self.target_fitness = target_fitness
        self.max_generations = max_generations

        individual.Individual.cnf_filename = cnf_file

        # Parse CNF to get structure
        self.clauses: typing.List[typing.List[typing.Tuple[int, bool]]] = []
        self.num_variables = 0
        self._parse_cnf(cnf_file)

        # Data storage
        self.snapshots: typing.List[typing.Dict[str, bool]] = []
        self.fitness_history: typing.List[float] = []
        self.generation_history: typing.List[int] = []

    def _parse_cnf(self, filename: str) -> None:
        """Parse CNF file to extract clause structure."""
        with open(filename, encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith('c'):
                    continue
                if line.startswith('p'):
                    parts = line.split()
                    self.num_variables = int(parts[2])
                    continue
                literals = line.split()
                clause = []
                for lit in literals:
                    lit_val = int(lit)
                    if lit_val == 0:
                        break
                    var_idx = abs(lit_val) - 1
                    is_negated = lit_val < 0
                    clause.append((var_idx, is_negated))
                if clause:
                    self.clauses.append(clause)

    def run_evolution(self) -> None:
        """Run the evolutionary algorithm and record snapshots."""
        pop = population.Population(self.mu, self.lambda_)

        def fitness_getter() -> typing.List[float]:
            return [ind.fitness for ind in pop.individuals]

        termination_conditions = [
            termination.FitnessTarget(self.target_fitness),
            termination.NumberOfGenerations(self.max_generations),
        ]

        termination_manager = termination.TerminationManager(
            termination_conditions, fitness_getter
        )

        gen = 0
        best = max(pop.individuals, key=lambda x: x.fitness)
        self._record_snapshot(best, gen)
        gen += 1

        while not termination_manager.should_terminate():
            pop = population.Population.survival_selection(pop)
            offspring = population.Population.generate_offspring(pop)
            pop.individuals += offspring.individuals

            best = max(pop.individuals, key=lambda x: x.fitness)
            self._record_snapshot(best, gen)
            gen += 1

        print(f"Evolution completed: {gen} generations")
        print(f"Best fitness: {self.fitness_history[-1]:.2f}%")

    def _record_snapshot(self, ind: individual.Individual, gen: int) -> None:
        """Record a snapshot of the individual's variable assignments."""
        variables = sorted(ind.genotype.variables, key=lambda x: int(x))
        snapshot = {var: ind.genotype[var] for var in variables}
        self.snapshots.append(snapshot)
        self.fitness_history.append(ind.fitness)
        self.generation_history.append(gen)

    def _evaluate_clause(
        self, clause: typing.List[typing.Tuple[int, bool]],
        var_values: typing.List[bool]
    ) -> bool:
        """Evaluate if a clause is satisfied."""
        for var_idx, is_negated in clause:
            val = var_values[var_idx]
            if is_negated:
                val = not val
            if val:
                return True
        return False

    def create_animation(
        self,
        interval: int = 200,
        save_path: typing.Optional[str] = None,
    ) -> None:
        """Create and display/save the animation."""
        n_vars = self.num_variables
        n_clauses = len(self.clauses)

        # Calculate grid layout for clauses
        cols = int(np.ceil(np.sqrt(n_clauses * 2)))
        rows = int(np.ceil(n_clauses / cols))

        # Figure setup
        fig = plt.figure(figsize=(12, 8))
        fig.patch.set_facecolor('#0d1117')

        # Create layout
        gs = fig.add_gridspec(3, 1, height_ratios=[1, 4, 0.8], hspace=0.25)
        ax_vars = fig.add_subplot(gs[0])
        ax_clauses = fig.add_subplot(gs[1])
        ax_info = fig.add_subplot(gs[2])

        for ax in [ax_vars, ax_clauses, ax_info]:
            ax.set_facecolor('#161b22')
            for spine in ax.spines.values():
                spine.set_color('#30363d')

        # Info axis setup
        ax_info.axis('off')
        info_text = ax_info.text(
            0.5, 0.5, '', transform=ax_info.transAxes,
            fontsize=16, color='white', ha='center', va='center',
            fontfamily='monospace', fontweight='bold'
        )

        # Colors
        GREEN = '#3fb950'
        RED = '#f85149'

        def animate(frame):
            ax_vars.clear()
            ax_clauses.clear()

            ax_vars.set_facecolor('#161b22')
            ax_clauses.set_facecolor('#161b22')

            # Get current snapshot
            snapshot = self.snapshots[frame]
            variables = sorted(snapshot.keys(), key=lambda x: int(x))
            var_values = [snapshot[v] for v in variables]

            # Draw variables as horizontal row
            ax_vars.set_xlim(-0.5, n_vars - 0.5)
            ax_vars.set_ylim(-0.8, 0.8)
            ax_vars.set_aspect('equal')
            ax_vars.set_xticks([])
            ax_vars.set_yticks([])
            ax_vars.set_title(
                f'Variables (True/False)',
                color='white', fontsize=14, fontweight='bold', pad=10
            )

            for i, val in enumerate(var_values):
                color = GREEN if val else RED
                rect = patches.FancyBboxPatch(
                    (i - 0.4, -0.4), 0.8, 0.8,
                    boxstyle="round,pad=0.02,rounding_size=0.1",
                    facecolor=color, edgecolor='#30363d', linewidth=1
                )
                ax_vars.add_patch(rect)

            # Draw clauses as grid
            ax_clauses.set_xlim(-0.5, cols - 0.5)
            ax_clauses.set_ylim(-0.5, rows - 0.5)
            ax_clauses.set_aspect('equal')
            ax_clauses.invert_yaxis()
            ax_clauses.set_xticks([])
            ax_clauses.set_yticks([])

            satisfied_count = 0
            for c_idx, clause in enumerate(self.clauses):
                is_satisfied = self._evaluate_clause(clause, var_values)
                if is_satisfied:
                    satisfied_count += 1

                row = c_idx // cols
                col = c_idx % cols
                color = GREEN if is_satisfied else RED

                rect = patches.FancyBboxPatch(
                    (col - 0.45, row - 0.45), 0.9, 0.9,
                    boxstyle="round,pad=0.02,rounding_size=0.1",
                    facecolor=color, edgecolor='#30363d', linewidth=1
                )
                ax_clauses.add_patch(rect)

            ax_clauses.set_title(
                f'Clauses (Satisfied/Unsatisfied)',
                color='white', fontsize=14, fontweight='bold', pad=10
            )

            # Update info
            gen = self.generation_history[frame]
            fitness = self.fitness_history[frame]
            info = (f"Generation {gen}   |   "
                   f"Fitness: {fitness:.1f}%   |   "
                   f"Satisfied: {satisfied_count}/{n_clauses}")
            info_text.set_text(info)

            return [info_text]

        anim = animation.FuncAnimation(
            fig, animate,
            frames=len(self.snapshots), interval=interval, blit=False
        )

        # Legend
        legend_elements = [
            patches.Patch(facecolor=GREEN, edgecolor='#30363d', label='Pass'),
            patches.Patch(facecolor=RED, edgecolor='#30363d', label='Fail'),
        ]
        fig.legend(
            handles=legend_elements, loc='upper right',
            facecolor='#161b22', edgecolor='#30363d',
            fontsize=11, labelcolor='white'
        )

        plt.subplots_adjust(top=0.9, bottom=0.08, left=0.05, right=0.92)

        if save_path:
            print(f"Saving animation to {save_path}...")
            if save_path.endswith('.gif'):
                anim.save(save_path, writer='pillow', fps=1000//interval,
                         savefig_kwargs={'facecolor': '#0d1117'})
            else:
                anim.save(save_path, writer='ffmpeg', fps=1000//interval,
                         savefig_kwargs={'facecolor': '#0d1117'})
            print("Done!")
        else:
            plt.show()

        plt.close()


def main() -> None:
    """Run the visualization."""
    args = parse_arguments()

    if not os.path.exists(args.cnf_file):
        print(f"Error: CNF file not found: {args.cnf_file}")
        sys.exit(1)

    visualizer = SATVisualizer(
        cnf_file=args.cnf_file,
        mu=args.mu,
        lambda_=args.lambda_,
        target_fitness=args.target,
        max_generations=args.max_gens,
    )

    print(f"Running evolution on {args.cnf_file}...")
    visualizer.run_evolution()
    visualizer.create_animation(interval=args.interval, save_path=args.save)


if __name__ == "__main__":
    main()
