# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU

"""
Test set for BioSim class interface. The following tests check if the class interface can be used,
whereas the class functions are tested in their own files.
"""

import glob
import os
import random

import pytest

from biosim.ecosystem.fauna import Herbivore
from biosim.simulation import BioSim


# TODO: Create tests similar to the ones in test_biosim_interface,
def test_create_island():
    """All types of islands can be created, as long as the border is water"""

    BioSim(island_map="WWW\nWWW\nWWW", ini_pop=[], seed=1, vis_years=0)


@pytest.mark.parametrize('island_map', ["LWW\nWWW\nWWL", "WWW\nWWW\nWWL", "DWW\nWLW\nWWD",
                                        "LHL\nLWL\nLHL", "HWW\nWWW\nDDD", "WWW\nLWL\nWWW"])
def test_island_border(island_map):
    """The border of the island can only be surrounded by water"""
    with pytest.raises(ValueError):
        BioSim(island_map=island_map, ini_pop=[], seed=1, vis_years=0)


@pytest.mark.parametrize('bad_value', [-1, 100, "A", "P", "Å", "*"])
def test_geo_input_param(bad_value):
    """Input of invalid geo type should raise an error"""
    with pytest.raises(ValueError):
        BioSim(island_map="WWW\nW{}W\nWWW", ini_pop=[], seed=1, vis_years=0)


def test_size_of_island():
    """The grid of the island should be a square"""
    with pytest.raises(ValueError):
        BioSim(island_map="WWW\nWW\nWWW", ini_pop=[], seed=1, vis_years=0)
        BioSim(island_map="WWW\nWW\nWWWWWW", ini_pop=[], seed=1, vis_years=0)


@pytest.fixture
def reset_fauna_params():
    yield
    BioSim(island_map="W",
           ini_pop=[], seed=1, vis_years=0).set_animal_parameters('Herbivore',
                                                                  {'w_birth': 8.,
                                                                   'sigma_birth': 1.5,
                                                                   'beta': 0.9,
                                                                   'eta': 0.05,
                                                                   'a_half': 40.,
                                                                   'phi_age': 0.6,
                                                                   'w_half': 10.,
                                                                   'phi_weight': 0.1,
                                                                   'mu': 0.25,
                                                                   'gamma': 0.2,
                                                                   'zeta': 3.5,
                                                                   'xi': 1.2,
                                                                   'omega': 0.4,
                                                                   'F': 10.}
                                                                  )
    # noinspection DuplicatedCode
    BioSim(island_map="W",
           ini_pop=[], seed=1, vis_years=0).set_animal_parameters('Carnivore',
                                                                  {'w_birth': 6.,
                                                                   'sigma_birth': 1.0,
                                                                   'beta': 0.75,
                                                                   'eta': 0.125,
                                                                   'a_half': 40.,
                                                                   'phi_age': 0.3,
                                                                   'w_half': 4.,
                                                                   'phi_weight': 0.4,
                                                                   'mu': 0.4,
                                                                   'gamma': 0.8,
                                                                   'zeta': 3.5,
                                                                   'xi': 1.1,
                                                                   'omega': 0.8,
                                                                   'F': 50.,
                                                                   'DeltaPhiMax': 10.})


@pytest.mark.parametrize('fauna_type, set_param', [('Herbivore', {'F': 5.0}),
                                                   ('Carnivore', {'DeltaPhiMax': 11.0})])
def test_set_default_animal_params(reset_fauna_params, fauna_type, set_param):
    """It should be possible to define and set parameters of your own choosing when instantiating
    an animal, either Herbivore or Carnivore."""
    animal_params = {"w_birth": 6,
                     "sigma_birth": 1,
                     "beta": 0.75,
                     "eta": 0.125,
                     "a_half": 40,
                     "phi_age": 0.3,
                     "w_half": 4,
                     "phi_weight": 0.4,
                     "mu": 0.4,
                     "gamma": 0.8,
                     "zeta": 3.5,
                     "xi": 1.1,
                     "omega": 0.8,
                     "F": 50,
                     "DeltaPhiMax": 10}
    animal_params |= set_param

    BioSim(island_map="W",
           ini_pop=[], seed=1, vis_years=0).set_animal_parameters(fauna_type, set_param)


