# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
import UnitArea


class Rossumoya:
    _cells: [[UnitArea]] = [[]]

    def __init__(self, cells: [[UnitArea]] = None):
        self._cells = cells if cells is not None else [[]]
