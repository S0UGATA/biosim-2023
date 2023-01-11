# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU

import math
import random

from biosim.exception import NotToBeUsedException
from biosim.model.Parameters import FaunaParam


class Fauna:
    """
    Super class used to represent each species on Rossumøya: Herbivores and Carnivores

    Subclasses: Herbivore and Carnivore
    ...

    Attributes
    -----------
    _params: Parameters.Fauna
    A parameter which contains all the specified parameters for Fauna, imported from the module
    Parameters.py, where the type is Fauna.

    Methods
    -----------
    set_animal_parameters(cls, params: {})
    A class method that changes the default values for the aninmal parameters. The user can change
    any of the values, and as many as preferred, before the simulation is started.

    weight_of_baby(mean, sd)
    Method that calculates the weight of the newborn from an animal of type Herbivore or Carnivore.
    Parameters are defined beforehand, and changes depending on the Fauna (Herbivore or Carnivore).

    calculate_fitness(self):
    Method that changes the fitness for each animal, which describes the overall condition of
    the animal. The value changes each annual cycle, calculated based on age and weight using
    the formula (3) and equation values are given by formula (4).
    # TODO Add the formula in the description, or refer to it in another way

    new_animal(self, param, w_baby)
    Method that is used to create a new animal of type Herbivore or Carnivore.

    _change_weight(self, by_amount)
    Private method that calculates the new weight of an animal. The current weight either decreseas
    or increases, but if a decrease results in a negative value the weight is set to 0.

    procreate(self, N: int)
    Method that decides which animals are producing an offspring. The following conditions are set:
    a) An animal can only have offspring if its weight < zeta (w_birth + sigma_birth)
    b) For each animal there is a probability for producing offspring, which is
     min(1, (gamma * fitness * N)) where N is the number of animals of the same species in the cell at
     the start of the breeding season. The gamma value is set before the simulation, either by user
     or by default, and the fitness is calculated by the method calculate_fitness(self).
     c) Each animal can give birth to at most one offspring per year.
     d) At birth, the parent loses xi times the actual birthweight of the baby.
     e) If the parent would lose more than their own weight, no baby is born and the weight of the
     parent remains unchanged.

     get_older(self)
     Method that adds one year to the animal after an annual cycle.

     lose_weight(self)
     Method that uses the _change_weight method to decrease the weight of an animal.

     maybe_die(self)
     A boolean method that checks if an animal dies or not. Two conditions decides: if the animals
     weight is equal to zero, death definitely follows. Then there is a probability condition, set
     by the following equation: omega(1 - fitness).
    """
    _params: FaunaParam


    @classmethod
    def set_animal_parameters(cls, params: {}):
        """
        Set the parameters of an animal, either by default or by the input of a user
        Parameters
        ----------
        params: {}
        """
        for key, value in params.items():
            try:
                if cls._params.key is not None:
                    cls._params.key = value
                else:
                    print(f"[{key}:{value}] is invalid, ignoring it.")
            except Exception:
                print(f"[{key}:{value}] is invalid, ignoring it.")

    @staticmethod
    def weight_of_baby(mean, sd):
        """
        Calculate the weight of a newborn animal

        Parameters
        ----------
        mean: int
        sd: int
        """
        return random.lognormvariate(mean, sd)

    def __init__(self, age=0, weight=0):
        self._age = age
        self._weight = weight
        self._fitness = self._calculate_fitness()

    def _calculate_fitness(self):
        """
        Calculate and return the fitness of an animal
        """
        if self._weight <= 0:
            return 0
        q_plus = 1 / (
                1 + (math.e ** (self._params.phi_age * (self._age - self._params.a_half))))
        q_minus = 1 / (
                1 + (math.e ** -(self._params.phi_weight * (self._weight - self._params.w_half))))
        return q_plus * q_minus

    # possible methods:

    def new_animal(self, age, weight):
        """
        Create a new animal

        Parameters
        ----------
        param: {}
        w_baby: int

        """
        raise NotToBeUsedException

    def _change_weight(self, by_amount):
        """
        Change the weight of an animal based on set conditions

        Parameters
        ----------
        by_amount: int
        """
        self._weight = max(self._weight + by_amount, 0)

    # 1
    def procreate(self, N: int):
        """
        Procreation of new animals. An offspring is produced based on five different conditions.

        Parameters
        ----------
        N: int

        """
        # a:
        if self._weight < self._params.zeta * (self._params.w_birth + self._params.sigma_birth):
            return None
        # b,c:
        prob = min(1, self._params.gamma * self._fitness * N)
        # weight of baby:
        w_baby = Fauna.weight_of_baby(self._params.w_birth, self._params.sigma_birth)
        # d:
        xi_w_baby = self._params.xi * w_baby
        if self._weight < xi_w_baby:
            return None
        self._change_weight(-xi_w_baby)
        return self.new_animal(0, w_baby) if random.random() < prob else None

    # 4.
    def get_older(self):
        """
        Adds one year to an animal's age
        """
        self._age += 1

    # 5.
    def lose_weight(self):
        """
        Decreases the weight of an animal
        """
        self._change_weight(-self._params.eta * self._params.omega)

    # 6.
    def maybe_die(self) -> bool:
        """
        Check if an animal is likely to die or not, returning either true or false
        """
        if self._weight <= 0:
            return True
        else:
            return random.random() < self._weight * (1 - self._fitness)


class Herbivore(Fauna):
    """
    A class used to represent a Herbivore as a type under the superclass Fauna.
    ...

    Attributes
    ----------
    _params = Parameteres.Fauna()
    The default parameters that defines a Herbivore.

    """
    _params = FaunaParam(w_birth=8,
                         sigma_birth=1.5,
                         beta=0.9,
                         eta=0.05,
                         a_half=40,
                         phi_age=0.6,
                         w_half=10,
                         phi_weight=0.1,
                         mu=0.25,
                         gamma=0.2,
                         zeta=3.5,
                         xi=1.2,
                         omega=0.4,
                         F=10,
                         DeltaPhiMax=None)

    def __init__(self, age: int = 0, weight: int = 0):
        """

        Parameters
        ----------
        age: int


        weight: int
        """
        super().__init__(age, weight)

    def new_animal(self, age, weight):
        return Herbivore(age, weight)

    # 2.
    def feed(self, start_fodder):
        """
        Return the amount of remaining fodder.
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
    _params = FaunaParam(w_birth=6,
                         sigma_birth=1,
                         beta=0.75,
                         eta=0.125,
                         a_half=40,
                         phi_age=0.3,
                         w_half=4,
                         phi_weight=0.4,
                         mu=0.4,
                         gamma=0.8,
                         zeta=3.5,
                         xi=1.1,
                         omega=0.8,
                         F=50,
                         DeltaPhiMax=10)

    def __init__(self, age: int = 0, weight: int = 0):
        super().__init__(age, weight)

    def new_animal(self, age, weight):
        return Carnivore(age, weight)

    # TODO feed() on herbivores.
