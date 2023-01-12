"""
Simulate herbivore population in single lowland cell for several seeds.
"""

__author__ = 'Hans Ekkehard Plesser, NMBU'

import re
import sys
import textwrap
from pathlib import Path

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

for seed in range(100, 150):
    sim = BioSim(geogr, ini_herbs, seed=seed,
                 log_file=f'reference_examples/data/mono_ho_{seed:05d}',
                 img_dir='results',
                 img_base=f'mono_ho_{seed:05d}',
                 img_years=300)
    sim.simulate(301)

# Analyze logs:
data = []
for logfile in Path(f"{sys.path[1]}/reference_examples/data").glob('mono_ho_*.csv'):
    d = pd.read_csv(logfile, skiprows=1, usecols=[0, 1], index_col=0,
                    names=['Year', 'Herbivores'])
    d['Seed'] = int(re.match(r'.*_(\d+)\.csv', str(logfile))[1])
    data.append(d)
hd = pd.concat(data).pivot(columns='Seed')
print(hd.head())
hd.Herbivores.plot(legend=False, alpha=0.8)
plt.show()
