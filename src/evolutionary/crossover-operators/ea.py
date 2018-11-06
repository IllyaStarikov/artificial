#!/usr/local/bin/python3
#
# ea.py
# src
#
# Created by Illya Starikov on 10/12/18.
# Copyright 2018. Illya Starikov. MIT License.  #

from population import Population
from termination_manager import TerminationManager

from termination_conditions import NoChangeInAverageFitness, NoChangeInBestFitness


class EA:
    def __init__(self, μ, λ):
        """Initialize an EA.

        :μ (int): The population size.
        :λ (int): The offspring size.
        """
        self.μ, self.λ = μ, λ

    def search(self, termination_conditions):
        """Run the genetic algorithm with specified `termination_conditions`.

        Args:
            termination_conditions (list<TerminationCondition>): The criteria that must be met before terminating (meeting any of them will terminate the EA).

        :returns: The fittest individual.
        """
        epochs, generation, total_generations = 1, 1, 1
        self.population = Population(self.μ, self.λ)

        previous_epoch = []
        fitness_getter = lambda: [individual.fitness for individual in self.population.individuals]  # noqa

        termination_manager = TerminationManager(termination_conditions, fitness_getter)
        epoch_manager_best_fitness = TerminationManager([NoChangeInBestFitness(250)], fitness_getter)
        epoch_manager_average_fitness = TerminationManager([NoChangeInAverageFitness(250)], fitness_getter)

        while not termination_manager.should_terminate():
            if epoch_manager_best_fitness.should_terminate() and epoch_manager_average_fitness.should_terminate():
                if len(previous_epoch) > 0:
                    epoch_manager_best_fitness.reset()
                    epoch_manager_average_fitness.reset()

                    self.population.individuals += previous_epoch
                    previous_epoch = []
                else:
                    epoch_manager_best_fitness.reset()
                    epoch_manager_average_fitness.reset()

                    previous_epoch = self.population.individuals
                    self.population = Population(self.μ, self.λ)

                    generation = 0
                    epochs += 1

            self.population = Population.survival_selection(self.population)

            offspring = Population.generate_offspring(self.population)
            self.population.individuals += offspring.individuals

            self.__log(total_generations, epochs, generation)

            total_generations += 1
            generation += 1

        print("Result: {}".format(self.population.fittest.genotype))
        return self.population.fittest

    def __log(self, total_generations, epochs, generation):
        """Log the process of the Evolutionary Algorithm.

        Args:
            total_generations (int): The total number of generations that have passed.
            epochs (int): The number of epochs that have passed.
            generations (int): The number of generations in this, current epoch.
        """
        fitnesses = [individual.fitness for individual in self.population.individuals]

        best_fitness = max(fitnesses)
        average_fitness = sum(fitnesses) / len(fitnesses)

        format_string = "Total Generations #{}, Epoch #{}, Generation #{}: Best – {:.4f}, Average – {:.4f}"
        log_string = format_string.format(total_generations, epochs, generation, best_fitness, average_fitness)

        print(log_string)
