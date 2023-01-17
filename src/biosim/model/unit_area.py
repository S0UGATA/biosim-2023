# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
import logging
import random
from typing import Tuple

from biosim.model.fauna import Herbivore, Carnivore, Fauna
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
            * Validates if animals are allowed in the cell.
            * Validates if the cell can be a boundary.

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
        self._loc = loc
        self._is_animals_allowed = True
        self._geo: Geography = self._assign_geo(geo)
        self._herbs = herbs if herbs is not None else []
        self._carns = carns if carns is not None else []

    def __str__(self):
        val = f"{str(self._geo)}"
        if len(self._herbs) > 0:
            val += f".H{len(self._herbs)}"
        if len(self._carns) > 0:
            val += f".C{len(self._carns)}"
        return val

    @property
    def herbs(self):
        return self._herbs

    @property
    def carns(self):
        return self._carns

    def add_herb(self, herbivore: Herbivore):
        """
        Adding a Herbivore to the list of Herbivores.

        Parameters
        ----------
        herbivore
            A single herbivore
        """
        if herbivore is None:
            return
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
        if herbivores is None:
            return
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
        if carnivore is None:
            return
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
        if carnivores is None:
            return
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
        logging.debug("\tHerb-babies:")
        self.add_herbs(self._make_babies_of(self._herbs))

        logging.debug("\tCarn-babies:")
        self.add_carns(self._make_babies_of(self._carns))

    def eat(self):
        logging.debug("\tEat:")
        self._herbivores_eat()
        self._carnivores_eat()

    def wander_away(self, row, col, cells):
        """
        Migration of animals to neighbouring UnitAreas as step 3 in the annual cycle of the island.
        """
        to_remove = []
        for herb in self._herbs:
            move_to = self._migrate_to(herb, row, col, cells)
            if move_to is None:
                continue
            move_to.add_herb(herb)
            to_remove.append(herb)
            herb.has_moved = True
        self._herbs = [herb for herb in self._herbs if herb not in to_remove]

        to_remove = []
        for carn in self._carns:
            move_to = self._migrate_to(carn, row, col, cells)
            if move_to is None:
                continue
            move_to.add_carn(carn)
            to_remove.append(carn)
            carn.has_moved = True
        self._carns = [carn for carn in self._carns if carn not in to_remove]

    def grow_old(self):
        """
        Adds one year to the age of an animal as step 4 in the annual cycle of the island.
        Uses method get_older(self) in fauna.py.
        """
        logging.debug("\tGet Old:")
        [logging.debug(f"\therb.a_before:{herb.age}") for herb in self._herbs]
        [herb.get_older() for herb in self._herbs]
        [logging.debug(f"\therb.a_after:{herb.age}") for herb in self._herbs]

        [logging.debug(f"\tcarn.a_before:{carn.age}") for carn in self._carns]
        [carn.get_older() for carn in self._carns]
        [logging.debug(f"\tcarn.a_after:{carn.age}") for carn in self._carns]

    def get_thin(self):
        """
        Decreases the weight of an animal as step 5 in the annual cycle of the island.
        Uses the method lose_weight(self) in fauna.py.
        """
        logging.debug("\tGet thin:")
        [logging.debug(f"\therb.w_before:{herb.weight}") for herb in self._herbs]
        [herb.lose_weight() for herb in self._herbs]
        [logging.debug(f"\therb.w_after:{herb.weight}") for herb in self._herbs]

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
        self._herbs = [herb for herb in self._herbs if not herb.maybe_die()]
        logging.debug(f"\tcount herbs_after: {len(self._herbs)}")

        logging.debug(f"\tcount carns_before: {len(self._carns)}")
        self._carns = [carn for carn in self._carns if not carn.maybe_die()]
        logging.debug(f"\tcount carns_after: {len(self._carns)}")

    def can_animals_move_here(self):
        return self._geo.can_animals_move_here

    def can_be_border(self):
        return self._geo.can_be_border

    def reset_animal_move_flag(self):
        """
        Resets the movement flag for animals to False at the start of the annual cycle.
        This flag is set to True to prevent migration waves in the same year.
        """
        for herb in self.herbs:
            herb.has_moved = False
        for carn in self.carns:
            carn.has_moved = False

    def _assign_geo(self, geo) -> Geography:
        """
        Initializing and creating the map of the island by defining each UnitArea with the right
        geo value: H for Highland, L for Lowland, W for water, and D for Desert.

        Validates if the cell can be a boundary.

        Parameters
        ----------
        geo
        Specifying the type of the UnitArea.

        """
        match geo:
            case "H":
                self._raise_error_if_boundary(geo)
                return Highland()
            case "L":
                self._raise_error_if_boundary(geo)
                return Lowland()
            case "W":
                self._is_animals_allowed = False
                return Water()
            case "D":
                self._raise_error_if_boundary(geo)
                return Desert()
            case _:
                raise ValueError(f"Geography {geo} is not a valid value.")

    def _make_babies_of(self, animals):
        no_animals = len(animals)
        babies = []
        logging.debug(f"\t no_animal_start:{no_animals}")
        logging.debug(f"\t no_babies_start:{len(babies)}")
        for animal in animals:
            baby = animal.procreate(no_animals)
            if baby is not None:
                babies.append(baby)
        logging.debug(f"\t no_babies_after:{len(babies)}")
        logging.debug(f"\t no_animals_after:{len(self._herbs)}")
        return babies

    def _herbivores_eat(self):
        """
        Decides which herbs get to eat. The amount of fodder is determined by the parameter f_max,
        The list of herbs is shuffled randomly before feeding.
        As long as there is food, herbs get to eat. If the value of the remaining fodder is
        equal to 0, cycle breaks and no more herbs get to eat.
        """
        logging.debug("\tHerbs:")
        remaining_fodder = self._geo.params.f_max
        logging.debug(f"\t Start Fodder:{remaining_fodder}")
        herb_indices = list(range(len(self._herbs)))
        random.shuffle(herb_indices)
        for index in herb_indices:
            if remaining_fodder <= 0:
                break
            logging.debug(f"\t Herb:{index}")
            remaining_fodder = self._herbs[index].feed_and_gain_weight(remaining_fodder)
            logging.debug(f"\t Remaining Fodder:{remaining_fodder}")

    def _carnivores_eat(self):
        """
        Carnivores try to kill + eat as per their decreasing fitness, on herbivores as per their
        increasing fitness.
        """
        logging.debug("\tCarns:")
        self._carns.sort(key=lambda carn: -carn.fitness)
        self._herbs.sort(key=lambda herb: herb.fitness)
        for carn in self._carns:
            logging.debug(f"\t {carn}")
            eaten_herbs = carn.feed_on_herbivores_and_gain_weight(self._herbs)
            if self._herbs is not None and eaten_herbs is not None:
                self._herbs = [herb for herb in self._herbs if herb not in eaten_herbs]
                Herbivore.decrease_count(len(eaten_herbs))
            logging.debug(f"\t {carn}")

    def _raise_error_if_boundary(self, geo):
        """
        Blindly raises a ValueError if cell is a boundary.
        Should be called only from a non-water cell.
        """
        if self._loc[0] == 1 or self._loc[1] == 1:
            raise ValueError(f"{geo} cannot be a border cell.")

    @staticmethod
    def _migrate_to(animal: Fauna, row, col, cells):
        """
        Calculates the relative movement of an animal.

        Parameters
        ----------
        animal
            The animal in question
        row
            Current row of animal
        col
            Current col of animal
        cells
            Total Island

        Returns
        -------
        Returns a tuple with relative coordinates (delta-row, delta-col)
        to which an animal will move, if at all.
        """
        will_move = animal.will_you_move()
        if not will_move:
            return None
        relative_position: Tuple = animal.where_will_you_move()
        move_to: UnitArea = cells[row + relative_position[0]][col + relative_position[1]]
        return move_to if move_to.can_animals_move_here() else None
