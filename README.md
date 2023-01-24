# Modelling the Ecosystem of Rossumøya

---

The project simulates life at the imaginary island of Rossumøya, given several initial parameters.
As a user and initializer you have the possibility to create an island of your choice with pre-
defined values for the different parameters. Another option is to run simulations with the default
set of parameters. In the examples folder you are presented with some examples of different types
of simulations. What varies is the size of the island, the distribution of landscape types, and 
the distribution and initialization of animals. 

### How the simulation works
Whether or not you want do define your own parameters for the island, one has to instantiate the 
island itself, the distribution of the different geography types, and the animals you want to 
populate the island with. An example of instantiating the island looks like this:

```
geogr = """\
           WWWW
           WLHW
           WWWW"""
```
Here we have an island instantiated with one column of type **Lowland(L)** and one column of type 
**Highland(H)**. The only restriction the user has to follow when pre-defining the island, is that
the border can *only be of type **Water(w)***. 
Creating the population of this island would look like the following example:

```
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
The user initiates the wanted number of Herbivores and Carbivores to populate the island, and in
*loc* you specify where on the island they should be placed. As the island in the example above 
only consists of two possible cells to populate, we choose one for each of the animal types. The 
only values that are always pre-defined is the weight and age (where weight != 0). The other 
parameters are taken from the default values in this example (can be set, see example 3.).

Initializing the simulation would look like this:
```
for seed in range(100, 103):
    sim = BioSim(geogr, [ini_herbs and/or ini_herbs], seed=seed,
                 log_file=f'data/simulation_hc_{seed:05d}',
                 img_dir='data', img_base=f'simulation_hc_{seed:05d}', img_years=300)
```

The different parameters and what type of values that can be used is documented in 
```biosim/simulation.py```.

The final simulation is called by using```sim.simulate(301)```.

Where the chosen value is the number of years you want to simulate. For further documentation and 
information about the different classes, parameters and possible restrictions is documented in each
file and package in the folder ```biosim```.

---

## Examples of simulations
The following examples are different types of simulation, where the initialized parameter vary. All
can be found in the folder ```/examples``` and run from there. A short explanation is given for 
each, to enable better understanding in creating your own simulation.

#### 1. Simulation with a default set of parameters
```
examples/simulation_migration_default_params.py
```
In this simulation, [found here](examples/simulation_migration_default_params.py), the default set of parameters are used for both initializing Herbivores and 
Carnivores. The weight and age is instantiated, and the number of each fauna type. Here, 
```console_output=True```, meaning that you get the map and distribution of animals in the console
in addition to having the information presented in a separate window. 
The simulation starts off with 50 Herbivores, and after 10 years 20 Carnivores are added. 

#### 2. Simulation with changed parameters
```
examples/simulation_hc_changed_params.py
```
In this simulation, [found here](examples/simulation_hc_changed_params.py), some of the parameters 
have been changed.

#### 3. Full simulation with visualization over 200 years
```
examples/simulation.visual.py
```
In this simulation, [found here](examples/simulation_visual.py), we simulate a period of 400 years. 
The initialized animals in year 0 are 200 Herbivores and 50 Carnivores. The movie found 
[here](result) is the changes visualized per year from this simulation. 




### Extra additions
#### 1. 
In ```biosim/simulation.py```, an extra parameter has been added to the *BioSim*-class parameters: 
**console_output_island**. Setting this to *True* enables print-out of island map in the console. 
Running ```examples/simulation.py``` ([here](examples/simulation_migration.py)) gives us the following output in the console for year 3:
![Output of island map in console.](readme_imgs/console_map.png)
The parameters in the mentioned file is set in a way so that we can observe that the migration 
for each animal in each cell works properly (following the set restrictions).

#### 2. 
- while getting the details of the animals in each cells, we set the length of the animals = 1 in each cell
- while refreshing the heatmaps we set a mask on the cells where the number of animals are -1
- in the visuals.py, we set the color of the mask = blue
- this makes sure that the water areas are masked, and therefore blue
In the separate window where the statistics are visualized, we have added the color blue to be 
added where the length of the list of animals = -1
![Output of island map in separate window](readme_imgs/stats_visual.png)

  
#### 3. 
-- added str to make debugging easier --
-- take pictures of different types of debugging --

### Credits:
 - Code optimization done with Sourcery: https://sourcery.ai/


### Authors and contributors to the project
- Sougata Bhattacharya, sougata.bhattacharya@nmbu.no
- Tonje Martine Lorgen Kirkholt, tonje.martine.lorgen.kirkholt@nmbu.no

[![Pipeline Status](https://gitlab.com/nmbu.no/emner/inf200/h2022/january-block-teams/a39_sougata_tonje/biosim-a39-sougata-tonje/badges/main/pipeline.svg)](https://gitlab.com/nmbu.no/emner/inf200/h2022/january-block-teams/a39_sougata_tonje/biosim-a39-sougata-tonje/-/pipelines?page=1&scope=branches&ref=main)  
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)  
[![Flake8 badge](https://img.shields.io/badge/linting-flake8-blue)](https://flake8.pycqa.org/en/latest/)  
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)  
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)  
[![made-with-sphinx-doc](https://img.shields.io/badge/Made%20with-Sphinx-1f425f.svg)](https://www.sphinx-doc.org/)   
[![Tox badge](https://img.shields.io/badge/Made%20with-tox-yellowgreen)](https://tox.wiki/en/latest/)