#!/usr/local/bin/python3
#
# stochastic_hill_climbing_with_restarts.py
# src
#
# Created by Illya Starikov on 10/13/18.
# Copyright 2018. Illya Starikov. MIT License.
#

from stochastic_hill_climber import StochasticHillClimber


class StochasticHillClimberWithRestarts(StochasticHillClimber):
    """A stochastic steepest-ascent hill-climbing algorithm with restarts."""

    def climb(self, number_of_generations):
        """Run the steepest-ascent hill-climbing algorithm with restarts upon discovering a local optimum,
        finding a local optimum in a function.

        Args:
            number_of_generations (int): The number of restarts allowed.

        Returns:
            Node: The local optimum discovered.
        """

        max_node = self._initial_node()

        for generations in range(number_of_generations):
            current_node = self._initial_node()

            while True:
                print("Generation {}, Exploring Node({}, {}), Current Max Node({}, {})".format(generations, current_node.x, current_node.y, max_node.x, max_node.y))

                neighbors = self._generate_all_neighbors(current_node)
                successor = self._get_random_uphill_move(current_node, neighbors)

                if self._value_at_node(max_node) < self._value_at_node(current_node):
                    max_node = current_node

                if self._value_at_node(successor) <= self._value_at_node(current_node):
                    break

                current_node = successor

        return max_node
