# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
import math
import random
import sys
from copy import copy
from typing import Tuple

from biosim.ecosystem.parameters import FaunaParam
from numba import jit


class Fauna:
    """
    Super class used to represent each species on Rossumøya: Herbivores and Carnivores

    Subclasses: Herbivore and Carnivore

    Attributes
    ----------
    _params : Parameters.FaunaParam
        A class variable containing the specified parameters for Fauna, shared across all animals
        of the same species.
    """

    _default_params: FaunaParam
    _params: FaunaParam
    _count: int

    def __init__(self, age=0, weight=0.):
        if age < 0:
            raise ValueError("Age cannot be negative")
        if weight <= 0.:
            raise ValueError("Weight has to be > 0")
        self._age = age
        self._weight = weight
        self.has_moved = False
        self.increase_count()

    def __str__(self):
        return f"{self.__class__.__name__[0]}" \
               f"-A{self._age}" \
               f"-W{round(self._weight, 2)}" \
               f"-F{round(self.fitness, 2)}" \
               f"-M{int(self.has_moved)}"

    @property
    def age(self):
        return self._age

    @property
    def weight(self):
        return self._weight

    @property
    def fitness(self):
        """
        Method that calculates the fitness for each animal, which describes the overall condition of
        the animal. The value changes each annual cycle, calculated based on age and weight using
        the formula (3) and equation values are given by formula (4).
        """

        return self._fitness(self._weight, self._params.phi_weight, self._params.w_half,
                             self._age, self._params.phi_age, self._params.a_half)

    @property
    def default_params(self):
        return copy(self._default_params)

    @classmethod
    def set_animal_parameters(cls, params: {}):
        """
        A class method that changes the default values for the animal parameters.
        The user can change any of the values, and as many as preferred,
        before the simulation is started.

        Parameters
        ----------
        params: {}
        """

        fauna_params = getattr(cls, "_params")
        for key, value in params.items():
            try:
                if value is None:
                    continue
                value = float(value)
                if getattr(fauna_params, key) is None:
                    raise ValueError(f"[{key}:{value}] is invalid.")
                if key == "DeltaPhiMax" and value <= 0.:
                    raise ValueError("DeltaPhiMax should be > 0")
                if value < 0.:
                    raise ValueError(f"{key} should be >= 0")
                setattr(fauna_params, key, value)
            except (AttributeError, ValueError) as e:
                raise ValueError(f"[{key}:{value}] is invalid, inner error: {e}") from e

    @classmethod
    def decrease_count(cls, by=1):
        """ Decrease the count of total amount of animals of a species.
        Method is used when an animal dies or is eaten.
        """
        cls._count -= by

    @classmethod
    def increase_count(cls):
        """
        Increase the count of total number of animals of a species.
        Method is used when offspring is produced.
        """
        cls._count += 1

    @classmethod
    def count(cls):
        """ Returns the current number of animals of a species. """
        return cls._count

    @classmethod
    def reset_count(cls):
        """ Resets the count of animals of a species to 0. """
        cls._count = 0

    def procreate(self, number_of_animals: int):
        """
        Method that decides which animals are producing an offspring.
        The following conditions are set:
        a) An animal can only have offspring if its weight < zeta (w_birth + sigma_birth)
        b) For each animal there is a probability for producing offspring, which is
        min(1, (gamma * fitness * N)) where N is the number of animals of the same species in the
        cell at the start of the breeding season. The gamma value is set before the simulation,
        either by user or by default, and the fitness is calculated by the method
        calculate_fitness(self).
        c) Each animal can give birth to at most one offspring per year.
        d) At birth, the parent loses xi times the actual birth-weight of the baby.
        e) If the parent would lose more than their own weight, no baby is born and the weight of
        the parent remains unchanged.

        Parameters
        ----------
        number_of_animals: int
        """

        if self._weight < self._params.zeta * (self._params.w_birth + self._params.sigma_birth):
            return None
        if random.random() >= min(1, self._params.gamma * self.fitness * number_of_animals):
            return None
        w_baby = Fauna._baby_weight(self._params.w_birth, self._params.sigma_birth)
        xi_w_baby = self._params.xi * w_baby
        if self._weight < xi_w_baby:
            return None
        self._change_weight(-xi_w_baby)
        return self._new_animal(0, w_baby)

    def get_older(self):
        """ Adds one year to the age of an animal """
        self._age += 1

    def lose_weight(self):
        """ Decreases the weight of an animal """

        by = -self._weight * self._params.eta
        self._change_weight(by)

    def maybe_die(self) -> bool:
        """
        Check if an animal is likely to die or not.
        Returning True if animal dies, False otherwise.
        """

        die: bool
        if self._weight <= 0:
            die = True
        else:
            die = random.random() < self._params.omega * (1 - self.fitness)
        if die:
            self.decrease_count()
        return die

    def will_you_move(self) -> float:
        """
        Returns the probability of an animal moving, depending on fitness and mu, and that the
        animal has not already moved once the current year.
        """
        return (not self.has_moved) and random.random() < self.fitness * self._params.mu

    def _new_animal(self, age, weight):
        """
        Create a new animal with input of specified age and weight.
        What species is created depends on the instance type of the caller.

        Parameters
        ----------
        age: int
        weight: float
        """
        return type(self)(age, weight)

    def _change_weight(self, by_amount):
        """
        Private method that calculates the new weight of an animal. The current weight either
        decreases or increases, but if a decrease results in a negative value the weight is set to 0

        Parameters
        ----------
        by_amount: float
        """
        self._weight = max(self._weight + by_amount, 0)

    @staticmethod
    def where_will_you_move() -> Tuple:
        """
        Decides where an animal may move.

        Returns
        -------
        A tuple with relative (row,col) values to where the animal is supposed to move.
        """
        return random.choice([(1, 0), (0, 1), (-1, 0), (0, -1)])

    @staticmethod
    @jit
    def _baby_weight(mean_birth, sd_birth):
        """
        Method that calculates the weight of the newborn from an animal of type
        Herbivore or Carnivore.

        Parameters
        ----------
        mean_birth: float
        sd_birth: float
        """

        mu2 = mean_birth ** 2
        sd2 = sd_birth ** 2
        mean = math.log(mu2 / math.sqrt(mu2 + sd2))
        sd = math.sqrt(math.log(1 + (sd2 / mu2)))
        return random.lognormvariate(mean, sd)

    @staticmethod
    @jit
    def _fitness(w, phi_weight, w_half, a, phi_age, a_half):
        if w <= 0:
            return 0
        q_plus = 1 / (
                1 + (math.e ** (phi_age * (a - a_half))))
        q_minus = 1 / (
                1 + (math.e ** -(phi_weight * (w - w_half))))
        fitness = q_plus * q_minus
        assert 0 <= fitness <= 1
        return fitness


