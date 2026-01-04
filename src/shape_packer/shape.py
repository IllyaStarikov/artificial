"""Shape representation for the shape packer.

Shapes are polyomino-like objects defined by direction-magnitude instructions.
This module provides efficient, cached point calculations for shape placement.

Example:
    shape = Shape.from_instructions("D1,R2,U1", shape_id=0)
    points = shape.get_points(rotation=1)  # Cached after first call
"""

from __future__ import annotations

import functools
from dataclasses import dataclass
from typing import FrozenSet, List, Tuple


class Point:
    """An immutable 2D point on the board (optimized with __slots__)."""

    __slots__ = ('row', 'col', '_hash')

    def __init__(self, row: int, col: int) -> None:
        object.__setattr__(self, 'row', row)
        object.__setattr__(self, 'col', col)
        object.__setattr__(self, '_hash', hash((row, col)))

    def __setattr__(self, name, value):
        raise AttributeError("Point is immutable")

    def __add__(self, other: Point) -> Point:
        return Point(self.row + other.row, self.col + other.col)

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return self.row == other.row and self.col == other.col

    def __repr__(self) -> str:
        return f"Point({self.row}, {self.col})"


# Direction vectors for shape instructions
_DIRECTIONS = {
    "U": Point(1, 0),   # Up increases row
    "D": Point(-1, 0),  # Down decreases row
    "L": Point(0, -1),  # Left decreases column
    "R": Point(0, 1),   # Right increases column
}


class Shape:
    """A polyomino shape defined by movement instructions.

    Shapes are defined by a sequence of direction-magnitude pairs like
    "D1,R2,U1" meaning: down 1, right 2, up 1. The shape occupies all
    cells along this path.

    Points are cached per rotation for performance. The original code
    recalculated points on every access, which was a major bottleneck.

    Attributes:
        shape_id: Unique identifier for this shape.
    """

    def __init__(
        self,
        instructions: List[Tuple[str, int]],
        shape_id: int,
    ) -> None:
        """Create a shape from parsed instructions.

        Args:
            instructions: List of (direction, magnitude) tuples.
                Direction is one of 'U', 'D', 'L', 'R'.
            shape_id: Unique identifier for this shape.

        Raises:
            ValueError: If instructions contain invalid directions.
        """
        for direction, _ in instructions:
            if direction not in _DIRECTIONS:
                raise ValueError(f"Invalid direction: {direction}")

        self._instructions = instructions
        self.shape_id = shape_id
        # Pre-cache points and bounds for all rotations
        self._cached_points = tuple(self._compute_points(r) for r in range(4))
        self._cached_bounds = tuple(self._compute_bounds(r) for r in range(4))

    @classmethod
    def from_instructions(cls, instruction_str: str, shape_id: int) -> Shape:
        """Create a shape from an instruction string.

        Args:
            instruction_str: Direction-magnitude pairs, separated by commas
                or spaces. Examples: "D1,R2,U1" or "D1 R2 U1" or "L3 L3".
            shape_id: Unique identifier for this shape.

        Returns:
            New Shape instance.

        Raises:
            ValueError: If instruction string is malformed.
        """
        instructions: List[Tuple[str, int]] = []

        # Handle both comma and space separated formats
        # Replace commas with spaces, then split on whitespace
        normalized = instruction_str.replace(",", " ")
        for part in normalized.split():
            part = part.strip()
            if not part:
                continue
            direction = part[0].upper()
            magnitude = int(part[1:])
            instructions.append((direction, magnitude))
        return cls(instructions, shape_id)

    def _compute_points(self, rotation: int) -> FrozenSet[Point]:
        """Compute points for a rotation (called once at init)."""
        current = Point(0, 0)
        points = {current}
        for direction, magnitude in self._instructions:
            delta = _DIRECTIONS[direction]
            for _ in range(magnitude):
                current = current + delta
                points.add(current)
        result = points
        for _ in range(rotation % 4):
            result = frozenset(Point(-p.col, p.row) for p in result)
        return frozenset(result)

    def _compute_bounds(self, rotation: int) -> Tuple[int, int, int, int]:
        """Compute bounds for a rotation (called once at init)."""
        points = self._cached_points[rotation % 4]
        rows = [p.row for p in points]
        cols = [p.col for p in points]
        return (min(rows), max(rows), min(cols), max(cols))

    def get_points(self, rotation: int = 0) -> FrozenSet[Point]:
        """Get all points occupied by this shape at origin (pre-cached)."""
        return self._cached_points[rotation % 4]

    @functools.lru_cache(maxsize=2048)
    def get_points_at(
        self,
        position: Point,
        rotation: int = 0,
    ) -> FrozenSet[Point]:
        """Get points when shape is placed at a position (cached)."""
        base_points = self._cached_points[rotation % 4]
        pr, pc = position.row, position.col
        return frozenset(Point(p.row + pr, p.col + pc) for p in base_points)

    def get_bounds(self, rotation: int = 0) -> Tuple[int, int, int, int]:
        """Get min/max row/col bounds for fast bounds checking (pre-cached)."""
        return self._cached_bounds[rotation % 4]

    @functools.cached_property
    def bounding_box(self) -> Tuple[int, int]:
        """Get the bounding box dimensions of the unrotated shape.

        Returns:
            Tuple of (width, height).
        """
        points = self.get_points(0)
        rows = [p.row for p in points]
        cols = [p.col for p in points]
        width = max(cols) - min(cols) + 1
        height = max(rows) - min(rows) + 1
        return (width, height)

    def __repr__(self) -> str:
        """Return string representation of shape."""
        instr_str = ",".join(f"{d}{m}" for d, m in self._instructions)
        return f"Shape(id={self.shape_id}, instructions='{instr_str}')"
