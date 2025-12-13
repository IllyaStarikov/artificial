# Local Search Algorithms

A Python implementation of local search optimization algorithms for finding optima in 2D function landscapes.

## Overview

This module provides implementations of classic local search algorithms:

- **Steepest-Ascent Hill Climbing**: Always moves to the best neighbor
- **Stochastic Hill Climbing**: Randomly selects among uphill moves
- **Random Restart Hill Climbing**: Multiple runs from random starting points

## Quick Start

```python
from function import Function
from hill_climber import HillClimber
from stochastic_hill_climber import StochasticHillClimber

# Define an objective function
func = Function(
    lambda x, y: -(x**2 + y**2),  # Maximize (find minimum of x² + y²)
    x_bounds=(-100, 100),
    y_bounds=(-100, 100)
)

# Basic hill climbing
climber = HillClimber(func)
optimum = climber.climb()
print(f"Found: ({optimum.x}, {optimum.y})")

# Stochastic with restarts
stochastic = StochasticHillClimber(func)
optimum = stochastic.climb(restarts=10)
print(f"Best found: ({optimum.x}, {optimum.y})")
```

## Modules

| Module | Description |
|--------|-------------|
| `hill_climber.py` | Steepest-ascent hill climbing |
| `stochastic_hill_climber.py` | Stochastic variant with optional restarts |
| `function.py` | Objective function wrapper with bounds |
| `node.py` | 2D point representation |
| `main.py` | Example usage demonstrations |

## Algorithms

### Steepest-Ascent Hill Climbing

1. Start at random position
2. Evaluate all neighbors (4-connected grid)
3. Move to highest-valued neighbor
4. Repeat until no neighbor is better
5. Return local optimum

**Pros**: Fast, deterministic given starting point
**Cons**: Gets stuck in local optima

### Stochastic Hill Climbing

1. Start at random position
2. Find all uphill neighbors
3. Randomly select one uphill neighbor
4. Repeat until no uphill moves exist
5. Return local optimum

**Pros**: Can escape some local optima
**Cons**: Still limited by local search

### Random Restart Hill Climbing

1. Run stochastic hill climbing
2. Repeat from new random starting point
3. Track best result across all runs
4. Return global best

**Pros**: Better global optimization
**Cons**: Computationally expensive

## Usage

```bash
make install  # Install dependencies
make run      # Run example demonstrations
make build    # Run linting and type checks
```

## Function Definition

Functions are defined with explicit bounds:

```python
from function import Function
from math import sin, cos

# Complex multi-modal function
complex_func = Function(
    lambda x, y: -(x**2) - (y**2) + (x * y * cos(x) * sin(y)),
    x_bounds=(-100, 100),
    y_bounds=(-100, 100)
)
```

## Limitations

- **Grid-based**: Operates on integer coordinates only
- **2D only**: Limited to two-dimensional search spaces
- **Local search**: No guarantee of finding global optimum
