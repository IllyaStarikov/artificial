"""Hill Climber module.

This module provides implementations of local search optimization algorithms:
- Hill Climbing (steepest ascent and stochastic variants)
- Optional random restarts for escaping local optima

These algorithms are designed to find local optima in continuous function
optimization problems over discrete 2D grids.

Example:
    from hill_climber import Function, Node, HillClimber

    func = Function(
        lambda x, y: -(x**2 + y**2), (-100, 100), (-100, 100)
    )

    # Steepest-ascent
    climber = HillClimber(func)
    optimum = climber.climb()

    # Stochastic with restarts
    climber = HillClimber(func, stochastic=True)
    optimum = climber.climb(restarts=10)
"""

from hill_climber.function import Function
from hill_climber.node import Node
from hill_climber.hill_climber import HillClimber

__all__ = [
    "Function",
    "Node",
    "HillClimber",
]
