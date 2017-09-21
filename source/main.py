#!/usr/local/bin/python3
#
# main.py
# 2017-fs-1a-hw1-isgx2
#
# Created by Illya Starikov on 09/05/17.
# Copyright 2017. Illya Starikov. All rights reserved.
#

from os import path
from solution import Solution
from utilities import configure, get_shapes_and_board_dimensions, output_log, output_solution


def main():
    filename, max_iterations, number_of_runs, seed, path_to_log, path_to_solution = configure()

    configuration_parameters = {"Input File": path.abspath(filename), "Max Iterations": max_iterations, "Runs": number_of_runs, "Seed": seed, "Log Path": path.abspath(path_to_log), "Solution Path": path.abspath(path_to_solution)}

    max_fitness = -1

    for run in range(1, number_of_runs + 1):
        fitnesses = []

        for iteration in range(max_iterations):
            shapes, dimensions = get_shapes_and_board_dimensions(filename)
            solution = Solution(shapes, dimensions, run)
            fitness = solution.fitness(dimensions)

            if fitness > max_fitness:
                max_solution = solution
                max_fitness = fitness

            if len(fitnesses) < 1:
                greatest_fitness_thus_far = 0
            else:
                _, greatest_fitness_thus_far = fitnesses[-1]

            if fitness > greatest_fitness_thus_far:
                fitnesses += [(iteration, fitness)]

        output_log(path_to_log, configuration_parameters, fitnesses, run)
        print("Run #{} Finished With Max Fitness.".format(run), max_fitness)

        output_solution(path_to_solution, max_solution)
    print("Max Fitness: {}".format(max_fitness))


if __name__ == "__main__":
    main()
