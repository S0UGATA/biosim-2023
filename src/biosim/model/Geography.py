# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
from biosim.model.Parameters import GeoParam


class Geography:
    """
    Super class for the four different types of nature that can exist on Rossumøya

    Attributes
    ----------
     _params: GeoParam
    Contains all the specified parameters for Geograpny, imported from the module
    Parameters.py, where the type is GeoParam.
    """
    _params: GeoParam

    @classmethod
    def initialize_fodder_max(cls, f_max):
        """
        Initialize the maximum amount of fodder, and define parameter f_max.

        Parameters
        ----------
        f_max: int

        """
        cls._params.f_max = f_max

    def __init__(self, fodder=None):
        if fodder is not None:
            self.initialize_fodder_max(fodder)

    def __str__(self):
        return self.__class__.__name__[0]

    @property
    def params(self):
        """ Defines the property of the parameters for instances of the Geography class."""
        return self._params


class Highland(Geography):
    """
    Child class which extends the super class Geography, type Highland

    Attributes
    ----------
    _params = GeoParam(300)
    Set parameter for the default amount of fodder in Highland: amount = 300
    """
    _params = GeoParam(300)

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
    _params = GeoParam(800)

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
        super().__init__(0)
