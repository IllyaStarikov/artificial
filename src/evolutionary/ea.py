"""Evolutionary Algorithm implementation.

This module provides the main EA class that orchestrates the evolutionary
process, including population management, termination, and epoch-based restarts.

Example:
    import ea
    import individual
    import termination

    individual.Individual.cnf_filename = "input.cnf"
    algorithm = ea.EA(mu=100, lambda_=50)
    result = algorithm.search([termination.FitnessTarget(95.0)])
"""

from __future__ import annotations

import typing

import population
import termination


class EA:
    """Evolutionary Algorithm with configurable termination and epoch restarts.

    Implements a (mu + lambda) evolutionary strategy with tournament selection,
    recombination, and mutation. Supports epoch-based restarts when progress
    stagnates.

    Attributes:
        mu: Population size (number of parents).
        lambda_: Offspring size (number of children per generation).
        population: Current population of individuals.
    """

    def __init__(self, mu: int, lambda_: int) -> None:
        """Initialize the evolutionary algorithm.

        Args:
            mu: Population size (number of parents to maintain).
            lambda_: Offspring size (number of children per generation).
        """
        self.mu = mu
        self.lambda_ = lambda_
        self.population: population.Population = None

    def search(
        self,
        termination_conditions: typing.List[termination.TerminationCondition],
    ) -> "individual.Individual":
        """Run the evolutionary algorithm until termination.

        Executes the EA loop with epoch-based restarts. When both average
        and best fitness stagnate for 250 generations, the algorithm either
        merges populations or restarts with a new random population.

        Args:
            termination_conditions: List of conditions that trigger termination
                (any condition being met will stop the algorithm).

        Returns:
            The fittest individual found during the search.
        """
        epochs = 1
        generation = 1
        total_generations = 1

        self.population = population.Population(self.mu, self.lambda_)
        previous_epoch: typing.List["individual.Individual"] = []

        def fitness_getter() -> typing.List[float]:
            return [ind.fitness for ind in self.population.individuals]

        termination_manager = termination.TerminationManager(
            termination_conditions, fitness_getter
        )
        epoch_manager_best = termination.TerminationManager(
            [termination.NoChangeInBestFitness(250)], fitness_getter
        )
        epoch_manager_avg = termination.TerminationManager(
            [termination.NoChangeInAverageFitness(250)], fitness_getter
        )

        while not termination_manager.should_terminate():
            # Check for epoch restart
            if (epoch_manager_best.should_terminate() and
                    epoch_manager_avg.should_terminate()):
                if previous_epoch:
                    # Merge with previous epoch
                    epoch_manager_best.reset()
                    epoch_manager_avg.reset()
                    self.population.individuals += previous_epoch
                    previous_epoch = []
                else:
                    # Start new epoch
                    epoch_manager_best.reset()
                    epoch_manager_avg.reset()
                    previous_epoch = self.population.individuals
                    self.population = population.Population(
                        self.mu, self.lambda_
                    )
                    generation = 0
                    epochs += 1

            # Selection and reproduction
            self.population = population.Population.survival_selection(
                self.population
            )
            offspring = population.Population.generate_offspring(
                self.population
            )
            self.population.individuals += offspring.individuals

            self._log(total_generations, epochs, generation)

            total_generations += 1
            generation += 1

        print(f"Result: {self.population.fittest.genotype}")
        return self.population.fittest

    def _log(
        self, total_generations: int, epochs: int, generation: int
    ) -> None:
        """Log the current state of the evolutionary algorithm.

        Args:
            total_generations: Total number of generations across all epochs.
            epochs: Current epoch number.
            generation: Generation number within the current epoch.
        """
        fitnesses = [ind.fitness for ind in self.population.individuals]
        best_fitness = max(fitnesses)
        avg_fitness = sum(fitnesses) / len(fitnesses)

        print(
            f"Total Generations #{total_generations}, "
            f"Epoch #{epochs}, "
            f"Generation #{generation}: "
            f"Best - {best_fitness:.4f}, "
            f"Average - {avg_fitness:.4f}"
        )
