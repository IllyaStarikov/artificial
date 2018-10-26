#!/usr/local/bin/python3
#
# individual.py
# src
#
# Created by Illya Starikov on 10/12/18.
# Copyright 2018. Illya Starikov. MIT License.
#

from secret_message import SecretMessage

from string import ascii_letters
from random import choice


class Individual:
    message = SecretMessage("")

    def __init__(self):
        """Initialize an Individual object.

        Note:
            Individual.message should be initialized first.
        """
        length = Individual.message.length
        characters = [choice(ascii_letters) for _ in range(length)]
        self.genotype = "".join(characters)

    @property
    def fitness(self):
        """Get the fitness of an individual. This is done via a percentage of how many characters
        in the genotype match the actual message.

        :return (float): The fitness of an individual.
        """
        return 100 * Individual.message.letters_match(self.genotype) / Individual.message.length

    @staticmethod
    def mutate(individual, rate):
        """Mutation operator --- mutate an individual with a specified rate.
        This is done via a uniform random mutation, by selecting random genes and swapping them.

        Note:
            rate should be a floating point number (0.0 < rate < 1.0).

        :individual (Individual): The individual to mutate.
        :rate (float): The rate at which to mutate the individual's genotype.
        """
        number_of_characters_to_mutate = int(rate * individual.message.length)
        genotype_list = list(individual.genotype)  # Strings are immutable, we have to use a list

        for _ in range(number_of_characters_to_mutate):
            character_to_mutate = choice(range(individual.message.length))
            genotype_list[character_to_mutate] = choice(ascii_letters)

        individual.genotype = "".join(genotype_list)

    @staticmethod
    def recombine(parent_one, parent_two):
        """Recombination operator --- combine two individuals to generate an offspring.

        :parent_one (Individual): The first parent.
        :parent_two (Individual): The second parent.
        :returns (Individual): The combination of the two parents (the offspring).
        """
        new_genotype = ""

        for gene_one, gene_two in zip(parent_one.genotype, parent_two.genotype):
            gene = choice([gene_one, gene_two])
            new_genotype += gene

        individual = Individual()
        individual.genotype = new_genotype
        return individual
