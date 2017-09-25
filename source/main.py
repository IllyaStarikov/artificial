#!/usr/local/bin/python3
#
# main.py
# 2017-fs-1a-hw1-isgx2
#
# Created by Illya Starikov on 09/05/17.
# Copyright 2017. Illya Starikov. All rights reserved.
#

from utilities import configure, output_log, output_solution, get_number_of_runs
from history import History
from math import floor


def main():
    max_fitness = -1

    for run in range(1, get_number_of_runs() + 1):
        evolutionary_algorithm, path_to_solution, path_to_log, configuration_parameters = configure()

        chunks = floor(evolutionary_algorithm.get_evalutions_until_termination() / 10)

        iterations = 0
        fitnesses = []
        max_solution = max(evolutionary_algorithm.get_solutions())

        history = History(evolutionary_algorithm.get_termination_number_best(), evolutionary_algorithm.get_termination_number_average())

        while not evolutionary_algorithm.determine_if_should_terminate(iterations, history):
            offspring = evolutionary_algorithm.reproduce()
            evolutionary_algorithm.combine_offspring_and_parents(offspring)

            evolutionary_algorithm.run_survival()

            current_best_solution = evolutionary_algorithm.get_best()
            fitness = current_best_solution.fitness()

            average_fitness = evolutionary_algorithm.get_average()

            if fitness > max_fitness:
                max_solution = current_best_solution
                max_fitness = fitness

            fitnesses += [(iterations, fitness, average_fitness)]
            iterations += evolutionary_algorithm.mu

            if iterations % chunks == 0:
                print("Iteration #{} Finished".format(iterations))

        output_log(path_to_log, configuration_parameters, fitnesses, run)
        print("Run #{} Finished With Max Fitness.".format(run), max_fitness)

        output_solution(path_to_solution, max_solution)
    print("Max Fitness: {}".format(max_fitness))


if __name__ == "__main__":
    main()
