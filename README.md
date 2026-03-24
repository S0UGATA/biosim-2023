[![Flake8 badge](https://img.shields.io/badge/linting-flake8-blue)](https://flake8.pycqa.org/en/latest/)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![made-with-sphinx-doc](https://img.shields.io/badge/Made%20with-Sphinx-1f425f.svg)](https://www.sphinx-doc.org/)
[![Tox badge](https://img.shields.io/badge/Made%20with-tox-yellowgreen)](https://tox.wiki/en/latest/)

<p align="center">
  <img src="readme_imgs/epap_seal.png" alt="Environmental Protection Agency of Pylandia" width="300"/>
</p>

# Modelling the Ecosystem of Rossumøya

---

The project simulates life at the imaginary island of Rossumøya, given several initial parameters.
As a user and initializer you have the possibility to create an island of your choice with 
pre-defined values for the different parameters. Another option is to run simulations with the 
default set of parameters.  
In the `examples` folder you are presented with some examples of different 
types of simulations. What varies is the size of the island, the distribution of landscape types, 
and the distribution and initialization of animals. 

### Architecture

```mermaid
flowchart TD
    subgraph ui [" User Interface "]
        BioSim["<b>BioSim</b><br/><i>simulation.py</i><br/>Top-level API"]
    end

    subgraph core [" Ecosystem Core "]
        Rossumoya["<b>Rossumoya</b><br/><i>rossumoya.py</i><br/>Island grid · annual cycle"]
        UnitArea["<b>UnitArea</b><br/><i>unit_area.py</i><br/>Feeding · breeding<br/>migration · death"]
    end

    subgraph vis [" Visualization "]
        Visuals["<b>Visuals</b><br/><i>visuals.py</i><br/>Matplotlib plots · heatmaps<br/>histograms · movie export"]
    end

    subgraph fauna_group [" Fauna "]
        Fauna["<b>Fauna</b><br/><i>fauna.py</i><br/>Fitness · aging · weight<br/>procreation · death"]
        Herbivore["<b>Herbivore</b><br/>Eats fodder"]
        Carnivore["<b>Carnivore</b><br/>Hunts herbivores"]
        FaunaParam["<b>FaunaParam</b><br/><i>parameters.py</i>"]
    end

    subgraph geo [" Geography "]
        Geography["<b>Geography</b><br/><i>geography.py</i>"]
        Highland["<b>Highland</b><br/>f_max = 300"]
        Lowland["<b>Lowland</b><br/>f_max = 800"]
        Desert["<b>Desert</b><br/>f_max = 0"]
        Water["<b>Water</b><br/>Impassable"]
        GeoParam["<b>GeoParam</b><br/><i>parameters.py</i>"]
    end

    BioSim --> Rossumoya
    BioSim --> Visuals
    Rossumoya --> UnitArea
    UnitArea --> Fauna
    UnitArea --> Geography
    Fauna --> Herbivore & Carnivore
    Fauna -.-> FaunaParam
    Geography --> Highland & Lowland & Desert & Water
    Geography -.-> GeoParam

    classDef blue fill:#3B82F6,stroke:#2563EB,color:#fff,stroke-width:2px
    classDef purple fill:#8B5CF6,stroke:#7C3AED,color:#fff,stroke-width:2px
    classDef slate fill:#475569,stroke:#334155,color:#fff,stroke-width:2px
    classDef slateLight fill:#64748B,stroke:#475569,color:#fff,stroke-width:2px
    classDef orange fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:2px
    classDef green fill:#22C55E,stroke:#16A34A,color:#fff,stroke-width:2px
    classDef red fill:#EF4444,stroke:#DC2626,color:#fff,stroke-width:2px
    classDef teal fill:#14B8A6,stroke:#0D9488,color:#fff,stroke-width:2px
    classDef highlandGreen fill:#86EFAC,stroke:#4ADE80,color:#1a1a1a,stroke-width:2px
    classDef lowlandGreen fill:#16A34A,stroke:#15803D,color:#fff,stroke-width:2px
    classDef desert fill:#FDE68A,stroke:#FCD34D,color:#1a1a1a,stroke-width:2px
    classDef water fill:#38BDF8,stroke:#0EA5E9,color:#fff,stroke-width:2px
    classDef param fill:#CBD5E1,stroke:#94A3B8,color:#1a1a1a,stroke-width:2px

    class BioSim blue
    class Visuals purple
    class Rossumoya slate
    class UnitArea slateLight
    class Fauna orange
    class Herbivore green
    class Carnivore red
    class Geography teal
    class Highland highlandGreen
    class Lowland lowlandGreen
    class Desert desert
    class Water water
    class FaunaParam,GeoParam param

    style ui fill:#EFF6FF,stroke:#3B82F6,stroke-width:2px,color:#1E40AF
    style core fill:#F8FAFC,stroke:#475569,stroke-width:2px,color:#1E293B
    style vis fill:#F5F3FF,stroke:#8B5CF6,stroke-width:2px,color:#5B21B6
    style fauna_group fill:#FFF7ED,stroke:#F59E0B,stroke-width:2px,color:#92400E
    style geo fill:#F0FDFA,stroke:#14B8A6,stroke-width:2px,color:#134E4A
```

**Annual Cycle** (executed per cell each year):
1. **Procreation** -- Animals give birth based on fitness and population size
2. **Feeding** -- Herbivores eat fodder; Carnivores hunt herbivores
3. **Migration** -- Animals move to adjacent cells (not water)
4. **Aging** -- All animals age by one year
5. **Weight Loss** -- All animals lose weight
6. **Death** -- Animals may die based on fitness and weight

---

### How the simulation works
Defining the geography of the island:
```python
geogr = """\
           WWWW
           WLHW
           WWWW"""
```
Border can only be water, everything else can be either **Highland(H)**, **Lowland(L)**, or 
**Desert(D)**.

Initiating the population of the island:
```python
ini_herbs = [{'loc': (2, 2),
                  'pop': [{'species': 'Herbivore',
                           'age': 5,
                           'weight': 20}
                          for _ in range(50)]}]
ini_carns = [{'loc': (2, 3),
              'pop': [{'species': 'Carnivore',
                       'age': 5,
                       'weight': 20}
                      for _ in range(20)]}]
```
Choose the location, species and their age and weight. The rest of the parameters are taken from the 
default values, but can be changed and specified by the user (see example 3).

Initializing the simulation:
```python
for seed in range(100, 103):
    sim = BioSim(geogr, [ini_herbs and/or ini_herbs], seed=seed,
                 log_file=f'data/simulation_hc_{seed:05d}',
                 img_dir='data', img_base=f'simulation_hc_{seed:05d}', img_years=300)
```

The different parameters and what type of values that can be used is documented
[here](src/biosim/simulation.py) in `biosim/simulation.py`.

One can add animals and change parameters once a simulation is completed for a set of years.
It is then possible to restart simulation for another set of years with the new parameters. e.g.
```python
sim = BioSim(...)
sim.simulate(<some number of years>)
sim.add_population(<some extra population>)
sim.set_animal_parameters(<changed animal parameters>)
sim.set_landscape_parameters(<changed landscape parameters>)
sim.simulate(<a few more years>)
```
For further documentation and 
information about the different classes, parameters and possible restrictions is documented in each
file and package in the folder ```biosim```, [here](src/biosim).

---

## Content of the`examples`-folder
In this folder you have various python files, all containing code to run different types of 
simulations.

#### 1. `analyze_data.py`
[Python file here](examples/analyze_data.py).  
If you want to analyze previously saved logs, this file can be used to get this data visualized
in a plot. 

#### 2. `check_sim.py`
[Python file here](examples/check_sim.py).  
Same as the file in ```reference_examples```, but in this file we have added the ```make_movie()```-
method.

#### 3. `sample_sim.py`
[Python file here](examples/sample_sim.py).  
Sample simulation with bigger island.  
*Note: make two inner folders inside `examples` called `data`
and `results`. This is where the logs and results will be saved.*


#### 4. `simulation_hc.py`
[Python file here](examples/simulation_hc.py).  
Simulation of island with Herbivores for 50 years, then adding Carnivores and simulation goes
on for 251 years (260 in total).


#### 5. `simulation_hc_changed_params.py`
[Python file here](examples/simulation_hc_changed_params.py).   
Simulation of 10 years with only Herbivores, then Carnivores are added and the simulation goes on
for 251 more years (260 years in total). 

#### 6. `simulation_ho.py`
[Python file here](examples/simulation_ho.py).  
Simulation of a small island with only Herbivores. Logs the population count and statistics are
visualized in plots in a separate window.


#### 7. `simulation_migration.py`
[Python file here](examples/simulation_migration.py).   
Simulation of 7 years with both Herbivores and Carnivores initialized from year 0. Parameters have
been changed to ensure that only migration happens and nothing else. This is so that we can verify 
that the migration works correctly. Map and distribution of animals is shown in the console.


#### 8. `simulation_migration_default_params.py`
[Python file here](examples/simulation_migration_default_params.py).  
Simulation of 10 years with only Herbivores, then Carnivores are added and the simulation goes on
for 50 more years. Weight and age of animals are initialized, and the number of each fauna type.
Default parameters used. Map and distribution of animals is only shown in the console.

#### 9. `simulation_visual.py`
[Python file here](examples/simulation_visual.py).  
We simulate a period of 400 years. 
The initialized animals in year 0 are 200 Herbivores and 50 Carnivores. The movie found 
[here](Exam/simulation_visual.mp4) is the changes visualized per year from this simulation.

---


### Extra additions
#### 1. Colorful console output:
In `biosim/simulation.py`, an extra parameter has been added to the `BioSim`-instance parameters:
`console_output_island`. Setting this to `True` enables print-out of island map in the console.
Running `examples/simulation_migration.py` ([here](examples/simulation_migration.py)) gives us the
following animated output showing migration over 7 years:

![Console output animation](readme_imgs/console_output.gif)

The parameters in the mentioned file are set so that only migration happens, allowing us to verify
that animals spread correctly across the island (following the set restrictions).

#### 2. Heatmap has water highlighted in blue:
The image below presents how the statistics from the simulation are visualized. In the two windows
showing the distribution of Herbivore and Carnivores, we have chosen to make the part of the map 
that is set to geography type *Water*, blue. 
The distribution is set by getting the details of the animals in each cell, and we then set the 
count of the animals = -1 where its water. While refreshing the heatmaps we set a mask on the cells 
where the number of animals is equal to -1 (which is done where there is geo type water on the map). 
In visuals.py, [here](src/biosim/visualization/visuals.py), the color of this mask is set to blue.
This ensures that the water areas are masked, and therefore blue, making the visualization better.  
![Simulation statistics visualization](readme_imgs/sample.gif)

  
#### 3. Easier debugging:
We have added `__str__` to all of our objects. This can be observed during debugging, 
as shown in the image below.   
![Picture of console output](readme_imgs/str_info.png){width=300 height=50}   
The letters indicate the following:

- **C** = Carnivore
- **H** = Herbivore
- **A** followed by number = Represents the age
- **W** followed by number = Represents the weight
- **F** followed by number = Represents the fitness
- **M** followed by 0 or 1 = Boolean value, telling us if the animal has moved or not 



### How to install and run
While in root file, run the following command in the terminal:
```python
python -m build
pip install .
```
Then, all simulations in the `examples` folder will be runnable. 

### Results
The saved videos from `examples/check_sim.py` and `examples/simulation_visual.py` can be found and
viewed from folder `Exam`. In the same folder you can view saved images of plots that were made
during the process of the project (folder `Exam/pics`).

### Credits:
 - Code optimization done with Sourcery: https://sourcery.ai/

### License
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

### Authors and contributors to the project
- Sougata Bhattacharya, sougata.bhattacharya@nmbu.no
- Tonje Martine Lorgen Kirkholt, tonje.martine.lorgen.kirkholt@nmbu.no