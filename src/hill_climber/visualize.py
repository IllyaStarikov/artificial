#!/usr/bin/env python3
"""Matplotlib visualization for hill climbing optimization.

Shows the optimization path on a contour map as the climber finds peaks.

Usage:
    python visualize.py
    python visualize.py --stochastic
    python visualize.py --restarts 3
    python visualize.py --save climb.gif
"""

from __future__ import annotations

import argparse
import math
import random
import typing

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

from hill_climber import function
from hill_climber import node


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Visualize hill climbing optimization"
    )
    parser.add_argument(
        "--stochastic",
        action="store_true",
        help="Use stochastic hill climbing",
    )
    parser.add_argument(
        "--restarts",
        type=int,
        default=0,
        help="Number of random restarts (default: 0)",
    )
    parser.add_argument(
        "--function",
        choices=["peaks", "quadratic", "ripple"],
        default="peaks",
        help="Function to optimize (default: peaks)",
    )
    parser.add_argument(
        "--save",
        type=str,
        help="Save animation to file (e.g., climb.gif)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=100,
        help="Animation interval in ms (default: 100)",
    )
    return parser.parse_args()


def get_function(name: str) -> function.Function:
    """Get objective function by name."""
    if name == "quadratic":
        return function.Function(
            lambda x, y: -(x ** 2) - (y ** 2),
            (-50, 50),
            (-50, 50),
        )
    elif name == "ripple":
        return function.Function(
            lambda x, y: (
                math.cos(math.sqrt(x**2 + y**2) / 3) * 50 -
                (x**2 + y**2) / 50
            ),
            (-50, 50),
            (-50, 50),
        )
    else:  # peaks - multiple local optima
        return function.Function(
            lambda x, y: (
                50 * math.exp(-((x - 20) ** 2 + (y - 20) ** 2) / 200) +
                30 * math.exp(-((x + 15) ** 2 + (y - 10) ** 2) / 150) +
                40 * math.exp(-((x + 10) ** 2 + (y + 25) ** 2) / 180) +
                35 * math.exp(-((x - 25) ** 2 + (y + 15) ** 2) / 160) -
                (x ** 2 + y ** 2) / 100
            ),
            (-50, 50),
            (-50, 50),
        )


