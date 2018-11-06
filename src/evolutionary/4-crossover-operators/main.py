#!/usr/local/bin/python3
#
# main.py
# src
#
# Created by Illya Starikov on 10/12/18.
# Copyright 2018. Illya Starikov. MIT License.
#

import datetime

from ea import EA
from individual import Individual
from termination_conditions import FitnessTarget, DateTarget, NoChangeInAverageFitness, NoChangeInBestFitness, NumberOfFitnessEvaluations, NumberOfGenerations


def main():
    μ = 15
    λ = 100

    Individual.cnf_filename = "input.cnf"

    termination_conditions = [
        FitnessTarget(100),
        DateTarget(datetime.datetime.now() + datetime.timedelta(hours=8)),
        NumberOfGenerations(10000)
    ]

    ea = EA(μ, λ)
    ea.search(termination_conditions)


if __name__ == "__main__":
    main()
