# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU

"""
Test set for Geography super class interface, in addition to child classes Highland, Lowland,
Water, and Desert interface.
"""
import pytest

from biosim.ecosystem.geography import Highland, Lowland, Desert, Water, Geography
from biosim.ecosystem.unit_area import UnitArea


@pytest.mark.parametrize('bad_fodder', [(-1), None])
def test_init_fodder(bad_fodder):
    """Initialization of fodder value in one of the four geography types can not be negative."""
    h_land = Highland()
    l_land = Lowland()
    d_land = Desert()
    w_land = Water()
    with pytest.raises(ValueError):
        h_land.initialize_fodder_max(bad_fodder)
        l_land.initialize_fodder_max(bad_fodder)
        d_land.initialize_fodder_max(bad_fodder)
        w_land.initialize_fodder_max(bad_fodder)


@pytest.mark.parametrize('fodder_value', [1, 10, 100])
def test_init_fodder_desert_water(fodder_value):
    """Initialization of a fodder value other than 0 should not be possible in Geography types Water
    and Desert."""
    d_land = Desert()
    w_land = Water()
    with pytest.raises(ValueError):
        d_land.initialize_fodder_max(fodder_value)
        w_land.initialize_fodder_max(fodder_value)
