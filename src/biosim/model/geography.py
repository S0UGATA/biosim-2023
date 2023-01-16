# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
from biosim.model.parameters import GeoParam


class Geography:
    """
    Super class for the four different types of nature that can exist on Rossumøya

    Attributes
    ----------
    _params: GeoParam
    Contains all the specified parameters for Geograpny
    """

    _params: GeoParam

    def __init__(self,
                 fodder: int = None,
                 can_animals_move_here: bool = True,
                 can_be_border: bool = False):
        if fodder is not None:
            self.initialize_fodder_max(fodder)
        self._can_animals_move_here = can_animals_move_here
        self._can_be_border = can_be_border

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

    @classmethod
    def initialize_fodder_max(cls, f_max):
        """
        Initialize the maximum amount of fodder per type of Geography.

        Parameters
        ----------
        f_max: int

        """
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
    _params = _default_params

    def __init__(self, fodder=None):
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
    _params = _default_params

    def __init__(self, fodder=None):
        super().__init__(fodder)


class Desert(Geography):
    """
    Child class which extends the super class Geography, type Desert

    Attributes
    ----------
    Set parameter for the default value of fodder in Desert: amount = 0
    """
    _params = GeoParam(0)

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
    _params = GeoParam(0)

    def __init__(self):
        super().__init__(fodder=0,
                         can_animals_move_here=False,
                         can_be_border=True)
