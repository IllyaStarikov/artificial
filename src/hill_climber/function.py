"""Function wrapper for local search optimization.

This module provides the Function class that wraps objective functions
with bounds for use in local search algorithms.

Example:
    func = Function(lambda x, y: -(x**2 + y**2), (-100, 100), (-100, 100))
    node = Node(0, 0)
    value = func(node)  # Returns 0
"""

from __future__ import annotations

import typing

import node


class Function:
    """An objective function with bounded domain.

    Wraps a callable function and enforces domain bounds during evaluation.

    Attributes:
        x_bounds: The (min, max) bounds for the x-coordinate.
        y_bounds: The (min, max) bounds for the y-coordinate.
    """

    def __init__(
        self,
        function: typing.Callable[[int, int], float],
        x_bounds: typing.Tuple[int, int],
        y_bounds: typing.Tuple[int, int],
    ) -> None:
        """Create a Function with specified bounds.

        Args:
            function: A callable that takes (x, y) and returns a numeric value.
            x_bounds: Tuple of (min_x, max_x) defining the x domain.
            y_bounds: Tuple of (min_y, max_y) defining the y domain.
        """
        self._function = function
        self._x_bounds = x_bounds
        self._y_bounds = y_bounds

    def __call__(self, n: node.Node) -> float:
        """Evaluate the function at a given node.

        Args:
            n: The point at which to evaluate the function.

        Returns:
            The function value at the given point.

        Raises:
            ValueError: If the node is outside the defined bounds.
        """
        if not self._x_bounds[0] <= n.x <= self._x_bounds[1]:
            raise ValueError(f"x={n.x} is outside bounds {self._x_bounds}")
        if not self._y_bounds[0] <= n.y <= self._y_bounds[1]:
            raise ValueError(f"y={n.y} is outside bounds {self._y_bounds}")
        return self._function(n.x, n.y)

    @property
    def x_bounds(self) -> typing.Tuple[int, int]:
        """Get the x-coordinate bounds.

        Returns:
            Tuple of (min_x, max_x).
        """
        return self._x_bounds

    @property
    def y_bounds(self) -> typing.Tuple[int, int]:
        """Get the y-coordinate bounds.

        Returns:
            Tuple of (min_y, max_y).
        """
        return self._y_bounds
