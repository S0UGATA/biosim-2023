# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
from biosim.model.UnitArea import UnitArea


class Rossumoya:

    def __init__(self, cells: [[UnitArea]] = None):
        self._cells = cells if cells is not None else [[UnitArea]]

    def __str__(self):
        return '\n'.join(['\t|\t'.join([str(col) for col in row]) for row in self._cells])

    @property
    def cells(self):
        return self._cells
