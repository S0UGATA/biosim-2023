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


def test_age_carn_herb():
    """ Test that the default age for an instance of an Herbivore or Carnivore is equal to 0. """
    reset_animal_params()
    herb = Herbivore()
    carn = Carnivore()
    herb_set = Herbivore(5, 20)
    carn_set = Carnivore(6, 24)

    assert herb.age == 0
    assert carn.age == 0

    assert herb_set.age == 5
    assert carn_set.age == 6


def test_get_older_carn_herb():
    """ Test that the age of an animal increases by one when get_older() is used."""
    herb = Herbivore()
    carn = Carnivore()
    herb_set = Herbivore(5, 20)
    carn_set = Carnivore(6, 24)

    for year in range(10):
        herb.get_older()
        herb_set.get_older()
        carn.get_older()
        carn_set.get_older()
        assert herb.age == year + 1
        assert herb_set.age == year + 6
        assert carn.age == year + 1
        assert carn_set.age == year + 7





def test_eat_and_gain_weight_herb():
    """ Test that an Herbivore that has eaten an F amount of fodder gains weight according to the
    formula β*F, where β = 0.9 for Herbivores."""
    herb = Herbivore()
    carn = Carnivore()
    herb_set = Herbivore(5, 20)
    carn_set = Carnivore(6, 24)

    amount_fodder = 10
    herb.feed_and_gain_weight(amount_fodder)
    assert herb.weight == pytest.approx(9)

    herb_set.feed_and_gain_weight(amount_fodder)
    assert herb_set.weight == pytest.approx(29)


def test_eat_and_gain_weight_carn():
    """Carnivore eating and gaining weight. Weight gain is Fodder*β, where beta = 0.75"""
    herb = Herbivore()
    carn = Carnivore()
    herb_set = Herbivore(5, 20)
    carn_set = Carnivore(6, 24)

    carn.set_animal_parameters(params={'DeltaPhiMax': 0.01})
    herbs = [herb, herb_set]
    assert carn_set.weight == 24
    carn_set.feed_on_herbivores_and_gain_weight(herbs)
    assert carn_set.weight != 24
