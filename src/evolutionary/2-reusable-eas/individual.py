#!/usr/local/bin/python3
#
# individual.py
# src
#
# Created by Illya Starikov on 10/12/18.
# Copyright 2018. Illya Starikov. MIT License.
#

from random import choice

from sat import SAT


class Individual:
    cnf_filename = ""

    def __init__(self):
        """Initialize an Individual object.

        Note:
            Individual.cnf_filename should be set before calling this.
        """
        self.genotype = SAT(Individual.cnf_filename)

    @property
    def fitness(self):
        """Get the fitness of an individual. This is done via a percentage of how many clauses are
        satisfied.

        :return (float): The fitness of an individual.
        """
        return 100 * self.genotype.clauses_satisfied / self.genotype.total_clauses

    @staticmethod
    def mutate(individual, rate):
        """Mutation operator --- mutate an individual with a specified rate.
        This is done via a uniform random mutation, by selecting random genes and swapping them.

        Note:
            rate should be a floating point number (0.0 < rate < 1.0).

        :individual (Individual): The individual to mutate.
        :rate (float): The rate at which to mutate the individual's genotype.
        """
        number_of_variables_to_mutate = int(rate * individual.genotype.total_clauses)

        for _ in range(number_of_variables_to_mutate):
            variable_to_mutate = choice(individual.genotype.variables)
            individual.genotype[variable_to_mutate] = not individual.genotype[variable_to_mutate]

    @staticmethod
    def recombine(parent_one, parent_two):
        """Recombination operator --- combine two individuals to generate an offspring.

        :parent_one (Individual): The first parent.
        :parent_two (Individual): The second parent.
        :returns (Individual): The combination of the two parents (the offspring).
        """
        new_genotype = SAT(Individual.cnf_filename)

        for variable in parent_one.genotype.variables:
            gene = choice([parent_one.genotype[variable], parent_two.genotype[variable]])
            new_genotype[variable] = gene

        individual = Individual()
        individual.genotype = new_genotype
        return individual
