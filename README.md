# Artificial Intelligence Algorithms

A collection of AI optimization algorithms implemented in Python, featuring evolutionary algorithms and local search methods.

## Modules

### [Evolutionary Algorithms](src/evolutionary/README.md)

Implementation of evolutionary computation techniques for solving optimization problems:

- (μ + λ) Evolutionary Strategy
- Tournament Selection
- Multiple Crossover Operators (Uniform, N-Point, Davis)
- Adaptive Epoch Management
- SAT Problem Solver

### [Local Search Algorithms](src/local_search/README.md)

Classic local search optimization algorithms:

- Steepest-Ascent Hill Climbing
- Stochastic Hill Climbing
- Random Restart Hill Climbing

## Quick Start

```bash
# Install development dependencies
make install-dev

# Run all checks (lint + type-check)
make build

# Run examples
make run-evolutionary
make run-local_search
```

## Project Structure

```
artificial/
├── makefile                    # Top-level build commands
├── requirements.txt            # Runtime dependencies
├── requirements-dev.txt        # Development dependencies
├── README.md                   # This file
└── src/
    ├── evolutionary/           # Evolutionary algorithms
    │   ├── makefile
    │   ├── README.md
    │   ├── __init__.py
    │   ├── ea.py               # Main EA implementation
    │   ├── individual.py       # Individual representation
    │   ├── population.py       # Population management
    │   ├── sat.py              # SAT problem representation
    │   ├── termination.py      # Termination conditions and manager
    │   └── input.cnf           # Example SAT problem
    └── local_search/           # Local search algorithms
        ├── makefile
        ├── README.md
        ├── __init__.py
        ├── hill_climber.py     # Steepest-ascent hill climbing
        ├── stochastic_hill_climber.py  # Stochastic variant
        ├── function.py         # Objective function wrapper
        ├── node.py             # 2D point representation
        └── main.py             # Example usage
```

## Requirements

- Python 3.8+
- No external runtime dependencies

## Development

```bash
# Format code
make format

# Run linter
make lint

# Run type checker
make type-check

# Run tests
make test

# Clean build artifacts
make clean
```

## License

MIT License - See individual module files for details.
