"""Example usage of local search algorithms.

This module demonstrates the use of various hill climbing algorithms
on simple objective functions.

Usage:
    python main.py
"""

from __future__ import annotations

import math

import function
import hill_climber
import stochastic_hill_climber


def main() -> None:
    """Run example demonstrations of local search algorithms."""
    # Simple quadratic function (global optimum at origin)
    print("=" * 80)
    print("Steepest-Ascent Hill Climber on f(x,y) = -x^2 - y^2")
    print("=" * 80)

    quadratic = function.Function(
        lambda x, y: -(x ** 2) - (y ** 2),
        (-100, 100),
        (-100, 100)
    )

    climber = hill_climber.HillClimber(quadratic)
    result = climber.climb()
    print(f"Found optimum at: ({result.x}, {result.y})")
    print("-" * 80)

    # More complex function with multiple local optima
    print("\nStochastic Hill Climber on complex function")
    print("=" * 80)

    complex_func = function.Function(
        lambda x, y: -(x ** 2) - (y ** 2) + (x * y * math.cos(x) * math.sin(y)),
        (-100, 100),
        (-100, 100)
    )

    shc = stochastic_hill_climber.StochasticHillClimber
    stochastic_climber = shc(complex_func)
    result = stochastic_climber.climb()
    print(f"Found optimum at: ({result.x}, {result.y})")
    print("-" * 80)

    # Stochastic hill climber with restarts
    print("\nStochastic Hill Climber with 10 Restarts")
    print("=" * 80)

    stochastic_climber = shc(complex_func)
    result = stochastic_climber.climb(restarts=10)
    print(f"Found optimum at: ({result.x}, {result.y})")
    print("-" * 80)


if __name__ == "__main__":
    main()
