"""Local Search Algorithms module.

This module provides implementations of local search optimization algorithms:
- Hill Climbing (steepest ascent and stochastic variants)
- Optional random restarts for escaping local optima

These algorithms are designed to find local optima in continuous function
optimization problems over discrete 2D grids.

Example:
    import function
    import hill_climber

    func = function.Function(
        lambda x, y: -(x**2 + y**2), (-100, 100), (-100, 100)
    )

    # Steepest-ascent
    climber = hill_climber.HillClimber(func)
    optimum = climber.climb()

    # Stochastic with restarts
    climber = hill_climber.HillClimber(func, stochastic=True)
    optimum = climber.climb(restarts=10)
"""

__all__ = [
    "Function",
    "Node",
    "HillClimber",
]
