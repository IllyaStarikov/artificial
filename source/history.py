#!/usr/local/bin/python3
#
# history.py
# source
#
# Created by Illya Starikov on 09/24/17.
# Copyright 2017. Illya Starikov. All rights reserved.
#


class History():
    last_averages = []
    last_best = []
    n_for_average, n_for_best = 0, 0

    def __init__(self, n_for_average, n_for_best):
        self.n_for_average = n_for_average
        self.n_for_best = n_for_best

    def add_best_and_average(self, best_, average_):
        if self.get_averages():
            self.last_averages.pop(0)

        if self.get_best():
            self.last_best.pop(0)

        self.last_averages += [average_]
        self.last_best += [best_]

    def determine_if_average_got_better(self):
        if self.get_averages() is None:
            return True

        average_ = self.get_averages()[0]
        for element in self.get_averages():
            if element > average_:
                return True

        return False

    def determine_if_best_got_better(self):
        if self.get_best() is None:
            return True

        best = self.get_best()[0]
        for element in self.get_best():
            if element > best:
                return True

        return False

    # MARK: Getters
    def get_averages(self):
        if len(self.last_averages) < self.n_for_average:
            return None

        return self.last_averages

    def get_best(self):
        if len(self.last_best) < self.n_for_best:
            return None

        return self.last_best
