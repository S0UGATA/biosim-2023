# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
import Parameters


class Geography:
    _f_max: Parameters.Geography.f_max
    _f_current: int


class Highland(Geography):
    def __init__(self, fodder_max=None):
        self._f_max = 300 if fodder_max is None else fodder_max
        self._f_current = self._f_max


class Lowland(Geography):
    def __init__(self, fodder_max=None):
        self._f_max = 800 if fodder_max is None else fodder_max
        self._f_current = self._f_max


class Desert(Geography):
    def __init__(self):
        self._f_max = 0
        self._f_current = 0


class Water(Geography):
    def __init__(self):
        self._f_max = 0
        self._f_current = 0
