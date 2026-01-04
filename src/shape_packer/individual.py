"""Individual (candidate solution) for shape packer EA.

An individual represents a complete packing arrangement - all shapes
placed on the board. Fitness is cached on construction to avoid
recalculation during comparisons (a major performance issue in the
original code).

Example:
    individual = Individual.random(shapes, board_dims, config)
    print(individual.fitness)  # Cached value
"""

from __future__ import annotations

import random
from typing import List, Optional, Tuple

from shape_packer.board import Board, Placement
from shape_packer.config import ShapePackerConfig
from shape_packer.shape import Point, Shape


class Individual:
    """A candidate solution for the shape packing problem.

    Each individual represents a complete placement of all shapes on
    the board. Fitness is computed once at construction and cached.

    The original code recalculated fitness in __lt__, causing O(n)
    fitness calculations per comparison during sorting.

    Attributes:
        placements: List of shape placements.
        board_width: Width of the board.
        board_height: Height of the board.
        fitness: Cached fitness value (higher is better).
    """

    def __init__(
        self,
        placements: List[Placement],
        board_width: int,
        board_height: int,
    ) -> None:
        """Create an individual from placements.

        Args:
            placements: List of shape placements.
            board_width: Width of the board.
            board_height: Height of the board.
        """
        self.placements = placements
        self.board_width = board_width
        self.board_height = board_height
        self._fitness: Optional[float] = None

    @property
    def fitness(self) -> float:
        """Get the fitness value (cached).

        Fitness = board_width - rightmost_occupied_column.
        Higher fitness means more empty space on the left.

        Returns:
            Fitness value.
        """
        if self._fitness is None:
            if not self.placements:
                self._fitness = float(self.board_width)
            else:
                rightmost = -1
                for placement in self.placements:
                    for point in placement.points:
                        if point.col > rightmost:
                            rightmost = point.col
                self._fitness = float(self.board_width - rightmost - 1)
        return self._fitness

    @classmethod
    def random(
        cls,
        shapes: List[Shape],
        board_dims: Tuple[int, int],
        config: ShapePackerConfig,
    ) -> Individual:
        """Create an individual using purely random placement.

        Places shapes in random order at random positions to create
        diverse initial population with room for improvement.

        Args:
            shapes: List of shapes to place.
            board_dims: Tuple of (width, height).
            config: Configuration with max_placement_attempts.

        Returns:
            New Individual with placements.
        """
        width, height = board_dims
        board = Board(width, height)
        placements: List[Placement] = []

        # Shuffle shapes randomly
        shapes_to_place = list(shapes)
        random.shuffle(shapes_to_place)

        for shape in shapes_to_place:
            placement = cls._try_place_shape_random(shape, board, config)
            if placement is None:
                # Restart with different order
                return cls.random(shapes, board_dims, config)
            placements.append(placement)
            board.place(placement)

        return cls(placements, width, height)

    @staticmethod
    def _try_place_shape_random(
        shape: Shape,
        board: Board,
        config: ShapePackerConfig,
    ) -> Optional[Placement]:
        """Try to place a shape randomly on the board.

        Args:
            shape: Shape to place.
            board: Current board state.
            config: Configuration with max_placement_attempts.

        Returns:
            Valid Placement if found, None otherwise.
        """
        # Limit attempts for speed
        max_attempts = min(config.max_placement_attempts, 150)
        for _ in range(max_attempts):
            rotation = random.randint(0, 3)
            row = random.randint(0, board.height - 1)
            col = random.randint(0, board.width - 1)
            placement = Placement(shape, Point(row, col), rotation)
            if board.can_place(placement):
                return placement
        return None

    def get_shapes(self) -> List[Shape]:
        """Get shapes in order of their IDs.

        Returns:
            List of shapes sorted by shape_id.
        """
        return sorted(
            [p.shape for p in self.placements],
            key=lambda s: s.shape_id,
        )

    def __lt__(self, other: Individual) -> bool:
        """Compare by fitness (cached).

        Args:
            other: Other individual to compare.

        Returns:
            True if this individual has lower fitness.
        """
        return self.fitness < other.fitness

    def __eq__(self, other: object) -> bool:
        """Check equality by fitness.

        Args:
            other: Other object to compare.

        Returns:
            True if other is Individual with same fitness.
        """
        if not isinstance(other, Individual):
            return NotImplemented
        return self.fitness == other.fitness

    def __hash__(self) -> int:
        """Hash by fitness for set operations.

        Returns:
            Hash value.
        """
        return hash(self.fitness)

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String with fitness and placement count.
        """
        return f"Individual(fitness={self.fitness:.2f}, shapes={len(self.placements)})"
