# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
import Parameters


class Geography:
    _fodder_max: Parameters.Geography.f_max
    _fodder_current: int


class Highland(Geography):
    def __init__(self, fodder_max=None):
        self._fodder_max = 300 if fodder_max is None else fodder_max
        self._fodder_current = self._fodder_max


class Lowland(Geography):
    def __init__(self, fodder_max=None):
        self._fodder_max = 800 if fodder_max is None else fodder_max
        self._fodder_current = self._fodder_max


class Desert(Geography):
    def __init__(self, fodder_max=None):
        self._fodder_max = 0 if fodder_max is None else fodder_max
        self._fodder_current = self._fodder_max


class Water(Geography):
    def __init__(self, fodder_max=None):
        self._fodder_max = -1 if fodder_max is None else fodder_max
        self._fodder_current = self._fodder_max  # TODO: think of what happens when user inputs a negative value.
