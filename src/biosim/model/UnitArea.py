# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
from biosim.model.Fauna import Herbivore, Carnivore
from biosim.model.Geography import Geography, Highland, Lowland, Water, Desert


class UnitArea:
    _loc: tuple[int, int]
    _geo: Geography
    _herbs: list[Herbivore]
    _carns: list[Carnivore]

    def __init__(self,
                 loc: tuple,
                 geo: str,
                 herbs: list[Herbivore] = None,
                 carns: list[Carnivore] = None):
        self._loc = loc
        self.find_geo(geo)
        self._herbs = herbs if herbs is not None else []
        self._carns = carns if carns is not None else []

    def find_geo(self, geo):
        match geo:
            case "H":
                self._geo = Highland()
            case "L":
                self._geo = Lowland()
            case "W":
                self._geo = Water()
            case "D":
                self._geo = Desert()
            case None:
                raise ValueError("Geography cannot be empty")
            case _:
                raise ValueError(f"Geography {geo} is not a valid value.")

    def total_pop(self):
        return len(self._herbs) + len(self._carns)
