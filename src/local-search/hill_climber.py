#!/usr/local/bin/python3
#
# hill_climbing.py
# src
#
# Created by Illya Starikov on 10/13/18.
# Copyright 2018. Illya Starikov. MIT License.
#

from random import randint, shuffle, choice

from function import Function
from node import Node


class HillClimber:
    """A steepest-ascent hill-climbing algorithm."""

    def __init__(self, function):
        """Create a HillClimber objection.

        Args:
            function (Function): The function to maximize.
        """

        self.function = function

    def _value_at_node(self, node):
        """Evaluate a value at `node`.

        Args:
            node (Node): Where to evaluate the value at.
        """

        return self.function(node)

    def _initial_node(self):
        """Generate a random, initial node.

        Returns:
            Node: A random, initial node.
        """

        x = randint(self.function.x_bounds[0], self.function.x_bounds[1])
        y = randint(self.function.y_bounds[0], self.function.y_bounds[1])

        return Node(x, y)

    def _generate_all_neighbors(self, node):
        """Generate all neighbors of `node`.

        Args:
            node (Node): The node to generate neighbors for.

        Returns:
            list<Node>: All neighbors of `node`.
        """

        x, y = node.x, node.y

        nodes = [Node(x, y)]

        if x < self.function.x_bounds[1]:
            nodes.append(Node(x + 1, y))
        if x > self.function.x_bounds[0]:
            nodes.append(Node(x - 1, y))
        if y < self.function.y_bounds[1]:
            nodes.append(Node(x, y + 1))
        if y > self.function.x_bounds[0]:
            nodes.append(Node(x, y - 1))

        shuffle(nodes)
        return nodes

    def _highest_valued_node(self, neighbors):
        """Find the node with the highest value.

        neighbors (list<Node>): The list to search the highest value in.

        Returns:
            Node: The highest valued node.
        """

        max_point = neighbors[0]

        for point in neighbors[1:]:
            if self._value_at_node(point) > self._value_at_node(max_point):
                max_point = point

        return max_point

    def climb(self):
        """Run the steepest-ascent hill-climbing algorithm, finding a local optimum in a function.

        Returns:
            Node: The local optimum discovered.
        """
        current_node = self._initial_node()

        while True:
            print("Exploring Node({}, {})".format(current_node.x, current_node.y))
            neighbors = self._generate_all_neighbors(current_node)
            successor = self._highest_valued_node(neighbors)

            if self._value_at_node(successor) <= self._value_at_node(current_node):
                return current_node

            current_node = successor
