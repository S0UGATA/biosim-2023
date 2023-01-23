# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
import subprocess

import matplotlib
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import SubFigure, Figure
from matplotlib.image import AxesImage
from matplotlib.lines import Line2D
from matplotlib.patches import StepPatch
from matplotlib.text import Annotation
from numpy import ndarray

from biosim.ecosystem.fauna import Herbivore, Carnivore


class Visuals:
    """
    The Visuals class holds all parameters and methods used for graphical representation of the
    simulation of animal characteristics over the Island of Rossumøya.

    matplotlib is used to create plots and save them.
    ffmpeg is used to create a movie out of the saved figures.
    """

    #                    R    G    B    A
    _rgba_value = {'W': (0.0, 0.7, 1.0, 1.0),  # blue
                   'L': (0.0, 0.4, 0.0, 0.8),  # dark green
                   'H': (0.5, 1.0, 0.5, 0.8),  # light green
                   'D': (1.0, 1.0, 0.5, 0.8)}  # light yellow

    _ylgn = matplotlib.cm.YlGn
    _ylgn.set_bad(color=(0.0, 0.7, 1.0, 1.0))
    _oranges = matplotlib.cm.Oranges
    _oranges.set_bad(color=(0.0, 0.7, 1.0, 1.0))

    def __init__(self,
                 vis_years=1,
                 ymax_animals=None,
                 cmax_animals=None,
                 hist_specs=None,
                 img_years=None,
                 img_dir=None,
                 img_base=None,
                 img_fmt='png'):
        """
        Initializes the visual params of this class.

        Parameters
        ----------
        vis_years
        ymax_animals
        cmax_animals
        hist_specs
        img_years
        img_dir
        img_base
        img_fmt
        """

        if vis_years > 0 and img_years is not None and img_years % vis_years != 0:
            raise ValueError("img_years needs to be multiples of vis_years")

        self._vis_years = vis_years
        self._ymax_animals = ymax_animals
        self._cmax_animals = cmax_animals
        self._hist_specs = hist_specs

        self._img_years = img_years if img_years is not None else vis_years
        self._img_dir = img_dir
        self._img_base = img_base
        self._img_fmt = img_fmt
        self._img_counter = 0

        # Initialized in initialize_figure():
        self._figure: Figure = None
        self._island: Axes = None
        self._island_legend: Axes = None
        self._year: Annotation = None
        self._animal_count: Axes = None
        self._herb_heat: Axes = None
        self._carn_heat: Axes = None
        self._herb_count_line: Line2D = None
        self._carn_count_line: Line2D = None
        self._herb_heat_image: AxesImage = None
        self._carn_heat_image: AxesImage = None
        self._subfigs: [SubFigure] = None
        self._hists: {str: Axes} = {}
        self._hist_carn: {str: StepPatch} = {}
        self._hist_herb: {str: StepPatch} = {}
        self._hist_bin_edges: {str: ndarray} = {}

    @property
    def img_years(self):
        return self._img_years

    @property
    def vis_years(self):
        return self._vis_years

    def is_enabled(self):
        return self._vis_years != 0

    def initialize_figure(self, year_max, animal_details) -> {}:
        """
        Initializes the figure to br drawn in the following format:

        +-----------+-----------+-----------+-----------+---------+---+
        |  Island_map | Legend |   Year       |      Animal Count     |
        +-----------+-----------+-----------+-----------+---------+---+
        |    Herbivore distribution    |    Carnivore distribution    |
        +-----------+-----------+-----------+-----------+---------+---+
        |       Fitness       |       Age       |       Weight        |
        +-----------+-----------+-----------+-----------+---------+---+

        Returns
        -------
        skele:
            A dictionary of references to the initialized
            Figure, SubFigure, axes, Line2Ds, AxesImages, StepPatches etc.
        """

        # Validation, and default value assignment:
        if self._hist_specs is None:
            self._hist_specs = {'fitness': {'max': 1.0, 'delta': 0.05},
                                'age': {'max': 60.0, 'delta': 2},
                                'weight': {'max': 60, 'delta': 2}}

        # Main Figure
        if self._figure is None:
            self._figure = plt.figure(constrained_layout=True, figsize=(10, 10))

        # Subfigs of 3 rows
        self._subfigs = self._figure.subfigures(3, 1, height_ratios=[2, 2, 1])

        self._subfigs[0].set_facecolor("floralwhite")
        self._subfigs[1].set_facecolor("floralwhite")
        self._subfigs[2].set_facecolor("floralwhite")

        # 1st row has Island, year, and animal count graph:
        row1 = self._subfigs[0].subplots(1, 4, width_ratios=[3, 1, 2, 3])

        # Island
        self._island = row1[0]
        self._island.set_title("Island")

        self._island_legend = row1[1]
        self._island_legend.axis("off")

        # Year
        row1[2].axis("off")
        self._year = row1[2].annotate("Year: 0", (0.2, 0.5),
                                      color='darkslategrey', weight='bold',
                                      ha='center', va='center', size=14)
        # Animal count graph
        self._animal_count = row1[3]
        self._animal_count.set_title("Animal Count")
        self._animal_count.set_xlim(0, year_max + 1)
        self._animal_count.set_facecolor("antiquewhite")
        if self._ymax_animals is not None:
            self._animal_count.set_ylim(0, self._ymax_animals)
        xdata = np.arange(0, year_max + 1, self._vis_years)
        self._herb_count_line = self._animal_count.plot(xdata,
                                                        np.full_like(xdata,
                                                                     np.nan,
                                                                     dtype=float),
                                                        linestyle='-')[0]
        ydata = self._herb_count_line.get_ydata()
        ydata[0] = 0
        self._herb_count_line.set_ydata(ydata)

        self._carn_count_line = self._animal_count.plot(xdata,
                                                        np.full_like(xdata,
                                                                     np.nan,
                                                                     dtype=float),
                                                        linestyle='-',
                                                        color='red')[0]
        ydata = self._carn_count_line.get_ydata()
        ydata[0] = 0
        self._carn_count_line.set_ydata(ydata)

        # 2nd row has heat maps for herbivores and carnivores.
        row2 = self._subfigs[1].subplots(1, 2)

        cmax_h = 200
        cmax_c = 100
        if self._cmax_animals is not None:
            cmax_h = self._cmax_animals["Herbivore"]
            cmax_c = self._cmax_animals["Carnivore"]

        self._herb_heat = row2[0]
        self._herb_heat.set_title("Herbivore Distribution")
        self._herb_heat.axis("off")

        self._herb_heat_image = self._herb_heat.imshow(animal_details["count_herbivore"],
                                                       interpolation='nearest',
                                                       cmap=self._ylgn)
        plt.colorbar(self._herb_heat_image,
                     ax=self._herb_heat,
                     orientation='vertical',
                     location="right")
        self._herb_heat_image.set_clim(0, cmax_h)

        self._carn_heat = row2[1]
        self._carn_heat.set_title("Carnivore Distribution")
        self._carn_heat.axis("off")

        self._carn_heat_image = self._carn_heat.imshow(animal_details["count_carnivore"],
                                                       interpolation='nearest',
                                                       cmap=self._oranges)
        plt.colorbar(self._carn_heat_image,
                     ax=self._carn_heat,
                     orientation='vertical',
                     location="right")
        self._carn_heat_image.set_clim(0, cmax_c)

        # 3rd row has histograms for Fitness, Age and Weight.
        row3 = self._subfigs[2].subplots(1, len(self._hist_specs))

        for col, key in enumerate(self._hist_specs):
            row3[col].set_title(key.capitalize())
            row3[col].set_facecolor("antiquewhite")
            bin_max = self._hist_specs[key]["max"]
            bin_width = self._hist_specs[key]["delta"]
            self._hist_bin_edges[key] = np.arange(0, bin_max + bin_width / 2, bin_width)
            hist_counts = np.zeros_like(self._hist_bin_edges[key][:-1], dtype=float)
            self._hist_carn[key] = row3[col].stairs(hist_counts,
                                                    self._hist_bin_edges[key],
                                                    color='red',
                                                    lw=2)
            self._hist_herb[key] = row3[col].stairs(hist_counts,
                                                    self._hist_bin_edges[key],
                                                    lw=2)
            self._hists[key] = row3[col]

    def set_island(self, island_map):
        """
        The method sets up the island axes.

        Parameters
        ----------
        island_map
        """

        map_rgba = [[self._rgba_value[column] for column in row]
                    for row in island_map.splitlines()]

        self._island.imshow(map_rgba)

        for ix, name in enumerate(('W', 'L', 'H', 'D')):
            self._island_legend.add_patch(plt.Rectangle((0., ix * 0.2), 0.3, 0.1,
                                                        edgecolor='none',
                                                        facecolor=self._rgba_value[name]))
            self._island_legend.text(0.35, ix * 0.2, name, transform=self._island_legend.transAxes)

    def refresh(self, current_year, animal_details):
        """
        This method is called every year to recalculate the changes in the animal characteristics
        and reflect them on the figure.

        Parameters
        ----------
        current_year: int
            The current year.
        animal_details: dict
            A dictionary containing animal characteristics, like count, age, weight, fitness
        """
        self._refresh_year(current_year)
        self._refresh_animal_count_graph(Herbivore.count(), Carnivore.count(), current_year)
        self._refresh_heatmaps(animal_details)
        self._refresh_histograms(animal_details)
        self._flush_it()
        plt.pause(1e-6)
        self.save_frame(current_year)

    def save_frame(self, current_year):
        """
        Saves a single frame to disk as per the img_file_name.

        Parameters
        ----------
        current_year: int
            The current year.
        """
        if self._img_dir is None and self._img_base is None:
            return

        if (self._img_dir is None) ^ (self._img_base is None):
            raise ValueError("img_dir and img_base must both be None or filled")

        if current_year % self._img_years != 0:
            return

        plt.savefig(f"./{self._img_dir}/{self._img_base}_{self._img_counter:05d}.{self._img_fmt}")
        self._img_counter += 1

    def make_movie(self):
        """
        Make a movie from the saved pictures from the save_frame() function.
        """
        if self._img_dir is None and self._img_base is None:
            return

        if (self._img_dir is None) ^ (self._img_base is None):
            raise ValueError("img_dir and img_base must both be None or filled")

        try:
            # Parameters chosen according to http://trac.ffmpeg.org/wiki/Encode/H.264,
            # section "Compatibility"
            subprocess.check_call(
                [
                    "ffmpeg",
                    '-i',
                    f'./{self._img_dir}/{self._img_base}_%05d.png',
                    '-y',
                    '-profile:v',
                    'baseline',
                    '-level',
                    '3.0',
                    '-pix_fmt',
                    'yuv420p',
                    "-vf",
                    "pad=ceil(iw/2)*2:ceil(ih/2)*2",
                    f'./{self._img_dir}/{self._img_base}.mp4',
                ]
            )
        except subprocess.CalledProcessError as err:
            raise RuntimeError(f'ERROR: ffmpeg failed with: {err}') from err

    def _refresh_year(self, year):
        self._year.set_text(f"Year: {year}")

    def _refresh_animal_count_graph(self, hcount, ccount, current_year):
        index = current_year // self._vis_years

        hline = self._herb_count_line.get_ydata()
        hline[index] = hcount
        self._herb_count_line.set_ydata(hline)

        cline = self._carn_count_line.get_ydata()
        cline[index] = ccount
        self._carn_count_line.set_ydata(cline)

        if self._ymax_animals is None:
            self._animal_count.set_ylim(0, max(max(hline), max(cline)) * 1.10)

    def _refresh_heatmaps(self, animal_details: {}):
        hc = animal_details["count_herbivore"]
        cc = animal_details["count_carnivore"]
        self._herb_heat_image.set_data(np.ma.masked_where(hc == -1, hc))
        self._carn_heat_image.set_data(np.ma.masked_where(cc == -1, cc))

    def _refresh_histograms(self, animal_details):
        for hist_type in self._hists:
            data_herb = animal_details[f"{hist_type}_herbivore"]
            hist_counts_herb, _ = np.histogram(data_herb, self._hist_bin_edges[hist_type])
            self._hist_herb[hist_type].set_data(hist_counts_herb)

            data_carn = animal_details[f"{hist_type}_carnivore"]
            hist_counts_carn, _ = np.histogram(data_carn, self._hist_bin_edges[hist_type])
            self._hist_carn[hist_type].set_data(hist_counts_carn)

            self._hists[hist_type].set_ylim(
                [0, max(hist_counts_herb.max(axis=0, initial=0),
                        hist_counts_carn.max(axis=0, initial=0)) * 1.1])

    def _flush_it(self):
        self._subfigs[0].canvas.draw()
        self._subfigs[1].canvas.draw()
        self._subfigs[2].canvas.draw()
        self._subfigs[0].canvas.flush_events()
        self._subfigs[1].canvas.flush_events()
        self._subfigs[2].canvas.flush_events()
