"""Node representation for local search algorithms.

This module provides the Node class representing a point in 2D search space.

Example:
    node = Node(5, 10)
    print(f"Position: ({node.x}, {node.y})")
"""

from __future__ import annotations


class Node:
    """A point in 2D search space.

    Represents a position (x, y) that can be evaluated by an objective function.

    Attributes:
        x: The x-coordinate.
        y: The y-coordinate.
    """

    def __init__(self, x: int, y: int) -> None:
        """Create a Node at the specified position.

        Args:
            x: The x-coordinate.
            y: The y-coordinate.
        """
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        """Get a string representation of this node.

        Returns:
            String in format "Node(x, y)".
        """
        return f"Node({self.x}, {self.y})"

    def __eq__(self, other: object) -> bool:
        """Check equality with another node.

        Args:
            other: The object to compare with.

        Returns:
            True if both coordinates match, False otherwise.
        """
        if not isinstance(other, Node):
            return NotImplemented
        return self.x == other.x and self.y == other.y
