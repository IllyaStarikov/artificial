"""SAT (Boolean Satisfiability) problem representation.

This module provides a representation for SAT problems in CNF (Conjunctive
Normal Form) format, commonly used as a benchmark for evolutionary algorithms.

Example:
    import sat

    problem = sat.SAT("input.cnf")
    problem.randomize_variables()
    print(f"Satisfied: {problem.clauses_satisfied}/{problem.total_clauses}")
"""

from __future__ import annotations

import random
import typing


class SAT:
    """Boolean Satisfiability problem representation.

    This class reads a CNF file and provides methods to manipulate variable
    assignments and evaluate clause satisfaction.

    Attributes:
        variables: List of variable names in the SAT instance.
        total_clauses: Total number of clauses in the SAT instance.
        clauses_satisfied: Number of currently satisfied clauses.
    """

    class Clause:
        """A clause in a SAT formula (disjunction of literals).

        Attributes:
            variables: List of (variable_name, is_negated) tuples.
        """

        def __init__(self) -> None:
            """Initialize an empty Clause."""
            self.variables: typing.List[typing.Tuple[str, bool]] = []

        def add_variable(self, variable: str, negated: bool) -> None:
            """Add a variable to this clause.

            Args:
                variable: The variable name (without negation symbol).
                negated: Whether the variable is negated in this clause.
            """
            self.variables.append((variable, negated))

        def evaluate(self, definitions: typing.Dict[str, bool]) -> bool:
            """Evaluate this clause with the given variable assignments.

            A clause is satisfied if at least one literal evaluates to True.

            Args:
                definitions: Mapping of variable names to boolean values.

            Returns:
                True if the clause is satisfied, False otherwise.
            """
            result = False
            for variable, negated in self.variables:
                value = definitions[variable]
                result |= (not value) if negated else value
            return result

    def __init__(self, filename: str) -> None:
        """Create a SAT instance from a CNF file.

        Args:
            filename: Path to the CNF file to read.
        """
        self._clauses: typing.List[SAT.Clause] = []
        self._variables: typing.Dict[str, typing.Optional[bool]] = {}

        lines = self._read_in_cnf(filename)
        self._parse_clauses(lines)
        self.randomize_variables()

    def _read_in_cnf(self, filename: str) -> typing.List[str]:
        """Read a CNF file and extract clause definitions.

        Args:
            filename: Path to the CNF file.

        Returns:
            List of clause strings with comments and line endings removed.
        """
        with open(filename) as fh:
            lines = [line.replace('\n', '') for line in fh.readlines()]
            lines_without_comments = [
                line for line in lines if line and line[0] not in ['c', 'p']
            ]
            lines_without_endings = [
                line[:-2] for line in lines_without_comments
            ]
            return lines_without_endings

    def _parse_clauses(self, lines_from_cnf: typing.List[str]) -> None:
        """Parse clauses from CNF file lines.

        Args:
            lines_from_cnf: List of clause strings from the CNF file.
        """
        self._clauses = []
        self._variables = {}

        for line in lines_from_cnf:
            clause = self.Clause()
            variables = line.split(' ')

            for variable in variables:
                negated = '-' in variable
                if negated:
                    variable_name = variable.replace('-', '')
                else:
                    variable_name = variable

                self._variables[variable_name] = None
                clause.add_variable(variable_name, negated)

            self._clauses.append(clause)

    def randomize_variables(self) -> None:
        """Assign random boolean values to all variables."""
        for variable in self._variables:
            self._variables[variable] = random.choice([True, False])

    @property
    def variables(self) -> typing.List[str]:
        """Get all variable names in this SAT instance.

        Returns:
            List of variable names.
        """
        return list(self._variables.keys())

    @property
    def total_clauses(self) -> int:
        """Get the total number of clauses.

        Returns:
            Number of clauses in this SAT instance.
        """
        return len(self._clauses)

    @property
    def clauses_satisfied(self) -> int:
        """Get the number of currently satisfied clauses.

        Returns:
            Count of clauses that evaluate to True.
        """
        return sum(
            1 for clause in self._clauses
            if clause.evaluate(self._variables)
        )

    def __getitem__(self, key: str) -> bool:
        """Get the value of a variable.

        Args:
            key: The variable name.

        Returns:
            The boolean value assigned to the variable.

        Raises:
            AssertionError: If the variable does not exist.
        """
        assert key in self.variables, f"Variable '{key}' does not exist"
        return self._variables[key]

    def __setitem__(self, key: str, value: bool) -> None:
        """Set the value of a variable.

        Args:
            key: The variable name.
            value: The boolean value to assign.

        Raises:
            AssertionError: If variable doesn't exist or value isn't boolean.
        """
        assert key in self.variables, f"Variable '{key}' does not exist"
        assert isinstance(value, bool), "Value must be a boolean"
        self._variables[key] = value

    def __str__(self) -> str:
        """Get a string representation of all variable assignments.

        Returns:
            Comma-separated list of variable: value pairs.
        """
        description = [f"{var}: {self[var]}" for var in self.variables]
        return ", ".join(description)
