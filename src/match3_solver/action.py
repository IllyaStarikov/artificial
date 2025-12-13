"""Action representation for match-3 puzzles."""

from __future__ import annotations

import typing

import direction as direction_module


class Action:
    """A swap action in the match-3 game."""

    def __init__(
        self,
        row_column_pair: typing.Tuple[int, int],
        direction: direction_module.Direction,
    ) -> None:
        """Initialize an action.

        Args:
            row_column_pair: (row, column) of the tile to swap.
            direction: Direction to swap toward.
        """
        self.row_column_pair = row_column_pair
        self.direction = direction

    def __eq__(self, other: object) -> bool:
        """Check if two actions swap the same tiles."""
        if not isinstance(other, Action):
            return NotImplemented
        as_unit_vector = other.direction.unit_vector
        return (
            self.row_column_pair[0]
            == (other.row_column_pair[0] + as_unit_vector[0])
            and self.row_column_pair[1]
            == (other.row_column_pair[1] + as_unit_vector[1])
        )

    def __str__(self) -> str:
        """Return string representation."""
        as_unit_vector = self.direction.unit_vector
        new_point = (
            self.row_column_pair[0] + as_unit_vector[0],
            self.row_column_pair[1] + as_unit_vector[1],
        )
        return (
            f"({self.row_column_pair[0]}, {self.row_column_pair[1]}) -> "
            f"({new_point[0]}, {new_point[1]})"
        )
