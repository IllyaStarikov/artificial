#!/usr/local/bin/python3
#
# population.py
# src
#
# Created by Illya Starikov on 10/12/18.
# Copyright 2018. Illya Starikov. MIT License.
#

from copy import deepcopy
from random import choice, sample

from individual import Individual


class Population:
    def __init__(self, μ, λ):
        """Initialize a population of individuals.

        :μ (int): The population size.
        :λ (int): The offspring size.
        """
        self.μ, self.λ = μ, λ

        self.individuals = [Individual() for _ in range(self.μ)]

    @property
    def fittest(self):
        """Find the fittest individual in a population, according to the individual fitness function.

        :return (Individual): The fittest individual.
        """
        return max(self.individuals, key=lambda individual: individual.fitness)

    @staticmethod
    def random_parents(population):
        """Get two random parents from a population.

        :return (Individual, Individual): Two random parents.

        """
        split = choice(range(1, len(population.individuals) - 1))
        return choice(population.individuals[:split]), choice(population.individuals[split:])

    @staticmethod
    def generate_offspring(population):
        """Generate offspring from a Population by picking two random parents, recombining them,
        mutating the child, and adding it to the offspring. The number of offspring is determine by
        λ.

        :population (Population): The population to generate the offspring from.
        :returns (Population): The offspring (of size λ).
        """
        offspring = Population(population.μ, population.λ)
        offspring.individual = []

        for _ in range(population.λ):
            parent_one, parent_two = Population.random_parents(population)

            child = Individual.recombine(parent_one, parent_two)
            child.mutate(child, 0.15)

            offspring.individuals += [child]

        return offspring

    @staticmethod
    def survival_selection(population):
        """Determine from the population what individuals should not be killed. This is done via
        k-tournament selection: generate a tournament of k random individuals, pick the fittest
        individuals, add it to the survivors, and remove it from the original population.

        Note:
            The population should be of size μ + λ. The resultant population will be of size μ.

        :population (Population): The population to run survival selection on. Must be of size μ + λ.
        :returns (Population): The resultant population after killing off unfit individual. Will be
        of size μ.
        """
        new_population = Population(population.μ, population.λ)
        new_population.individuals = []

        individuals = deepcopy(population.individuals)

        for _ in range(population.μ):
            tournament = sample(individuals, 25)
            victor = max(tournament, key=lambda individual: individual.fitness)

            new_population.individuals += [victor]
            individuals.remove(victor)

        return new_population
