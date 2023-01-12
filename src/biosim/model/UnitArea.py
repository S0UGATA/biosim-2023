# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
import random

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

    def make_babies(self):
        no_herbs = len(self.herbs)
        babies = []
        for herb in self.herbs:
            baby = herb.procreate(no_herbs)
            if baby is not None:
                babies.append(baby)
        if babies:
            self.add_herbs(babies)

    def eat(self):
        remaining_fodder = self.geo.params.f_max
        herb_indices = [*range(len(self.herbs))]
        random.shuffle(herb_indices)
        for index in herb_indices:
            if remaining_fodder <= 0:
                break
            remaining_fodder = self.herbs[index].feed_and_gain_weight(remaining_fodder)

    def grow_old(self):
        [herb.get_older() for herb in self.herbs]

    def get_thin(self):
        [herb.lose_weight() for herb in self.herbs]

    def maybe_die(self):
        self._herbs = [herb for herb in self.herbs if not herb.maybe_die()]

    def wander_away(self, cells):
        # TODO migration
        pass
