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

""" Instances were initialized weight and age is zero, in addition to input of age and weight"""


def reset_animal_params():
    """ Reset the animal parameters before running the tests."""
    yield
    Herbivore.set_animal_parameters(Herbivore.default_params)
    Carnivore.set_animal_parameters(Herbivore.default_params)


herb = Herbivore()
carn = Carnivore()
herb_set = Herbivore(5, 20)
carn_set = Carnivore(6, 24)


def test_age_carn_herb():
    """ Default age for an instance of a Carnivore or Herbivore should be 0 """
    assert herb.age == 0
    assert carn.age == 0

    assert herb_set.age == 5
    assert carn_set.age == 6


def test_get_older_carn_herb():
    """ Animal growing 1 year older.  """
    herb.get_older()
    carn.get_older()
    assert herb.age != 0
    assert carn.age != 0

    herb.get_older()
    herb.get_older()
    assert herb.age == 3

    herb_set.get_older()
    carn_set.get_older()
    assert herb_set.age == 6
    assert carn_set.age == 7


def test_eat_and_gain_weight_herb():
    """Herbivore eating fodder and gaining weight. Weight gain is Fodder*beta, where beta = 0.9"""
    fodder = 10
    herb.feed_and_gain_weight(fodder)
    assert herb.weight == pytest.approx(9)

    herb_set.feed_and_gain_weight(fodder)
    assert herb_set.weight == pytest.approx(29)

def test_eat_and_gain_weight_carn():
    """Carnivore eating and gaining weight. Weight gain is Fodder*beta, where beta = 0.75"""
    herbs = [herb, herb_set]
    carn_set.feed_on_herbivores_and_gain_weight(herbs)
    assert carn_set.weight != 24
    assert carn_set.weight > 24




