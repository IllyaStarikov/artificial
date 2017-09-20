#!/usr/local/bin/python3
#
# shape.py
# source
#
# Created by Illya Starikov on 09/12/17.
# Copyright 2017. Illya Starikov. All rights reserved.
#

# shapes are stores as a list of strings as [DirectionMagnitude,...]
# i.e, ["D3", "U1"]


class Shape():
    rotations = 0
    rotations_list = []
    start_position = (0, 0)

    def __init__(self, shapes_list):
        self.rotations = 0
        self.start_position = (0, 0)
        self.shapes_list = shapes_list

    def get_height(self):
        _, height = self.__calculate_height_width()
        return height

    def get_width(self):
        height, _ = self.__calculate_height_width()
        return height

    def set_start_position(self, start_position):
        self.start_position = start_position

    def get_start_position(self):
        return self.start_position

    def set_rotation(self, rotation):
        self.rotations = rotation

    def get_rotations(self):
        return self.rotations

    def get_rightmost_point(self):
        max_point = list(self.get_points_in_path())[0]

        for row, column in self.get_points_in_path():
            max_row, max_column = max_point

            if column > max_column:
                max_point = (row, column)

        return max_point

    def get_points_in_path(self):
        current_row, current_column = 0, 0
        positions_list = set([(current_row, current_column)])

        # for now, just generate the points as if they began at 0, 0
        for direction, magnitude in self.shapes_list:
            magnitude = int(magnitude)

            for _ in range(magnitude):
                if direction == "L":
                    current_column -= 1
                elif direction == "R":
                    current_column += 1
                elif direction == "U":
                    current_row += 1
                elif direction == "D":
                    current_row -= 1

                positions_list.add((current_row, current_column))

        # actually rotate the list now.
        for _ in range(self.rotations):
            positions_list_rotated = set()

            for row, column in positions_list:
                new_position = (-column, row)
                positions_list_rotated.add(new_position)

            positions_list = positions_list_rotated

        # finally
        final_list = set()
        start_row, start_column = self.start_position

        for row, column in positions_list:
            final_list.add((row + start_row, column + start_column))

        return final_list

    def get_matrix_representation(self):
        width, height = self.__calculate_height_width()
        max_left, _, _, max_down = self.get_max_points()
        x, y = 0, 0

        shape_list = [[0] * (width + 1) for __ in range(height + 1)]

        if abs(max_left) > 0:
            x = abs(max_left)

        if abs(max_down) > 0:
            y = abs(max_down)

        self.start_point = (height - y, x)
        shape_list[height - y][x] = 1
        for shape in self.shapes_list:
            direction = shape[0]
            magnitude = int(shape[1])

            for _ in range(magnitude):
                if direction == 'L':
                    x -= 1
                if direction == 'R':
                    x += 1
                if direction == 'U':
                    y += 1
                if direction == 'D':
                    y -= 1

                shape_list[height - y][x] = 1

        return shape_list

    def get_max_points(self):
        max_left, max_right, max_up, max_down = 0, 0, 0, 0
        current_height, current_width = 0, 0

        for element in self.shapes_list:
            direction = element[0]
            magnitude = int(element[1])

            if direction == 'L':
                current_width -= magnitude
                if current_width < max_left:
                    max_left = current_width

            elif direction == 'R':
                current_width += magnitude
                if current_width > max_right:
                    max_right = current_width

            elif direction == 'U':
                current_height += magnitude
                if current_height > max_up:
                    max_up = current_height

            elif direction == 'D':
                current_height -= magnitude
                if current_height < max_down:
                    max_down = current_height

        return (abs(max_left), max_right, max_up, abs(max_down))

    def __calculate_height_width(self):
        max_left, max_right, max_up, max_down = self.get_max_points()

        return (max_right + abs(max_left), max_up + abs(max_down))
