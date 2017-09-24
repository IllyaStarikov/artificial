#!/usr/local/bin/python3
#
# EA.py
# source
#
# Created by Illya Starikov on 09/24/17.
# Copyright 2017. Illya Starikov. All rights reserved.
#

from random import uniform


class EA():
    mu = -1  # number of candidate solutions in the parent generation
    lambda_ = -1  # number of children to create
    solutions = []

    def get_sum_fitness(self):
        return self.get_sum_from_solutions(self.get_solutions())

    def get_sum_from_solutions(self, solutions):
        sum_ = 0

        for solution in solutions:
            sum_ += solution.fitness()

        return sum_

    def fitness_proportional_selection(self):
        sorted_solutions = sorted(self.get_solutions())
        selected = []

        while len(selected) < self.mu:
            max_ = self.get_sum_fitness()
            pick = uniform(0, max_)

            current = 0

            for solution in sorted_solutions:
                current += solution.fitness()

                if current > pick:
                    selected += [solution]
                    sorted_solutions.remove(solution)

                    break

        return selected

    def get_solutions(self):
        return self.solutions
