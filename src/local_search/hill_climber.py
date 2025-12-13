"""Steepest-ascent hill climbing algorithm.

This module provides the HillClimber class implementing the classic
steepest-ascent hill climbing optimization algorithm.

Example:
    func = Function(lambda x, y: -(x**2 + y**2), (-100, 100), (-100, 100))
    climber = HillClimber(func)
    optimum = climber.climb()
"""

from __future__ import annotations

import random
import typing

import function
import node


class HillClimber:
    """Steepest-ascent hill climbing optimizer.

    Finds a local optimum by iteratively moving to the highest-valued
    neighboring position until no improvement is possible.

    Attributes:
        function: The objective function to maximize.
    """

    def __init__(self, func: function.Function) -> None:
        """Create a HillClimber for the given function.

        Args:
            func: The objective function to maximize.
        """
        self.function = func

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
        x = random.randint(self.function.x_bounds[0], self.function.x_bounds[1])
        y = random.randint(self.function.y_bounds[0], self.function.y_bounds[1])
        return node.Node(x, y)

    def _generate_all_neighbors(self, n: node.Node) -> typing.List[node.Node]:
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

    def _highest_valued_node(self, neighbors: typing.List[node.Node]) -> node.Node:
        """Find the node with the highest function value.

        Args:
            neighbors: List of nodes to compare.

        Returns:
            The node with the highest objective function value.
        """
        return max(neighbors, key=lambda nd: self._value_at_node(nd))

    def climb(self) -> node.Node:
        """Run the steepest-ascent hill climbing algorithm.

        Starting from a random position, iteratively moves to the
        highest-valued neighbor until a local optimum is reached.

        Returns:
            The local optimum found.
        """
        current_node = self._initial_node()

        while True:
            print(f"Exploring Node({current_node.x}, {current_node.y})")

            neighbors = self._generate_all_neighbors(current_node)
            successor = self._highest_valued_node(neighbors)

            if self._value_at_node(successor) <= self._value_at_node(current_node):
                return current_node

            current_node = successor
