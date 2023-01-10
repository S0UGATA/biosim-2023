# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
import math

import Parameters


class Fauna:
    _params: Parameters.Fauna

    def __init__(self, age=0, weight=0):
        self._age = age
        self._weight = weight
        self._fitness = self.fitness()

    @property
    def fitness(self):
        """Calculate fitness."""
        if self._weight <= 0:
            return 0
        q_plus = 1 / (
                1 + (math.e ** (self._params.phi_age * (self._age - self._params.a_half))))
        q_minus = 1 / (
                1 + (math.e ** -(self._params.phi_weight * (self._weight - self._params.w_half))))
        return q_plus * q_minus

    @classmethod
    def override_params(cls, params: {}):
        for key, value in params.items():
            try:
                cls._params.key = value
            except Exception:
                print(f"[{key}:{value}] is invalid, ignoring it.")


# possible methods:


# get older
# lose weight at the end of the year
# procreate
# eats
# dies
class Herbivore(Fauna):
    _params = Parameters.Fauna(w_birth=8,
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

    def __init__(self, age: int = 0, weight: int = 0, params: {} = None):
        self.override_params(params)
        super().__init__(age, weight)


class Carnivore(Fauna):
    _params = Parameters.Fauna(w_birth=6,
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

    def __init__(self, age: int = 0, weight: int = 0, params: {} = None):
        self.override_params(params)
        super().__init__(age, weight)
