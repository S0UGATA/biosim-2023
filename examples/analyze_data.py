# Analyze logs:
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

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

print(sum(hc.loc[299, 'Carnivores'] == 0))
print(sum(hc.loc[299, 'Herbivores'] == 0))

with_c = (hc.loc[299, 'Herbivores'] > 0) & (hc.loc[299, 'Carnivores'] > 0)
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
