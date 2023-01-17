"""
Template for BioSim class.
"""
import csv
import logging
import random
import sys
from os import path

from biosim.model.fauna import Herbivore, Carnivore
from biosim.model.rossumoya import Rossumoya

# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Hans Ekkehard Plesser / NMBU

logging.basicConfig(filename=f'{sys.path[0]}/biosim.log',
                    format='%(message)s',
                    level=logging.INFO)


class BioSim:
    """
    Top-level interface to BioSim package.
    """

    def __init__(self,
                 island_map,
                 ini_pop,
                 seed,
                 vis_years=1,
                 ymax_animals=None,
                 cmax_animals=None,
                 hist_specs=None,
                 img_years=None,
                 img_dir=None,
                 img_base=None,
                 img_fmt='png',
                 log_file=None):
        """
        Parameters
        ----------
        island_map : str
            Multi-line string specifying island geography
        ini_pop : list
            List of dictionaries specifying initial population
        seed : int
            Integer used as random number seed
        vis_years : int
            Years between visualization updates (if 0, disable graphics)
        ymax_animals : int
            Number specifying y-axis limit for graph showing animal numbers
        cmax_animals : dict
            Color-scale limits for animal densities, see below
        hist_specs : dict
            Specifications for histograms, see below
        img_years : int
            Years between visualizations saved to files (default: `vis_years`)
        img_dir : str
            Path to directory for figures
        img_base : str
            Beginning of file name for figures
        img_fmt : str
            File type for figures, e.g. 'png' or 'pdf'
        log_file : str
            If given, write animal counts to this file

        Notes
        -----
        - If `ymax_animals` is None, the y-axis limit should be adjusted automatically.
        - If `cmax_animals` is None, sensible, fixed default values should be used.
        - `cmax_animals` is a dict mapping species names to numbers, e.g.,

          .. code:: python

             {'Herbivore': 50, 'Carnivore': 20}

        - `hist_specs` is a dictionary with one entry per property for which a histogram
          shall be shown. For each property, a dictionary providing the maximum value
          and the bin width must be given, e.g.,

          .. code:: python

             {'weight': {'max': 80, 'delta': 2},
              'fitness': {'max': 1.0, 'delta': 0.05}}

          Permitted properties are 'weight', 'age', 'fitness'.
        - If `img_dir` is None, no figures are written to file.
        - Filenames are formed as

          .. code:: python

             Path(img_dir) / f'{img_base}_{img_number:05d}.{img_fmt}'

          where `img_number` are consecutive image numbers starting from 0.

        - `img_dir` and `img_base` must either be both None or both strings.
        """
        self._island = Rossumoya(island_map)
        self._island.populate_island(ini_pop, initial=True)
        random.seed(seed)
        self._vis_years = vis_years
        self._ymax_animals = ymax_animals
        self._cmax_animals = cmax_animals
        self._hist_specs = hist_specs
        self._img_years = img_years
        self._img_dir = img_dir
        self._img_base = img_base
        self._img_fmt = img_fmt
        self._log_file = log_file
        self._simulated_until_years = 0

    def set_animal_parameters(self, species, params):
        """
        Set parameters for animal species.

        Parameters
        ----------
        species : str
            Name of species for which parameters shall be set.
        params : dict
            New parameter values

        Raises
        ------
        ValueError
            If invalid parameter values are passed.
        """
        Rossumoya.set_animal_params(species, params)

    def set_landscape_parameters(self, landscape, params):
        """
        Set parameters for landscape type.

        Parameters
        ----------
        landscape : str
            Code letter for landscape
        params : dict
            New parameter values

        Raises
        ------
        ValueError
            If invalid parameter values are passed.
        """
        Rossumoya.set_island_params(landscape, params)

    def simulate(self, num_years):
        """
        Run simulation while visualizing the result.

        Parameters
        ----------
        num_years : int
            Number of years to simulate
        """
        csvfile = None
        writer = None
        if self._log_file is not None:
            file_path = f"{sys.path[0]}/{self._log_file}.csv"
            new_file = not path.exists(file_path)
            csvfile = open(f"{sys.path[0]}/{self._log_file}.csv", 'a', newline="")
            writer = csv.writer(csvfile, delimiter=',')
            if new_file:
                writer.writerow(["Year", "Herbivore Count", "Carnivore Count"])

        for _ in range(num_years):
            if self._log_file is not None:
                writer.writerow([self._simulated_until_years, Herbivore.count(), Carnivore.count()])
            logging.debug(f"Year:{self._simulated_until_years}")
            self._island.go_through_annual_cycle()
            self._simulated_until_years += 1
            self._print_migration_data()

        if self._log_file is not None:
            csvfile.flush()
            csvfile.close()

    def add_population(self, population):
        """
        Add a population to the island

        Parameters
        ----------
        population : List of dictionaries
            See BioSim Task Description, Sec 3.3.3 for details.
        """
        self._island.populate_island(population)

    @property
    def year(self):
        """Last year simulated."""
        return self._simulated_until_years

    @property
    def num_animals(self):
        """Total number of animals on island."""
        return Herbivore.count() + Carnivore.count()

    @property
    def num_animals_per_species(self):
        """Number of animals per species in island, as dictionary."""
        return {'Herbivore': Herbivore.count(), 'Carnivore': Carnivore.count()}

    def make_movie(self):
        """TODO Create MPEG4 movie from visualization images saved."""

    def _print_migration_data(self):
        print(f"Y:{self._simulated_until_years}")
        print(f"H:{Herbivore.count()}.C:{Carnivore.count()}")
        print(self._island)
