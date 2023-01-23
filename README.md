# Modelling the Ecosystem of Rossumøya

The project simulates life at the imaginary island of Rossumøya, given several initial parameters.
As a user and initializer you have the possibility to create an island of your choice with pre-
defined values for the different parameters. Another option is to run simulations with the default
set of parameters. In the examples folder you are presented with some examples of different types
of simulations. What varies is the size of the island, the distribution of landscape types, and 
the distribution and initialization of animals. 

###How the simulation works
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
```
biosim/simulation.py
```

The final simulation is called by using
```
sim.simulate(301)
```
Where the chosen value is the number of years you want to simulate. For further documentation and 
information about the different classes, parameters and possible restrictions is documented in each
file and package in the folder
```
biosim
```


### Examples of simulations
#### 1. Simulation with a default set of parameters
```
examples/simulation_migration_default_params.py
```
In this simulation, the default set of parameters are used for both initializing Herbivores and 
Carnivores. The weight and age is instantiated, and the number of each fauna type. 

#### 3. Simulation with changed parameters

#### 2. Full simulation with visualization over 200 years
```
examples/simulation.visual.py
```
In this simulation, 




### Running the project
Running any of the Python files in the ```/examples``` folder will initiate the simulation. 

### Credits:
 - Code optimization done with Sourcery: https://sourcery.ai/

[![Pipeline Status](https://gitlab.com/nmbu.no/emner/inf200/h2022/january-block-teams/a39_sougata_tonje/biosim-a39-sougata-tonje/badges/main/pipeline.svg)](https://gitlab.com/nmbu.no/emner/inf200/h2022/january-block-teams/a39_sougata_tonje/biosim-a39-sougata-tonje/-/pipelines?page=1&scope=branches&ref=main)


### Authors and contributors to the project
- Sougata Bhattacharya, sougata.bhattacharya@nmbu.no
- Tonje Martine Lorgen Kirkholt, tonje.martine.lorgen.kirkholt@nmbu.no