class HillClimbVisualizer:
    """Visualizes hill climbing with animated contour plot."""

    def __init__(
        self,
        func: function.Function,
        stochastic: bool = False,
    ) -> None:
        """Initialize the visualizer."""
        self.func = func
        self.stochastic = stochastic
        self.paths: typing.List[typing.List[node.Node]] = []

    def _generate_neighbors(self, n: node.Node) -> typing.List[node.Node]:
        """Generate valid neighbors."""
        x, y = n.x, n.y
        nodes = []
        if x < self.func.x_bounds[1]:
            nodes.append(node.Node(x + 1, y))
        if x > self.func.x_bounds[0]:
            nodes.append(node.Node(x - 1, y))
        if y < self.func.y_bounds[1]:
            nodes.append(node.Node(x, y + 1))
        if y > self.func.y_bounds[0]:
            nodes.append(node.Node(x, y - 1))
        random.shuffle(nodes)
        return nodes

    def _select_successor(
        self, current: node.Node, neighbors: typing.List[node.Node]
    ) -> node.Node:
        """Select next node."""
        if self.stochastic:
            current_val = self.func(current)
            uphill = [n for n in neighbors if self.func(n) > current_val]
            if not uphill:
                return current
            return random.choice(uphill)
        return max(neighbors, key=lambda n: self.func(n))

    def run_climb(self, restarts: int = 0) -> None:
        """Run hill climbing and record paths."""
        num_runs = max(1, restarts + 1)

        for _ in range(num_runs):
            x = random.randint(self.func.x_bounds[0], self.func.x_bounds[1])
            y = random.randint(self.func.y_bounds[0], self.func.y_bounds[1])
            current = node.Node(x, y)
            path = [current]

            while True:
                neighbors = self._generate_neighbors(current)
                successor = self._select_successor(current, neighbors)

                if self.func(successor) <= self.func(current):
                    break

                current = successor
                path.append(current)

            self.paths.append(path)

        best_path = max(self.paths, key=lambda p: self.func(p[-1]))
        best_node = best_path[-1]
        print(f"Climbs completed: {num_runs}")
        print(f"Best position: ({best_node.x}, {best_node.y})")
        print(f"Best value: {self.func(best_node):.2f}")

    def create_animation(
        self,
        interval: int = 100,
        save_path: typing.Optional[str] = None,
    ) -> None:
        """Create and display/save the animation."""
        fig, ax = plt.subplots(figsize=(10, 8))
        fig.patch.set_facecolor('#0d1117')
        ax.set_facecolor('#161b22')

        # Create contour data
        x_range = np.linspace(
            self.func.x_bounds[0], self.func.x_bounds[1], 150
        )
        y_range = np.linspace(
            self.func.y_bounds[0], self.func.y_bounds[1], 150
        )
        X, Y = np.meshgrid(x_range, y_range)
        Z = np.zeros_like(X)

        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                Z[i, j] = self.func(node.Node(int(X[i, j]), int(Y[i, j])))

        # Plot contour
        contour = ax.contourf(X, Y, Z, levels=25, cmap='plasma')
        cbar = fig.colorbar(contour, ax=ax)
        cbar.set_label('Function Value', color='white', fontsize=11)
        cbar.ax.yaxis.set_tick_params(color='white')
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
        ax.contour(X, Y, Z, levels=12, colors='white', alpha=0.2, linewidths=0.5)

        # Style
        ax.tick_params(colors='white')
        ax.set_xlabel('X', color='white', fontsize=12)
        ax.set_ylabel('Y', color='white', fontsize=12)
        for spine in ax.spines.values():
            spine.set_color('#30363d')

        # Path colors
        colors = ['#3fb950', '#58a6ff', '#f0883e', '#f85149', '#a371f7']

        path_lines = []
        current_markers = []

        for i, path in enumerate(self.paths):
            color = colors[i % len(colors)]
            line, = ax.plot([], [], '-', color=color, linewidth=2.5, alpha=0.9)
            current, = ax.plot([], [], 'o', color='white', markersize=14,
                              markeredgecolor=color, markeredgewidth=3)
            ax.plot(path[0].x, path[0].y, 's', color=color,
                   markersize=10, markeredgecolor='white',
                   markeredgewidth=2, label=f'Start {i+1}')
            path_lines.append(line)
            current_markers.append(current)

        # Best point star
        best_star, = ax.plot([], [], '*', color='#ffd700', markersize=25,
                            markeredgecolor='white', markeredgewidth=1.5)

        mode = "Stochastic" if self.stochastic else "Steepest-Ascent"
        ax.set_title(f'Hill Climbing ({mode})', color='white', fontsize=14, fontweight='bold')

        # Info text at bottom
        info_text = ax.text(
            0.5, -0.08, '', transform=ax.transAxes,
            fontsize=12, color='white', ha='center',
            fontfamily='monospace'
        )

        if len(self.paths) > 1:
            legend = ax.legend(loc='upper left', facecolor='#161b22',
                              edgecolor='#30363d', fontsize=10)
            for text in legend.get_texts():
                text.set_color('white')

        max_frames = max(len(p) for p in self.paths) + 5

        def animate(frame):
            best_val = float('-inf')
            best_pos = None

            for i, path in enumerate(self.paths):
                idx = min(frame, len(path) - 1)
                xs = [p.x for p in path[:idx + 1]]
                ys = [p.y for p in path[:idx + 1]]
                path_lines[i].set_data(xs, ys)
                current_markers[i].set_data([path[idx].x], [path[idx].y])

                val = self.func(path[idx])
                if val > best_val:
                    best_val = val
                    best_pos = path[idx]

            if best_pos:
                best_star.set_data([best_pos.x], [best_pos.y])

            info_text.set_text(f'Step {frame}  |  Best: {best_val:.1f}')

            return path_lines + current_markers + [best_star, info_text]

        anim = animation.FuncAnimation(
            fig, animate, frames=max_frames, interval=interval, blit=False
        )

        plt.tight_layout()

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

    func = get_function(args.function)
    visualizer = HillClimbVisualizer(func, stochastic=args.stochastic)

    print(f"Running hill climb on '{args.function}' function...")
    visualizer.run_climb(restarts=args.restarts)
    visualizer.create_animation(interval=args.interval, save_path=args.save)


if __name__ == "__main__":
    main()
