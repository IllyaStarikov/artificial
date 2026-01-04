"""Evolutionary algorithm for shape packing optimization.

This module provides the main EA loop for evolving shape placements.
Uses the TerminationManager from the evolutionary module for clean
termination handling.

Example:
    from sat_solver.termination import (
        TerminationManager,
        NumberOfFitnessEvaluations,
        NoChangeInBestFitness,
    )

    ea = ShapePackerEA(
        shapes=shapes,
        board_dims=(20, 50),
        config=config,
    )

    conditions = [
        NumberOfFitnessEvaluations(10000),
        NoChangeInBestFitness(100),
    ]
    best = ea.search(conditions)
"""

from __future__ import annotations

import random
from typing import List, Tuple

from sat_solver import termination

TerminationCondition = termination.TerminationCondition
TerminationManager = termination.TerminationManager

from shape_packer.config import ShapePackerConfig
from shape_packer.individual import Individual
from shape_packer.operators import (
    CrossoverOperator,
    LocalSearchMutation,
    MutationOperator,
    RandomReplaceMutation,
    UniformCrossover,
)
from shape_packer.population import Population
from shape_packer.selection import (
    SelectionStrategy,
    TournamentSelection,
    TruncationSelection,
)
from shape_packer.shape import Shape


class ShapePackerEA:
    """Evolutionary algorithm for shape packing.

    Implements (mu + lambda) evolution strategy:
    1. Select parents from population
    2. Create offspring via crossover and mutation
    3. Combine parents and offspring
    4. Select survivors for next generation

    Attributes:
        shapes: List of shapes to place.
        board_dims: Tuple of (width, height).
        config: EA configuration.
    """

    def __init__(
        self,
        shapes: List[Shape],
        board_dims: Tuple[int, int],
        config: ShapePackerConfig,
        parent_selection: SelectionStrategy | None = None,
        survival_selection: SelectionStrategy | None = None,
        crossover: CrossoverOperator | None = None,
        mutation: MutationOperator | None = None,
    ) -> None:
        """Create a shape packer EA.

        Args:
            shapes: List of shapes to place.
            board_dims: Tuple of (width, height).
            config: EA configuration.
            parent_selection: Strategy for selecting parents. Defaults to
                TournamentSelection with config.tournament_size.
            survival_selection: Strategy for selecting survivors. Defaults
                to TruncationSelection.
            crossover: Crossover operator. Defaults to UniformCrossover.
            mutation: Mutation operator. Defaults to RandomReplaceMutation.
        """
        self.shapes = shapes
        self.board_dims = board_dims
        self.config = config

        # Set random seed if specified
        if config.seed is not None:
            random.seed(config.seed)

        # Default operators
        self._parent_selection = parent_selection or TournamentSelection(
            k=config.tournament_size
        )
        self._survival_selection = survival_selection or TruncationSelection()
        self._crossover = crossover or UniformCrossover()
        self._mutation = mutation or RandomReplaceMutation()

        # State
        self._population: Population | None = None
        self._generation = 0
        self._best_ever: Individual | None = None

    def search(
        self,
        termination_conditions: List[TerminationCondition],
    ) -> Individual:
        """Run the EA until termination.

        Args:
            termination_conditions: List of conditions to check.

        Returns:
            Best individual found.
        """
        # Initialize population
        self._population = Population.random(
            self.shapes,
            self.board_dims,
            self.config,
            self.config.mu,
        )
        self._best_ever = self._population.fittest
        self._generation = 0

        # Set up termination manager
        term_manager = TerminationManager(
            termination_conditions,
            lambda: self._population.fitnesses,
        )

        # Main loop
        while not term_manager.should_terminate():
            self._generation += 1
            self._evolve_one_generation()

            # Track best ever
            current_best = self._population.fittest
            if current_best.fitness > self._best_ever.fitness:
                self._best_ever = current_best

        return self._best_ever

    def _evolve_one_generation(self) -> None:
        """Perform one generation of evolution with elitism."""
        # Elitism: always keep the best individual
        elite = self._population.fittest

        # Select parents
        parents = self._parent_selection.select(
            self._population.individuals,
            self.config.lambda_,
        )

        # Create offspring
        offspring: List[Individual] = []
        local_search = LocalSearchMutation()

        for i in range(0, len(parents) - 1, 2):
            parent1 = parents[i]
            parent2 = parents[i + 1] if i + 1 < len(parents) else parents[0]

            # Crossover
            child = self._crossover.crossover(
                parent1, parent2, self.board_dims, self.config
            )

            # Mutation (probabilistic)
            if random.random() < self.config.mutation_rate:
                child = self._mutation.mutate(child, self.board_dims, self.config)

            # Apply local search occasionally (5% of the time)
            if random.random() < 0.05:
                child = local_search.mutate(child, self.board_dims, self.config)

            offspring.append(child)

        # Combine with elitism: include elite in combined pool
        combined = self._population.individuals + offspring
        if elite not in combined:
            combined.append(elite)

        # Select survivors
        survivors = self._survival_selection.select(combined, self.config.mu)

        # Ensure elite survives (elitism guarantee)
        if elite not in survivors:
            survivors[-1] = elite

        self._population = Population(survivors)

    @property
    def population(self) -> Population | None:
        """Get current population.

        Returns:
            Current population, or None if not initialized.
        """
        return self._population

    @property
    def generation(self) -> int:
        """Get current generation number.

        Returns:
            Current generation count.
        """
        return self._generation

    @property
    def best_ever(self) -> Individual | None:
        """Get best individual found so far.

        Returns:
            Best individual, or None if not initialized.
        """
        return self._best_ever
