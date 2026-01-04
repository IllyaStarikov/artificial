"""Match-3 puzzle solver entry point."""

from __future__ import annotations

import utils
import solver
import timer as timer_module
import heuristic


def main() -> None:
    """Run the match-3 solver."""
    puzzle_timer = timer_module.Timer()

    filename, output_path = utils.parse_arguments()
    game_params = utils.parse_game_parameters(
        utils.get_file_contents(filename)
    )
    game = utils.create_game_from_params(game_params)

    puzzle_solver = solver.Solver(game)

    puzzle_timer.start()
    solution = puzzle_solver.a_star(heuristic.HeuristicType.SCORE_PER_NODE)
    puzzle_timer.stop()

    print()

    if solution is None:
        print("No Solution Found")
    else:
        utils.output_solution(
            output_path,
            filename,
            puzzle_timer.elapsed_seconds,
            solution,
            game,
        )


if __name__ == "__main__":
    main()
