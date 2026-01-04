"""Match-3 puzzle solver using various search algorithms.

Implements A*, Best-First Search, BFS, and Iterative Deepening DFS
to find optimal solutions for match-3 puzzles.
"""

from __future__ import annotations

import collections
import queue
import random
import typing

import action as action_module
import heuristic as heuristic_module
import match3
import search_node as search_node_module
import state as state_module


class Solver:
    """AI solver for match-3 puzzles."""

    def __init__(self, game: match3.Match3Game) -> None:
        """Initialize solver with a game instance.

        Args:
            game: The Match3Game to solve.
        """
        self.game = game
        self.max_score = 0

    def _get_heuristic(
        self, heuristic_type: heuristic_module.HeuristicType
    ) -> typing.Optional[typing.Callable[
        [search_node_module.SearchNode], float
    ]]:
        """Returns a heuristic function for the given type."""
        return heuristic_module.Heuristic.get_heuristic(
            heuristic_type, self.game.quota, self.game.swaps_allowed
        )

    def a_star(
        self, heuristic_type: heuristic_module.HeuristicType
    ) -> typing.Optional[search_node_module.SearchNode]:
        """Finds a solution using A* search.

        Args:
            heuristic_type: The heuristic to use.

        Returns:
            Solution node if found, None otherwise.
        """
        g = lambda node: node.path_cost
        h = self._get_heuristic(heuristic_type)
        f = lambda node: g(node) + h(node)

        node = search_node_module.SearchNode(
            self.game.initial_state, None, None, 1
        )
        h_value = f(node)

        self.max_score = 0
        nodes_generated = 0

        if match3.Match3Game.goal_test(node.state, self.game.quota):
            return node

        frontier: queue.PriorityQueue = queue.PriorityQueue()
        explored: set = set()

        frontier.put((h_value, nodes_generated, node))
        explored.add(node)

        while not frontier.empty():
            _, _, node = frontier.get()

            for action in match3.Match3Game.actions(node.state):
                child = self._child_node(node.state, node, action)

                if child not in explored:
                    nodes_generated += 1
                    self._log_progress(child)

                    if match3.Match3Game.goal_test(
                        child.state, self.game.quota
                    ):
                        return child

                    explored.add(child)
                    frontier.put((f(child), nodes_generated, child))

        return None

    def best_first_search(
        self, heuristic_type: heuristic_module.HeuristicType
    ) -> typing.Optional[search_node_module.SearchNode]:
        """Finds a solution using greedy best-first search.

        Args:
            heuristic_type: The heuristic to use.

        Returns:
            Solution node if found, None otherwise.
        """
        node = search_node_module.SearchNode(
            self.game.initial_state, None, None, 1
        )
        h = self._get_heuristic(heuristic_type)
        h_value = h(node)

        self.max_score = 0
        nodes_generated = 0

        if match3.Match3Game.goal_test(node.state, self.game.quota):
            return node

        frontier: queue.PriorityQueue = queue.PriorityQueue()
        explored: set = set()

        frontier.put((h_value, nodes_generated, node))
        explored.add(node)

        while not frontier.empty():
            _, _, node = frontier.get()

            for action in match3.Match3Game.actions(node.state):
                child = self._child_node(node.state, node, action)

                if child not in explored:
                    nodes_generated += 1
                    self._log_progress(child)

                    if match3.Match3Game.goal_test(
                        child.state, self.game.quota
                    ):
                        return child

                    explored.add(child)
                    frontier.put((h(child), nodes_generated, child))

        return None

    def iterative_deepening_dfs(
        self,
    ) -> typing.Optional[search_node_module.SearchNode]:
        """Finds a solution using iterative deepening DFS.

        Returns:
            Solution node if found, None otherwise.
        """
        for depth in range(self.game.swaps_allowed + 1):
            result = self._depth_limited_search(depth)
            if result:
                return result
        return None

    def _depth_limited_search(
        self, depth_limit: int
    ) -> typing.Optional[search_node_module.SearchNode]:
        """Runs depth-limited DFS."""
        node = search_node_module.SearchNode(
            self.game.initial_state, None, None, 1
        )
        return self._recursive_dls(node, depth_limit)

    def _recursive_dls(
        self, node: search_node_module.SearchNode, limit: int
    ) -> typing.Optional[search_node_module.SearchNode]:
        """Recursive depth-limited search helper."""
        if match3.Match3Game.goal_test(node.state, self.game.quota):
            return node
        if limit == 0:
            return None

        children = []
        for action in match3.Match3Game.actions(node.state):
            child = self._child_node(node.state, node, action)
            children.append(child)

        random.shuffle(children)
        for child in children:
            result = self._recursive_dls(child, limit - 1)
            self._log_progress(child)
            if result:
                return result

        return None

    def breadth_first_search(
        self,
    ) -> typing.Optional[search_node_module.SearchNode]:
        """Finds a solution using breadth-first search.

        Returns:
            Solution node if found, None otherwise.
        """
        node = search_node_module.SearchNode(
            self.game.initial_state, None, None, 1
        )
        self.max_score = 0

        if match3.Match3Game.goal_test(node.state, self.game.quota):
            return node

        frontier = collections.deque([node])

        while frontier:
            node = frontier.popleft()

            for action in match3.Match3Game.actions(node.state):
                child = self._child_node(node.state, node, action)
                self._log_progress(child)

                if match3.Match3Game.goal_test(child.state, self.game.quota):
                    return child

                frontier.append(child)

        return None

    def _child_node(
        self,
        state: state_module.State,
        parent: search_node_module.SearchNode,
        action: action_module.Action,
    ) -> search_node_module.SearchNode:
        """Creates a child node from a state and action."""
        new_state = match3.Match3Game.result(state, action)
        cost = parent.path_cost + match3.Match3Game.path_cost(new_state, action)
        return search_node_module.SearchNode(new_state, action, parent, cost)

    def _log_progress(self, node: search_node_module.SearchNode) -> None:
        """Updates progress tracking."""
        self.max_score = max(self.max_score, node.state.points)
