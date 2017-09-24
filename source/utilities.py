#!/usr/local/bin/python3
#
# utilities.py
# source
#
# Created by Illya Starikov on 09/20/17.
# Copyright 2017. Illya Starikov. All rights reserved.
#

import random
import json
import time
import os
import sys

from copy import deepcopy
from shape import Shape
from enum import Enum
from math import floor


Side = Enum("left", "right")


def generate_initial_population(board_dimensions, shapes, size):
    from solution import Solution  # prevent interpretor error. literally just a bandaid
    solutions = []

    for i in range(size):
        solutions += [Solution(shapes, board_dimensions, 0)]

    return solutions


def chunks(list_to_chunk, every_x_elements_chunk):
    every_x_elements_chunk = max(1, every_x_elements_chunk)
    return list(list_to_chunk[i:i + every_x_elements_chunk] for i in range(0, len(list_to_chunk), every_x_elements_chunk))


def is_even(x):
    return x % 2 == 0


def n_point_crossover(list_one, list_two, n):
    length_of_lists = min(len(list_one), len(list_two))
    number_of_chunks = floor(length_of_lists / n)

    chunk_one, chunk_two = chunks(list_one, number_of_chunks), chunks(list_two, number_of_chunks)
    solution_one, solution_two = [], []

    for index, (segment_one, segment_two) in enumerate(zip(chunk_one, chunk_two)):

        if is_even(index):
            solution_one += segment_one
            solution_two += segment_two
        else:
            solution_one += segment_two
            solution_two += segment_two

    return solution_one, solution_two


def shuffled_array(array):
    array2 = deepcopy(array)
    random.shuffle(array2)
    return array2


def add_list_of_sets(sets):
    added_set = set()

    for set_ in sets:
        added_set = added_set.union(set_)

    return added_set


def random_arbitrary(floor, ceiling):
    return random.randint(floor, ceiling)


# x_bounds is a tuple (min, max) the values x can take
# same for y
def generate_random_point(row_bounds, column_bounds):
    row_min, row_max = row_bounds
    column_min, column_max = column_bounds
    return (random_arbitrary(row_min, row_max), random_arbitrary(column_min, column_max))


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

    filename = sys.argv[2]
    initial_population = configuration["initial-population"]
    path_to_solution = configuration["path-to-solution"]
    path_to_log = configuration["path-to-log"]
    mutation_rate = configuration["mutation-rate"]

    if not os.path.isdir(path_to_solution):
        os.makedirs(path_to_solution)

    if not os.path.isdir(path_to_log):
        os.makedirs(path_to_log)

    return filename, max_iterations, number_of_runs, seed_, path_to_log, path_to_solution, initial_population, mutation_rate


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
            max_width += max(shape.get_width(), shape.get_height())

    return shapes, (max_width, max_height - 1)  # -1 because the height given isn't zero indexed


def output_to_file(filename, string):
    with open(filename, 'a') as out:
        out.write(string + "\n")


def output_solution(solution_directory, solution):
    # current_date_time = time.strftime("%Y-%m-%d_%H-%M-%S")
    # filename = solution_directory + "/solution-" + current_date_time + ".txt"
    # run = solution.get_run()

    filename = solution_directory + "solution_this_one.txt"
    # output_to_file(filename, "-- Solution Found on Run #{} --".format(run))
    for shape in solution.get_shapes():
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
