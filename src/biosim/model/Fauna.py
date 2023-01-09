# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
import Parameters


class Fauna:
    _age: int
    _weight: float
    _fitness: float
    _animal_parameters: Parameters.Fauna


class Herbivore(Fauna):

    def __init__(self, age, weight, fitness, animal_parameters=None):
        self._age = age
        self._weight = weight
        self._fitness = fitness
        self._animal_parameters = Parameters.Fauna(8, 1.5, 0.9, 0.05, 40, 0.6, 10, 0.1,
                                                   0.25, 0.2, 3.5, 1.2, 0.4, 10, -1)
        if animal_parameters is not None:
            pass
            # TODO: overwite values in self._animal_parameters
            #  from the passed dictionary  animal_parameters


class Carnivore(Fauna):
    def __init__(self, age, weight, fitness, animal_parameters=None):
        self._age = age
        self._weight = weight
        self._fitness = fitness
        self._animal_parameters = Parameters.Fauna(6, 1, 0.75, 0.125, 40, 0.3, 4, 0.4,
                                                   0.4, 0.8, 3.5, 1.1, 0.8, 50, 10)

        if animal_parameters is not None:
            pass
            # TODO: overwite values in self._animal_parameters
            #  from the passed dictionary  animal_parameters
