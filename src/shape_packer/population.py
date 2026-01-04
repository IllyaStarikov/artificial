"""Population management for shape packer EA.

Example:
    population = Population.random(shapes, board_dims, config)
    print(population.fittest)
    print(population.average_fitness)
"""

from __future__ import annotations

from typing import List, Tuple

from shape_packer.config import ShapePackerConfig
from shape_packer.individual import Individual
from shape_packer.shape import Shape


class Population:
    """A collection of individuals with aggregate statistics.

    Attributes:
        individuals: List of individuals in the population.
    """

    def __init__(self, individuals: List[Individual]) -> None:
        """Create a population from a list of individuals.

        Args:
            individuals: List of individuals.

        Raises:
            ValueError: If individuals list is empty.
        """
        if not individuals:
            raise ValueError("Population cannot be empty")
        self.individuals = individuals

    @classmethod
    def random(
        cls,
        shapes: List[Shape],
        board_dims: Tuple[int, int],
        config: ShapePackerConfig,
        size: int,
    ) -> Population:
        """Create a population with random individuals.

        Args:
            shapes: List of shapes to place.
            board_dims: Tuple of (width, height).
            config: Configuration.
            size: Number of individuals to create.

        Returns:
            New Population with random individuals.
        """
        individuals = [
            Individual.random(shapes, board_dims, config)
            for _ in range(size)
        ]
        return cls(individuals)

    @property
    def fittest(self) -> Individual:
        """Get the individual with highest fitness.

        Returns:
            Best individual.
        """
        return max(self.individuals)

    @property
    def average_fitness(self) -> float:
        """Get the average fitness of the population.

        Returns:
            Mean fitness value.
        """
        total = sum(ind.fitness for ind in self.individuals)
        return total / len(self.individuals)

    @property
    def fitnesses(self) -> List[float]:
        """Get all fitness values.

        Returns:
            List of fitness values.
        """
        return [ind.fitness for ind in self.individuals]

    def __len__(self) -> int:
        """Get population size.

        Returns:
            Number of individuals.
        """
        return len(self.individuals)

    def __iter__(self):
        """Iterate over individuals.

        Returns:
            Iterator over individuals.
        """
        return iter(self.individuals)

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String with size and fitness stats.
        """
        return (
            f"Population(size={len(self)}, "
            f"best={self.fittest.fitness:.2f}, "
            f"avg={self.average_fitness:.2f})"
        )
