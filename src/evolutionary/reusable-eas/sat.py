#!/usr/local/bin/python3
#
# sat.py
# reusable-eas
#
# Created by Illya Starikov on 10/17/18.
# Copyright 2018. Illya Starikov. MIT License.
#

from random import choice


class SAT:
    class Clause:
        def __init__(self):
            """Create a Clause object."""
            self.variables = []

        def add_variable(self, variable, negated):
            """Add a variable to a clause.

            Args:
                variable (str): The variable name (without the negation `-` symbol).
                negated (bool): Is the variable negated?
            """
            self.variables += [(variable, negated)]

        def evaluate(self, definitions):
            """Evaluate all the variables with predefined definitions.

            Args:
                definitions (dict<str, bool>): The definitions of all the variables, where the
                    variable is the key and its value is the value.
            """
            result = False

            for variable, negated in self.variables:
                result |= not definitions[variable] if negated else definitions[variable]

            return result

    def __init__(self, filename):
        """Create a SAT object.

        Args:
            filename (string): The CNF file to get clauses from.
        """
        self.__clauses = None
        self.__variables = None

        lines = self.__read_in_cnf(filename)
        self.__parse_clauses(lines)
        self.randomize_variables()

    def __read_in_cnf(self, filename):
        """Read in a CNF file and return all the clauses (stripped of line endings and
        comments).

        Args:
            filename (string): The CNF file to get clauses from.

        Returns:
            list<str>: The clauses without any '0' line endings and comments.
        """
        with open(filename) as fh:
            lines = [line.replace('\n', '') for line in fh.readlines()]
            lines_without_comments = [line for line in lines if line[0] not in ['c', 'p']]
            lines_without_comments_and_0_ending = [line[:-2] for line in lines_without_comments]

            return lines_without_comments_and_0_ending

        raise Exception('File not found')

    def __parse_clauses(self, lines_from_cnf):
        """Parse clauses from the lines in a CNF file (with the comments and line endings stripped).

        Args:
             lines_from_cnf (list<str>): The clauses without any '0' line endings and comments.

        Note:
            This modifies self.__clauses by adding all the keys to variables in the CNF file (with
            values of None) and self.__variables by adding all the variables to the list.
        """
        self.__clauses = []
        self.__variables = {}

        for line in lines_from_cnf:
            clause = self.Clause()
            variables = line.split(' ')

            for variable in variables:
                negated = '-' in variable
                variable_name = variable.replace('-', '') if negated else variable

                self.__variables[variable_name] = None
                clause.add_variable(variable_name, negated)

            self.__clauses += [clause]

    def randomize_variables(self):
        """Assign all the variables to a random value."""
        for variable in self.__variables.keys():
            self.__variables[variable] = choice([True, False])

    @property
    def variables(self):
        """Get all the variables in the SAT instance as a list.

        Returns:
            list<str>: All the variables in SAT instance.
        """
        return list(self.__variables.keys())

    @property
    def total_clauses(self):
        """Get the total number of clauses in the SAT instance.

        Returns:
            int: The total number of clauses in the SAT instance.
        """
        return len(self.__clauses)

    @property
    def clauses_satisfied(self):
        """Get the total number of clauses satisfied (all the variables are assigned a value
        such that a clause is true) in the SAT instance.

        Returns:
            int: The total number of clauses satisfied in the SAT instance.
        """
        total_satisfied = 0

        for clause in self.__clauses:
            satisfied = clause.evaluate(self.__variables)

            if satisfied:
                total_satisfied += 1

        return total_satisfied

    def __getitem__(self, key):
        """A getter to the value of a variable.

        Returns:
            bool: The value that the variable holds.
        """
        assert key in self.variables, "Getting variable that does not exist"
        return self.__variables[key]

    def __setitem__(self, key, value):
        """A setter to the value of a variable. Modifies the value of the variable to True or False.

        Note:
            The value can only be True or False.
        """
        assert key in self.variables, "Getting variable that does not exist"
        assert value in [True, False], "Setting variable to not a boolean"

        self.__variables[key] = value

    def __str__(self):
        """Get a string description of all the variables and their associated values."""
        description = ["{}: {}".format(variable, self[variable]) for variable in self.variables]
        return ", ".join(description)
