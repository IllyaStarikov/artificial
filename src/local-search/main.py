#!/usr/local/bin/python3
#
# main.py
# src
#
# Created by Illya Starikov on 10/13/18.
# Copyright 2018. Illya Starikov. MIT License.
#

from function import Function
from hill_climber import HillClimber
from stochastic_hill_climber import StochasticHillClimber
from stochastic_hill_climber_with_restarts import StochasticHillClimberWithRestarts

from math import sin, cos


def main():
    function = Function(lambda x, y: -x**2 - y**2, (-100, 100), (-100, 100))

    hill_climber = HillClimber(function)
    hill_climber.climb()
    print("-"*100)

    function = Function(lambda x, y: (-x**2 - y**2) + (x * y * cos(x) * sin(y)), (-100, 100), (-100, 100))

    hill_climber = StochasticHillClimber(function)
    hill_climber.climb()
    print("-"*100)

    function = Function(lambda x, y: (-x**2 - y**2) + (x * y * cos(x) * sin(y)), (-100, 100), (-100, 100))

    hill_climber = StochasticHillClimberWithRestarts(function)
    hill_climber.climb(10)
    print("-"*100)


if __name__ == "__main__":
    main()
