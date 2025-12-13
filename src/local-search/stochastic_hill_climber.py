#!/usr/local/bin/python3
#
# stochastic_hill_climbing.py
# src
#
# Created by Illya Starikov on 10/13/18.
# Copyright 2018. Illya Starikov. MIT License.
#


from random import choice

from hill_climber import HillClimber


class StochasticHillClimber(HillClimber):
    """A stochastic steepest-ascent hill-climbing algorithm with optional restarts."""

    def _get_random_uphill_move(self, current_node, neighbors):
        """Find a random uphill move relative to `current_node` in `neighbors`.

        Args:
            current_node (Node): The current node in the search.
            neighbors (list<Node>): The neighbors of `current_node`.

        Returns:
            Node: A random, uphill move.
        """

        uphill_nodes = []

        for point in neighbors:
            if self._value_at_node(point) > self._value_at_node(current_node):
                uphill_nodes.append(point)

        return current_node if len(uphill_nodes) == 0 else choice(uphill_nodes)

    def climb(self, restarts=None):
        """Run the stochastic hill-climbing algorithm, finding a local optimum in a function.

        Args:
            restarts (int, optional): Number of restarts to perform. If None, runs without restarts.

        Returns:
            Node: The local optimum discovered.
        """
        if restarts is None:
            return self._climb_once()
        else:
            return self._climb_with_restarts(restarts)

    def _climb_once(self):
        """Run a single climb without restarts.

        Returns:
            Node: The local optimum discovered.
        """
        current_node = self._initial_node()

        while True:
            print("Exploring Node({}, {})".format(current_node.x, current_node.y))

            neighbors = self._generate_all_neighbors(current_node)
            successor = self._get_random_uphill_move(current_node, neighbors)

            if self._value_at_node(successor) <= self._value_at_node(current_node):
                return current_node

            current_node = successor

    def _climb_with_restarts(self, number_of_restarts):
        """Run the hill-climbing algorithm with restarts upon discovering a local optimum.

        Args:
            number_of_restarts (int): The number of restarts allowed.

        Returns:
            Node: The best local optimum discovered across all restarts.
        """
        max_node = self._initial_node()

        for generation in range(number_of_restarts):
            current_node = self._initial_node()

            while True:
                print("Generation {}, Exploring Node({}, {}), Current Max Node({}, {})".format(
                    generation, current_node.x, current_node.y, max_node.x, max_node.y))

                neighbors = self._generate_all_neighbors(current_node)
                successor = self._get_random_uphill_move(current_node, neighbors)

                if self._value_at_node(max_node) < self._value_at_node(current_node):
                    max_node = current_node

                if self._value_at_node(successor) <= self._value_at_node(current_node):
                    break

                current_node = successor

        return max_node
