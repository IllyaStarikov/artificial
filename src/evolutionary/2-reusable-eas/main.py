#!/usr/local/bin/python3
#
# main.py
# src
#
# Created by Illya Starikov on 10/12/18.
# Copyright 2018. Illya Starikov. MIT License.
#

from ea import EA
from individual import Individual


def main():
    μ = 15
    λ = 100

    Individual.cnf_filename = "input.cnf"

    ea = EA(μ, λ)
    ea.search()


if __name__ == "__main__":
    main()