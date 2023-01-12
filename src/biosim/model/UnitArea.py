# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
from biosim.model.Fauna import Herbivore, Carnivore
from biosim.model.Geography import Highland, Lowland, Water, Desert, Geography


class UnitArea:
    """
    Class that defines the map/grid of the island.
    """

    def __init__(self,
                 loc: tuple,
                 geo: str,
                 herbs: list[Herbivore] = None,
                 carns: list[Carnivore] = None):
        self._geo = UnitArea._find_geo(geo)
        self._loc = loc
        self._herbs = herbs if herbs is not None else []
        self._carns = carns if carns is not None else []

    def __str__(self):
        return f"{str(self._geo)}-H{len(self._herbs)}-C{len(self._carns)}"

    @staticmethod
    def _find_geo(geo) -> Geography:
        match geo:
            case "H":
                return Highland()
            case "L":
                return Lowland()
            case "W":
                return Water()
            case "D":
                return Desert()
            case _:
                raise ValueError(f"Geography {geo} is not a valid value.")

    def total_pop(self):
        return len(self._herbs) + len(self._carns)

    def add_herb(self, herbivore: Herbivore):
        self._herbs.append(herbivore)

    def add_herbs(self, herbivores: [Herbivore]):
        self._herbs.extend(herbivores)

    def add_carn(self, carnivore):
        self._carns.append(carnivore)

    def add_carns(self, carnivores: [Carnivore]):
        self._carns.extend(carnivores)

    @property
    def herbs(self):
        return self._herbs

    @property
    def geo(self):
        return self._geo
