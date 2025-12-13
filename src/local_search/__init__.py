"""Local Search Algorithms module.

This module provides implementations of local search optimization algorithms:
- Hill Climbing (steepest ascent)
- Stochastic Hill Climbing with optional random restarts

These algorithms are designed to find local optima in continuous function
optimization problems over discrete 2D grids.

Example:
    import function
    import stochastic_hill_climber

    func = function.Function(lambda x, y: -(x**2 + y**2), (-100, 100), (-100, 100))
    climber = stochastic_hill_climber.StochasticHillClimber(func)
    optimum = climber.climb(restarts=10)
"""

__all__ = [
    "Function",
    "Node",
    "HillClimber",
    "StochasticHillClimber",
]
