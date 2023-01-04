# -*- coding: utf-8 -*-

"""
Test set for BioSim class interface for INF200 January 2022.

This set of tests checks the interface of the BioSim class to be provided by
the simulation module of the biosim package.

Notes:
     - The BioSim class should pass all tests in this set.
     - The tests check only that the class interface can be used, not that
       the class functions correctly. You need to write your own tests for that.
     - You should only run these tests on your code *after* you have implemented
       both animal and all landscape classes.
"""

__author__ = 'Hans Ekkehard Plesser'
__email__ = 'hans.ekkehard.plesser@nmbu.no'

import pytest
import glob
import os
import os.path
import matplotlib.pyplot as plt

from biosim.simulation import BioSim


@pytest.fixture(autouse=True)
def close_figures():
    yield
    plt.close("all")


def test_empty_island():
    """Empty island can be created"""
    BioSim(island_map="WW\nWW", ini_pop=[], seed=1, vis_years=0)


def test_minimal_island():
    """Island of single jungle cell"""
    BioSim(island_map="WWW\nWLW\nWWW", ini_pop=[], seed=1, vis_years=0)


def test_all_types():
    """All types of landscape can be created"""
    BioSim(island_map="WWWW\nWLHW\nWWDW\nWWWW", ini_pop=[], seed=1, vis_years=0)


@pytest.mark.parametrize('bad_boundary',
                         ['L', 'H', 'D'])
def test_invalid_boundary(bad_boundary):
    """Non-ocean boundary must raise error"""
    with pytest.raises(ValueError):
        BioSim(island_map="{}WW\nWLW\nWWW".format(bad_boundary),
               ini_pop=[], seed=1, vis_years=0)


def test_invalid_landscape():
    """Invalid landscape type must raise error"""
    with pytest.raises(ValueError):
        BioSim(island_map="WWW\nWRW\nWWW", ini_pop=[], seed=1, vis_years=0)


def test_inconsistent_length():
    """Inconsistent line length must raise error"""
    with pytest.raises(ValueError):
        BioSim(island_map="WWW\nWLLW\nWWW", ini_pop=[], seed=1, vis_years=0)


@pytest.fixture
def reset_animal_defaults():
    # no setup
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


@pytest.mark.parametrize('species, extra',
                         [('Herbivore', {}),
                          ('Carnivore', {'DeltaPhiMax': 0.5})])
def test_set_param_animals(reset_animal_defaults, species, extra):
    """Parameters can be set on animal classes"""

    params = {'w_birth': 8.,
              'sigma_birth': 1.5,
              'beta': 0.9,
              'eta': 0.05,
              'a_half': 40.,
              'phi_age': 0.2,
              'w_half': 10.,
              'phi_weight': 0.1,
              'mu': 0.25,
              'gamma': 0.2,
              'zeta': 3.5,
              'xi': 1.2,
              'omega': 0.4,
              'F': 10.}
    params.update(extra)

    BioSim(island_map="W",
           ini_pop=[], seed=1, vis_years=0).set_animal_parameters(species, params)


@pytest.fixture
def reset_landscape_defaults():
    # no setup
    yield
    BioSim(island_map="W",
           ini_pop=[], seed=1, vis_years=0).set_landscape_parameters('L', {'f_max': 800.0})
    BioSim(island_map="W",
           ini_pop=[], seed=1, vis_years=0).set_landscape_parameters('H', {'f_max': 300.0})


@pytest.mark.parametrize('lscape, params',
                         [('L', {'f_max': 100.}),
                          ('H', {'f_max': 200.})])
def test_set_param_landscape(reset_landscape_defaults, lscape, params):
    """Parameters can be set on landscape classes"""

    BioSim(island_map="W", ini_pop=[], seed=1, vis_years=0).set_landscape_parameters(lscape, params)


def test_initial_population():
    """Test that population can be placed on construction"""

    # noinspection DuplicatedCode
    BioSim(island_map="WWWW\nWLHW\nWWWW",
           ini_pop=[{'loc': (2, 2),
                     'pop': [{'species': 'Herbivore', 'age': 1, 'weight': 10.},
                             {'species': 'Carnivore', 'age': 1, 'weight': 10.}]},
                    {'loc': (2, 3),
                     'pop': [{'species': 'Herbivore', 'age': 1, 'weight': 10.},
                             {'species': 'Carnivore', 'age': 1, 'weight': 10.}]}],
           seed=1,
           vis_years=0)


@pytest.fixture
def plain_sim():
    """Return a simple island for used in various tests below"""
    return BioSim(island_map="WWWW\nWLHW\nWWWW",
                  ini_pop=[],
                  seed=1,
                  vis_years=0)


def test_add_population(plain_sim):
    """Test that population can be added to simulation"""

    # noinspection DuplicatedCode
    plain_sim.add_population([{'loc': (2, 2),
                               'pop': [{'species': 'Herbivore', 'age': 1, 'weight': 10.},
                                       {'species': 'Carnivore', 'age': 1, 'weight': 10.}]},
                              {'loc': (2, 3),
                               'pop': [{'species': 'Herbivore', 'age': 1, 'weight': 10.},
                                       {'species': 'Carnivore', 'age': 1, 'weight': 10.}]}])


def test_vis_img_steps():
    """Test that simulation can be called with visualization step values"""

    bs = BioSim(island_map="WWWW\nWLHW\nWWWW",
                ini_pop=[],
                seed=1,
                vis_years=10, img_years=20)

    bs.simulate(num_years=30)


def test_multi_simulate(plain_sim):
    """Test that simulation can be called repeatedly"""

    plain_sim.simulate(num_years=10)
    plain_sim.simulate(num_years=10)


def test_get_years(plain_sim):
    """Test that number of years simulated is available"""

    plain_sim.simulate(num_years=2)
    assert plain_sim.year == 2
    plain_sim.simulate(num_years=3)
    assert plain_sim.year == 5


def test_get_num_animals(plain_sim):
    """Test that total number of animals is available"""

    assert plain_sim.num_animals == 0


def test_get_animals_per_species(plain_sim):
    """Test that total number of animals per species is available"""

    assert plain_sim.num_animals_per_species == {'Herbivore': 0, 'Carnivore': 0}


def test_set_plot_limits():
    """Test that y-axis and color limits for plots can be set."""
    BioSim(island_map='W', ini_pop=[], seed=1, ymax_animals=20,
           cmax_animals={'Herbivore': 10, 'Carnivore': 20})


@pytest.mark.parametrize('prop, config',
                         [('fitness', {'max': 1.0, 'delta': 0.05}),
                          ('age', {'max': 60.0, 'delta': 2}),
                          ('weight', {'max': 60, 'delta': 2})])
def test_configure_histograms(prop, config):
    """Test that y-axis and color limits for plots can be set."""
    BioSim(island_map='W', ini_pop=[], seed=1, ymax_animals=20,
           cmax_animals={'Herbivore': 10, 'Carnivore': 20},
           hist_specs={prop: config})


@pytest.fixture
def figfile_base():
    """Provide name for figfile base and delete figfiles after test completes"""

    fbase = "figfileroot"
    yield fbase
    for f in glob.glob(f"{fbase}_0*.png"):
        os.remove(f)


def test_figure_saved(figfile_base):
    """Test that figures are saved during simulation"""

    sim = BioSim(island_map="WWWW\nWLHW\nWWWW",
                 ini_pop=[],
                 seed=1,
                 img_dir='.',
                 img_base=figfile_base,
                 img_fmt='png')
    sim.simulate(2)

    assert os.path.isfile(figfile_base + '_00000.png')
    assert os.path.isfile(figfile_base + '_00001.png')
