"""Stochastic hill climbing algorithm with optional restarts.

This module provides the StochasticHillClimber class implementing a
stochastic variant of hill climbing that randomly selects among uphill
moves, with optional random restarts.

Example:
    func = Function(lambda x, y: -(x**2 + y**2), (-100, 100), (-100, 100))
    climber = StochasticHillClimber(func)

    # Single run
    optimum = climber.climb()

    # With restarts
    optimum = climber.climb(restarts=10)
"""

from __future__ import annotations

import random
import typing

import hill_climber
import node


class StochasticHillClimber(hill_climber.HillClimber):
    """Stochastic hill climbing optimizer with optional restarts.

    Instead of always choosing the steepest ascent, this variant randomly
    selects among uphill moves. This can help escape local optima. Optional
    random restarts further improve global optimization.

    Attributes:
        function: The objective function to maximize.
    """

    def _get_random_uphill_move(
        self, current_node: node.Node, neighbors: typing.List[node.Node]
    ) -> node.Node:
        """Find a random uphill move from the neighbors.

        Args:
            current_node: The current position.
            neighbors: List of neighboring nodes.

        Returns:
            A randomly selected uphill neighbor, or current_node if none exist.
        """
        current_value = self._value_at_node(current_node)
        uphill_nodes = [
            n for n in neighbors
            if self._value_at_node(n) > current_value
        ]

        if not uphill_nodes:
            return current_node
        return random.choice(uphill_nodes)

    def climb(self, restarts: typing.Optional[int] = None) -> node.Node:
        """Run the stochastic hill climbing algorithm.

        Args:
            restarts: Number of random restarts to perform. If None, runs
                a single climb without restarts.

        Returns:
            The best local optimum found (across all restarts if applicable).
        """
        if restarts is None:
            return self._climb_once()
        return self._climb_with_restarts(restarts)

    def _climb_once(self) -> node.Node:
        """Perform a single stochastic hill climb.

        Returns:
            The local optimum found.
        """
        current_node = self._initial_node()

        while True:
            print(f"Exploring Node({current_node.x}, {current_node.y})")

            neighbors = self._generate_all_neighbors(current_node)
            successor = self._get_random_uphill_move(current_node, neighbors)

            successor_val = self._value_at_node(successor)
            current_val = self._value_at_node(current_node)
            if successor_val <= current_val:
                return current_node

            current_node = successor

    def _climb_with_restarts(self, num_restarts: int) -> node.Node:
        """Perform multiple stochastic hill climbs with random restarts.

        Args:
            num_restarts: Number of independent climbs to perform.

        Returns:
            The best local optimum found across all restarts.
        """
        best_node = self._initial_node()

        for generation in range(num_restarts):
            current_node = self._initial_node()

            while True:
                print(
                    f"Generation {generation}, "
                    f"Exploring Node({current_node.x}, {current_node.y}), "
                    f"Current Max Node({best_node.x}, {best_node.y})"
                )

                neighbors = self._generate_all_neighbors(current_node)
                successor = self._get_random_uphill_move(
                    current_node, neighbors
                )

                current_val = self._value_at_node(current_node)
                best_val = self._value_at_node(best_node)
                if current_val > best_val:
                    best_node = current_node

                successor_val = self._value_at_node(successor)
                if successor_val <= current_val:
                    break

                current_node = successor

        return best_node
