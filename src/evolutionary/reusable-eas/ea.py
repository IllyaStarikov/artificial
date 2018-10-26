#!/usr/local/bin/python3
#
# ea.py
# src
#
# Created by Illya Starikov on 10/12/18.
# Copyright 2018. Illya Starikov. MIT License.
#

from population import Population


class EA:
    def __init__(self, μ, λ):
        """Initialize an EA.

        :μ (int): The population size.
        :λ (int): The offspring size.
        """
        self.μ, self.λ = μ, λ

    def search(self):
        """Run the genetic algorithm until the fittness reaches 100%.

        :returns: The fittest individual.
        """
        generation = 1
        self.population = Population(self.μ, self.λ)

        while self.population.fittest.fitness < 100.0:
            offspring = Population.generate_offspring(self.population)
            self.population.individuals += offspring.individuals
            self.population = Population.survival_selection(self.population)

            print("Generation #{}: {}".format(generation, self.population.fittest.fitness))
            generation += 1

        print("Result: {}".format(self.population.fittest.genotype))
        return self.population.fittest
