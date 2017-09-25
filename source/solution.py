#!/usr/local/bin/python3
#
# solution.py
# source
#
# Created by Illya Starikov on 09/20/17.
# Copyright 2017. Illya Starikov. All rights reserved.
#

from utilities import random_arbitrary, generate_random_point, shuffled_array, add_list_of_sets, n_point_crossover
from math import floor
from copy import deepcopy
import random
import operator

MAX_ATTEMPT_TO_PLACE_SHAPE = 255  # a nice, CS number


class Solution():
    # MARK: Properties
    shapes = []
    all_points = set()
    run = -1
    dimensions = (-1, -1)

    # MARK: Constructors
    def __init__(self, shapes, dimensions, run):
        self.run = run
        self.dimensions = dimensions
        self.shapes = shapes

        self.shapes, self.all_points = self.__generate_solution(self.shapes, set())

    def fitness(self):
        max_length, _ = self.get_dimensions()
        rightmost_column = 0

        for shape in self.__get_shapes_unsorted():
            _, max_right = shape.get_rightmost_point()
            rightmost_shape_value = max_right

            if rightmost_shape_value > rightmost_column:
                rightmost_column = rightmost_shape_value
        length_used = rightmost_column
        return max_length - length_used

    def mutated(self, rate):
        number_of_mutations = floor(len(self.shapes) * rate)
        random_shapes = shuffled_array(self.shapes)

        mutated_shapes = random_shapes[number_of_mutations:]  # random take off (at the end) the specified rate of mutation
        shapes_to_mutate = random_shapes[:number_of_mutations]  # this is just the inverse of above

        mutated_shapes_list = [(x.get_points_in_path()) for x in mutated_shapes]
        mutated_shapes_points = add_list_of_sets(mutated_shapes_list)

        new_shapes, new_points = self.__generate_solution(shapes_to_mutate, mutated_shapes_points)
        new_solution = self.__init_solved_solution(new_points, mutated_shapes + new_shapes)

        return new_solution

    def recombination(self, other_solution, n):
        solution_one_shapes = deepcopy(self.get_shapes())
        solution_two_shapes = deepcopy(other_solution.get_shapes())

        solution_one_shapes = n_point_crossover(solution_one_shapes, solution_two_shapes, n)

        solution_one = Solution([], self.get_dimensions(), self.get_run())
        solution_one.set_shapes(solution_one_shapes)
        solution_one.repair()

        return solution_one

    def repair(self):
        all_points = set()
        new_shapes = []

        for shape in self.get_shapes():
            index = 0

            points_in_path = list(shape.get_points_in_path())

            while index < len(points_in_path):
                point = points_in_path[index]

                if point in all_points:
                    shapes, points = self.__generate_solution([shape], all_points)
                    shape = shapes[0]
                    points_in_path = list(shape.get_points_in_path())

                    index = 0
                else:
                    index += 1

            new_shapes += [shape]
            all_points = all_points.union(shape.get_points_in_path())

        self.set_shapes(new_shapes)
        self.set_all_used_points(all_points)

    # MARK: Private Methods
    def __init_solved_solution(self, new_points, new_shapes):
        new_solution = Solution([], self.dimensions, self.run)
        new_solution.set_all_used_points(new_points)
        new_solution.set_shapes(new_shapes)

        return new_solution

    def __init_solved_solution_without_points(self, new_shapes):
        new_solution = Solution([], self.dimensions, self.run)
        new_solution.set_shapes(new_shapes)

        for shape in new_shapes:
            used_points = new_solution.get_all_used_points()
            shape_points = shape.get_points_in_path()
            new_solution.set_all_used_points(used_points.union(shape_points))

        return new_solution

    def __generate_solution(self, shapes, current_points):
        shapes_thus_far = []
        all_points = current_points
        index = 0

        while index < len(shapes):
            shape = shapes[index]
            solution_found, shape = self.__attempt_to_place_shape(shape, all_points)

            if solution_found:
                points = shape.get_points_in_path()
                all_points = all_points.union(points)
                shapes_thus_far += [shape]
                index += 1
            else:
                all_points = current_points
                shapes_thus_far = []
                index = 0

        return shapes_thus_far, all_points

    # tries ONE time to place a shape in a random plot
    # does NOT have to be successful. returns if it is
    def __attempt_to_place_shape(self, shape, current_points):
        board_columns, board_rows = self.dimensions

        place_found = False
        attempts = 0

        while attempts < MAX_ATTEMPT_TO_PLACE_SHAPE and not place_found:
            attempts += 1

            random_rotation = random_arbitrary(0, 3)
            random_point = generate_random_point((0, board_rows), (0, board_columns))

            shape.set_rotation(random_rotation)
            shape.set_start_position(random_point)

            place_found = True
            for row, column in shape.get_points_in_path():
                if (row, column) in current_points or not (0 <= row < board_rows) or not (0 <= column < board_columns):
                    place_found = False

        return place_found, shape

    def randomize_shape_order(self):
        random.shuffle(self.shapes)

    # MARK: Getters/Setters
    def set_shapes(self, shapes):
        self.shapes = shapes

    def get_shapes(self):
        return sorted(self.shapes, key=operator.attrgetter('shape_number'))

    def __get_shapes_unsorted(self):
        return self.shapes

    def set_all_used_points(self, points):
        self.all_points = points

    def get_all_used_points(self):
        return self.all_points

    def set_run(self, run):
        self.run = run

    def get_run(self):
        return self.run

    def get_dimensions(self):
        return self.dimensions

    # MARK: Operator Overloading
    def __lt__(self, other):
        return self.fitness() < other.fitness()
