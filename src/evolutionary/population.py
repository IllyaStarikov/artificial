"""Population management for evolutionary algorithms.

This module provides the Population class for managing collections of
individuals, including selection and offspring generation.

Example:
    import individual
    import population

    individual.Individual.cnf_filename = "input.cnf"
    pop = population.Population(mu=100, lambda_=50)
    offspring = population.Population.generate_offspring(pop)
"""

from __future__ import annotations

import copy
import random
import typing

import individual


class Population:
    """A collection of individuals in the evolutionary algorithm.

    Manages population initialization, parent selection, offspring generation,
    and survival selection using tournament selection.

    Attributes:
        mu: The population size (number of parents).
        lambda_: The offspring size (number of children per generation).
        individuals: List of Individual objects in the population.
        fittest: The individual with the highest fitness.
    """

    def __init__(self, mu: int, lambda_: int) -> None:
        """Initialize a population with random individuals.

        Args:
            mu: Population size (number of parents to maintain).
            lambda_: Offspring size (number of children per generation).
        """
        self.mu = mu
        self.lambda_ = lambda_
        self.individuals: typing.List[individual.Individual] = [
            individual.Individual() for _ in range(self.mu + self.lambda_)
        ]

    @property
    def fittest(self) -> individual.Individual:
        """Get the fittest individual in the population.

        Returns:
            The individual with the highest fitness value.
        """
        return max(self.individuals, key=lambda ind: ind.fitness)

    @staticmethod
    def random_parents(
        pop: Population
    ) -> typing.Tuple[individual.Individual, individual.Individual]:
        """Select two random parents from the population.

        Args:
            pop: The population to select from.

        Returns:
            A tuple of two randomly selected individuals.
        """
        split = random.choice(range(1, len(pop.individuals) - 1))
        return (
            random.choice(pop.individuals[:split]),
            random.choice(pop.individuals[split:])
        )

    @staticmethod
    def generate_offspring(pop: Population) -> Population:
        """Generate offspring through recombination and mutation.

        Creates lambda_ new individuals by selecting parents, recombining
        their genes, and applying mutation.

        Args:
            pop: The parent population.

        Returns:
            A new Population containing only the offspring.
        """
        offspring = Population(pop.mu, pop.lambda_)
        offspring.individuals = []

        for _ in range(pop.lambda_):
            parent_one, parent_two = Population.random_parents(pop)
            child = individual.Individual.recombine(parent_one, parent_two)
            individual.Individual.mutate(child, 0.05)
            offspring.individuals.append(child)

        return offspring

    @staticmethod
    def survival_selection(pop: Population) -> Population:
        """Select survivors using k-tournament selection.

        Reduces a population of size mu + lambda_ to size mu by repeatedly
        running tournaments and selecting winners.

        Args:
            pop: The population to select from (size mu + lambda_).

        Returns:
            A new Population of size mu containing the survivors.
        """
        new_population = Population(pop.mu, pop.lambda_)
        new_population.individuals = []

        candidates = copy.deepcopy(pop.individuals)

        for _ in range(pop.mu):
            tournament_size = min(25, len(candidates))
            tournament = random.sample(candidates, tournament_size)
            winner = max(tournament, key=lambda ind: ind.fitness)
            new_population.individuals.append(winner)
            candidates.remove(winner)

        return new_population
