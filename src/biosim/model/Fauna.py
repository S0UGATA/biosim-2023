# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU

import math
import random

from biosim.exception import NotToBeUsedException
from biosim.model.Parameters import FaunaParam


class Fauna:
    _params: FaunaParam

    @classmethod
    def set_animal_parameters(cls, params: {}):
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
        return random.lognormvariate(mean, sd)

    def __init__(self, age=0, weight=0):
        self._age = age
        self._weight = weight
        self._fitness = self._calculate_fitness()

    def _calculate_fitness(self):
        """Calculate fitness."""
        if self._weight <= 0:
            return 0
        q_plus = 1 / (
                1 + (math.e ** (self._params.phi_age * (self._age - self._params.a_half))))
        q_minus = 1 / (
                1 + (math.e ** -(self._params.phi_weight * (self._weight - self._params.w_half))))
        return q_plus * q_minus

    # possible methods:

    def new_animal(self, age, weight):
        raise NotToBeUsedException

    def _change_weight(self, by_amount):
        self._weight = max(self._weight + by_amount, 0)

    # 1
    def procreate(self, N: int):
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
        self._age += 1

    # 5.
    def lose_weight(self):
        self._change_weight(-self._params.eta * self._params.omega)

    # 6.
    def maybe_die(self) -> bool:
        if self._weight <= 0:
            return True
        else:
            return random.random() < self._weight * (1 - self._fitness)


class Herbivore(Fauna):
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
