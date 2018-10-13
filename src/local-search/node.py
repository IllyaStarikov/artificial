#!/usr/local/bin/python3
#
# node.py
# src
#
# Created by Illya Starikov on 10/13/18.
# Copyright 2018. Illya Starikov. MIT License.
#


class Node:
    """A node in a search space (similar to a point (x, y)."""

    def __init__(self, x, y):
        """Create a Node object.

        Args:
            x (int): The x part of (x, y).
            y (int): The y part of (x, y).

        """

        self.x = x
        self.y = y
