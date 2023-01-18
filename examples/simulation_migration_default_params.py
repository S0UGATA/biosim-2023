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
               WWWWWWWWWWWWWWWWWWWWW
               WWWWWWWWHWWWWLLLLLLLW
               WHHHHHLLLLWWLLLLLLLWW
               WHHHHHHHHHWWLLLLLLWWW
               WHHHHHLLLLLLLLLLLLWWW
               WHHHHHLLLDDLLLHLLLWWW
               WHHLLLLLDDDLLLHHHHWWW
               WWHHHHLLLDDLLLHWWWWWW
               WHHHLLLLLDDLLLLLLLWWW
               WHHHHLLLLDDLLLLWWWWWW
               WWHHHHLLLLLLLLWWWWWWW
               WWWHHHHLLLLLLLWWWWWWW
               WWWWWWWWWWWWWWWWWWWWW"""
    geogr = textwrap.dedent(geogr)

    ini_herbs = [{'loc': (3, 2),
                  'pop': [{'species': 'Herbivore',
                           'age': 5,
                           'weight': 20}
                          for _ in range(50)]}]
    ini_carns = [{'loc': (3, 2),
                  'pop': [{'species': 'Carnivore',
                           'age': 5,
                           'weight': 20}
                          for _ in range(20)]}]

    sim = BioSim(island_map=geogr,
                 ini_pop=ini_herbs,
                 seed=100,
                 console_output_island=True)

    sim.simulate(10)
    sim.add_population(ini_carns)
    sim.simulate(50)
