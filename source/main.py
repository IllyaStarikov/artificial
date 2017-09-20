#!/usr/local/bin/python3
#
# main.py
# 2017-fs-1a-hw1-isgx2
#
# Created by Illya Starikov on 09/05/17.
# Copyright 2017. Illya Starikov. All rights reserved.
#

import random
import json
import time
import os
import sys
import numpy as np

from shape import Shape


def main():
    filename, max_iterations, number_of_runs, seed, path_to_log, path_to_solution = configure()

    configuration_parameters = {"Input File": os.path.abspath(filename), "Max Iterations": max_iterations, "Runs": number_of_runs, "Seed": seed, "Log Path": os.path.abspath(path_to_log), "Solution Path": os.path.abspath(path_to_solution)}

    max_solution = []
    max_fitness = -1
    max_run = -1

    for run in range(1, number_of_runs + 1):
        fitnesses = []

        for iteration in range(max_iterations):
            shapes, dimensions = get_shapes_and_board_dimensions(filename)
            solution = generate_solution(shapes, dimensions)
            fitness = calculate_fitness(solution, dimensions)

            if fitness > max_fitness:
                max_fitness = fitness
                max_solution = solution
                max_run = run

            if len(fitnesses) < 1:
                greatest_fitness_thus_far = 0
            else:
                _, greatest_fitness_thus_far = fitnesses[-1]

            if fitness > greatest_fitness_thus_far:
                fitnesses += [(iteration, fitness)]

        output_log(path_to_log, configuration_parameters, fitnesses, run)
        print("Run #{} Finished With Max Fitness.".format(run), max_fitness)

        output_solution(path_to_solution, max_solution, max_run)
    print("Max Fitness: {}".format(max_fitness))


def get_file_contents(filename):
    with open(filename) as file_:
        return file_.read().split("\n")


def get_config_contents(config_filename):
    contents = get_file_contents(config_filename)
    contents = "\n".join(contents)

    json_data = json.loads(contents)
    return json_data


def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate


def configure():
    configuration = get_config_contents(sys.argv[1])
    max_iterations = configuration["iterations"]
    number_of_runs = configuration["runs"]

    if configuration["predefined-seed"]:
        seed_ = configuration["seed"]
        random.seed(seed_)
    else:
        seed_ = random_arbitrary(0, 2**31 - 1)
        random.seed(seed_)

    np.set_printoptions(threshold=np.nan)

    filename = sys.argv[2]
    path_to_solution = configuration["path-to-solution"]
    path_to_log = configuration["path-to-log"]

    if not os.path.isdir(path_to_solution):
        os.makedirs(path_to_solution)

    if not os.path.isdir(path_to_log):
        os.makedirs(path_to_log)

    return filename, max_iterations, number_of_runs, seed_, path_to_log, path_to_solution


def random_arbitrary(floor, ceiling):
    return random.randint(floor, ceiling)


# x_bounds is a tuple (min, max) the values x can take
# same for y
def generate_random_point(row_bounds, column_bounds):
    row_min, row_max = row_bounds
    column_min, column_max = column_bounds
    return (random_arbitrary(row_min, row_max), random_arbitrary(column_min, column_max))


def get_shapes_and_board_dimensions(filename):
    file_contents = get_file_contents(filename)

    shapes = []
    max_width = 0
    max_height, _ = [int(x) for x in file_contents[0].split(' ')]

    for line in file_contents[1:]:
        if line != "":
            input_ = line.split(' ')
            shape = Shape(input_)

            shapes += [shape]
            max_width += shape.get_width()

    return shapes, (max_width, max_height - 1)


def generate_solution(shapes, dimensions):
    solution = []

    index = 0
    board_columns, board_rows = dimensions

    current_points = set()
    while index < len(shapes):
        shape = shapes[index]
        attempts = 0

        solution_found = False
        while attempts < 100 or not solution_found:
            random_rotation = random_arbitrary(0, 3)
            random_point = generate_random_point((0, board_rows), (0, board_columns))

            shape.set_rotation(random_rotation)
            shape.set_start_position(random_point)

            solution_found = True
            for row, column in shape.get_points_in_path():
                if (row, column) in current_points or not (0 <= row < board_rows) or not (0 <= column < board_columns):
                    solution_found = False

            attempts += 1

        if solution_found:
            points = shape.get_points_in_path()
            current_points = current_points.union(points)
            solution += [shape]
            index += 1
        else:
            current_points = set()
            solution = []
            index = 0

    return solution


def calculate_fitness(solution, board_dimensions):
    max_length, _ = board_dimensions
    rightmost_column = 0

    for shape in solution:
        _, max_right = shape.get_rightmost_point()
        rightmost_shape_value = max_right

        if rightmost_shape_value > rightmost_column:
            rightmost_column = rightmost_shape_value
    length_used = rightmost_column
    return max_length - length_used


def output_to_file(filename, string):
    with open(filename, 'a') as out:
        out.write(string + "\n")


def output_solution(solution_directory, solution, run):
    # current_date_time = time.strftime("%Y-%m-%d_%H-%M-%S")
    # filename = solution_directory + "/solution-" + current_date_time + ".txt"
    filename = solution_directory + "solution_this_one.txt"

    #output_to_file(filename, "-- Solution Found on Run #{} --".format(run))
    for shape in solution:
        row, column = shape.get_start_position()
        rotations = shape.get_rotations()
        output_to_file(filename, "{},{},{}".format(column, row, rotations))


@static_vars(already_output_header=False, filename=None)
def output_log(path_to_log, configuration_parameters, fitnesses, run):
    if output_log.filename is None:
        current_date = time.strftime("%Y-%m-%d")
        output_log.filename = path_to_log + "/log-" + current_date + ".txt"

    if not output_log.already_output_header:
        output_log.already_output_header = True

        for key, value in configuration_parameters.items():
            output_to_file(output_log.filename, "{}: {}".format(key.ljust(20), str(value)))

    output_to_file(output_log.filename, "-- Run #{} --".format(run))

    for iteration, fitness in fitnesses:
        output_to_file(output_log.filename, "{}\t{}".format(iteration, fitness))

    output_log.last_run = run


if __name__ == "__main__":
    main()
