"""Match-3 puzzle solver module.

An AI solver for match-3 style puzzles using various search algorithms
including A*, Best-First Search, BFS, and Iterative Deepening DFS.

Example:
    import match3
    import solver
    import heuristic

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

    puzzle_solver = solver.Solver(game)
    solution = puzzle_solver.a_star(heuristic.HeuristicType.SCORE_PER_NODE)
"""

__all__ = [
    "Match3Game",
    "Solver",
    "State",
    "Action",
    "Direction",
    "SearchNode",
    "Heuristic",
    "HeuristicType",
]
