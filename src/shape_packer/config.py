"""Configuration dataclasses for shape packer evolutionary algorithm.

This module provides type-safe configuration for the shape packing EA,
replacing the JSON-based configuration from the original implementation.

Example:
    config = ShapePackerConfig(
        mu=100,
        lambda_=50,
        mutation_rate=0.05,
    )
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ShapePackerConfig:
    """Configuration for the shape packer evolutionary algorithm.

    Attributes:
        mu: Parent population size.
        lambda_: Number of offspring per generation.
        mutation_rate: Probability of mutation (0.0 to 1.0).
        tournament_size: Size of tournament for parent selection.
        max_evaluations: Maximum fitness evaluations before termination.
        stagnation_generations: Generations without improvement to trigger
            termination.
        max_placement_attempts: Maximum random attempts to place a shape.
        seed: Random seed for reproducibility. None for random seed.
    """

    mu: int = 100
    lambda_: int = 50
    mutation_rate: float = 0.05
    tournament_size: int = 5
    max_evaluations: int = 10000
    stagnation_generations: int = 250
    max_placement_attempts: int = 255
    seed: Optional[int] = None

    def __post_init__(self) -> None:
        """Validate configuration values.

        Raises:
            ValueError: If any configuration value is invalid.
        """
        if self.mu < 1:
            raise ValueError(f"mu must be >= 1, got {self.mu}")
        if self.lambda_ < 1:
            raise ValueError(f"lambda_ must be >= 1, got {self.lambda_}")
        if not 0.0 <= self.mutation_rate <= 1.0:
            raise ValueError(
                f"mutation_rate must be in [0.0, 1.0], got {self.mutation_rate}"
            )
        if self.tournament_size < 1:
            raise ValueError(
                f"tournament_size must be >= 1, got {self.tournament_size}"
            )
        if self.max_evaluations < 1:
            raise ValueError(
                f"max_evaluations must be >= 1, got {self.max_evaluations}"
            )
        if self.stagnation_generations < 1:
            raise ValueError(
                f"stagnation_generations must be >= 1, "
                f"got {self.stagnation_generations}"
            )
        if self.max_placement_attempts < 1:
            raise ValueError(
                f"max_placement_attempts must be >= 1, "
                f"got {self.max_placement_attempts}"
            )
