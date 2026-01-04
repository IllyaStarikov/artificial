"""Individual representation for evolutionary algorithms.

This module provides the Individual class representing a candidate solution
in the evolutionary algorithm, with support for mutation and recombination.

Example:
    import individual

    individual.Individual.cnf_filename = "input.cnf"
    ind = individual.Individual()
    print(f"Fitness: {ind.fitness}")
"""

from __future__ import annotations

import random
import typing

from evolutionary import sat


class Individual:
    """A candidate solution in the evolutionary algorithm.

    Each individual has a genotype (SAT variable assignment) and a fitness
    value based on the number of satisfied clauses.

    Attributes:
        cnf_filename: Class variable specifying the CNF file to use.
        genotype: The SAT instance representing the individual's genes.
        fitness: The fitness score (percentage of satisfied clauses).
    """

    cnf_filename: str = ""

    def __init__(self, genotype: typing.Optional[sat.SAT] = None) -> None:
        """Initialize an Individual.

        Args:
            genotype: Optional pre-built SAT instance. If None, creates a new
                random SAT from cnf_filename.

        Note:
            Individual.cnf_filename must be set before creating instances
            without a genotype.
        """
        if genotype is None:
            self.genotype = sat.SAT(Individual.cnf_filename)
        else:
            self.genotype = genotype

    @property
    def fitness(self) -> float:
        """Calculate the fitness of this individual.

        Fitness is the percentage of satisfied clauses (0-100).

        Returns:
            The fitness score as a percentage.
        """
        satisfied = self.genotype.clauses_satisfied
        total = self.genotype.total_clauses
        return 100 * satisfied / total

    @staticmethod
    def mutate(individual: Individual, rate: float) -> None:
        """Apply mutation to an individual's genotype.

        Performs uniform random mutation by flipping randomly selected
        variables based on the mutation rate.

        Args:
            individual: The individual to mutate (modified in-place).
            rate: Mutation rate (0.0 to 1.0), proportion of variables to flip.
        """
        num_to_mutate = int(rate * len(individual.genotype.variables))

        for _ in range(num_to_mutate):
            variable = random.choice(individual.genotype.variables)
            individual.genotype[variable] = not individual.genotype[variable]

    @staticmethod
    def recombine(parent_one: Individual, parent_two: Individual) -> Individual:
        """Create offspring by recombining two parents.

        Uses n-point crossover with n=5 to create a new individual.

        Args:
            parent_one: The first parent.
            parent_two: The second parent.

        Returns:
            A new individual combining genes from both parents.
        """
        return Individual._n_point_crossover(parent_one, parent_two, 5)

    @staticmethod
    def _uniform_crossover(
        parent_one: Individual, parent_two: Individual
    ) -> Individual:
        """Create offspring using uniform crossover.

        Each gene is randomly selected from either parent with equal
        probability.

        Args:
            parent_one: The first parent.
            parent_two: The second parent.

        Returns:
            A new individual with genes randomly selected from parents.
        """
        new_genotype = sat.SAT(Individual.cnf_filename)

        for variable in parent_one.genotype.variables:
            gene = random.choice([
                parent_one.genotype[variable],
                parent_two.genotype[variable]
            ])
            new_genotype[variable] = gene

        return Individual(genotype=new_genotype)

    @staticmethod
    def _n_point_crossover(
        parent_one: Individual, parent_two: Individual, n: int
    ) -> Individual:
        """Create offspring using n-point crossover.

        Divides the genome into n+1 sections, alternating between parents.

        Args:
            parent_one: The first parent.
            parent_two: The second parent.
            n: Number of crossover points.

        Returns:
            A new individual with alternating sections from each parent.
        """
        new_genotype = sat.SAT(Individual.cnf_filename)
        variables = sorted(parent_one.genotype.variables)
        splits = [(i * len(variables) // (n + 1)) for i in range(1, n + 2)]

        i = 0
        for index, split in enumerate(splits):
            for _ in range(i, split):
                parent = parent_one if index % 2 == 0 else parent_two
                new_genotype[variables[i]] = parent.genotype[variables[i]]
                i += 1

        return Individual(genotype=new_genotype)

    @staticmethod
    def _davis_crossover(
        parent_one: Individual, parent_two: Individual
    ) -> Individual:
        """Create offspring using Davis order crossover.

        Selects a random segment from parent_one and fills the rest from
        parent_two.

        Args:
            parent_one: The first parent (provides middle segment).
            parent_two: The second parent (provides outer segments).

        Returns:
            A new individual with a segment from parent_one and rest from
            parent_two.
        """
        new_genotype = sat.SAT(Individual.cnf_filename)
        variables = sorted(parent_one.genotype.variables)
        split_one, split_two = sorted(random.sample(range(len(variables)), 2))

        for variable in variables[:split_one]:
            new_genotype[variable] = parent_two.genotype[variable]

        for variable in variables[split_one:split_two]:
            new_genotype[variable] = parent_one.genotype[variable]

        for variable in variables[split_two:]:
            new_genotype[variable] = parent_two.genotype[variable]

        return Individual(genotype=new_genotype)
