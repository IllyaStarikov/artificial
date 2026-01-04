"""Shape packer module using evolutionary algorithms.

This module provides an evolutionary algorithm implementation for the
shape packing optimization problem: place geometric shapes on a board
to maximize empty space on the left side.

Example:
    from shape_packer import ShapePackerEA, ShapePackerConfig, parse_input_file
    from sat_solver.termination import NumberOfFitnessEvaluations

    shapes, board_dims = parse_input_file("shapes.txt")
    config = ShapePackerConfig(mu=100, lambda_=50)
    ea = ShapePackerEA(shapes, board_dims, config)

    best = ea.search([NumberOfFitnessEvaluations(10000)])
    print(f"Best fitness: {best.fitness}")
"""

from shape_packer.board import Board, Placement
from shape_packer.config import ShapePackerConfig
from shape_packer.ea import ShapePackerEA
from shape_packer.individual import Individual
from shape_packer.io import format_solution, parse_input_file, write_solution
from shape_packer.operators import (
    CrossoverOperator,
    LocalSearchMutation,
    MutationOperator,
    RandomReplaceMutation,
    UniformCrossover,
)
from shape_packer.population import Population
from shape_packer.selection import (
    FitnessProportionalSelection,
    RandomSelection,
    SelectionStrategy,
    TournamentSelection,
    TruncationSelection,
)
from shape_packer.shape import Point, Shape
from shape_packer.visualize import ShapePackerVisualizer, VisualShapePackerEA

__all__ = [
    # Core classes
    "ShapePackerEA",
    "ShapePackerConfig",
    "Individual",
    "Population",
    "Shape",
    "Point",
    "Board",
    "Placement",
    # Selection strategies
    "SelectionStrategy",
    "TournamentSelection",
    "TruncationSelection",
    "FitnessProportionalSelection",
    "RandomSelection",
    # Operators
    "CrossoverOperator",
    "MutationOperator",
    "UniformCrossover",
    "RandomReplaceMutation",
    "LocalSearchMutation",
    # I/O
    "parse_input_file",
    "write_solution",
    "format_solution",
    # Visualization
    "ShapePackerVisualizer",
    "VisualShapePackerEA",
]