@pytest.fixture
def reusable_island():
    """Create an island that can be used in other tests."""
    return BioSim(island_map="WWWW\nWHLW\nWWWW",
                  ini_pop=[],
                  seed=1,
                  vis_years=0)


@pytest.mark.parametrize('geo_type', ['H', 'L', 'D'])
def test_placement_of_population(geo_type):
    """Population of animals can be placed on all geo types except water"""
    BioSim(island_map="WWWW\nWW{}W\nWWWW".format(geo_type),
           ini_pop=[{'loc': (2, 3),
                     'pop': [{'species': 'Herbivore', 'age': 3, 'weight': 5.},
                             {'species': 'Carnivore', 'age': 3, 'weight': 12.}]},
                    {'loc': (2, 3),
                     'pop': [{'species': 'Herbivore', 'age': 2, 'weight': 20.},
                             {'species': 'Carnivore', 'age': 2, 'weight': 14.}]}],
           seed=1,
           vis_years=0)
    with pytest.raises(ValueError):
        BioSim(island_map="WWWW\nWWWW\nWWWW".format(geo_type),
               ini_pop=[{'loc': (2, 3),
                         'pop': [{'species': 'Herbivore', 'age': 3, 'weight': 5.},
                                 {'species': 'Carnivore', 'age': 3, 'weight': 12.}]},
                        {'loc': (2, 3),
                         'pop': [{'species': 'Herbivore', 'age': 2, 'weight': 20.},
                                 {'species': 'Carnivore', 'age': 2, 'weight': 14.}]}],
               seed=1, vis_years=0)


def test_multi_call_simulation(reusable_island):
    """The simulation can be called repeatedly"""
    random.seed(1234)
    cycles = 20
    for _ in range(cycles):
        no_years = random.randint(10, 100)
        reusable_island.simulate(num_years=no_years)


def test_num_years_simulated(reusable_island):
    """The number of years that has been simulated is available"""
    random.seed(1234)
    cycles = 20
    prev_years_sim = 0
    for _ in range(cycles):
        add_years_sim = random.randint(10, 100)
        reusable_island.simulate(num_years=add_years_sim)
        prev_years_sim += add_years_sim
        assert reusable_island.year == prev_years_sim


def test_total_no_animals(reusable_island):
    """The total amount of animals is available. Tested with and without adding population."""
    assert reusable_island.num_animals == 0
    ini_herbs = [{'loc': (2, 2),
                  'pop': [{'species': 'Herbivore',
                           'age': 5,
                           'weight': 20}
                          for _ in range(50)]}]
    reusable_island.add_population(ini_herbs)
    assert reusable_island.num_animals == 50


def test_animal_count_per_species(reusable_island):
    """The total amount of animals per species should be available."""
    assert reusable_island.num_animals_per_species == {'Herbivore': 0, 'Carnivore': 0}


# This is resused from test_biosim_interface
@pytest.fixture
def figfile_base():
    """Name for the figfile is provided and the figfiles can be deleted after the test is
    completed."""
    file = 'img_name'
    yield file
    for f in glob.glob(f"{file}_0*.png"):
        os.remove(f)


# TODO: Check this after image saving is done
def test_figure_saved(figfile_base):
    """Test that figure are saved during simulation"""
    sim = BioSim(island_map="WWWW\nWLHW\nWWWW",
                 ini_pop=[],
                 seed=1,
                 img_dir='.',
                 img_base=figfile_base,
                 img_fmt='png')
    sim.simulate(2)

    assert os.path.isfile(figfile_base + '_00001.png')
    assert os.path.isfile(figfile_base + '_00002.png')

# TODO: Add tests for visualization and images when this is done
