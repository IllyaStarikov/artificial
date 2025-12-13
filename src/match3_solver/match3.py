"""Match-3 puzzle game logic.

Core game mechanics for a match-3 puzzle solver including grid manipulation,
match detection, and state transitions.
"""

from __future__ import annotations

import copy
import typing

import action as action_module
import direction as direction_module
import state as state_module


class Match3Game:
    """A match-3 puzzle game instance."""

    @property
    def initial_state(self) -> state_module.State:
        """Returns the initial game state."""
        return state_module.State(
            self.grid, self.pool, 0, self.swaps_allowed, 0, self.device_types
        )

    def __init__(
        self,
        quota: int,
        swaps_allowed: int,
        device_types: int,
        column_max: int,
        row_max: int,
        pool_height: int,
        bonuses_being_used: int,
        pool: typing.List[typing.List[int]],
        grid: typing.List[typing.List[int]],
    ) -> None:
        """Initialize game configuration.

        Args:
            quota: Target score to reach.
            swaps_allowed: Maximum number of swaps permitted.
            device_types: Number of distinct tile types.
            column_max: Grid width.
            row_max: Grid height.
            pool_height: Height of the tile pool above grid.
            bonuses_being_used: Number of bonus types in play.
            pool: 2D list of tiles waiting to drop into grid.
            grid: 2D list representing the game board.
        """
        self.quota = quota
        self.swaps_allowed = swaps_allowed
        self.device_types = device_types
        self.column_max = column_max
        self.row_max = row_max
        self.pool_height = pool_height
        self.bonuses_being_used = bonuses_being_used
        self.pool = pool
        self.grid = grid

    @staticmethod
    def grid_size(
        grid: typing.List[typing.List[int]],
    ) -> typing.Tuple[int, int]:
        """Returns (row_max, column_max) for the grid.

        Args:
            grid: The game grid.

        Returns:
            Tuple of (row count, column count).

        Raises:
            ValueError: If grid dimensions are less than 3x3.
        """
        row_max = len(grid)
        if row_max <= 2:
            raise ValueError(f"Grid row count must be > 2, got {row_max}")

        column_max = len(grid[0])
        if column_max <= 2:
            raise ValueError(f"Grid column count must be > 2, got {column_max}")

        return (row_max, column_max)

    @staticmethod
    def pool_size(
        pool: typing.List[typing.List[int]],
    ) -> typing.Tuple[int, int]:
        """Returns (row_max, column_max) for the pool.

        Args:
            pool: The tile pool.

        Returns:
            Tuple of (row count, column count).

        Raises:
            ValueError: If pool dimensions are invalid.
        """
        row_max = len(pool)
        if row_max <= 0:
            raise ValueError(f"Pool row count must be > 0, got {row_max}")

        column_max = len(pool[0])
        if column_max <= 2:
            raise ValueError(f"Pool column count must be > 2, got {column_max}")

        return (row_max, column_max)

    @staticmethod
    def goal_test(state: state_module.State, quota: int) -> bool:
        """Checks if the state meets the goal.

        Args:
            state: Current game state.
            quota: Target score.

        Returns:
            True if points >= quota.
        """
        return state.points >= quota

    @staticmethod
    def actions(
        state: state_module.State,
    ) -> typing.Union[
        typing.List[action_module.Action],
        typing.Generator[action_module.Action, None, None],
    ]:
        """Generates all valid actions that produce a match.

        Args:
            state: Current game state.

        Returns:
            Generator of valid Action objects, or empty list if no swaps left.
        """
        row_max, column_max = Match3Game.grid_size(state.grid)

        if state.swaps >= state.max_swaps:
            return []

        return (
            action_module.Action((row, column), direction)
            for row in range(0, row_max)
            for column in range(0, column_max)
            for direction in [
                direction_module.Direction.UP,
                direction_module.Direction.LEFT,
            ]
            if Match3Game.swap_is_valid(state.grid, (row, column), direction)
        )

    @staticmethod
    def result(
        state: state_module.State, action: action_module.Action
    ) -> state_module.State:
        """Applies an action and returns the resulting state.

        Performs the swap, then reduces the grid until no matches remain.

        Args:
            state: Current game state.
            action: The swap action to perform.

        Returns:
            New state after applying the action.
        """
        new_grid = copy.deepcopy(state.grid)
        new_pool = copy.deepcopy(state.pool)
        points = state.points

        Match3Game.swap(new_grid, action.row_column_pair, action.direction)

        while Match3Game.match_exists(new_grid):
            matches = Match3Game.find_all_points_of_matches(new_grid)
            points += len(matches)
            Match3Game.reduce(new_grid, new_pool, state.number_of_device_types)

        return state_module.State(
            new_grid,
            new_pool,
            state.swaps + 1,
            state.max_swaps,
            points,
            state.number_of_device_types,
        )

    @staticmethod
    def path_cost(
        state: state_module.State, action: action_module.Action
    ) -> int:
        """Returns the cost of applying an action.

        Args:
            state: Current game state.
            action: The action to cost.

        Returns:
            Cost value (always 1).
        """
        del state, action  # Unused
        return 1

    @staticmethod
    def swap(
        grid: typing.List[typing.List[int]],
        row_column_pair: typing.Tuple[int, int],
        direction: direction_module.Direction,
    ) -> None:
        """Swaps two adjacent tiles in the grid.

        Args:
            grid: The game grid (mutated in place).
            row_column_pair: (row, column) of the tile to swap.
            direction: Direction to swap toward.

        Raises:
            ValueError: If swap would go out of bounds.
        """
        as_unit_vector = direction.unit_vector

        old_row, old_column = row_column_pair
        new_row = old_row + as_unit_vector[0]
        new_column = old_column + as_unit_vector[1]

        row_max, column_max = Match3Game.grid_size(grid)

        if not (0 <= new_row < row_max and 0 <= old_row < row_max):
            raise ValueError(
                f"Row indices out of bounds: old={old_row}, new={new_row}, "
                f"max={row_max}"
            )
        if not (0 <= new_column < column_max and 0 <= old_column < column_max):
            raise ValueError(
                f"Column indices out of bounds: old={old_column}, "
                f"new={new_column}, max={column_max}"
            )

        grid[old_row][old_column], grid[new_row][new_column] = (
            grid[new_row][new_column],
            grid[old_row][old_column],
        )

    @staticmethod
    def reduce(
        grid: typing.List[typing.List[int]],
        pool: typing.List[typing.List[int]],
        number_of_device_types: int,
    ) -> None:
        """Removes matches and drops new tiles from the pool.

        Args:
            grid: The game grid (mutated in place).
            pool: The tile pool (mutated in place).
            number_of_device_types: Total tile type count.
        """

        def pool_fill_function(
            column: int,
            column_device_type: int,
            device_replace_count: int,
            num_types: int,
        ) -> int:
            return (
                column_device_type + column + device_replace_count + num_types
            ) % num_types + 1

        row_columns_of_matches = sorted(
            list(Match3Game.find_all_points_of_matches(grid))
        )
        pool_row_max, _ = Match3Game.pool_size(pool)
        device_replace_count = 0

        for row, column in row_columns_of_matches:
            device_replace_count += 1
            new_pool_device = pool_fill_function(
                column,
                pool[0][column],
                device_replace_count,
                number_of_device_types,
            )

            if row > 0:
                Match3Game._percolate_down(grid, column, row + 1)

            grid[0][column] = pool[-1][column]

            Match3Game._percolate_down(pool, column, pool_row_max)
            pool[0][column] = new_pool_device

    @staticmethod
    def _percolate_down(
        pool_or_grid: typing.List[typing.List[int]],
        column_to_percolate: int,
        row_max_to_percolate: int,
    ) -> None:
        """Shifts tiles down in a column.

        Args:
            pool_or_grid: Grid or pool to modify.
            column_to_percolate: Column index.
            row_max_to_percolate: Number of rows to shift.
        """
        sorted_rows = sorted(range(row_max_to_percolate), reverse=True)

        for i in range(len(sorted_rows) - 1):
            column = column_to_percolate
            old_row = sorted_rows[i]
            new_row = sorted_rows[i + 1]

            pool_or_grid[old_row][column], pool_or_grid[new_row][column] = (
                pool_or_grid[new_row][column],
                pool_or_grid[old_row][column],
            )

    @staticmethod
    def swap_is_valid(
        grid: typing.List[typing.List[int]],
        row_column_pair: typing.Tuple[int, int],
        direction: direction_module.Direction,
    ) -> bool:
        """Checks if a swap would produce a match.

        Args:
            grid: The game grid.
            row_column_pair: (row, column) of the tile.
            direction: Direction to swap.

        Returns:
            True if the swap produces at least one match.
        """
        row, column = row_column_pair
        row_unit_vector, column_unit_vector = direction.unit_vector
        row_max, column_max = Match3Game.grid_size(grid)

        if not (0 <= row + row_unit_vector < row_max):
            return False
        if not (0 <= column + column_unit_vector < column_max):
            return False

        Match3Game.swap(grid, row_column_pair, direction)
        is_valid = Match3Game.match_exists(grid)
        Match3Game.swap(grid, row_column_pair, direction)

        return is_valid

    @staticmethod
    def match_exists(grid: typing.List[typing.List[int]]) -> bool:
        """Checks if any match of 3+ exists in the grid.

        Args:
            grid: The game grid.

        Returns:
            True if a match exists.
        """
        row_max, column_max = Match3Game.grid_size(grid)

        # Check horizontal matches
        for row in range(0, row_max):
            last_two = (grid[row][0], grid[row][1])
            for column in range(2, column_max):
                current_element = grid[row][column]
                if last_two[0] == last_two[1] == current_element:
                    return True
                last_two = (last_two[1], current_element)

        # Check vertical matches
        for column in range(0, column_max):
            last_two = (grid[0][column], grid[1][column])
            for row in range(2, row_max):
                current_element = grid[row][column]
                if last_two[0] == last_two[1] == current_element:
                    return True
                last_two = (last_two[1], current_element)

        return False

    @staticmethod
    def find_all_points_of_matches(
        grid: typing.List[typing.List[int]],
    ) -> typing.Set[typing.Tuple[int, int]]:
        """Finds all grid positions that are part of a match.

        Args:
            grid: The game grid.

        Returns:
            Set of (row, column) tuples in matches.
        """
        return Match3Game._find_all_horizontal_matches(
            grid
        ) | Match3Game._find_all_vertical_matches(grid)

    @staticmethod
    def _find_all_horizontal_matches(
        grid: typing.List[typing.List[int]],
    ) -> typing.Set[typing.Tuple[int, int]]:
        """Finds all positions in horizontal matches."""
        intersecting_points: typing.Set[typing.Tuple[int, int]] = set()
        row_max, column_max = Match3Game.grid_size(grid)

        for row in range(0, row_max):
            last_two = (grid[row][0], grid[row][1])
            for column in range(2, column_max):
                current_element = grid[row][column]
                if last_two[0] == last_two[1] == current_element:
                    points = [(row, column - i) for i in range(3)]
                    intersecting_points = intersecting_points.union(points)
                last_two = (last_two[1], current_element)

        return intersecting_points

    @staticmethod
    def _find_all_vertical_matches(
        grid: typing.List[typing.List[int]],
    ) -> typing.Set[typing.Tuple[int, int]]:
        """Finds all positions in vertical matches."""
        intersecting_points: typing.Set[typing.Tuple[int, int]] = set()
        row_max, column_max = Match3Game.grid_size(grid)

        for column in range(0, column_max):
            last_two = (grid[0][column], grid[1][column])
            for row in range(2, row_max):
                current_element = grid[row][column]
                if last_two[0] == last_two[1] == current_element:
                    points = [(row - i, column) for i in range(3)]
                    intersecting_points = intersecting_points.union(points)
                last_two = (last_two[1], current_element)

        return intersecting_points
