# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
from copy import copy

from biosim.ecosystem.parameters import GeoParam


class Geography:
    """
    Super class for the four different types of nature that can exist on Rossumøya

    Attributes
    ----------
    _params: GeoParam
    Contains all the specified parameters for Geograpny
    """
    _default_params: GeoParam
    _params: GeoParam
    _can_animals_move_here: bool
    _can_be_border: bool
    _can_have_fodder: bool

    def __init__(self, fodder: float = 0.):
        self.initialize_fodder_max(fodder)

    def __str__(self):
        return self.__class__.__name__[0]

    @property
    def params(self):
        return self._params

    @property
    def can_animals_move_here(self):
        return self._can_animals_move_here

    @property
    def can_be_border(self):
        return self._can_be_border

    @property
    def can_have_fodder(self):
        return self._can_have_fodder

    @classmethod
    def initialize_fodder_max(cls, f_max):
        """
        Initialize the maximum amount of fodder per type of Geography.

        Parameters
        ----------
        f_max: float

        """
        if f_max is None or f_max < 0.0:
            raise ValueError("Fodder cannot be negative.")
        if not cls._can_have_fodder and f_max > 0:
            raise ValueError("Can not add fodder here.")
        cls._params.f_max = f_max


class Highland(Geography):
    """
    Child class which extends the super class Geography, type Highland

    Attributes
    ----------
    _params = GeoParam(300)
    Set parameter for the default amount of fodder in Highland: amount = 300
    """
    _default_params = GeoParam(300)
    _params = copy(_default_params)
    _can_animals_move_here = True
    _can_be_border = False
    _can_have_fodder = True

    def __init__(self, fodder=_default_params.f_max):
        super().__init__(fodder)


class Lowland(Geography):
    """
    Child class which extends the super class Geography, type Lowland

    Attributes
    ----------
    _params = GeoParam(800)
    Set parameter for the default amount of fodder in Lowland: amount = 800
    """
    _default_params = GeoParam(800)
    _params = copy(_default_params)
    _can_animals_move_here = True
    _can_be_border = False
    _can_have_fodder = True

    def __init__(self, fodder=_default_params.f_max):
        super().__init__(fodder)


class Desert(Geography):
    """
    Child class which extends the super class Geography, type Desert

    Attributes
    ----------
    Set parameter for the default value of fodder in Desert: amount = 0
    """
    _default_params = GeoParam(0)
    _params = GeoParam(0)
    _can_animals_move_here = True
    _can_be_border = False
    _can_have_fodder = False

    def __init__(self):
        super().__init__(0)


class Water(Geography):
    """
     Child class which extends the super class Geography, type Water

     Attributes
     ----------
     _params = GeoParam(0)
     Set parameter for the default value of fodder in Water: amount = 0
    """
    _default_params = GeoParam(0)
    _params = GeoParam(0)
    _can_animals_move_here = False
    _can_be_border = True
    _can_have_fodder = False

    def __init__(self):
        super().__init__(fodder=0)
