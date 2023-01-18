# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU

"""
Test set for BioSim class interface.
"""
import pytest

from biosim.simulation import BioSim


# TODO: Create tests similar to the ones in test_biosim_interface,
def test_create_island():
    """All types of islands can be created, as long as the border is water"""

    BioSim(island_map="WWW\nWWW\nWWW", ini_pop=[], seed=1, vis_years=0)


def test_island_border():
    """The island border can only be water"""
    BioSim(island_map="LWW\nWWW\nWWL", ini_pop=[], seed=1, vis_years=0)

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
def test_set_default_animal_params(reset_animal_params, fauna_type, set_param):
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
