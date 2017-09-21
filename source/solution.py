#!/usr/local/bin/python3
#
# solution.py
# source
#
# Created by Illya Starikov on 09/20/17.
# Copyright 2017. Illya Starikov. All rights reserved.
#

from utilities import random_arbitrary, generate_random_point


class Solution():
    # MARK: Properties
    shapes = []
    all_points = set()
    run = -1

    # MARK: Constructors
    def __init__(self, shapes, dimensions, run):
        solution_shapes = []

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
                solution_shapes += [shape]
                index += 1
            else:
                current_points = set()
                solution_shapes = []
                index = 0

        self.shapes = solution_shapes
        self.all_points = points
        self.run = run

    # MARK: Getters/Setters
    def set_shapes(self, shapes):
        self.shapes = shapes

    def get_shapes(self):
        return self.shapes

    def set_all_used_points(self, points):
        return self.all_pointss

    def get_all_used_points(self):
        return self.all_points

    def set_run(self, run):
        self.run = run

    def get_run(self):
        return self.run

    def fitness(self, board_dimensions):
        max_length, _ = board_dimensions
        rightmost_column = 0

        for shape in self.shapes:
            _, max_right = shape.get_rightmost_point()
            rightmost_shape_value = max_right

            if rightmost_shape_value > rightmost_column:
                rightmost_column = rightmost_shape_value
        length_used = rightmost_column
        return max_length - length_used
