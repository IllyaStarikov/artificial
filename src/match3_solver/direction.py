"""Direction enumeration for match-3 puzzles."""

from __future__ import annotations

import enum
import typing


class Direction(enum.Enum):
    """Cardinal directions for tile swapping."""

    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3

    @property
    def unit_vector(self) -> typing.Tuple[int, int]:
        """Returns (row_delta, column_delta) for this direction."""
        return {
            Direction.LEFT: (0, -1),
            Direction.RIGHT: (0, 1),
            Direction.UP: (-1, 0),
            Direction.DOWN: (1, 0),
        }[self]
