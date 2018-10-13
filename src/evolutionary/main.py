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
from secret_message import SecretMessage


def main():
    μ = 15
    λ = 100

    message = SecretMessage("FreneticArray")
    Individual.message = message

    ea = EA(μ, λ)
    ea.search()


if __name__ == "__main__":
    main()
