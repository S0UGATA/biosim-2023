# -*- coding: utf-8 -*-
# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU

"""
Test set for UnitArea class interface.
"""

import pytest
import numpy as np

from biosim.ecosystem.unit_area import UnitArea
from biosim.ecosystem.fauna import Herbivore, Carnivore
from biosim.ecosystem.geography import Highland, Lowland, Water, Desert


@pytest.fixture
def unit_area():
    return UnitArea((1, 1), 'L')


def test_make_babies(unit_area):
    """
    Test the make_babies method to ensure changes work.
    """
    herb = Herbivore(5, 20)
    carn = Carnivore(5, 20)
    unit_area.add_herb(herb)
    unit_area.add_carn(carn)
    initial_herb_count = len(unit_area.herbs)
    initial_carn_count = len(unit_area.carns)
    unit_area.make_babies()
    assert len(unit_area.herbs) > initial_herb_count
    assert len(unit_area.carns) > initial_carn_count


def test_herbivores_eat(unit_area):
    """
    Test the _herbivores_eat method to ensure changes work.
    """
    herb1 = Herbivore(5, 20)
    herb2 = Herbivore(5, 20)
    unit_area.add_herb(herb1)
    unit_area.add_herb(herb2)
    initial_weight_herb1 = herb1.weight
    initial_weight_herb2 = herb2.weight
    unit_area._herbivores_eat()
    assert herb1.weight > initial_weight_herb1
    assert herb2.weight > initial_weight_herb2
