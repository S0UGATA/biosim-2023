# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
import logging
import random

from biosim.model.fauna import Herbivore, Carnivore
from biosim.model.geography import Highland, Lowland, Water, Desert, Geography


class UnitArea:
    """
    Class that defines the building blocks of the island.
    """

    def __init__(self,
                 loc: tuple,
                 geo: str,
                 herbs: list[Herbivore] = None,
                 carns: list[Carnivore] = None):
        """
        Initializes an UnitArea cell.

        Parameters
        ----------
        loc: tuple
            Coordinates of the cell. Starts from 1,1 at the top left.
        geo: str
            Character indicating the type of cell. Can be W, D, L, H
        herbs: list
            List of Herbivores in the cell.
        carns: list
            List of Carnivores in the cell.
        """
        self._is_animals_allowed = True
        self._geo = self._find_geo(geo)
        self._loc = loc
        self._herbs = herbs if herbs is not None else []
        self._carns = carns if carns is not None else []

    def __str__(self):
        return f"{str(self._geo)}-H{len(self._herbs)}-C{len(self._carns)}"

    @property
    def herbs(self):
        return self._herbs

    @property
    def geo(self):
        return self._geo

    def add_herb(self, herbivore: Herbivore):
        """
        Adding a Herbivore to the list of Herbivores.

        Parameters
        ----------
        herbivore
            A single herbivore
        """
        if not self._is_animals_allowed:
            raise ValueError(f"No animals allowed in {self._geo}")
        self._herbs.append(herbivore)

    def add_herbs(self, herbivores: [Herbivore]):
        """
        Adding a list of Herbivores to the existing list.

        Parameters
        ----------
        herbivores
        """
        if not self._is_animals_allowed:
            raise ValueError(f"No animals allowed in {self._geo}")
        self._herbs.extend(herbivores)

    def add_carn(self, carnivore):
        """
        Adding a Carnivore to the list of Carnivores,

        Parameters
        ----------
        carnivore
            A single carnivore
        """
        if not self._is_animals_allowed:
            raise ValueError(f"No animals allowed in {self._geo}")
        self._carns.append(carnivore)

    def add_carns(self, carnivores: [Carnivore]):
        """
        Adding a list of Carnivores to the esiting list.

        Parameters
        ----------
        carnivores
            List of Carnivores
        """
        if not self._is_animals_allowed:
            raise ValueError(f"No animals allowed in {self._geo}")
        self._carns.extend(carnivores)

    def make_babies(self):
        """
        Create new animals as a part of the annual cycle.
        Uses the method ..py:func::`UnitArea.UnitArea.procreate` to verify necessary conditions that
        must be met to produce new offspring.
        The offspring is added to a list containing the newborns from the current cycle, which is
        then added back to the list of animals of that species at the end.
        """
        logging.debug("\tBabies:")
        no_herbs = len(self.herbs)
        babies = []
        logging.debug(f"\tno_herbs_start:{no_herbs}")
        logging.debug(f"\tno_babies_start:{len(babies)}")
        for herb in self.herbs:
            baby = herb.procreate(no_herbs)
            if baby is not None:
                babies.append(baby)
        if babies:
            self.add_herbs(babies)
        logging.debug(f"\tno_babies_after:{len(babies)}")
        logging.debug(f"\tno_herbs_after:{len(self.herbs)}")

        babies = []
        no_carns = len(self._carns)
        logging.debug(f"\tno_carns_start:{no_carns}")
        logging.debug(f"\tno_babies_start:{len(babies)}")
        for carn in self._carns:
            baby = carn.procreate(no_carns)
            if baby is not None:
                babies.append(baby)
        if babies:
            self.add_carns(babies)
        logging.debug(f"\tno_carns_after:{no_carns}")
        logging.debug(f"\tno_babies_after:{len(babies)}")

    def eat(self):
        """
        Decides which animals get to eat. The amount of fodder is determined by the parameter f_max,
        The list of animals is shuffled randomly to ensure that the animal that gets to eat is
        chosen at random.
        As long as there is food, animals get to eat. If the value of the remaining fodder is
        equal to 0, cycle breaks and no more animals get to eat.
        """
        logging.debug("\tEat:")
        remaining_fodder = self.geo.params.f_max
        logging.debug(f"\t Start Fodder:{remaining_fodder}")
        herb_indices = list(range(len(self.herbs)))
        random.shuffle(herb_indices)
        for index in herb_indices:
            if remaining_fodder <= 0:
                break
            logging.debug(f"\t Herb:{index}")
            remaining_fodder = self.herbs[index].feed_and_gain_weight(remaining_fodder)
            logging.debug(f"\t Remaining Fodder:{remaining_fodder}")

        self._carns.sort(key=lambda carn: -carn.fitness)
        self._herbs.sort(key=lambda herb: herb.fitness)
        for carn in self._carns:
            logging.debug(f"\t {carn}")
            carn.feed_on_herbivores_and_gain_weight(self._herbs)
            logging.debug(f"\t {carn}")

    def wander_away(self, cells):
        """
        Migration of animals to neighbouring UnitAreas as step 3 in the annual cycle of the island.
        """
        # TODO migration
        pass

    def grow_old(self):
        """
        Adds one year to the age of an animal as step 4 in the annual cycle of the island.
        Uses method get_older(self) in fauna.py.
        """
        logging.debug("\tGet Old:")
        [logging.debug(f"\therb.a_before:{herb.age}") for herb in self.herbs]
        [herb.get_older() for herb in self.herbs]
        [logging.debug(f"\therb.a_after:{herb.age}") for herb in self.herbs]
        [logging.debug(f"\tcarn.a_before:{carn.age}") for carn in self._carns]
        [carn.get_older() for carn in self._carns]
        [logging.debug(f"\tcarn.a_after:{carn.age}") for carn in self._carns]

    def get_thin(self):
        """
        Decreases the weight of an animal as step 5 in the annual cycle of the island.
        Uses the method lose_weight(self) in fauna.py.
        """
        logging.debug("\tGet thin:")
        [logging.debug(f"\therb.w_before:{herb.weight}") for herb in self.herbs]
        [herb.lose_weight() for herb in self.herbs]
        [logging.debug(f"\therb.w_after:{herb.weight}") for herb in self.herbs]

        [logging.debug(f"\tcarn.w_before:{carn.weight}") for carn in self._carns]
        [carn.lose_weight() for carn in self._carns]
        [logging.debug(f"\tcarn.w_after:{carn.weight}") for carn in self._carns]

    def maybe_die(self):
        """
        Checks if an animal is likely to die or not as step 6 in the annual cycle of the island.
        Uses the method maybe_die(self) in fauna.py
        """
        logging.debug("\tDie:")
        logging.debug(f"\tcount herbs_before: {len(self._herbs)}")
        self._herbs = [herb for herb in self.herbs if not herb.maybe_die()]
        logging.debug(f"\tcount herbs_after: {len(self._herbs)}")

        logging.debug(f"\tcount carns_before: {len(self._carns)}")
        self._carns = [carn for carn in self._carns if not carn.maybe_die()]
        logging.debug(f"\tcount carns_after: {len(self._carns)}")

    def _find_geo(self, geo) -> Geography:
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
                self._is_animals_allowed = False
                return Water()
            case "D":
                return Desert()
            case _:
                raise ValueError(f"Geography {geo} is not a valid value.")
