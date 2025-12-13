# Evolutionary Algorithms

A Python implementation of evolutionary algorithms for solving optimization problems, specifically designed for Boolean Satisfiability (SAT) problems.

## Overview

This module provides a complete framework for evolutionary computation including:

- **(μ + λ) Evolutionary Strategy**: Configurable population and offspring sizes
- **Tournament Selection**: K-tournament survival selection
- **Multiple Crossover Operators**: Uniform, n-point, and Davis crossover
- **Adaptive Epoch Management**: Automatic restarts when progress stagnates
- **Flexible Termination Conditions**: Fitness targets, generation limits, time limits, and stagnation detection

## Quick Start

```python
from ea import EA
from individual import Individual
from termination import FitnessTarget, NumberOfGenerations

# Configure the problem
Individual.cnf_filename = "input.cnf"

# Create and run the EA
ea = EA(mu=100, lambda_=50)
result = ea.search([
    FitnessTarget(95.0),
    NumberOfGenerations(10000)
])

print(f"Best fitness: {result.fitness}")
```

## Modules

| Module | Description |
|--------|-------------|
| `ea.py` | Main evolutionary algorithm with epoch management |
| `individual.py` | Individual representation with mutation and crossover |
| `population.py` | Population management and selection operators |
| `sat.py` | SAT problem representation (CNF format) |
| `termination.py` | Termination conditions and manager |

## Termination Conditions

- `FitnessTarget(value)`: Stop when fitness reaches target
- `NumberOfGenerations(n)`: Stop after n generations
- `NumberOfFitnessEvaluations(n)`: Stop after n fitness evaluations
- `DateTarget(datetime)`: Stop at specified time
- `NoChangeInBestFitness(n)`: Stop if best fitness stagnates
- `NoChangeInAverageFitness(n)`: Stop if average fitness stagnates

## Input Format

The SAT solver expects input in DIMACS CNF format:

```
c Comment line
p cnf <num_variables> <num_clauses>
1 -2 3 0
-1 2 0
```

## Usage

```bash
make install  # Install dependencies
make run      # Run with example input
make build    # Run linting and type checks
```

## Algorithm Details

### Selection
- **Parent Selection**: Random split selection
- **Survival Selection**: K-tournament (k=25) without replacement

### Variation
- **Mutation**: Uniform random bit flip (5% rate)
- **Crossover**: 5-point crossover (configurable)

### Epoch Management
When both best and average fitness stagnate for 250 generations:
1. First stagnation: Save population, restart with random individuals
2. Second stagnation: Merge saved population with current, continue
