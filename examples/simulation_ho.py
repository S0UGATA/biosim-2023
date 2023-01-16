"""
Simulate herbivore population in single lowland cell for several seeds.
"""

__author__ = 'Tonje, Sougata, NMBU'

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

for seed in range(100, 105):
    sim = BioSim(geogr, ini_herbs, seed=seed,
                 log_file=f'data/simulation_ho_{seed:05d}',
                 img_dir='results',
                 img_base=f'mono_ho_{seed:05d}',
                 img_years=300)
    sim.simulate(301)

# Analyze logs:
data = []
plt.rcParams['figure.figsize'] = (12, 6)
for logfile in Path(f"{sys.path[0]}/data").glob('simulation_ho_*.csv'):
    d = pd.read_csv(logfile,
                    skiprows=1,
                    usecols=[0, 1],
                    index_col=0,
                    names=['Year', 'Herbivores'])
    d['Seed'] = int(re.match(r'.*_(\d+)\.csv', str(logfile))[1])
    data.append(d)
hd = pd.concat(data).pivot(columns='Seed')
print(hd.head())
hd.Herbivores.plot(legend=False, alpha=0.8)
plt.show()

hd_eq = hd.loc[hd.index >= 100, :]
print(f"Mean list: {hd_eq.mean()}")
print(f"Std list: {hd_eq.std()}")
print(f"Mean: {hd_eq.unstack().mean()}")
print(f"Std: {hd_eq.unstack().std()}")

bins = np.arange(160, 240, 2)
plt.hist(hd_eq.Herbivores.unstack(), bins=bins, fc='b', histtype='stepfilled', alpha=0.4)
plt.show()
