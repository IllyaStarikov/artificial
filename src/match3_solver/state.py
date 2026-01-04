"""Game state representation for match-3 puzzles."""

from __future__ import annotations

import typing


class State:
    """Immutable snapshot of a match-3 game state."""

    def __init__(
        self,
        grid: typing.List[typing.List[int]],
        pool: typing.List[typing.List[int]],
        swaps: int,
        max_swaps: int,
        points: int,
        number_of_device_types: int,
    ) -> None:
        """Initialize a game state.

        Args:
            grid: Current board configuration.
            pool: Tiles waiting above the grid.
            swaps: Number of swaps used so far.
            max_swaps: Maximum swaps allowed.
            points: Current score.
            number_of_device_types: Total tile type count.
        """
        self.grid = grid
        self.pool = pool
        self.swaps = swaps
        self.max_swaps = max_swaps
        self.points = points
        self.number_of_device_types = number_of_device_types

    def __eq__(self, other: object) -> bool:
        """Check state equality."""
        if not isinstance(other, State):
            return NotImplemented
        return self.__dict__ == other.__dict__

    def __str__(self) -> str:
        """Return string representation."""
        return str(self.__dict__)
