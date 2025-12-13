"""Termination conditions and manager for evolutionary algorithms.

This module defines termination conditions and the manager that evaluates them
to determine when an evolutionary algorithm should stop.

Example:
    import termination

    conditions = [
        termination.FitnessTarget(95.0),
        termination.NumberOfGenerations(1000),
    ]
    manager = termination.TerminationManager(
        conditions, lambda: [90.0, 85.0, 92.0]
    )

    while not manager.should_terminate():
        # Run EA iteration
        pass
"""

from __future__ import annotations

import datetime
import math
import typing


# =============================================================================
# Termination Conditions
# =============================================================================


class TerminationCondition:
    """Base class for all termination conditions.

    Subclasses define specific criteria for terminating an EA run.
    """

    pass


class FitnessTarget(TerminationCondition):
    """Terminate when an individual reaches a target fitness.

    Attributes:
        target_fitness: The fitness threshold to reach.
    """

    def __init__(self, value: float) -> None:
        """Create a FitnessTarget condition.

        Args:
            value: The target fitness value (0-100 scale typically).
        """
        self.target_fitness = value


class DateTarget(TerminationCondition):
    """Terminate after a specific date and time.

    Attributes:
        date: The datetime after which to terminate.
    """

    def __init__(self, date: datetime.datetime) -> None:
        """Create a DateTarget condition.

        Args:
            date: The target datetime for termination.
        """
        self.date = date


class NoChangeInAverageFitness(TerminationCondition):
    """Terminate when average fitness stagnates.

    Triggers termination when the average population fitness has not
    improved for a specified number of generations.

    Attributes:
        number_of_generations: Generations of stagnation before termination.
    """

    def __init__(self, generations: int) -> None:
        """Create a NoChangeInAverageFitness condition.

        Args:
            generations: Number of generations without improvement to trigger.
        """
        self.number_of_generations = generations


class NoChangeInBestFitness(TerminationCondition):
    """Terminate when best fitness stagnates.

    Triggers termination when the best fitness has not improved for a
    specified number of generations.

    Attributes:
        number_of_generations: Generations of stagnation before termination.
    """

    def __init__(self, generations: int) -> None:
        """Create a NoChangeInBestFitness condition.

        Args:
            generations: Number of generations without improvement to trigger.
        """
        self.number_of_generations = generations


class NumberOfFitnessEvaluations(TerminationCondition):
    """Terminate after a specific number of fitness evaluations.

    Attributes:
        number_of_fitness_evaluations: Maximum evaluations allowed.
    """

    def __init__(self, evaluations: int) -> None:
        """Create a NumberOfFitnessEvaluations condition.

        Args:
            evaluations: Maximum number of fitness evaluations.
        """
        self.number_of_fitness_evaluations = evaluations


class NumberOfGenerations(TerminationCondition):
    """Terminate after a specific number of generations.

    Attributes:
        number_of_generations: Maximum generations to run.
    """

    def __init__(self, generations: int) -> None:
        """Create a NumberOfGenerations condition.

        Args:
            generations: Maximum number of generations to run.
        """
        self.number_of_generations = generations


# =============================================================================
# Termination Manager
# =============================================================================


