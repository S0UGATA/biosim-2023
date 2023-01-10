# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
import Parameters


class Geography:
    _f_max: Parameters.Geography.f_max

    @classmethod
    def fodder_max(cls, f_max):
        cls._f_max = f_max


class Highland(Geography):
    def __init__(self, fodder_max=None):
        if fodder_max is None:
            self.fodder_max(300)
        else:
            self.fodder_max(fodder_max)
        self._f_current = Highland._f_max


class Lowland(Geography):
    def __init__(self, fodder_max=None):
        if fodder_max is None:
            self.fodder_max(800)
        else:
            self.fodder_max(fodder_max)
        self._f_current = Lowland._f_max


class Desert(Geography):
    def __init__(self):
        self.fodder_max(0)
        self._f_current = 0


class Water(Geography):
    def __init__(self):
        self.fodder_max(0)
        self._f_current = 0
