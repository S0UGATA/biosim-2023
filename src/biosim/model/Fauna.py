# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
import Parameters


class Fauna:
    _age: int
    _weight: float
    _fitness: float  # TODO this would be a calculated value by default.
    _animal_parameters: Parameters.Fauna


# possible methods:
# get older
# lose weight at the end of the year
# procreate
# eats
# dies
class Herbivore(Fauna):

    def __init__(self, age, weight, fitness, animal_parameters=None):
        self._age = age
        self._weight = weight
        self._fitness = fitness
        self._animal_parameters = Parameters.Fauna(w_birth=8,
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
        if animal_parameters is not None:
            pass
            # TODO: overwite values in self._animal_parameters
            #  from the passed dictionary  animal_parameters


class Carnivore(Fauna):
    def __init__(self, age, weight, fitness, animal_parameters=None):
        self._age = age
        self._weight = weight
        self._fitness = fitness
        self._animal_parameters = Parameters.Fauna(w_birth=6,
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

        if animal_parameters is not None:
            pass
            # TODO: overwite values in self._animal_parameters
            #  from the passed dictionary  animal_parameters
