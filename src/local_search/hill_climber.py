"""Hill climbing optimization algorithms.

This module provides the HillClimber class implementing both steepest-ascent
and stochastic hill climbing algorithms with optional random restarts.

Example:
    import function
    import hill_climber

    func = function.Function(
        lambda x, y: -(x**2 + y**2), (-100, 100), (-100, 100)
    )

    # Steepest-ascent hill climbing
    climber = hill_climber.HillClimber(func)
    optimum = climber.climb()

    # Stochastic hill climbing with restarts
    climber = hill_climber.HillClimber(func, stochastic=True)
    optimum = climber.climb(restarts=10)
"""

from __future__ import annotations

import random
import typing

import function
import node


class HillClimber:
    """Hill climbing optimizer with configurable behavior.

    Supports both steepest-ascent and stochastic hill climbing strategies.
    Steepest-ascent always moves to the highest-valued neighbor, while
    stochastic randomly selects among uphill moves. Optional random restarts
    help escape local optima.

    Attributes:
        function: The objective function to maximize.
        stochastic: Whether to use stochastic neighbor selection.
    """

    def __init__(
        self, func: function.Function, stochastic: bool = False
    ) -> None:
        """Create a HillClimber for the given function.

        Args:
            func: The objective function to maximize.
            stochastic: If True, randomly select among uphill moves.
                If False (default), always choose steepest ascent.
        """
        self.function = func
        self.stochastic = stochastic

    def _value_at_node(self, n: node.Node) -> float:
        """Evaluate the objective function at a node.

        Args:
            n: The position to evaluate.

        Returns:
            The function value at the node.
        """
        return self.function(n)

    def _initial_node(self) -> node.Node:
        """Generate a random starting position.

        Returns:
            A Node with random coordinates within the function bounds.
        """
        x = random.randint(
            self.function.x_bounds[0], self.function.x_bounds[1]
        )
        y = random.randint(
            self.function.y_bounds[0], self.function.y_bounds[1]
        )
        return node.Node(x, y)

    def _generate_all_neighbors(
        self, n: node.Node
    ) -> typing.List[node.Node]:
        """Generate all valid neighbors of a node.

        Creates nodes in the 4 cardinal directions (up, down, left, right)
        that are within the function bounds.

        Args:
            n: The node to find neighbors for.

        Returns:
            List of valid neighboring nodes (shuffled).
        """
        x, y = n.x, n.y
        nodes = [node.Node(x, y)]

        if x < self.function.x_bounds[1]:
            nodes.append(node.Node(x + 1, y))
        if x > self.function.x_bounds[0]:
            nodes.append(node.Node(x - 1, y))
        if y < self.function.y_bounds[1]:
            nodes.append(node.Node(x, y + 1))
        if y > self.function.y_bounds[0]:
            nodes.append(node.Node(x, y - 1))

        random.shuffle(nodes)
        return nodes

    def _select_successor(
        self, current_node: node.Node, neighbors: typing.List[node.Node]
    ) -> node.Node:
        """Select the next node to move to.

        Uses steepest-ascent or stochastic selection based on configuration.

        Args:
            current_node: The current position.
            neighbors: List of neighboring nodes.

        Returns:
            The selected successor node.
        """
        if self.stochastic:
            return self._get_random_uphill_move(current_node, neighbors)
        return self._get_highest_valued_node(neighbors)

    def _get_highest_valued_node(
        self, neighbors: typing.List[node.Node]
    ) -> node.Node:
        """Find the node with the highest function value.

        Args:
            neighbors: List of nodes to compare.

        Returns:
            The node with the highest objective function value.
        """
        return max(neighbors, key=lambda nd: self._value_at_node(nd))

    def _get_random_uphill_move(
        self, current_node: node.Node, neighbors: typing.List[node.Node]
    ) -> node.Node:
        """Find a random uphill move from the neighbors.

        Args:
            current_node: The current position.
            neighbors: List of neighboring nodes.

        Returns:
            A randomly selected uphill neighbor, or current_node if none.
        """
        current_value = self._value_at_node(current_node)
        uphill_nodes = [
            n for n in neighbors
            if self._value_at_node(n) > current_value
        ]

        if not uphill_nodes:
            return current_node
        return random.choice(uphill_nodes)

    def climb(
        self, restarts: typing.Optional[int] = None
    ) -> node.Node:
        """Run the hill climbing algorithm.

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
        """Perform a single hill climb.

        Returns:
            The local optimum found.
        """
        current_node = self._initial_node()

        while True:
            print(f"Exploring Node({current_node.x}, {current_node.y})")

            neighbors = self._generate_all_neighbors(current_node)
            successor = self._select_successor(current_node, neighbors)

            successor_val = self._value_at_node(successor)
            current_val = self._value_at_node(current_node)
            if successor_val <= current_val:
                return current_node

            current_node = successor

    def _climb_with_restarts(self, num_restarts: int) -> node.Node:
        """Perform multiple hill climbs with random restarts.

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
                successor = self._select_successor(current_node, neighbors)

                current_val = self._value_at_node(current_node)
                best_val = self._value_at_node(best_node)
                if current_val > best_val:
                    best_node = current_node

                successor_val = self._value_at_node(successor)
                if successor_val <= current_val:
                    break

                current_node = successor

        return best_node
