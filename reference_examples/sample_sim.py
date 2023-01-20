"""
Full island simulation with herbivores and carnivores
including movie creation.
"""

__author__ = 'Hans Ekkehard Plesser, NMBU'

import re
import sys
import textwrap

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.path import Path

from biosim.simulation import BioSim

if __name__ == '__main__':
    geogr = """\
               WWWWWWWWWWWWWWWWWWWWW
               WHHHHHLLLLWWLLLLLLLWW
               WHHHHHLLLLWWLLLLLLLWW
               WHHHHHLLLLWWLLLLLLLWW
               WWHHLLLLLLLWWLLLLLLLW
               WWHHLLLLLLLWWLLLLLLLW
               WWWWWWWWHWWWWLLLLLLLW
               WHHHHHLLLLWWLLLLLLLWW
               WHHHHHHHHHWWLLLLLLWWW
               WHHHHHDDDDDLLLLLLLWWW
               WHHHHHDDDDDLLLLLLLWWW
               WHHHHHDDDDDLLLLLLLWWW
               WHHHHHDDDDDWWLLLLLWWW
               WHHHHDDDDDDLLLLWWWWWW
               WWHHHHDDDDDDLWWWWWWWW
               WWHHHHDDDDDLLLWWWWWWW
               WHHHHHDDDDDLLLLLLLWWW
               WHHHHDDDDDDLLLLWWWWWW
               WWHHHHDDDDDLLLWWWWWWW
               WWWHHHHLLLLLLLWWWWWWW
               WWWHHHHHHWWWWWWWWWWWW
               WWWWWWWWWWWWWWWWWWWWW"""
    geogr = textwrap.dedent(geogr)

    ini_herbs = [{'loc': (2, 7),
                  'pop': [{'species': 'Herbivore',
                           'age': 5,
                           'weight': 20}
                          for _ in range(200)]}]
    ini_carns = [{'loc': (2, 7),
                  'pop': [{'species': 'Carnivore',
                           'age': 5,
                           'weight': 20}
                          for _ in range(50)]}]

    sim = BioSim(geogr, ini_herbs + ini_carns, seed=1,
                 hist_specs={'fitness': {'max': 1.0, 'delta': 0.05},
                             'age': {'max': 60.0, 'delta': 2},
                             'weight': {'max': 60, 'delta': 2}},
                 cmax_animals={'Herbivore': 200, 'Carnivore': 50},
                 img_dir='results',
                 img_base='sample', log_file=f'data/simulation_hc_{1:05d}')
    sim.simulate(400)
    sim.make_movie()

# Analyze logs:
data = []
for logfile in Path(f"{sys.path[0]}/data").glob('simulation_hc_*.csv'):
    d = pd.read_csv(logfile,
                    skiprows=1,
                    index_col=0,
                    names=['Year', 'Herbivores', 'Carnivores'])
    d['Seed'] = int(re.match(r'.*_(\d+)\.csv', str(logfile))[1])
    data.append(d)
hc = pd.concat(data).pivot(columns='Seed')
print(hc.tail())

plt.plot(hc.Herbivores, 'b', alpha=0.4)
plt.plot(hc.Carnivores, 'r', alpha=0.4)
plt.show()

print(sum(hc.loc[399, 'Carnivores'] == 0))
print(sum(hc.loc[399, 'Herbivores'] == 0))

with_c = (hc.loc[399, 'Herbivores'] > 0) & (hc.loc[399, 'Carnivores'] > 0)
hc_eq = hc.loc[hc.index >= 175, np.hstack((with_c.values, with_c.values))]
print(hc_eq.Herbivores.unstack().mean(), hc_eq.Herbivores.unstack().std())
print(hc_eq.Carnivores.unstack().mean(), hc_eq.Carnivores.unstack().std())

bins = np.arange(0, 140, 2)
plt.hist(hc_eq.Herbivores.unstack(), bins=bins, fc='b', histtype='step', alpha=1, lw=3,
         label='Herbivores')
plt.hist(hc_eq.Carnivores.unstack(), bins=bins, fc='r', histtype='step', alpha=1, lw=3,
         label='Carnivores')
plt.legend()
plt.show()
