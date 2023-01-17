"""
Check Migration

Test migration
"""

__author__ = "Tonje Martine Lorgen Kirkholt", "Sougata Bhattacharya"
__email__ = "tonje.martine.lorgen.kirkholt@nmbu.no", "sougata.bhattacharya@nmbu.no"

import textwrap

from biosim.simulation import BioSim

if __name__ == '__main__':
    geogr = """\
               WWWWWWWWWWW
               WLLLLLLLLLW
               WLLLLLLLLLW
               WLLLLLLLLLW
               WLLLLLLLLLW
               WLLLLLLLLLW
               WLLLLLLLLLW
               WLLLLLLLLLW
               WWWWWWWWWWW"""
    geogr = textwrap.dedent(geogr)

    ini_herbs = [{'loc': (5, 6),
                  'pop': [{'species': 'Herbivore',
                           'age': 0,
                           'weight': 5000}
                          for _ in range(500)]}]
    ini_carns = [{'loc': (5, 6),
                  'pop': [{'species': 'Carnivore',
                           'age': 0,
                           'weight': 5000}
                          for _ in range(500)]}]

    sim = BioSim(island_map=geogr,
                 ini_pop=ini_herbs,
                 seed=100)

    sim.add_population(ini_carns)

    sim.set_animal_parameters('Herbivore',
                              {'mu': 1, 'omega': 0, 'gamma': 0, 'eta': 0,
                               'F': 0, 'a_half': 10000})
    sim.set_animal_parameters('Carnivore',
                              {'mu': 1, 'omega': 0, 'gamma': 0, 'eta': 0,
                               'F': 0, 'a_half': 10000})

    sim.simulate(num_years=5)