class Herbivore(Fauna):
    """
    A class used to represent a Herbivore as a type under the superclass Fauna.
    ...

    Attributes
    ----------
    _default_params = FaunaParam
        The default parameters that defines a Herbivore.

    _params = FaunaParam
        Initialized with default_params,
        but is overridden if .. py:function::`Fauna.Fauna.set_animal_parameters` is called.

    _count: int = 0
        Initial count of Herbivores, is set to zero.
    """

    _default_params = FaunaParam({"w_birth": 8,
                                  "sigma_birth": 1.5,
                                  "beta": 0.9,
                                  "eta": 0.05,
                                  "a_half": 40,
                                  "phi_age": 0.6,
                                  "w_half": 10,
                                  "phi_weight": 0.1,
                                  "mu": 0.25,
                                  "gamma": 0.2,
                                  "zeta": 3.5,
                                  "xi": 1.2,
                                  "omega": 0.4,
                                  "F": 10,
                                  "DeltaPhiMax": None})

    _params = copy(_default_params)
    _count: int = 0

    def __init__(self, age: int = 0, weight: float = sys.float_info.min):
        """
        Parameters
        ----------
        age: int
        weight: float
        """
        super().__init__(age, weight)

    # 2.
    def feed_and_gain_weight(self, start_fodder: float) -> float:
        """
        Changes the weight of the Herbivore that eats, and returns the value of the remaining
        fodder.

        Parameters
        ----------
        start_fodder: int
            The amount of eatable fodder in the cell.

        Returns
        -------
        remaining_fodder: int
            The amount of fodder left after the animal has eaten.
        """

        if self._params.F <= start_fodder:
            eat_fodder = self._params.F
            remaining_fodder = start_fodder - eat_fodder
        else:
            eat_fodder = start_fodder
            remaining_fodder = 0

        self._change_weight(self._params.beta * eat_fodder)
        return remaining_fodder


class Carnivore(Fauna):
    """
    A class used to represent a Carnivore as a type under the superclass Fauna.
    ...

    Attributes
    ----------
    _default_params = FaunaParam
        The default parameters with set values which defines a Carnivore.

    _params = FaunaParam
        Initialized with default_params, can be overridden by Fauna.set_animal_parameters

    _count = 0
        Initial count of Carnivores is set to zero.

    """

    _default_params = FaunaParam({"w_birth": 6,
                                  "sigma_birth": 1,
                                  "beta": 0.75,
                                  "eta": 0.125,
                                  "a_half": 40,
                                  "phi_age": 0.3,
                                  "w_half": 4,
                                  "phi_weight": 0.4,
                                  "mu": 0.4,
                                  "gamma": 0.8,
                                  "zeta": 3.5,
                                  "xi": 1.1,
                                  "omega": 0.8,
                                  "F": 50,
                                  "DeltaPhiMax": 10})

    _params = copy(_default_params)
    _count = 0

    def __init__(self, age: int = 0, weight: float = sys.float_info.min):
        super().__init__(age, weight)

    def feed_on_herbivores_and_gain_weight(self, eat_herbs: [Herbivore]):
        """
        Changes the number of Herbivores as the Carnivores feed on them.
        The weight of the Carnivores are updated accordingly.
        """

        remaining_meat = self._params.F
        eaten_herbs = []
        for herb in eat_herbs:
            c_fitness = self.fitness
            h_fitness = herb.fitness
            if c_fitness <= h_fitness:
                return
            if 0 < (c_fitness - h_fitness) < self._params.DeltaPhiMax:
                prob = ((c_fitness - h_fitness) / self._params.DeltaPhiMax)
            else:
                prob = 1
            rand = random.random()
            will_kill = rand < prob
            if remaining_meat > 0 and will_kill:
                amount_to_eat = min(remaining_meat, herb.weight)
                remaining_meat -= amount_to_eat
                eaten_herbs.append(herb)
                self._change_weight(self._params.beta * amount_to_eat)
        return eaten_herbs
