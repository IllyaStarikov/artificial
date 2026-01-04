"""Evolutionary Algorithms module.

This module provides a framework for evolutionary algorithms, including:
- Genetic algorithm implementation with configurable termination conditions
- SAT (Boolean Satisfiability) problem representation
- Various crossover operators (uniform, n-point, Davis)
- Population management with tournament selection

Example:
    import evolutionary

    evolutionary.Individual.cnf_filename = "input.cnf"
    algorithm = evolutionary.EA(mu=100, lambda_=50)
    result = algorithm.search([evolutionary.FitnessTarget(95.0)])
"""

from evolutionary import ea
from evolutionary import individual
from evolutionary import population
from evolutionary import sat
from evolutionary import termination

EA = ea.EA
Individual = individual.Individual
Population = population.Population
SAT = sat.SAT
TerminationCondition = termination.TerminationCondition
TerminationManager = termination.TerminationManager
FitnessTarget = termination.FitnessTarget
DateTarget = termination.DateTarget
NoChangeInAverageFitness = termination.NoChangeInAverageFitness
NoChangeInBestFitness = termination.NoChangeInBestFitness
NumberOfFitnessEvaluations = termination.NumberOfFitnessEvaluations
NumberOfGenerations = termination.NumberOfGenerations

__all__ = [
    "EA",
    "Individual",
    "Population",
    "SAT",
    "TerminationCondition",
    "TerminationManager",
    "FitnessTarget",
    "DateTarget",
    "NoChangeInAverageFitness",
    "NoChangeInBestFitness",
    "NumberOfFitnessEvaluations",
    "NumberOfGenerations",
]
