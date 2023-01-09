# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
import Cell


class World:
    _cells: [[Cell]] = [[]]

    def __init__(self, cells: [[Cell]]):
        self._cells = cells
