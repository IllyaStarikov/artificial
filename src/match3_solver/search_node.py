"""Search node for graph-based puzzle solving."""

from __future__ import annotations

import typing

import action as action_module
import state as state_module


class SearchNode:
    """A node in the search tree."""

    def __init__(
        self,
        state: state_module.State,
        action: typing.Optional[action_module.Action],
        parent: typing.Optional["SearchNode"],
        path_cost: int,
    ) -> None:
        """Initialize a search node.

        Args:
            state: The game state at this node.
            action: The action that led to this state.
            parent: The parent node in the search tree.
            path_cost: Cumulative cost to reach this node.
        """
        self.state = state
        self.action = action
        self.parent = parent
        self.path_cost = path_cost

    def __eq__(self, other: object) -> bool:
        """Check node equality."""
        if not isinstance(other, SearchNode):
            return NotImplemented
        return self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        """Hash based on state and path cost."""
        return hash(f"{self.state}-{self.path_cost}")
