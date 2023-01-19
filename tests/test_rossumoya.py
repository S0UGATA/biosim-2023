# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU

"""
Test set for Rossumøya class interface.
"""
from unittest import mock

import pytest

from biosim.ecosystem.rossumoya import Rossumoya
from biosim.simulation import BioSim
from unittest.mock import MagicMock, Mock

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
def reusable_island():
    """Create an island that can be used in other tests."""
    return BioSim(island_map="WWWW\nWHLW\nWWWW", ini_pop=ini_herbs,
                  seed=1,
                  vis_years=0)


def test_annual_cycle(reusable_island):
    """For each year of the simulation all the cycles are called."""
    reusable_island.add_population(ini_carns)
    reusable_island.simulate(num_years=50)

@mock.patch('simulation.simulate.Rossumoya.go_through_annual_cycle')
def test_island(self, go_through_annual_cycle):
    simulation = BioSim()
    BioSim.simulate(num_years=10)
    go_through_annual_cycle.assert_called_with(num_years=10)



