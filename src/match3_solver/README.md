# Match-3 Puzzle Solver

An AI solver for match-3 puzzles (similar to Candy Crush or Bejeweled) using various search algorithms.

## Overview

This module implements several search algorithms to find optimal solutions for match-3 puzzles:

- **A* Search**: Optimal pathfinding with heuristics
- **Best-First Search**: Greedy heuristic-based search
- **Breadth-First Search**: Exhaustive level-by-level exploration
- **Iterative Deepening DFS**: Memory-efficient depth exploration

## Quick Start

```python
import match3
import solver
import heuristic

# Create a game instance
game = match3.Match3Game(
    quota=100,
    swaps_allowed=10,
    device_types=3,
    column_max=8,
    row_max=8,
    pool_height=4,
    bonuses_being_used=0,
    pool=[[1, 2, 3, 1, 2, 3, 1, 2], ...],
    grid=[[1, 2, 3, 1, 2, 3, 1, 2], ...],
)

# Solve using A*
puzzle_solver = solver.Solver(game)
solution = puzzle_solver.a_star(heuristic.HeuristicType.SCORE_PER_NODE)
```

## Command Line Usage

```bash
python main.py input/puzzle0.txt
python main.py input/puzzle0.txt --solution_path output.txt
```

## Modules

| Module | Description |
|--------|-------------|
| `match3.py` | Core game mechanics and state transitions |
| `solver.py` | Search algorithm implementations |
| `heuristic.py` | Heuristic functions for informed search |
| `state.py` | Game state representation |
| `action.py` | Swap action representation |
| `direction.py` | Cardinal direction enumeration |
| `search_node.py` | Search tree node structure |
| `utils.py` | File I/O and argument parsing |
| `timer.py` | Simple stopwatch utility |
| `main.py` | CLI entry point |

## Input File Format

```
59        # quota (target score)
13        # swaps_allowed
3         # device_types (tile types)
8         # column_max
8         # row_max
4         # pool_height
0         # bonuses_being_used
3 2 1 3 1 2 3 2    # pool rows (pool_height lines)
3 1 2 2 1 2 2 2    # grid rows (row_max lines)
...
```

## Heuristics

- **SCORE_DIFFERENCE**: Ratio of remaining points to remaining swaps
- **HOMOGENOUS**: Standard deviation of tile type distribution
- **SCORE_PER_NODE**: Points-per-move efficiency metric
