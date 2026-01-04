"""Heuristic functions for match-3 puzzle solving."""

from __future__ import annotations

import enum
import math
import typing

import search_node as search_node_module


class HeuristicType(enum.Enum):
    """Available heuristic types."""

    SCORE_DIFFERENCE = 1
    HOMOGENOUS = 2
    SCORE_PER_NODE = 3


class Heuristic:
    """Heuristic function implementations."""

    @staticmethod
    def get_heuristic(
        heuristic_type: HeuristicType,
        max_points: typing.Optional[int] = None,
        max_swaps: typing.Optional[int] = None,
    ) -> typing.Optional[typing.Callable[
        [search_node_module.SearchNode], float
    ]]:
        """Returns a heuristic function for the given type.

        Args:
            heuristic_type: The type of heuristic.
            max_points: Target score (quota).
            max_swaps: Maximum swaps allowed.

        Returns:
            A callable that takes a node and returns a heuristic value.
        """
        if heuristic_type is HeuristicType.SCORE_DIFFERENCE:
            return lambda node: Heuristic.score_difference(
                node, max_points, max_swaps
            )
        if heuristic_type is HeuristicType.HOMOGENOUS:
            return lambda node: Heuristic.homogenous_devices(node)
        if heuristic_type is HeuristicType.SCORE_PER_NODE:
            return lambda node: Heuristic.score_per_node(node, max_points)
        return None

    @staticmethod
    def score_difference(
        node: search_node_module.SearchNode, max_points: int, max_swaps: int
    ) -> float:
        """Computes score difference ratio heuristic."""
        return (max_points - node.state.points) / (
            max_swaps - node.state.swaps + 1
        )

    @staticmethod
    def homogenous_devices(node: search_node_module.SearchNode) -> float:
        """Computes standard deviation of tile type counts.

        Lower values indicate more homogenous boards which may have
        fewer matching opportunities.
        """
        device_and_count: typing.Dict[int, int] = {}

        for row in node.state.grid:
            for element in row:
                if element not in device_and_count:
                    device_and_count[element] = 0
                device_and_count[element] += 1

        results = list(device_and_count.values())
        mean = sum(results) / len(results)
        variance = sum((xi - mean) ** 2 for xi in results) / len(results)

        return math.sqrt(variance)

    @staticmethod
    def score_per_node(
        node: search_node_module.SearchNode, max_points: int
    ) -> float:
        """Computes points-per-move efficiency heuristic."""
        if node.state.points == 0 or node.path_cost == 0:
            return math.inf

        return (max_points - node.state.points) / (
            node.state.points / node.path_cost
        )
