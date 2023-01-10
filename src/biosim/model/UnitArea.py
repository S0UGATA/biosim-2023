# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
import Fauna
import Geography


class UnitArea:
    _loc: tuple[int, int]
    _geo: Geography
    _herbs: list[Fauna.Herbivore]
    _carns: list[Fauna.Carnivore]

    def __init__(self,
                 loc: tuple,
                 geo: str,
                 herbs: list[Fauna.Herbivore] = None,
                 carns: list[Fauna.Carnivore] = None):
        self._loc = loc
        self._geo = self.find_geo(geo)
        self._herbs = herbs
        self._carns = carns

    def find_geo(self, geo):
        match geo:
            case "H":
                self._geo = Geography.Highland()
            case "L":
                self._geo = Geography.Lowland()
            case "W":
                self._geo = Geography.Water()
            case "D":
                self._geo = Geography.Desert()
            case None:
                raise ValueError("Geography cannot be empty")
            case _:
                raise ValueError(f"Geography {geo} is not a valid value.")

    def total_pop(self):
        return len(self._herbs) + len(self._carns)