class TerminationManager:
    """Manages and evaluates termination conditions for an EA.

    Tracks fitness history and other metrics to determine when any of the
    configured termination conditions have been met.

    Attributes:
        termination_conditions: List of conditions to evaluate.
    """

    def __init__(
        self,
        termination_conditions: typing.List[TerminationCondition],
        fitness_selector: typing.Callable[[], typing.List[float]],
    ) -> None:
        """Create a TerminationManager.

        Args:
            termination_conditions: List of conditions to check.
            fitness_selector: Callable returning current population fitnesses.

        Raises:
            AssertionError: If termination_conditions is not a list or contains
                invalid condition types.
        """
        assert isinstance(termination_conditions, list)
        assert all(
            isinstance(c, TerminationCondition) for c in termination_conditions
        ), "All conditions must be TerminationCondition instances"

        self.termination_conditions = termination_conditions
        self._fitness_selector = fitness_selector

        self._best_fitnesses: typing.List[float] = []
        self._average_fitnesses: typing.List[float] = []
        self._num_fitness_evaluations = 0
        self._num_generations = 0

    def should_terminate(self) -> bool:
        """Check if any termination condition is met.

        Returns:
            True if any condition is satisfied, False otherwise.
        """
        for condition in self.termination_conditions:
            if isinstance(condition, FitnessTarget):
                if self._check_fitness_target():
                    return True
            elif isinstance(condition, DateTarget):
                if self._check_date_target():
                    return True
            elif isinstance(condition, NoChangeInAverageFitness):
                if self._check_average_fitness_stagnation():
                    return True
            elif isinstance(condition, NoChangeInBestFitness):
                if self._check_best_fitness_stagnation():
                    return True
            elif isinstance(condition, NumberOfFitnessEvaluations):
                if self._check_fitness_evaluations():
                    return True
            elif isinstance(condition, NumberOfGenerations):
                if self._check_generations():
                    return True

        return False

    def reset(self) -> None:
        """Reset all tracked metrics.

        Call this when starting a new epoch or restarting the algorithm.
        """
        self._best_fitnesses = []
        self._average_fitnesses = []
        self._num_fitness_evaluations = 0
        self._num_generations = 0

    def _check_fitness_target(self) -> bool:
        """Check if the fitness target has been reached.

        Returns:
            True if max fitness >= target fitness.
        """
        fitnesses = self._fitness_selector()
        condition = next(
            c for c in self.termination_conditions
            if isinstance(c, FitnessTarget)
        )
        return max(fitnesses) >= condition.target_fitness

    def _check_date_target(self) -> bool:
        """Check if the target date has passed.

        Returns:
            True if current time >= target date.
        """
        condition = next(
            c for c in self.termination_conditions
            if isinstance(c, DateTarget)
        )
        return datetime.datetime.now() >= condition.date

    def _check_average_fitness_stagnation(self) -> bool:
        """Check if average fitness has stagnated.

        Uses a quartile comparison to detect stagnation.

        Returns:
            True if average fitness hasn't improved significantly.
        """
        fitnesses = self._fitness_selector()
        avg_fitness = sum(fitnesses) / len(fitnesses)

        condition = next(
            c for c in self.termination_conditions
            if isinstance(c, NoChangeInAverageFitness)
        )
        generations_threshold = condition.number_of_generations

        self._average_fitnesses = self._add_to_queue(
            avg_fitness, self._average_fitnesses, generations_threshold
        )

        if len(self._average_fitnesses) < generations_threshold:
            return False

        quartile_mark = math.ceil(len(self._average_fitnesses) / 4)
        oldest_sum = sum(self._average_fitnesses[:quartile_mark])
        oldest_avg = oldest_sum / quartile_mark

        return all(
            f <= oldest_avg
            for f in self._average_fitnesses[quartile_mark:]
        )

    def _check_best_fitness_stagnation(self) -> bool:
        """Check if best fitness has stagnated.

        Uses a quartile comparison to detect stagnation.

        Returns:
            True if best fitness hasn't improved significantly.
        """
        fitnesses = self._fitness_selector()
        best_fitness = max(fitnesses)

        condition = next(
            c for c in self.termination_conditions
            if isinstance(c, NoChangeInBestFitness)
        )
        generations_threshold = condition.number_of_generations

        self._best_fitnesses = self._add_to_queue(
            best_fitness, self._best_fitnesses, generations_threshold
        )

        if len(self._best_fitnesses) < generations_threshold:
            return False

        quartile_mark = math.ceil(len(self._best_fitnesses) / 4)
        oldest_sum = sum(self._best_fitnesses[:quartile_mark])
        oldest_avg = oldest_sum / quartile_mark

        return all(
            f <= oldest_avg
            for f in self._best_fitnesses[quartile_mark:]
        )

    def _check_fitness_evaluations(self) -> bool:
        """Check if the fitness evaluation limit has been reached.

        Returns:
            True if total evaluations > limit.
        """
        fitnesses = self._fitness_selector()
        self._num_fitness_evaluations += len(fitnesses)

        condition = next(
            c for c in self.termination_conditions
            if isinstance(c, NumberOfFitnessEvaluations)
        )
        max_evals = condition.number_of_fitness_evaluations
        return self._num_fitness_evaluations > max_evals

    def _check_generations(self) -> bool:
        """Check if the generation limit has been reached.

        Returns:
            True if total generations > limit.
        """
        self._num_generations += 1

        condition = next(
            c for c in self.termination_conditions
            if isinstance(c, NumberOfGenerations)
        )
        return self._num_generations > condition.number_of_generations

    @staticmethod
    def _add_to_queue(
        value: float, queue: typing.List[float], max_length: int
    ) -> typing.List[float]:
        """Add a value to a bounded queue.

        Args:
            value: The value to add.
            queue: The existing queue.
            max_length: Maximum queue length.

        Returns:
            The updated queue with the new value.
        """
        if len(queue) < max_length:
            return queue + [value]

        queue.pop(0)
        return queue + [value]
