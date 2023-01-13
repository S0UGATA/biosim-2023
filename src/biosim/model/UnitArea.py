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
        """
        Initializing and creating the map of the island by defining each UnitArea with the right
        geo value: H for Highland, L for Lowland, W for water, and D for Desert.

        Parameters
        ----------
        geo
        Specifying the type of the UnitArea.

        """
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
        """
        Returning the total population of animals, including both Herbivores and Carnivores
        """
        return len(self._herbs) + len(self._carns)

    def add_herb(self, herbivore: Herbivore):
        """
        Adding a Herbivore to the list of Herbivores, used in the initialization of the island
        and first population of the island (see populate_island(self, population: [{}]) in file
        Rossumoya.py)

        Parameters
        ----------
        herbivore
        A single herbivore
        """
        self._herbs.append(herbivore)

    def add_herbs(self, herbivores: [Herbivore]):
        """
        Adding newborn Herbivores to the list of Herbivores
        Parameters
        ----------
        herbivores

        Returns
        -------

        """
        self._herbs.extend(herbivores)

    def add_carn(self, carnivore):
        """
        Adding a Carnivore to the list of Carnivores, used in the initialization of the island
        and first population of the island (see populate_island(self, population: [{}]) in file
        Rossumoya.py)

        Parameters
        ----------
        carnivore
        """
        self._carns.append(carnivore)

    def add_carns(self, carnivores: [Carnivore]):
        """
        Adding newborn Carnivores to the list of Carnivores.

        Parameters
        ----------
        carnivores
        List of newborn Carnivores
        """
        self._carns.extend(carnivores)

    @property
    def herbs(self):
        """ Returns the property attribute for the list of herbs."""
        return self._herbs

    @property
    def geo(self):
        """ Returns the property attribute for the geo type."""
        return self._geo

    def make_babies(self):
        """
        Create new Herbivores as a part of the annual cycle. Uses the method
        procreate(self, number_of_animals: int) to verify necessary conditions that must be met
        to produce new offspring. The offspring is added to a list containing the newborn from
        the current cycle. This list is used in the method add_herbs(self, herbivores: [Herbivore])
        at the end of the current cycle.
        """
        no_herbs = len(self.herbs)
        babies = []
        for herb in self.herbs:
            baby = herb.procreate(no_herbs)
            if baby is not None:
                babies.append(baby)
        if babies:
            self.add_herbs(babies)

    def eat(self):
        """
        Decides which animals get to eat. The amount of fodder is set by the parameter f_max, value
        is initialized in the creation of the island and start of simulation. The list of animals
        is randomly shuffled to ensure that the animal that gets to eat is chosen by random.
        As long as there is food, animals get to eat. If the value of the remaining fodder is
        equal to 0, cycle breaks and no more animals get to eat.

        """
        remaining_fodder = self.geo.params.f_max
        herb_indices = [*range(len(self.herbs))]
        random.shuffle(herb_indices)
        for index in herb_indices:
            if remaining_fodder <= 0:
                break
            remaining_fodder = self.herbs[index].feed_and_gain_weight(remaining_fodder)

    def wander_away(self, cells):
        """
        Migration of animals to neighbouring UnitAreas as step 3 in the annual cycle of the island.
        """
        # TODO migration
        pass

    def grow_old(self):
        """
        Adds one year to the current year of an animal as step 4 in the annual cycle of the island.
        Uses method get_older(self) in Fauna.py.
        """
        [herb.get_older() for herb in self.herbs]

    def get_thin(self):
        """
        Decreases the weight of an animal as step 5 in the annual cycle of the island.
        Uses the method lose_weight(self) in Fauna.py.
        """
        [herb.lose_weight() for herb in self.herbs]

    def maybe_die(self):
        """
        Checks if an animal is likely to die or not as step 6 in the annual cycle of the island.
        Uses the method maybe_die(self) in Fauna.py
        """
        self._herbs = [herb for herb in self.herbs if not herb.maybe_die()]
