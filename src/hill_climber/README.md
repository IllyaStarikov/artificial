# Hill Climber

A Python implementation of hill climbing optimization algorithms for finding optima in 2D function landscapes.

## Overview

This module provides implementations of classic hill climbing algorithms:

- **Steepest-Ascent Hill Climbing**: Always moves to the best neighbor
- **Stochastic Hill Climbing**: Randomly selects among uphill moves
- **Random Restart Hill Climbing**: Multiple runs from random starting points

## Quick Start

```python
import function
import hill_climber

# Define an objective function
func = function.Function(
    lambda x, y: -(x**2 + y**2),  # Maximize (find minimum of x² + y²)
    x_bounds=(-100, 100),
    y_bounds=(-100, 100)
)

# Basic hill climbing
climber = hill_climber.HillClimber(func)
optimum = climber.climb()
print(f"Found: ({optimum.x}, {optimum.y})")

# Stochastic with restarts
climber = hill_climber.HillClimber(func, stochastic=True)
optimum = climber.climb(restarts=10)
print(f"Best found: ({optimum.x}, {optimum.y})")
```

## Modules

| Module | Description |
|--------|-------------|
| `hill_climber.py` | Hill climbing with steepest-ascent and stochastic modes |
| `function.py` | Objective function wrapper with bounds |
| `node.py` | 2D point representation |
| `main.py` | Example usage demonstrations |

## Usage

```bash
make install  # Install dependencies
make run      # Run example demonstrations
make build    # Run linting and type checks
```
