"""Board state and placement management for shape packer.

This module handles the board representation and collision detection
for placing shapes. Uses numpy array for fast collision detection.

Example:
    board = Board(width=20, height=50)
    placement = Placement(shape, Point(5, 10), rotation=1)
    if board.can_place(placement):
        board.place(placement)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Set

import numpy as np

from shape_packer.shape import Point, Shape


class Placement:
    """A shape placed on the board at a specific position and rotation."""

    __slots__ = ('shape', 'position', 'rotation', '_points')

    def __init__(self, shape: Shape, position: Point, rotation: int) -> None:
        self.shape = shape
        self.position = position
        self.rotation = rotation
        # Cache points on creation
        self._points = shape.get_points_at(position, rotation)

    @property
    def points(self) -> FrozenSet[Point]:
        """Get all points occupied by this placement (cached)."""
        return self._points

    def __hash__(self) -> int:
        return hash((self.shape.shape_id, self.position, self.rotation))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Placement):
            return NotImplemented
        return (self.shape.shape_id == other.shape.shape_id and
                self.position == other.position and
                self.rotation == other.rotation)


class Board:
    """A rectangular board for placing shapes.

    Uses numpy boolean array for fast collision detection.

    Attributes:
        width: Board width (number of columns).
        height: Board height (number of rows).
    """

    __slots__ = ('width', 'height', '_grid')

    def __init__(self, width: int, height: int) -> None:
        """Create an empty board."""
        self.width = width
        self.height = height
        self._grid = np.zeros((height, width), dtype=np.bool_)

    def can_place(self, placement: Placement) -> bool:
        """Check if a placement is valid (optimized with numpy)."""
        shape = placement.shape
        pos = placement.position
        min_r, max_r, min_c, max_c = shape.get_bounds(placement.rotation)

        # Fast bounds check
        if (pos.row + min_r < 0 or pos.row + max_r >= self.height or
            pos.col + min_c < 0 or pos.col + max_c >= self.width):
            return False

        # Check collision using numpy array lookup
        for point in placement.points:
            if self._grid[point.row, point.col]:
                return False
        return True

    def place(self, placement: Placement) -> None:
        """Place a shape on the board."""
        for point in placement.points:
            self._grid[point.row, point.col] = True

    def remove(self, placement: Placement) -> None:
        """Remove a shape from the board."""
        for point in placement.points:
            self._grid[point.row, point.col] = False

    def is_occupied(self, point: Point) -> bool:
        """Check if a point is occupied."""
        return self._grid[point.row, point.col]

    @property
    def rightmost_column(self) -> int:
        """Get the rightmost occupied column."""
        cols = np.any(self._grid, axis=0)
        if not np.any(cols):
            return -1
        return int(np.max(np.where(cols)))

    @property
    def occupied_points(self) -> FrozenSet[Point]:
        """Get all occupied points."""
        rows, cols = np.where(self._grid)
        return frozenset(Point(int(r), int(c)) for r, c in zip(rows, cols))

    def clear(self) -> None:
        """Remove all placements from the board."""
        self._grid.fill(False)

    def copy(self) -> Board:
        """Create a copy of this board."""
        new_board = Board(self.width, self.height)
        new_board._grid = self._grid.copy()
        return new_board
