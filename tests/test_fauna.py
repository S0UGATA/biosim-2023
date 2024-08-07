# -*- coding: utf-8 -*-
# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU

"""
Test set for Fauna super class interface, in addition to child classes Herbivore and Carnivore
interface.
"""
import math
import random

import pytest
from matplotlib import pyplot as plt
from statsmodels.stats.weightstats import ztest

from biosim.ecosystem.fauna import Herbivore, Carnivore

"""Random seed for tests"""
SEED = 123456
"""Significance level for statistical tests"""
ALPHA = 0.01


def test_init_animal():
    """ Test that the default age for an instance of a Herbivore or Carnivore is equal to 0, and
    the weight is greater than 0. """
    random.seed(20)
    cycles = 10
    for _ in range(cycles):
        herb = Herbivore()
        carn = Carnivore()
        assert herb.age == 0
        assert herb.weight != 0
        assert carn.age == 0
        assert carn.weight != 0


def test_set_init_animal():
    """Initialization of animal with set input of age and weight."""
    random.seed(20)
    cycles = 20
    age = random.randint(0, 10)
    weight = random.randint(1, 50)
    for _ in range(1, cycles):
        Herbivore(age, weight)
        Carnivore(age, weight)


def test_get_older_carn_herb():
    """Test that the age of an animal increases by one when get_older() is used."""
    herb = Herbivore()  # Initialized without set values for weight and age
    carn = Carnivore()  # Initialized without set values for weight and age
    herb_set = Herbivore(5, 20)  # Herbivore with set values for weight and age
    carn_set = Carnivore(6, 24)  # Carnivore with set values for weight and age

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


def test_init_weight():
    """The initialized weight of an animal has to be greater than 0."""
    herb = Herbivore()
    carn = Carnivore()
    assert herb.weight != 0
    assert carn.weight != 0

    year = 10
    for age in range(1, year):
        weight = random.randint(1, 20)
        herb = Herbivore(age, weight)
        carn = Carnivore(age, weight)
        assert herb.weight != 0
        assert carn.weight != 0


def test_eat_and_gain_weight_herb():
    """ Test that a Herbivore that has eaten an F amount of fodder gains weight according to the
    formula β(beta)*F, where the default value for β = 0.9 for Herbivores."""
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
    """Carnivore eating and gaining weight. Weight gain is Fodder*β(beta), where the
    default value for beta = 0.75 for Carnivores. """
    herb = Herbivore()
    carn = Carnivore()
    herb_set = Herbivore(5, 20)
    carn_set = Carnivore(6, 24)

    carn.set_animal_parameters(params={'DeltaPhiMax': 0.01})
    herbs = [herb, herb_set]
    assert carn_set.weight == 24
    carn_set.feed_on_herbivores_and_gain_weight(herbs)
    assert carn_set.weight > 24


@pytest.mark.parametrize('bad_age, bad_weight', [(-1, -1), (-1, 0), (-1, 1)])
def test_grow_old_herb_carn(bad_age, bad_weight):
    """Initialization of negative weight and/or age is not possible when initializing
    a new animal."""
    with pytest.raises(ValueError):
        Herbivore(bad_age, bad_weight)
        Carnivore(bad_age, bad_weight)


def test_animal_fitness():
    """The calculated fitness of an animal is always 0 < fitness_animal < 1."""
    random.seed(SEED)
    no_animals = 1000
    for _ in range(no_animals):
        age = random.randint(0, 60)
        weight = random.randint(1, 80)
        herb = Herbivore(age, weight)
        carn = Carnivore(age, weight)
        assert 0 < herb.fitness < 1
        assert 0 < carn.fitness < 1


def test_unfit_herbs_always_die():
    """An animal dies with certainty if weight = 0. """
    random.seed(SEED)
    cycles = 1000

    for _ in range(cycles):
        rand_age = random.randint(1000, 5000)
        herb = Herbivore(rand_age)
        herb.set_animal_parameters(params={'omega': 1})
        assert herb.maybe_die() is True


@pytest.mark.parametrize('bad_param', [({'a:half': -1}), ({'omega': -1}),
                                       ({'w.birth': -1}), ({'mu': -1})])
def test_bad_parameters_herb(bad_param):
    """All parameter values should be positive integers, except the delta phi max which should be
    strictly positive (only for Carnivores)."""
    herb = Herbivore()
    with pytest.raises(ValueError):
        herb.set_animal_parameters(params=bad_param)


@pytest.mark.parametrize('bad_param', [({'DeltaPhiMax': 0}), ({'DeltaPhiMax': -1}),
                                       ({'w.birth': -1}), ({'w_half': -1})])
def test_bad_param_carn(bad_param):
    carn = Carnivore()
    with pytest.raises(ValueError):
        carn.set_animal_parameters(params=bad_param)


def test_weight_of_newborns_distribution():
    """
    This test checks the distribution of the weight of the newborns.
    It uses `statsmodels.stats.weightstats.ztest()` to verify that the expected list and the actual
    list are both lognormally distributed.
    To do this, we check that the pvalue returned by the ztest() is not less than the arbitrarily
    selected value of APLHA (here, its 0.01)
    """

    random.seed(SEED)
    sample_size = 2000  # sample size
    animals = []
    actual_baby_weight = []
    for _ in range(sample_size):
        weight = random.randint(1000, 5010)  # High weight ensures babies are being born
        age = random.randint(1, 10)
        herb = Herbivore(age, weight)
        animals.append(herb)
        newborn = herb.procreate(sample_size)
        if newborn is not None:
            actual_baby_weight.append(newborn.weight)

    exp_mean = Herbivore._params.w_birth
    exp_sd = Herbivore._params.sigma_birth

    exp_baby_weight = [_baby_weight(exp_mean, exp_sd) for _ in actual_baby_weight]
    assert ztest(actual_baby_weight, exp_baby_weight, value=0)[1] > ALPHA

    plt.figure()
    plt.hist(actual_baby_weight, label="Actual")
    plt.hist(exp_baby_weight, color='red', alpha=0.5, label='Expected')
    plt.legend()
    plt.show(block=False)


def _baby_weight(mean_birth, sd_birth):
    """
    Method that calculates the weight of the newborn from an animal of type
    Herbivore or Carnivore. For use in other tests (test_weight_of_newborns_distribution()).

    Parameters
    ----------
    mean_birth: float
    sd_birth: float
    """

    mu2 = mean_birth ** 2
    sd2 = sd_birth ** 2
    mean = math.log(mu2 / math.sqrt(mu2 + sd2))
    sd = math.sqrt(math.log(1 + (sd2 / mu2)))
    return random.lognormvariate(mean, sd)
