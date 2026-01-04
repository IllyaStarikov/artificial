"""Selection strategies for the evolutionary algorithm.

Provides pluggable selection strategies for parent and survival selection.
The original code hardcoded selection with string matching; this uses
the Strategy pattern for flexibility and testability.

Example:
    selector = TournamentSelection(k=5)
    parents = selector.select(population, count=50)
"""

from __future__ import annotations

import bisect
import heapq
import random
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from shape_packer.individual import Individual


class SelectionStrategy(ABC):
    """Abstract base class for selection strategies."""

    @abstractmethod
    def select(
        self,
        individuals: List[Individual],
        count: int,
    ) -> List[Individual]:
        """Select individuals from a population.

        Args:
            individuals: List of individuals to select from.
            count: Number of individuals to select.

        Returns:
            List of selected individuals.
        """
        ...


class TournamentSelection(SelectionStrategy):
    """K-tournament selection with optional replacement.

    Selects individuals by running tournaments: randomly pick k individuals,
    the one with highest fitness wins.

    Attributes:
        k: Tournament size.
        with_replacement: If True, same individual can be selected multiple
            times. If False, selected individuals are removed from pool.
    """

    def __init__(self, k: int, with_replacement: bool = True) -> None:
        """Create tournament selection.

        Args:
            k: Tournament size. Larger k increases selection pressure.
            with_replacement: Whether to allow re-selection.

        Raises:
            ValueError: If k < 1.
        """
        if k < 1:
            raise ValueError(f"Tournament size must be >= 1, got {k}")
        self.k = k
        self.with_replacement = with_replacement

    def select(
        self,
        individuals: List[Individual],
        count: int,
    ) -> List[Individual]:
        """Select individuals via tournament selection.

        Args:
            individuals: List of individuals to select from.
            count: Number of individuals to select.

        Returns:
            List of selected individuals.

        Raises:
            ValueError: If count > len(individuals) and not with_replacement.
        """
        if not self.with_replacement and count > len(individuals):
            raise ValueError(
                f"Cannot select {count} individuals without replacement "
                f"from population of {len(individuals)}"
            )

        pool = list(individuals)
        selected: List[Individual] = []

        for _ in range(count):
            # Select k candidates (or fewer if pool is smaller)
            k = min(self.k, len(pool))
            candidates = random.sample(pool, k)
            winner = max(candidates)  # Uses __lt__ comparison
            selected.append(winner)

            if not self.with_replacement:
                pool.remove(winner)

        return selected


class TruncationSelection(SelectionStrategy):
    """Truncation selection: select the top individuals by fitness.

    Simple and deterministic. Always selects the best individuals.
    Uses heapq.nlargest for O(n log k) instead of O(n log n) sorting.
    """

    def select(
        self,
        individuals: List[Individual],
        count: int,
    ) -> List[Individual]:
        """Select the top individuals by fitness.

        Args:
            individuals: List of individuals to select from.
            count: Number of individuals to select.

        Returns:
            List of top individuals by fitness.
        """
        # heapq.nlargest is O(n log k) vs O(n log n) for full sort
        return heapq.nlargest(count, individuals)


class FitnessProportionalSelection(SelectionStrategy):
    """Fitness proportional (roulette wheel) selection.

    Probability of selection is proportional to fitness. Uses cumulative
    sum and binary search for O(n log n) instead of the original O(n^2).

    Note: Requires positive fitness values.
    """

    def select(
        self,
        individuals: List[Individual],
        count: int,
    ) -> List[Individual]:
        """Select individuals with probability proportional to fitness.

        Args:
            individuals: List of individuals to select from.
            count: Number of individuals to select.

        Returns:
            List of selected individuals.

        Raises:
            ValueError: If any fitness is negative.
        """
        if not individuals:
            return []

        # Build cumulative fitness array
        fitnesses = [ind.fitness for ind in individuals]
        if any(f < 0 for f in fitnesses):
            raise ValueError("Fitness proportional selection requires non-negative fitness")

        # Handle zero total fitness
        total = sum(fitnesses)
        if total == 0:
            # All equal, use uniform random
            return random.choices(individuals, k=count)

        # Build cumulative distribution
        cumulative: List[float] = []
        running = 0.0
        for f in fitnesses:
            running += f
            cumulative.append(running)

        # Select using binary search
        selected: List[Individual] = []
        for _ in range(count):
            pick = random.uniform(0, total)
            idx = bisect.bisect_left(cumulative, pick)
            # Handle edge case where pick == total
            idx = min(idx, len(individuals) - 1)
            selected.append(individuals[idx])

        return selected


class RandomSelection(SelectionStrategy):
    """Uniform random selection.

    Each individual has equal probability of selection.
    """

    def select(
        self,
        individuals: List[Individual],
        count: int,
    ) -> List[Individual]:
        """Select individuals uniformly at random.

        Args:
            individuals: List of individuals to select from.
            count: Number of individuals to select.

        Returns:
            List of randomly selected individuals.
        """
        return random.choices(individuals, k=count)
