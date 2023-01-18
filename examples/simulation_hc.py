"""
Simulate herbivore population in single lowland cell, then add carnivore population.
Repeat for several seeds.
"""

__author__ = "Tonje Martine Lorgen Kirkholt", "Sougata Bhattacharya"
__email__ = "tonje.martine.lorgen.kirkholt@nmbu.no", "sougata.bhattacharya@nmbu.no"

import re
import sys
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from biosim.simulation import BioSim

geogr = """\
           WWW
           WLW
           WWW"""
geogr = textwrap.dedent(geogr)

ini_herbs = [{'loc': (2, 2),
              'pop': [{'species': 'Herbivore',
                       'age': 5,
                       'weight': 20}
                      for _ in range(50)]}]
ini_carns = [{'loc': (2, 2),
              'pop': [{'species': 'Carnivore',
                       'age': 5,
                       'weight': 20}
                      for _ in range(20)]}]

for seed in range(100, 199):
    sim = BioSim(geogr, ini_herbs, seed=seed,
                 log_file=f'data/simulation_hc_{seed:05d}',
                 img_dir='results', img_base=f'simulation_hc_{seed:05d}', img_years=300)
    sim.simulate(50)
    sim.add_population(ini_carns)
    sim.simulate(251)

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

print(sum(hc.loc[300, 'Carnivores'] == 0))
print(sum(hc.loc[300, 'Herbivores'] == 0))

with_c = (hc.loc[300, 'Herbivores'] > 0) & (hc.loc[300, 'Carnivores'] > 0)
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
