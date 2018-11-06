#!/usr/local/bin/python3
#
# termination_conditions.py
# endgame-dynamics
#
# Created by Illya Starikov on 10/28/18.
# Copyright 2018. Illya Starikov. MIT License.
#


class _TerminationCondition:
    pass


class FitnessTarget(_TerminationCondition):
    """Terminate after an individual reaches a particular fitness."""

    def __init__(self, value):
        """Create a FitnessTarget object.

        Args:
            value (int): The target fitness after which an EA should terminate.
        """
        self.target_fitness = value


class DateTarget(_TerminationCondition):
    """Terminate after a particular date and time."""

    def __init__(self, date):
        """Create a DateTarget object.

        Args:
            date (datetime): The target date after which an EA should terminate.
        """
        self.date = date


class NoChangeInAverageFitness(_TerminationCondition):
    """Terminate after a there has been no change in the average fitness for a period of time."""

    def __init__(self, generations):
        """Create a NoChangeInAverageFitness object.

        Args:
            generations (int): The number of generations after no change in average fitness should terminate.
        """
        self.number_of_generations = generations


class NoChangeInBestFitness(_TerminationCondition):
    """Terminate after a there has been no change in the best fitness for a period of time."""

    def __init__(self, generations):
        """Create a NoChangeInBestFitness object.

        Args:
            generations (int): The number of generations after no change in best fitness should terminate.
        """
        self.number_of_generations = generations


class NumberOfFitnessEvaluations(_TerminationCondition):
    """Terminate after a particular number of fitness evaluations."""

    def __init__(self, evaluations):
        """Create a NumberOfFitnessEvaluations object.

        Args:
            evaluations (int): The number of fitness evaluations after which should terminate.
        """
        self.number_of_fitness_evaluations = evaluations


class NumberOfGenerations(_TerminationCondition):
    """Terminate after a particular number of generations."""

    def __init__(self, generations):
        """Create a NumberOfGenerations object.

        Args:
            evaluations (int): The number of generations after which should terminate.
        """
        self.number_of_generations = generations
