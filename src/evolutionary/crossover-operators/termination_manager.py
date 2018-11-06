#!/usr/local/bin/python3
#
# termination-manager.py
# endgame-dynamics
#
# Created by Illya Starikov on 10/25/18.
# Copyright 2018. Illya Starikov. MIT License.
#
import datetime
from math import ceil

from termination_conditions import _TerminationCondition, FitnessTarget, DateTarget, NoChangeInAverageFitness, NoChangeInBestFitness, NumberOfFitnessEvaluations, NumberOfGenerations


class TerminationManager:
    def __init__(self, termination_conditions, fitness_selector):
        """Create a TerminationManager object.

        Args:
            termination_conditions
            fitness_selector (lambda): Calling this should attain all fitness values of the EA population.
        """

        assert isinstance(termination_conditions, list)
        assert all(issubclass(type(condition), _TerminationCondition) for condition in termination_conditions), "Termination condition is not valid"

        self.termination_conditions = termination_conditions
        self.__fitness_selector = fitness_selector

        self.__best_fitnesses = []
        self.__average_fitnesses = []

        self.__number_of_fitness_evaluations = 0
        self.__number_of_generations = 0

    def should_terminate(self):
        """Determine if any of the termination conditions have been met.

        Returns:
            bool: True if any of the termination conditions have been met, False otherwise.
        """
        for condition in self.termination_conditions:
            if isinstance(condition, FitnessTarget) and self.__fitness_should_terminate():
                return True
            elif isinstance(condition, DateTarget) and self.__date_should_terminate():
                return True
            elif isinstance(condition, NoChangeInAverageFitness) and self.__average_fitness_should_terminate():
                return True
            elif isinstance(condition, NoChangeInBestFitness) and self.__best_fitness_should_terminate():
                return True
            elif isinstance(condition, NumberOfFitnessEvaluations) and self.__fitness_evaluations_should_terminate():
                return True
            elif isinstance(condition, NumberOfGenerations) and self.__generations_should_terminate():
                return True

        return False

    def reset(self):
        """Reset the best fitnesses, average fitnesses, number of generations, and number of fitness evaluations."""
        self.__best_fitnesses = []
        self.__average_fitnesses = []

        self.__number_of_fitness_evaluations = 0
        self.__number_of_generations = 0

    def __fitness_should_terminate(self):
        """Determine if should terminate based on the max fitness.

        Returns:
            bool: True if should terminate based on the max fitness, False otherwise.
        """

        fitness = self.__fitness_selector()

        target_fitness_class = next(condition for condition in self.termination_conditions if isinstance(condition, FitnessTarget))
        target_fitness = target_fitness_class.target_fitness

        return max(fitness) >= target_fitness

    def __date_should_terminate(self):
        """Determine if should terminate based on the date.

        Returns:
            bool: True if should terminate based on the date, False otherwise.
        """
        now = datetime.datetime.now()

        date_class = next(condition for condition in self.termination_conditions if isinstance(condition, DateTarget))
        target_date = date_class.date

        return now >= target_date

    def __average_fitness_should_terminate(self):
        """Determine if should terminate based on the average fitness for the last N generations.

        Returns:
            bool: True if should terminate based on the average fitness of the last N generations, False otherwise.
        """
        fitnesses = self.__fitness_selector()
        average_fitness = sum(fitnesses) / len(fitnesses)

        target_class = next(condition for condition in self.termination_conditions if isinstance(condition, NoChangeInAverageFitness))
        number_of_generations_till_termination = target_class.number_of_generations

        self.__average_fitnesses = TerminationManager.__add_fitness_to_fitness_queue(average_fitness, self.__average_fitnesses, number_of_generations_till_termination)
        if len(self.__average_fitnesses) < number_of_generations_till_termination:
            return False

        last_quartile_mark = ceil(len(self.__average_fitnesses) / 4)
        oldest_fitnesses = self.__average_fitnesses[:last_quartile_mark]
        average_fitness_of_last_quartile = sum(oldest_fitnesses) / len(oldest_fitnesses)

        should_terminate_ = all(fitness <= average_fitness_of_last_quartile for fitness in self.__average_fitnesses[last_quartile_mark:])

        return should_terminate_

    def __best_fitness_should_terminate(self):
        """Determine if should terminate based on the average fitness for the last N generations.

        Returns:
            bool: True if should terminate based on the average fitness of the last N generations, False otherwise.
        """
        fitnesses = self.__fitness_selector()
        best_fitness = max(fitnesses)

        target_class = next(condition for condition in self.termination_conditions if isinstance(condition, NoChangeInBestFitness))
        number_of_generations_till_termination = target_class.number_of_generations

        self.__best_fitnesses = TerminationManager.__add_fitness_to_fitness_queue(best_fitness, self.__best_fitnesses, number_of_generations_till_termination)

        if len(self.__best_fitnesses) < number_of_generations_till_termination:
            return False

        last_quartile_mark = ceil(len(self.__best_fitnesses) / 4)
        oldest_fitnesses = self.__best_fitnesses[:last_quartile_mark]
        average_fitness_of_last_quartile = sum(oldest_fitnesses) / len(oldest_fitnesses)

        should_terminate_ = all(fitness <= average_fitness_of_last_quartile for fitness in self.__best_fitnesses[last_quartile_mark:])

        return should_terminate_

    def __fitness_evaluations_should_terminate(self):
        """Determine if should terminate based on the number of fitness evaluations.

        Returns:
            bool: True if should terminate based on the number of fitness evaluations, False otherwise.
        """
        fitnesses = self.__fitness_selector()
        self.__number_of_fitness_evaluations += len(fitnesses)

        fitnesses_class = next(condition for condition in self.termination_conditions if isinstance(condition, NumberOfFitnessEvaluations))
        number_of_fitness_evaluations = fitnesses_class.number_of_fitness_evaluations

        return self.__number_of_fitness_evaluations > number_of_fitness_evaluations

    def __generations_should_terminate(self):
        """Determine if should terminate based on the number of generations.

        Returns:
            bool: True if should terminate based on the number of generations, False otherwise.
        """
        self.__number_of_generations += 1

        generation_class = next(condition for condition in self.termination_conditions if isinstance(condition, NumberOfGenerations))
        number_of_generations = generation_class.number_of_generations

        return self.__number_of_generations > number_of_generations

    @staticmethod
    def __add_fitness_to_fitness_queue(new_fitness, fitnesses, number_of_generations):
        """Add a new fitness to one of the fitness queues, keeping them at `number_of_generations`.

        Args:
            new_fitness (float): The new fitness to add to the queue.
            fitnesses (list<float>): The queue to add the fitnesses to.
            number_of_generations (int): The length to keep the fitness queues at.

        Returns:
            list<float>: The new fitnesses queue.
        """
        if len(fitnesses) < number_of_generations:
            return fitnesses + [new_fitness]

        fitnesses.pop(0)
        return fitnesses + [new_fitness]
