# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
from biosim.model.Parameters import GeoParam


class Geography:
    _params: GeoParam

    @classmethod
    def initialize_fodder_max(cls, f_max):
        cls._params.f_max = f_max

    def __init__(self, fodder=None):
        if fodder is not None:
            self.initialize_fodder_max(fodder)

    def __str__(self):
        return self.__class__.__name__[0]

    @property
    def params(self):
        return self._params


class Highland(Geography):
    _params = GeoParam(300)

    def __init__(self, fodder=None):
        super().__init__(fodder)


class Lowland(Geography):
    _params = GeoParam(800)

    def __init__(self, fodder=None):
        super().__init__(fodder)


class Desert(Geography):
    _params = GeoParam(0)

    def __init__(self):
        super().__init__(0)


class Water(Geography):
    _params = GeoParam(0)

    def __init__(self):
        super().__init__(0)
