# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU

"""
Test set for Rossumøya class interface.
"""

import pytest

from biosim.ecosystem.rossumoya import Rossumoya
from biosim.simulation import BioSim

ini_herbs = [{'loc': (2, 2),
              'pop': [{'species': 'Herbivore',
                       'age': 5,
                       'weight': 20}
                      for _ in range(200)]}]
ini_carns = [{'loc': (2, 2),
              'pop': [{'species': 'Carnivore',
                       'age': 5,
                       'weight': 20}
                      for _ in range(50)]}]


@pytest.fixture()
def reusable_simulation():
    """Create an island that can be used in other tests."""
    return BioSim(island_map="WWWW\nWHLW\nWWWW", ini_pop=ini_herbs,
                  seed=1,
                  vis_years=0)


def test_annual_cycle(reusable_simulation):
    """For each year of the simulation all the cycles are called."""
    reusable_simulation.add_population(ini_carns)
    reusable_simulation.simulate(num_years=50)


def test_island(mocker, reusable_simulation):
    mocker.spy(Rossumoya, 'go_through_annual_cycle')
    num_years = 10
    reusable_simulation.simulate(num_years)
    assert Rossumoya.go_through_annual_cycle.call_count == num_years
