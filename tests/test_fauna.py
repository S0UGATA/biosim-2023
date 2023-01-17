# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU

"""
Test set for Fauna super class interface, in addition to child classes Herbivore and Carnivore
interface.
"""

import pytest
from biosim.model.fauna import Herbivore, Carnivore
from biosim.model.parameters import FaunaParam

herb = Herbivore()
carn = Carnivore()


def reset_animal_params():
    """ Reset the animal parameters before running the tests."""
    yield
    Herbivore.set_animal_parameters(Herbivore.default_params)


def test_age_carn_herb():
    """ Default age for an instance of a Carnivore or Herbivore should be 0 """
    assert herb.age == 0
    assert carn.age == 0


def test_get_older_carn_herb():
    herb.get_older()
    carn.get_older()
    assert herb.age != 0
    assert carn.age != 0

    herb.get_older()
    herb.get_older()
    assert herb.age == 3
