"""
Template for BioSim class.
"""
import csv
import random
import sys
from os import path

from matplotlib import pyplot as plt

from biosim.ecosystem.fauna import Herbivore, Carnivore
from biosim.ecosystem.rossumoya import Rossumoya
from biosim.visualization.visuals import Visuals


# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Hans Ekkehard Plesser / NMBU


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
                 log_file=None,
                 console_output_island=False):
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
        self._island_map = island_map
        self._island = Rossumoya(island_map)
        self._island.populate_island(ini_pop, initial=True)
        random.seed(seed)
        self._visuals = Visuals(vis_years,
                                ymax_animals,
                                cmax_animals,
                                hist_specs,
                                img_years,
                                img_dir,
                                img_base,
                                img_fmt)
        self._log_file = log_file
        self._current_year = 0
        self._console_output_island = console_output_island

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

        self._print_migration_data()

        if self._visuals.is_enabled():
            self._visuals.initialize_figure(num_years, self._island.animal_details())
            self._visuals.set_island(self._island_map)
        else:
            print("Graphics is disabled.")

        for _ in range(num_years):
            if self._log_file is not None:
                writer.writerow([self._current_year, Herbivore.count(), Carnivore.count()])

            self._island.go_through_annual_cycle()

            self._print_migration_data()

            if self._visuals.is_enabled() and \
                    self._current_year % self._visuals.vis_years == 0:
                self._visuals.refresh(self._current_year, self._island.animal_details())

            self._current_year += 1

        if self._log_file is not None:
            csvfile.flush()
            csvfile.close()

        if self._visuals.is_enabled():
            plt.show(block=False)

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
        return self._current_year

    @property
    def num_animals(self):
        """Total number of animals on island."""
        return Herbivore.count() + Carnivore.count()

    @property
    def num_animals_per_species(self):
        """Number of animals per species in island, as dictionary."""
        return {'Herbivore': Herbivore.count(), 'Carnivore': Carnivore.count()}

    def make_movie(self):
        """ Create MPEG4 movie from visualization images saved."""
        self._visuals.make_movie()

    def _print_migration_data(self):
        if self._console_output_island:
            Rossumoya.console_output_island(True)
            print(f"Y:{self._current_year}")
            print(f"H:{Herbivore.count()}.C:{Carnivore.count()}")
            print(self._island)
