# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU

"""
Test set for Fauna super class interface, in addition to child classes Herbivore and Carnivore
interface.
"""
from random import random

import pytest
from biosim.model.fauna import Herbivore, Carnivore
from biosim.model.parameters import FaunaParam

"""Random seed for tests"""
SEED = 123456
"""Significance level for statistical tests"""
ALPHA = 0.01


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

    no_years = 10
    for _ in range(no_years):
        herb.get_older()
        herb_set.get_older()
        carn.get_older()
        carn_set.get_older()
    assert herb.age == no_years
    assert herb_set.age == no_years + 5
    assert carn.age == no_years
    assert carn_set.age == no_years + 6


def test_eat_and_gain_weight_herb():
    """ Test that an Herbivore that has eaten an F amount of fodder gains weight according to the
    formula β*F, where β = 0.9 for Herbivores."""
    herb = Herbivore()

    amount_fodder = 10
    beta = 0.9
    w_increase = amount_fodder * beta  # Formula for the increase of weight when a Herbivore eats
    w_before = herb.weight  # Weight of the Herbivore before feeding
    no_cycles = 10

    for _ in range(no_cycles):
        herb.feed_and_gain_weight(amount_fodder)
        assert herb.weight == pytest.approx(w_before + w_increase)
        w_before += w_increase


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
    assert carn_set.weight > 24


def test_weight_of_newborns_z_test():
    """This test is a probability test: executes procreate() N number of times.  We have that the
    number n of "successes", where procreate() returns an offspring, should be according to the log
    normal distribution ln(X) ~ N(μ, σ^2). Here, the parameters are
    the mean μ = w_birth and variance σ^2= (σ_birth)^2.

    We have
    Z = (sum of X - mean) / standard deviation

    """

    random.seed(SEED)
    no_trials = 100

    herb = Herbivore()
    herb.set_animal_parameters
