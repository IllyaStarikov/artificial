#!/usr/local/bin/python3
#
# EA.py
# source
#
# Created by Illya Starikov on 09/24/17.
# Copyright 2017. Illya Starikov. All rights reserved.
#

import random
import sys

from functools import partial, reduce
from math import ceil
from random import shuffle


class EA():
    mu = -1  # number of candidate solutions in the parent generation
    lambda_ = -1  # number of children to create
    mutation_rate = 0.0  # MUST be between 0 and 1, inclusive

    tourmanent_size_parent, tourmanent_size_survival = -1, -1
    evaluations_until_termination, number_of_runs = -1, -1
    evaluations = 0

    __parent_selection_algorithm, __survival_selection_algorithm = None, None
    __no_change_in_average_n, __no_change_in_best_n = 0, 0
    __termination_functions = None
    solutions = []

    def __init__(self, configuration):
        from utilities import get_shapes_and_board_dimensions, generate_initial_population

        filename = sys.argv[2]

        initial_population_size = configuration["initial-population"]
        self.mu, self.lambda_ = configuration["mu"], configuration["lambda"]
        self.mutation_rate = configuration["mutation-rate"]

        initilization_method = configuration["initialization"]
        parent_selection_algorithm = configuration["parent-selection"]
        surival_selection_algorithm = configuration["survival-selection"]
        termination_conditions = configuration["termination"]
        self.__set_termination_function(termination_conditions)

        self.evaluations_until_termination = configuration["evaluations-until-termination"]
        self.number_of_runs = configuration["number-of-runs"]

        shapes, dimensions = get_shapes_and_board_dimensions(filename)

        if initilization_method == "uniform-random":
            self.solutions = generate_initial_population(dimensions, shapes, initial_population_size)

        # below, just have arguments defaulted to what they should be
        if parent_selection_algorithm == "Fitness Proportional Selection":
            with_parially_applied_arguments = partial(self.__fitness_proportional_selection, cutoff=self.lambda_)
            self.__parent_selection_algorithm = with_parially_applied_arguments
        elif parent_selection_algorithm == "k-Tournament Selection with replacement":
            k_value = configuration["k"]
            with_parially_applied_arguments = partial(self.__k_tournament_selection, cutoff=self.lambda_, k=k_value, with_replacement=True)
            self.__parent_selection_algorithm = with_parially_applied_arguments

        if surival_selection_algorithm == "Truncation":
            with_parially_applied_arguments = partial(self.__truncation, cutoff=self.lambda_)
            self.__survival_selection_algorithm = with_parially_applied_arguments
        elif surival_selection_algorithm == "k-Tournament Selection without replacement":
            k_value = configuration["k"]
            with_parially_applied_arguments = partial(self.__k_tournament_selection, cutoff=self.lambda_, k=k_value, with_replacement=False)
            self.survival_selection_algorithm = with_parially_applied_arguments

    def __set_termination_function(self, configuration_for_termination):
        # all functions have the input {"parameter": value}
        functions = []
        index = 0

        while index < len(configuration_for_termination):
            function = configuration_for_termination[index]

            if function == "evaluations":
                functions += [lambda inputs: inputs["evaluations"] > self.evaluations_until_termination]
            elif function == "no-change-in-average":
                self.__no_change_in_average_n = configuration_for_termination[index + 1]
                functions += [lambda inputs: not inputs["history"].determine_if_average_got_better()]
                index += 1
            elif function == "no-change-in-best":
                self.__no_change_in_best_n = configuration_for_termination[index + 1]
                functions += [lambda inputs: not inputs["history"].determine_if_best_got_better()]
                index += 1

            index += 1

        self.__termination_functions = functions

    def __get_inputs(self, evals, history):
        inputs = {}
        inputs["evaluations"] = evals
        inputs["history"] = history

        return inputs

    def determine_if_should_terminate(self, evaluations, history):
        inputs = self.__get_inputs(evaluations, history)
        return reduce(lambda x, y: x or y(inputs), self.__termination_functions, False)

    def reproduce(self):
        from utilities import get_percentage_change, random_arbitrary

        parents = self.__parent_selection_algorithm()
        offspring = []

        for i in range(self.mu):
            parent_one, parent_two = random.sample(parents, 2)  # get two parents
            child = parent_one.recombination(parent_two, 2)

            should_mutate = get_percentage_change(self.mutation_rate * 100)
            if should_mutate:
                mutation_rate = ceil(random_arbitrary(1, 5) / 100)
                child = child.mutated(mutation_rate)

            offspring += [child]

        return offspring

    def run_survival(self):
        population = self.__survival_selection_algorithm()
        self.solutions = population

    def combine_offspring_and_parents(self, offspring):
        self.solutions += offspring
        return self.solutions

    def get_sum_fitness(self):
        return self.get_sum_from_solutions(self.get_solutions())

    def get_sum_from_solutions(self, solutions):
        sum_ = 0

        for solution in solutions:
            sum_ += solution.fitness()

        return sum_

    def get_average(self):
        return self.get_sum_from_solutions(self.solutions) / len(self.solutions)

    def get_best(self):
        return max(self.solutions)

    # MARK: Private Methods
    def __fitness_proportional_selection(self, cutoff):
        sorted_solutions = sorted(self.get_solutions())
        selected = []

        while len(selected) < self.mu:
            max_ = self.get_sum_fitness()
            pick = random.uniform(0, max_)

            current = 0

            for solution in sorted_solutions:
                current += solution.fitness()

                if current > pick:
                    selected += [solution]
                    sorted_solutions.remove(solution)

                    break

        return selected

    def __k_tournament_selection(self, k, with_replacement, cutoff):
        from copy import deepcopy

        selected = []
        solutions = deepcopy(self.get_solutions())
        random.shuffle(solutions)

        if k < len(selected):
            k = len(selected)

        while len(selected) < cutoff:
            tournament_candidates = solutions[:k]  # Fugh.. fugh.. fugh.. FIGHT
            winner = max(tournament_candidates)  # FLAWLESS VICTORY
            # reference: https://www.youtube.com/watch?v=0jFcBMY71-M

            selected += [winner]

            if not with_replacement:
                solutions.remove(winner)

        return selected

    def __truncation(self, cutoff):
        return sorted(self.shapes)[:cutoff]

    def get_solutions(self):
        return self.solutions

    def get_termination_number_average(self):
        return self.__no_change_in_average_n

    def get_termination_number_best(self):
        return self.__no_change_in_best_n

    def get_evalutions_until_termination(self):
        return self.evaluations_until_termination
