"""Evolutionary Algorithms module.

This module provides a framework for evolutionary algorithms, including:
- Genetic algorithm implementation with configurable termination conditions
- SAT (Boolean Satisfiability) problem representation
- Various crossover operators (uniform, n-point, Davis)
- Population management with tournament selection

Example:
    import ea
    import individual
    import termination

    individual.Individual.cnf_filename = "input.cnf"
    algorithm = ea.EA(mu=100, lambda_=50)
    result = algorithm.search([termination.FitnessTarget(95.0)])
"""

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
