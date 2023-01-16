# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
import logging
import math
import random

from biosim.model.parameters import FaunaParam


class Fauna:
    """
    Super class used to represent each species on Rossumøya: Herbivores and Carnivores

    Subclasses: Herbivore and Carnivore
    ...

    Attributes
    -----------
    _params: Parameters.FaunaParam
    A class variable containing the specified parameters for Fauna, shared across all animals
    of the same species.

    Methods
    -----------
    set_animal_parameters(params: {})
    A class method that changes the default values for the animal parameters. The user can change
    any of the values, and as many as preferred, before the simulation is started.

    fitness():
    Method that calculates the fitness for each animal, which describes the overall condition of
    the animal. The value changes each annual cycle, calculated based on age and weight using
    the formula (3) and equation values are given by formula (4).

    procreate(N)
    Method that decides which animals are producing an offspring. The following conditions are set:
    a) An animal can only have offspring if its weight < zeta (w_birth + sigma_birth)
    b) For each animal there is a probability for producing offspring, which is
     min(1, (gamma * fitness * N)) where N is the number of animals of the same species in the cell
     at the start of the breeding season. The gamma value is set before the simulation, either
     by user or by default, and the fitness is calculated by the method calculate_fitness(self).
     c) Each animal can give birth to at most one offspring per year.
     d) At birth, the parent loses xi times the actual birth-weight of the baby.
     e) If the parent would lose more than their own weight, no baby is born and the weight of the
     parent remains unchanged.

     get_older()
     Method that adds one year to the animal after an annual cycle.

     lose_weight()
     Method that uses the _change_weight() method to decrease the weight of an animal.

     maybe_die()
     A method that checks if an animal dies or not. Two conditions decides: if the animals
     weight is equal to zero, death definitely follows. Then there is a probability condition, set
     by the following equation: omega(1 - fitness).

    _change_weight(by_amount)
    Private method that calculates the new weight of an animal. The current weight either decreases
    or increases, but if a decrease results in a negative value the weight is set to 0.
     
    _baby_weight(mean_birth, sd_birth)
    Method that calculates the weight of the newborn from an animal of type Herbivore or Carnivore.
    Parameters are defined beforehand, and changes depending on the Fauna (Herbivore or Carnivore).

    _new_animal(age, weight)
    Method that is used to create a new animal of type Herbivore or Carnivore.
    """

    _params: FaunaParam
    _count: int

    def __init__(self, age=0, weight=0.):
        self._age = age
        self._weight = weight
        self.increase_count()

    def __str__(self):
        return f"A{self._age}-W{self._weight}-F{self.fitness}"

    @property
    def age(self):
        return self._age

    @property
    def weight(self):
        return self._weight

    @property
    def fitness(self):
        """
        Calculate and return the fitness of an animal defined by two factors; q_plus and
        q_minus, defined and used in the following equations:
        .. code:: python
           Phi (fitness)  = q(-1, a, a_half, phi_age) * q(1, w, w_half, phi_weight)
        where a = age, and w = weight.
        """

        if self._weight <= 0:
            return 0
        q_plus = 1 / (
                1 + (math.e ** (self._params.phi_age * (self._age - self._params.a_half))))
        q_minus = 1 / (
                1 + (math.e ** -(self._params.phi_weight * (self._weight - self._params.w_half))))
        fitness = q_plus * q_minus
        assert 0 <= fitness <= 1
        return fitness

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
                    logging.error(f"[{key}:{value}] is invalid, ignoring it.")
            except ValueError:
                logging.error(f"[{key}:{value}] is invalid, ignoring it.")

    @classmethod
    def decrease_count(cls):
        """ Decrease the count of total amount of animals of a species.
        Method is used when an animal dies (see method :func:~Fauna.Fauna.maybe_die).
        """
        cls._count -= 1

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
        Procreation of animals. 
        An offspring is produced based on five conditions.

        Parameters
        ----------
        number_of_animals: int
        """

        logging.debug("\t\tProcreate")
        logging.debug(f"\t\t{self}")

        if self._weight < self._params.zeta * (self._params.w_birth + self._params.sigma_birth):
            return None

        prob = min(1, self._params.gamma * self.fitness * number_of_animals)
        logging.debug(f"\t\t\tprob:{prob}")
        rand = random.random()
        logging.debug(f"\t\t\trand:{rand}")

        w_baby = Fauna._baby_weight(self._params.w_birth, self._params.sigma_birth)
        logging.debug(f"\t\t\tw_baby:{w_baby}")

        xi_w_baby = self._params.xi * w_baby
        logging.debug(f"\t\t\txi_w_baby:{xi_w_baby}")
        logging.debug(f"\t\t\tself._weight:{self._weight}")
        if self._weight < xi_w_baby:
            return None
        self._change_weight(-xi_w_baby)
        logging.debug(f"\t\t\tself._weight:{self._weight}")

        baby = self._new_animal(0, w_baby) if rand < prob else None
        logging.debug(f"\t\t\tBaby:{baby}")
        return baby

    def get_older(self):
        """ Adds one year to the age of an animal """
        self._age += 1

    def lose_weight(self):
        """ Decreases the weight of an animal """
        logging.debug("\t\tlose_weight")
        by = -self._weight * self._params.eta
        logging.debug(f"\t\t\tBy:{by}")
        self._change_weight(by)

    def maybe_die(self) -> bool:
        """ Check if an animal is likely to die or not.
        Returning True if animal dies, False otherwise. """
        logging.debug("\t\tdie")
        die: bool
        if self._weight <= 0:
            die = True
        else:
            rand = random.random()
            fitness = self.fitness
            prob = self._params.omega * (1 - fitness)
            logging.debug(f"\t\t\trand:{rand}")
            logging.debug(f"\t\t\tfitness:{fitness}")
            logging.debug(f"\t\t\tprob:{prob}")
            die = rand < prob
        if die:
            self.decrease_count()
        logging.debug(f"\t\t\tdie:{die}")
        return die

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
        Change the weight of an animal by the passed amount.

        Parameters
        ----------
        by_amount: float
        """
        self._weight = max(self._weight + by_amount, 0)

    @staticmethod
    def _baby_weight(mean_birth, sd_birth):
        """
        Calculate the weight of a newborn animal by using the mean and standard deviation

        Parameters
        ----------
        mean_birth: float
        sd_birth: float
        """

        logging.debug("\t\t\tweight_of_baby")
        logging.debug(f"\t\t\t\tmean_birth:{mean_birth}")
        logging.debug(f"\t\t\t\tsd_birth:{sd_birth}")
        mu2 = mean_birth ** 2
        logging.debug(f"\t\t\t\tmu2:{mu2}")
        sd2 = sd_birth ** 2
        logging.debug(f"\t\t\t\tsd2:{sd2}")
        mean = math.log(mu2 / math.sqrt(mu2 + sd2))
        logging.debug(f"\t\t\t\tmean:{mean}")
        sd = math.sqrt(math.log(1 + (sd2 / mu2)))
        logging.debug(f"\t\t\t\tsd:{sd}")
        baby_weight = random.lognormvariate(mean, sd)
        logging.debug(f"\t\t\t\tbaby_weight:{baby_weight}")
        return baby_weight


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

    _params = _default_params
    _count: int = 0

    def __init__(self, age: int = 0, weight: int = 0.):
        """
        Parameters
        ----------
        age: int
        weight: float
        """
        super().__init__(age, weight)

    # 2.
    def feed_and_gain_weight(self, start_fodder: int) -> int:
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
        logging.debug("\t\tfeed_and_gain_weight")
        if self._params.F <= start_fodder:
            eat_fodder = self._params.F
            remaining_fodder = start_fodder - eat_fodder
        else:
            eat_fodder = start_fodder
            remaining_fodder = 0
        logging.debug(f"\t\t\tWeight before:{self._weight}")
        self._change_weight(self._params.beta * eat_fodder)
        logging.debug(f"\t\t\tWeight after:{self._weight}")
        logging.debug(f"\t\t\tremaining_fodder:{remaining_fodder}")
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
    Initialized with default_params,
    but is overridden if .. py:function::`Fauna.Fauna.set_animal_parameters` is called.

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

    _params = _default_params
    _count = 0

    def __init__(self, age: int = 0, weight: int = 0):
        super().__init__(age, weight)

    # TODO feed() on herbivores.
