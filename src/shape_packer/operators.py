"""Genetic operators for shape packer EA.

Provides crossover and mutation operators for evolving shape placements.

Example:
    crossover = UniformCrossover()
    child = crossover.crossover(parent1, parent2, board_dims, config)

    mutation = RandomReplaceMutation()
    mutant = mutation.mutate(child, board_dims, config)
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from math import floor
from typing import Dict, List, Tuple

from shape_packer.board import Board, Placement
from shape_packer.config import ShapePackerConfig
from shape_packer.individual import Individual
from shape_packer.shape import Point, Shape


class CrossoverOperator(ABC):
    """Abstract base class for crossover operators."""

    @abstractmethod
    def crossover(
        self,
        parent1: Individual,
        parent2: Individual,
        board_dims: Tuple[int, int],
        config: ShapePackerConfig,
    ) -> Individual:
        """Create offspring from two parents.

        Args:
            parent1: First parent.
            parent2: Second parent.
            board_dims: Tuple of (width, height).
            config: Configuration.

        Returns:
            New Individual offspring.
        """
        ...


class MutationOperator(ABC):
    """Abstract base class for mutation operators."""

    @abstractmethod
    def mutate(
        self,
        individual: Individual,
        board_dims: Tuple[int, int],
        config: ShapePackerConfig,
    ) -> Individual:
        """Mutate an individual.

        Args:
            individual: Individual to mutate.
            board_dims: Tuple of (width, height).
            config: Configuration.

        Returns:
            New mutated Individual.
        """
        ...


class UniformCrossover(CrossoverOperator):
    """Uniform crossover: select each shape's placement preferring left positions.

    For each shape, choose the placement that is more to the left.
    Then repair any collisions using greedy left-to-right strategy.
    """

    def crossover(
        self,
        parent1: Individual,
        parent2: Individual,
        board_dims: Tuple[int, int],
        config: ShapePackerConfig,
    ) -> Individual:
        """Create offspring preferring left placements.

        Args:
            parent1: First parent.
            parent2: Second parent.
            board_dims: Tuple of (width, height).
            config: Configuration.

        Returns:
            New Individual with repaired placements.
        """
        # Build lookup by shape_id
        p1_placements: Dict[int, Placement] = {
            p.shape.shape_id: p for p in parent1.placements
        }
        p2_placements: Dict[int, Placement] = {
            p.shape.shape_id: p for p in parent2.placements
        }

        # Select placement that is more to the left (with some randomness)
        selected: List[Placement] = []
        for shape_id in p1_placements:
            p1 = p1_placements[shape_id]
            p2 = p2_placements[shape_id]

            # 70% chance to pick the one more to the left
            if random.random() < 0.7:
                if p1.position.col <= p2.position.col:
                    selected.append(p1)
                else:
                    selected.append(p2)
            else:
                # 30% random for diversity
                selected.append(random.choice([p1, p2]))

        # Sort by column position to repair from left to right
        selected.sort(key=lambda p: p.position.col)

        # Repair collisions
        repaired = self._repair(selected, board_dims, config)
        return Individual(repaired, board_dims[0], board_dims[1])

    def _repair(
        self,
        placements: List[Placement],
        board_dims: Tuple[int, int],
        config: ShapePackerConfig,
    ) -> List[Placement]:
        """Repair placements by re-placing colliding shapes.

        Uses greedy left-to-right strategy for better packing.

        Args:
            placements: List of potentially colliding placements.
            board_dims: Tuple of (width, height).
            config: Configuration.

        Returns:
            List of valid, non-colliding placements.
        """
        width, height = board_dims
        board = Board(width, height)
        repaired: List[Placement] = []

        for placement in placements:
            if board.can_place(placement):
                board.place(placement)
                repaired.append(placement)
            else:
                # Re-place using greedy strategy
                new_placement = self._try_place_greedy(placement.shape, board)
                if new_placement is None:
                    new_placement = self._try_place_random(
                        placement.shape, board, config
                    )
                if new_placement is not None:
                    board.place(new_placement)
                    repaired.append(new_placement)
                else:
                    # Worst case: restart repair with shuffled order
                    random.shuffle(placements)
                    return self._repair(placements, board_dims, config)

        return repaired

    @staticmethod
    def _try_place_greedy(shape: Shape, board: Board) -> Placement | None:
        """Try greedy left-to-right placement (optimized with sampling)."""
        rot = random.randint(0, 3)
        # Sample columns from left, with some randomness
        for col in range(min(board.width, 50)):  # Limit columns checked
            # Sample a few rows instead of all
            for _ in range(min(board.height, 10)):
                row = random.randint(0, board.height - 1)
                placement = Placement(shape, Point(row, col), rot)
                if board.can_place(placement):
                    return placement
            # Try other rotations at this column
            for r in range(4):
                if r != rot:
                    row = random.randint(0, board.height - 1)
                    placement = Placement(shape, Point(row, col), r)
                    if board.can_place(placement):
                        return placement
        return None

    @staticmethod
    def _try_place_random(
        shape: Shape,
        board: Board,
        config: ShapePackerConfig,
    ) -> Placement | None:
        """Try random placement as fallback."""
        for _ in range(min(config.max_placement_attempts, 100)):
            rotation = random.randint(0, 3)
            row = random.randint(0, board.height - 1)
            col = random.randint(0, board.width - 1)
            placement = Placement(shape, Point(row, col), rotation)
            if board.can_place(placement):
                return placement
        return None


class RandomReplaceMutation(MutationOperator):
    """Mutation by randomly re-placing a fraction of shapes.

    Selects a fraction of shapes (based on mutation_rate) and re-places
    them using greedy left-to-right strategy.
    """

    def mutate(
        self,
        individual: Individual,
        board_dims: Tuple[int, int],
        config: ShapePackerConfig,
    ) -> Individual:
        """Mutate by re-placing some shapes with greedy strategy.

        Args:
            individual: Individual to mutate.
            board_dims: Tuple of (width, height).
            config: Configuration with mutation_rate.

        Returns:
            New mutated Individual.
        """
        num_to_mutate = max(1, floor(len(individual.placements) * config.mutation_rate))

        # Shuffle and split
        placements = list(individual.placements)
        random.shuffle(placements)
        to_mutate = placements[:num_to_mutate]
        to_keep = placements[num_to_mutate:]

        # Build board with kept placements
        width, height = board_dims
        board = Board(width, height)
        for placement in to_keep:
            board.place(placement)

        # Re-place mutated shapes using greedy strategy
        new_placements = list(to_keep)
        for placement in to_mutate:
            # Try greedy placement first
            new_placement = self._try_place_greedy(placement.shape, board)
            if new_placement is None:
                new_placement = self._try_place_random(
                    placement.shape, board, config
                )
            if new_placement is not None:
                board.place(new_placement)
                new_placements.append(new_placement)
            else:
                # Keep original if can't re-place
                if board.can_place(placement):
                    board.place(placement)
                    new_placements.append(placement)
                else:
                    # Restart mutation
                    return self.mutate(individual, board_dims, config)

        return Individual(new_placements, width, height)

    @staticmethod
    def _try_place_greedy(shape: Shape, board: Board) -> Placement | None:
        """Try greedy left-to-right placement (optimized with sampling)."""
        rot = random.randint(0, 3)
        for col in range(min(board.width, 50)):
            for _ in range(min(board.height, 10)):
                row = random.randint(0, board.height - 1)
                placement = Placement(shape, Point(row, col), rot)
                if board.can_place(placement):
                    return placement
            for r in range(4):
                if r != rot:
                    row = random.randint(0, board.height - 1)
                    placement = Placement(shape, Point(row, col), r)
                    if board.can_place(placement):
                        return placement
        return None

    @staticmethod
    def _try_place_random(
        shape: Shape,
        board: Board,
        config: ShapePackerConfig,
    ) -> Placement | None:
        """Try random placement as fallback."""
        for _ in range(min(config.max_placement_attempts, 100)):
            rotation = random.randint(0, 3)
            row = random.randint(0, board.height - 1)
            col = random.randint(0, board.width - 1)
            placement = Placement(shape, Point(row, col), rotation)
            if board.can_place(placement):
                return placement
        return None


class LocalSearchMutation(MutationOperator):
    """Mutation using local search to nudge shapes left.

    For each shape, tries to move it to the left while maintaining validity.
    This is a hill-climbing step that improves fitness locally.
    """

    def mutate(
        self,
        individual: Individual,
        board_dims: Tuple[int, int],
        config: ShapePackerConfig,
    ) -> Individual:
        """Mutate by nudging shapes left.

        Args:
            individual: Individual to mutate.
            board_dims: Tuple of (width, height).
            config: Configuration.

        Returns:
            New mutated Individual with shapes nudged left.
        """
        width, height = board_dims
        improved = True
        placements = list(individual.placements)

        # Keep improving until no more improvements possible
        iterations = 0
        max_iterations = 3  # Limit iterations to avoid slow mutations

        while improved and iterations < max_iterations:
            improved = False
            iterations += 1
            random.shuffle(placements)

            for i, placement in enumerate(placements):
                # Build board without this shape
                board = Board(width, height)
                for j, p in enumerate(placements):
                    if i != j:
                        board.place(p)

                # Try to move shape left
                better = self._try_move_left(placement, board)
                if better is not None:
                    placements[i] = better
                    improved = True

        return Individual(placements, width, height)

    @staticmethod
    def _try_move_left(
        placement: Placement,
        board: Board,
    ) -> Placement | None:
        """Try to move a placement to the left.

        Args:
            placement: Current placement.
            board: Board without this shape.

        Returns:
            New placement if improvement found, None otherwise.
        """
        shape = placement.shape
        current_col = placement.position.col
        best_placement = None

        # Try all rotations, scanning from left
        for rotation in range(4):
            for col in range(current_col):  # Only check columns to the left
                for row in range(board.height):
                    new_placement = Placement(shape, Point(row, col), rotation)
                    if board.can_place(new_placement):
                        # Found a valid placement to the left
                        if best_placement is None or col < best_placement.position.col:
                            best_placement = new_placement

        return best_placement
