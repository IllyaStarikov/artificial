#!/usr/bin/env python3
"""Real-time visualization for shape packer evolutionary algorithm.

Shows a large board visualization with placed shapes and three compact
metric graphs: fitness convergence, population diversity, and improvement rate.

Usage:
    python -m shape_packer.visualize --input shapes.txt
    python -m shape_packer.visualize --input shapes.txt --mu 100 --interval 50
"""

from __future__ import annotations

import argparse
import random
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors
import matplotlib.gridspec as gridspec
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter

from sat_solver import termination

from shape_packer.board import Board, Placement
from shape_packer.config import ShapePackerConfig
from shape_packer.individual import Individual
from shape_packer.io import parse_input_file
from shape_packer.operators import RandomReplaceMutation
from shape_packer.population import Population
from shape_packer.selection import TournamentSelection, TruncationSelection
from shape_packer.shape import Point, Shape
from matplotlib.collections import PatchCollection


class RepairingCrossover:
    """Crossover that tries hard to repair collisions, maintaining diversity."""

    def crossover(
        self,
        parent1: Individual,
        parent2: Individual,
        board_dims: tuple,
        config: ShapePackerConfig,
    ) -> Individual:
        """Create offspring with thorough repair strategy."""
        p1_placements = {p.shape.shape_id: p for p in parent1.placements}
        p2_placements = {p.shape.shape_id: p for p in parent2.placements}

        # 60% prefer left placement, 40% random - slight bias for convergence
        selected = []
        for shape_id in p1_placements:
            p1 = p1_placements[shape_id]
            p2 = p2_placements[shape_id]
            if random.random() < 0.6:
                # Pick the one more to the left
                if p1.position.col <= p2.position.col:
                    selected.append(p1)
                else:
                    selected.append(p2)
            else:
                selected.append(random.choice([p1, p2]))

        # Repair with persistence - never discard shapes
        width, height = board_dims
        board = Board(width, height)
        repaired = []

        random.shuffle(selected)
        for placement in selected:
            if board.can_place(placement):
                board.place(placement)
                repaired.append(placement)
            else:
                # Try multiple repair strategies
                new_p = self._repair_placement(placement, board, width, height, config)
                if new_p:
                    board.place(new_p)
                    repaired.append(new_p)

        return Individual(repaired, width, height)

    def _repair_placement(self, placement, board, width, height, config):
        """Try multiple strategies to fix a colliding placement (optimized)."""
        shape = placement.shape
        orig_row, orig_col = placement.position.row, placement.position.col

        # Strategy 1: Try different rotations at same position
        for rot in range(4):
            p = Placement(shape, Point(orig_row, orig_col), rot)
            if board.can_place(p):
                return p

        # Strategy 2: Limited spiral search (max 10 distance)
        max_dist = min(10, max(width, height) // 4)
        for dist in range(1, max_dist + 1):
            # Sample perimeter instead of checking all
            for _ in range(min(8 * dist, 32)):  # Sample up to 32 positions per ring
                drow = random.randint(-dist, dist)
                dcol = random.choice([-dist, dist]) if abs(drow) != dist else random.randint(-dist, dist)
                new_row, new_col = orig_row + drow, orig_col + dcol
                if 0 <= new_row < height and 0 <= new_col < width:
                    rot = random.randint(0, 3)
                    p = Placement(shape, Point(new_row, new_col), rot)
                    if board.can_place(p):
                        return p

        # Strategy 3: Random sampling (faster than systematic scan)
        for _ in range(50):
            rot = random.randint(0, 3)
            row = random.randint(0, height - 1)
            col = random.randint(0, width - 1)
            p = Placement(shape, Point(row, col), rot)
            if board.can_place(p):
                return p

        return None


# Color scheme
COLORS = {
    "bg": "#1a1a2e",
    "board_bg": "#16213e",
    "board_empty": "#0f3460",
    "grid": "#e94560",
    "text": "#eaeaea",
    "accent": "#e94560",
    "best_line": "#00d9ff",
    "avg_line": "#ff6b6b",
    "min_line": "#feca57",
    "diversity": "#48dbfb",
    "improvement": "#1dd1a1",
}

# Shape colors - vibrant palette
SHAPE_COLORS = [
    "#ff6b6b", "#feca57", "#48dbfb", "#1dd1a1", "#ff9ff3",
    "#54a0ff", "#5f27cd", "#00d2d3", "#ff9f43", "#10ac84",
    "#ee5a24", "#0abde3", "#f368e0", "#01a3a4", "#c44569",
    "#7bed9f", "#70a1ff", "#eccc68", "#ff6348", "#5352ed",
]


class VisualShapePackerEA:
    """Shape packer EA with visualization callbacks.

    This version yields control after each generation to allow visualization
    updates.
    """

    def __init__(
        self,
        shapes: List[Shape],
        board_dims: Tuple[int, int],
        config: ShapePackerConfig,
    ) -> None:
        """Create a visualizable shape packer EA."""
        self.shapes = shapes
        self.board_dims = board_dims
        self.config = config

        if config.seed is not None:
            random.seed(config.seed)

        # Weaker selection pressure for more diversity
        self._parent_selection = TournamentSelection(k=2)  # Smaller tournament = weaker pressure
        self._survival_selection = TruncationSelection()
        self._crossover = RepairingCrossover()  # Repairs collisions, maintains diversity
        self._mutation = RandomReplaceMutation()

        self._population: Optional[Population] = None
        self._generation = 0
        self._best_ever: Optional[Individual] = None

        # History for plotting
        self.best_fitness_history: List[float] = []
        self.avg_fitness_history: List[float] = []
        self.min_fitness_history: List[float] = []
        self.diversity_history: List[float] = []
        self.improvement_history: List[float] = []

    def initialize(self) -> None:
        """Initialize the population."""
        self._population = Population.random(
            self.shapes,
            self.board_dims,
            self.config,
            self.config.mu,
        )
        self._best_ever = self._population.fittest
        self._generation = 0

        # Initialize history
        fitnesses = self._population.fitnesses
        self.best_fitness_history = [self._best_ever.fitness]
        self.avg_fitness_history = [self._population.average_fitness]
        self.min_fitness_history = [min(fitnesses)]
        self.diversity_history = [np.std(fitnesses) if len(fitnesses) > 1 else 0.0]
        self.improvement_history = [0.0]

    def step(self) -> bool:
        """Run one generation with elitism and local search.

        Returns:
            True if should continue, False if terminated.
        """
        self._generation += 1
        prev_best = self._best_ever.fitness

        # Elitism: keep the best
        elite = self._population.fittest

        # Select parents
        parents = self._parent_selection.select(
            self._population.individuals,
            self.config.lambda_,
        )

        # Create offspring (simple operators for gradual convergence)
        offspring: List[Individual] = []

        for i in range(0, len(parents) - 1, 2):
            parent1 = parents[i]
            parent2 = parents[i + 1] if i + 1 < len(parents) else parents[0]

            child = self._crossover.crossover(
                parent1, parent2, self.board_dims, self.config
            )

            if random.random() < self.config.mutation_rate:
                child = self._mutation.mutate(child, self.board_dims, self.config)

            offspring.append(child)

        # Combine with elitism
        combined = self._population.individuals + offspring
        survivors = self._survival_selection.select(combined, self.config.mu)

        # Ensure elite survives
        if elite not in survivors:
            survivors[-1] = elite

        # Random immigrants (5% of population) for diversity
        num_immigrants = max(1, self.config.mu // 20)
        for i in range(num_immigrants):
            immigrant = Individual.random(self.shapes, self.board_dims, self.config)
            survivors[-(i + 2)] = immigrant  # Replace worst individuals (except elite)

        self._population = Population(survivors)

        # Track best
        current_best = self._population.fittest
        if current_best.fitness > self._best_ever.fitness:
            self._best_ever = current_best

        # Record history
        fitnesses = self._population.fitnesses
        self.best_fitness_history.append(self._best_ever.fitness)
        self.avg_fitness_history.append(self._population.average_fitness)
        self.min_fitness_history.append(min(fitnesses))
        self.diversity_history.append(np.std(fitnesses) if len(fitnesses) > 1 else 0.0)
        self.improvement_history.append(self._best_ever.fitness - prev_best)

        return True

    @property
    def generation(self) -> int:
        return self._generation

    @property
    def best(self) -> Individual:
        return self._best_ever

    @property
    def population(self) -> Population:
        return self._population


class ShapePackerVisualizer:
    """Real-time visualization of shape packer EA with modern dark theme."""

    def __init__(
        self,
        ea: VisualShapePackerEA,
        update_interval: int = 10,
        max_generations: int = 1000,
        save_path: Optional[Path] = None,
        duration_seconds: Optional[int] = None,
    ) -> None:
        """Create visualizer.

        Args:
            ea: The EA to visualize.
            update_interval: Update display every N generations.
            max_generations: Maximum generations to run.
            save_path: Path to save animation as GIF. If None, shows live.
            duration_seconds: Max duration in seconds (for GIF saving).
        """
        self.ea = ea
        self.update_interval = update_interval
        self.max_generations = max_generations
        self.save_path = save_path
        self.duration_seconds = duration_seconds
        self._start_time: Optional[float] = None

        # Set up dark theme
        plt.style.use("dark_background")

        # Create figure with custom layout: large board left, small graphs right
        self.fig = plt.figure(figsize=(18, 10), facecolor=COLORS["bg"])

        # GridSpec: 3 rows, 2 columns. Board spans all 3 rows in column 0
        gs = gridspec.GridSpec(
            3, 2,
            width_ratios=[4, 1],  # Board takes 4/5 width
            height_ratios=[1, 1, 1],
            hspace=0.4,
            wspace=0.08,
            left=0.03,
            right=0.97,
            top=0.93,
            bottom=0.05,
        )

        # Board takes left 2/3, all rows
        self.ax_board = self.fig.add_subplot(gs[:, 0])

        # Three graphs stacked on right
        self.ax_fitness = self.fig.add_subplot(gs[0, 1])
        self.ax_diversity = self.fig.add_subplot(gs[1, 1])
        self.ax_improvement = self.fig.add_subplot(gs[2, 1])

        # Style all axes
        for ax in [self.ax_board, self.ax_fitness, self.ax_diversity, self.ax_improvement]:
            ax.set_facecolor(COLORS["board_bg"])
            ax.tick_params(colors=COLORS["text"], labelsize=8)
            for spine in ax.spines.values():
                spine.set_color(COLORS["grid"])
                spine.set_alpha(0.3)

        # Title
        self.fig.suptitle(
            "Shape Packer Evolution",
            fontsize=16,
            fontweight="bold",
            color=COLORS["text"],
        )

        # Initialize plots
        self._setup_board_plot()
        self._setup_fitness_plot()
        self._setup_diversity_plot()
        self._setup_improvement_plot()

    def _setup_board_plot(self) -> None:
        """Set up the board visualization."""
        width, height = self.ea.board_dims

        # Set limits with minimal padding
        self.ax_board.set_xlim(-0.5, width + 0.5)
        self.ax_board.set_ylim(-0.5, height + 0.5)
        # Auto aspect to fill available space
        self.ax_board.set_aspect("auto")

        # Labels
        self.ax_board.set_xlabel("Column", color=COLORS["text"], fontsize=10)
        self.ax_board.set_ylabel("Row", color=COLORS["text"], fontsize=10)

        # Draw empty board background
        board_rect = patches.Rectangle(
            (0, 0), width, height,
            linewidth=2,
            edgecolor=COLORS["accent"],
            facecolor=COLORS["board_empty"],
            alpha=0.3,
        )
        self.ax_board.add_patch(board_rect)

        # Light grid
        for x in range(width + 1):
            self.ax_board.axvline(x, color=COLORS["grid"], alpha=0.1, linewidth=0.5)
        for y in range(height + 1):
            self.ax_board.axhline(y, color=COLORS["grid"], alpha=0.1, linewidth=0.5)

        # Remove axis spines for cleaner look
        self.ax_board.spines["top"].set_visible(False)
        self.ax_board.spines["right"].set_visible(False)

    def _setup_fitness_plot(self) -> None:
        """Set up the fitness convergence plot."""
        self.ax_fitness.grid(True, alpha=0.2, color=COLORS["grid"])
        self.ax_fitness.tick_params(labelsize=7)

        self.line_best, = self.ax_fitness.plot(
            [], [], color=COLORS["best_line"], linewidth=1.5, label="Best"
        )
        self.line_avg, = self.ax_fitness.plot(
            [], [], color=COLORS["avg_line"], linewidth=1, label="Avg", alpha=0.7
        )
        self.line_min, = self.ax_fitness.plot(
            [], [], color=COLORS["min_line"], linewidth=1, label="Min", alpha=0.5
        )

        self.ax_fitness.legend(loc="lower right", fontsize=6, framealpha=0.3)
        self.fill_fitness = None

    def _setup_diversity_plot(self) -> None:
        """Set up the population diversity plot."""
        self.ax_diversity.grid(True, alpha=0.2, color=COLORS["grid"])
        self.ax_diversity.tick_params(labelsize=7)

        self.line_diversity, = self.ax_diversity.plot(
            [], [], color=COLORS["diversity"], linewidth=1.5
        )
        self.fill_diversity = None

    def _setup_improvement_plot(self) -> None:
        """Set up the improvement rate plot (cumulative)."""
        self.ax_improvement.grid(True, alpha=0.2, color=COLORS["grid"])
        self.ax_improvement.tick_params(labelsize=7)

        self.line_cumulative, = self.ax_improvement.plot(
            [], [], color=COLORS["improvement"], linewidth=1.5
        )
        self.fill_improvement = None

    def _draw_board(self, individual: Individual) -> None:
        """Draw the current best solution on the board (optimized)."""
        # Clear previous shapes
        while len(self.ax_board.patches) > 1:
            self.ax_board.patches[-1].remove()
        # Remove old collections
        for coll in list(self.ax_board.collections):
            coll.remove()

        width, height = self.ea.board_dims

        # Batch rectangles by color for faster rendering
        rects_by_color = {}
        rightmost = -1

        for placement in individual.placements:
            color = SHAPE_COLORS[placement.shape.shape_id % len(SHAPE_COLORS)]
            if color not in rects_by_color:
                rects_by_color[color] = []

            for point in placement.points:
                if 0 <= point.col < width and 0 <= point.row < height:
                    rightmost = max(rightmost, point.col)
                    rects_by_color[color].append(
                        patches.Rectangle((point.col, point.row), 1, 1)
                    )

        # Add collections (much faster than individual patches)
        for color, rects in rects_by_color.items():
            if rects:
                pc = PatchCollection(rects, facecolor=color, edgecolor="#ffffff",
                                     linewidth=0.2, alpha=0.9)
                self.ax_board.add_collection(pc)

        # Highlight empty columns
        empty_cols = width - rightmost - 1
        if rightmost < width - 1:
            empty_rect = patches.Rectangle(
                (rightmost + 1, 0), empty_cols, height,
                facecolor="#1dd1a1", alpha=0.15, linewidth=0,
            )
            self.ax_board.add_patch(empty_rect)

        # Update title
        self.ax_board.set_title(
            f"Fitness: {individual.fitness:.0f}  |  Empty: {empty_cols} cols",
            color=COLORS["text"], fontsize=11, fontweight="bold", pad=8,
        )

    def _update_fitness_plot(self) -> None:
        """Update the fitness convergence plot."""
        generations = list(range(len(self.ea.best_fitness_history)))

        self.line_best.set_data(generations, self.ea.best_fitness_history)
        self.line_avg.set_data(generations, self.ea.avg_fitness_history)
        self.line_min.set_data(generations, self.ea.min_fitness_history)

        # Update fill between best and min
        if self.fill_fitness:
            self.fill_fitness.remove()
        if len(generations) > 1:
            self.fill_fitness = self.ax_fitness.fill_between(
                generations,
                self.ea.min_fitness_history,
                self.ea.best_fitness_history,
                alpha=0.15,
                color=COLORS["best_line"],
            )

        # Adjust axes
        if generations:
            self.ax_fitness.set_xlim(0, max(10, len(generations)))
            all_fitness = (
                self.ea.best_fitness_history +
                self.ea.avg_fitness_history +
                self.ea.min_fitness_history
            )
            if all_fitness:
                min_f = min(all_fitness)
                max_f = max(all_fitness)
                margin = (max_f - min_f) * 0.1 or 1
                self.ax_fitness.set_ylim(max(0, min_f - margin), max_f + margin)

        self.ax_fitness.set_title(
            f"Gen {self.ea.generation} | Best: {self.ea.best.fitness:.0f}",
            color=COLORS["text"], fontsize=8, pad=3,
        )

    def _update_diversity_plot(self) -> None:
        """Update the population diversity plot."""
        generations = list(range(len(self.ea.diversity_history)))

        self.line_diversity.set_data(generations, self.ea.diversity_history)

        # Update fill
        if self.fill_diversity:
            self.fill_diversity.remove()
        if len(generations) > 1:
            self.fill_diversity = self.ax_diversity.fill_between(
                generations,
                0,
                self.ea.diversity_history,
                alpha=0.2,
                color=COLORS["diversity"],
            )

        # Adjust axes
        if generations:
            self.ax_diversity.set_xlim(0, max(10, len(generations)))
            max_div = max(self.ea.diversity_history) if self.ea.diversity_history else 1
            self.ax_diversity.set_ylim(0, max_div * 1.2 or 1)

        current_div = self.ea.diversity_history[-1] if self.ea.diversity_history else 0
        self.ax_diversity.set_title(
            f"Diversity σ={current_div:.1f}",
            color=COLORS["text"], fontsize=8, pad=3,
        )

    def _update_improvement_plot(self) -> None:
        """Update the cumulative improvement plot."""
        generations = list(range(len(self.ea.improvement_history)))

        # Cumulative improvement from start
        cumulative = np.cumsum(self.ea.improvement_history)
        self.line_cumulative.set_data(generations, cumulative)

        # Update fill
        if self.fill_improvement:
            self.fill_improvement.remove()
        if len(generations) > 1:
            self.fill_improvement = self.ax_improvement.fill_between(
                generations, 0, cumulative, alpha=0.2, color=COLORS["improvement"]
            )

        # Adjust axes
        if generations:
            self.ax_improvement.set_xlim(0, max(10, len(generations)))
            max_c = max(cumulative) if len(cumulative) > 0 else 1
            self.ax_improvement.set_ylim(0, max(10, max_c * 1.1))

        total_gain = cumulative[-1] if len(cumulative) > 0 else 0
        self.ax_improvement.set_title(
            f"Gain: +{total_gain:.0f}",
            color=COLORS["text"], fontsize=8, pad=3,
        )

    def _should_stop(self) -> bool:
        """Check if animation should stop."""
        if self.ea.generation >= self.max_generations:
            return True
        if self.duration_seconds and self._start_time:
            elapsed = time.time() - self._start_time
            if elapsed >= self.duration_seconds:
                return True
        return False

    def _animate(self, frame: int) -> None:
        """Animation update function."""
        # Run multiple generations per frame for speed
        for _ in range(self.update_interval):
            if self._should_stop():
                return
            self.ea.step()

        self._draw_board(self.ea.best)
        self._update_fitness_plot()
        self._update_diversity_plot()
        self._update_improvement_plot()

    def _frame_generator(self):
        """Generate frames until stopping condition is met."""
        frame = 0
        while not self._should_stop():
            yield frame
            frame += 1

    def run(self) -> Individual:
        """Run the visualization.

        Returns:
            Best individual found.
        """
        self.ea.initialize()
        self._start_time = time.time()
        self._draw_board(self.ea.best)
        self._update_fitness_plot()
        self._update_diversity_plot()
        self._update_improvement_plot()

        if self.save_path:
            # Use generator for time-based stopping
            print(f"Saving animation to {self.save_path}...")
            if self.duration_seconds:
                print(f"Recording for {self.duration_seconds} seconds...")

            anim = FuncAnimation(
                self.fig,
                self._animate,
                frames=self._frame_generator,
                interval=50,
                repeat=False,
                cache_frame_data=False,
            )

            writer = PillowWriter(fps=20)
            anim.save(str(self.save_path), writer=writer, dpi=100)
            final_gen = self.ea.generation
            print(f"Saved {final_gen} generations to {self.save_path}")
        else:
            # Live mode - calculate frames needed
            frames = self.max_generations // self.update_interval + 1
            anim = FuncAnimation(
                self.fig,
                self._animate,
                frames=frames,
                interval=50,
                repeat=False,
            )
            plt.show()

        return self.ea.best


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Visualize shape packer evolution",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--input", "-i",
        type=Path,
        required=True,
        help="Input file with shapes",
    )
    parser.add_argument(
        "--mu",
        type=int,
        default=50,
        help="Parent population size",
    )
    parser.add_argument(
        "--lambda",
        dest="lambda_",
        type=int,
        default=25,
        help="Offspring per generation",
    )
    parser.add_argument(
        "--mutation-rate",
        type=float,
        default=0.1,
        help="Mutation probability",
    )
    parser.add_argument(
        "--max-generations",
        type=int,
        default=500,
        help="Maximum generations to run",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Update display every N generations",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed",
    )
    parser.add_argument(
        "--save",
        type=Path,
        default=None,
        help="Save animation as GIF to this path (e.g., --save=run.gif)",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    args = parse_args(argv)

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
        seed=args.seed,
    )

    print(f"\nStarting visualization...")
    print(f"  μ={config.mu}, λ={config.lambda_}")
    print(f"  max_generations={args.max_generations}")
    print(f"  update_interval={args.interval}")
    print("\nClose the window to stop.")

    ea = VisualShapePackerEA(shapes, board_dims, config)
    visualizer = ShapePackerVisualizer(
        ea,
        update_interval=args.interval,
        max_generations=args.max_generations,
        save_path=args.save,
    )

    start_time = time.time()
    best = visualizer.run()
    elapsed = time.time() - start_time

    print(f"\nCompleted in {elapsed:.2f}s")
    print(f"Final generation: {ea.generation}")
    print(f"Best fitness: {best.fitness:.2f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
