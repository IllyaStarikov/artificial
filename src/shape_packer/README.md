# Shape Packer

A Python implementation of evolutionary algorithms for 2D shape packing optimization. Places irregular shapes on a board while minimizing used space.

<p align="center">
  <img src="../../assets/shape_packer.gif" alt="Shape Packer Demo">
</p>

## Overview

This module provides an evolutionary approach to shape packing:

- **(μ + λ) Evolution Strategy**: Configurable population and offspring sizes
- **Repairing Crossover**: Maintains diversity by fixing collisions instead of discarding
- **Tournament Selection**: Weak selection pressure (k=2) for exploration
- **Random Immigrants**: 5% of population replaced each generation
- **Numpy-Accelerated Collision Detection**: Fast O(1) placement validation

## Quick Start

```bash
# Run with visualization
cd src && python -m run shape-pack -i shape_packer/input/input-2.txt -v

# Save animation as GIF (15 seconds)
python -m run shape-pack -i shape_packer/input/input-2.txt --save=evolution.gif

# Save 30 second GIF
python -m run shape-pack -i shape_packer/input/input-2.txt --save=evolution.gif --duration=30

# Run without visualization
python -m run shape-pack -i shape_packer/input/input-2.txt
```

## Visualization

Real-time display showing shape placement optimization:
- **Left panel**: Board with placed shapes (colored by shape ID)
- **Green highlight**: Empty columns (fitness objective)
- **Right graphs**: Fitness convergence, diversity (σ), and cumulative gain

```bash
python -m run shape-pack -i INPUT [OPTIONS]
```

| Option | Description | Default |
|--------|-------------|---------|
| `-i, --input FILE` | Input shapes file | Required |
| `-v, --visualize` | Show real-time visualization | Off |
| `--save FILE` | Save animation as GIF | None |
| `--duration N` | Recording duration in seconds | 15 |
| `--mu N` | Population size | 100 |
| `--lambda N` | Offspring size | 50 |
| `--mutation-rate R` | Mutation probability | 0.05 |
| `--interval N` | Generations per frame | 5 |

## Python API

```python
from shape_packer import (
    ShapePackerEA,
    ShapePackerConfig,
    parse_input_file,
    format_solution,
)
from sat_solver.termination import (
    NumberOfFitnessEvaluations,
    NoChangeInBestFitness,
)

# Load shapes
shapes, board_dims = parse_input_file("shapes.txt")

# Configure EA
config = ShapePackerConfig(
    mu=100,
    lambda_=50,
    mutation_rate=0.05,
)

# Run optimization
ea = ShapePackerEA(shapes, board_dims, config)
best = ea.search([
    NumberOfFitnessEvaluations(10000),
    NoChangeInBestFitness(250),
])

print(format_solution(best))
```

## Modules

| Module | Description |
|--------|-------------|
| `ea.py` | Main evolutionary algorithm with elitism |
| `individual.py` | Solution representation with cached fitness |
| `shape.py` | Shape with pre-cached rotations and bounds |
| `board.py` | Numpy-based board with O(1) collision detection |
| `selection.py` | Tournament and truncation selection |
| `operators.py` | Crossover and mutation operators |
| `population.py` | Population management |
| `visualize.py` | Matplotlib visualization with GIF export |
| `io.py` | Input/output file handling |
| `config.py` | Configuration dataclass |

## Input Format

```
height width
D1 R2 U1      # Shape 1: direction-magnitude pairs
L3 D2 R1 U3   # Shape 2
...
```

Directions: `U` (up), `D` (down), `L` (left), `R` (right)
Magnitudes: 1, 2, or 3 cells

## Fitness Function

Fitness = number of empty columns on the left side of the board. The algorithm optimizes to pack all shapes as far right as possible, maximizing empty space on the left.

## Performance Optimizations

- **Point class with `__slots__`**: Reduced memory, pre-computed hash
- **Numpy grid for collision**: O(1) cell lookup vs O(n) set membership
- **Pre-cached shape rotations**: Points and bounds computed once at init
- **Placement caches points**: No recalculation during fitness evaluation
- **heapq.nlargest for selection**: O(n log k) vs O(n log n) sorting
- **Sampling-based repair**: Random sampling instead of exhaustive search
