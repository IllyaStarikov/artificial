#!/usr/local/bin/python3
#
# function.py
# src
#
# Created by Illya Starikov on 10/13/18.
# Copyright 2018. Illya Starikov. MIT License.
#


class Function:
    """A function and its respective bounds."""

    def __init__(self, function, x_bounds, y_bounds):
        """Create a Function object.

        Args:
            function (lambda(x, y)): The actual function, where z = function(x, y).
            x_bounds (tuple<int, int>): Representation of the domain of x of format (min, max).
            y_bounds (tuple<int, int>): Representation of the domain of y of format (min, max).
        """

        self.__function = function
        self.__x_bounds = x_bounds
        self.__y_bounds = y_bounds

    def __call__(self, node):
        """Evaluate the function at a given node

        Args:
            node (Point): The point to evaluate the function.

        Returns:
            int: The value evaluated function(x, y).
        """

        assert self.x_bounds[0] <= node.x <= self.x_bounds[1]
        assert self.y_bounds[0] <= node.y <= self.y_bounds[1]

        return self.__function(node.x, node.y)

    @property
    def x_bounds(self):
        """Get the x bounds of the function.

        Returns:
            tuple<int, int>: The x bounds of function.
        """

        return self.__x_bounds

    @property
    def y_bounds(self):
        """Get the y bounds of the function.

        Returns:
            tuple<int, int>: The y bounds of function.
        """

        return self.__y_bounds
