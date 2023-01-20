# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
import matplotlib
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure, SubFigure
from matplotlib.image import AxesImage
from matplotlib.lines import Line2D
from matplotlib.text import Annotation

from biosim.ecosystem.fauna import Herbivore, Carnivore


class Visuals:
    #                    R    G    B    A
    _rgba_value = {'W': (0.0, 0.7, 1.0, 0.6),  # blue
                   'L': (0.0, 0.4, 0.0, 0.8),  # dark green
                   'H': (0.5, 1.0, 0.5, 0.8),  # light green
                   'D': (1.0, 1.0, 0.5, 0.8)}  # light yellow

    _ylgn = matplotlib.cm.YlGn
    _ylgn.set_bad(color=(0.0, 0.7, 1.0, 0.6))
    _oranges = matplotlib.cm.Oranges
    _oranges.set_bad(color=(0.0, 0.7, 1.0, 0.6))

    def __init__(self,
                 vis_years=1,
                 ymax_animals=None,
                 cmax_animals=None,
                 hist_specs=None,
                 img_years=None,
                 img_dir=None,
                 img_base=None,
                 img_fmt='png'):

        if (img_dir is None) ^ (img_base is None):
            raise ValueError("img_dir and img_base must both be None or str")

        self._vis_years = vis_years
        self._ymax_animals = ymax_animals
        self._cmax_animals = cmax_animals
        self._hist_specs = hist_specs
        self._img_years = img_years
        self._img_dir = img_dir
        self._img_base = img_base
        self._img_fmt = img_fmt

        # Initialized in init:
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
        self._hists = {}

    def is_enabled(self):
        return self._vis_years != 0

    def initialize_figure(self, year_max, animal_distribution) -> {}:
        """
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
            A dict of references to the frame itself, and all the above axes.
        """

        if self._hist_specs is None:
            self._hist_specs = {'fitness': {'max': 1.0, 'delta': 0.05},
                                'age': {'max': 60.0, 'delta': 2},
                                'weight': {'max': 60, 'delta': 2}}

        if self._figure is None:
            self._figure = plt.figure(constrained_layout=True, figsize=(7, 7))

        self._subfigs = self._figure.subfigures(3, 1, height_ratios=[2, 2, 1])

        self._subfigs[0].set_facecolor("0.8")
        self._subfigs[1].set_facecolor("0.7")
        self._subfigs[2].set_facecolor("0.6")

        row1 = self._subfigs[0].subplots(1, 4, width_ratios=[3, 1, 2, 3])

        self._island = row1[0]
        self._island.set_title("Island")

        self._island_legend = row1[1]
        self._island_legend.axis("off")

        row1[2].axis("off")
        self._year = row1[2].annotate("Year: 0", (0.2, 0.5))

        self._animal_count = row1[3]
        self._animal_count.set_title("Animal Count")
        self._animal_count.set_xlim(0, year_max + 1)
        if self._ymax_animals is not None:
            self._animal_count.set_ylim(0, self._ymax_animals)
        xdata = np.arange(0, year_max + 1)
        self._herb_count_line = self._animal_count.plot(xdata,
                                                        np.full_like(xdata,
                                                                     np.nan,
                                                                     dtype=float))[0]
        ydata = self._herb_count_line.get_ydata()
        ydata[0] = 0
        self._herb_count_line.set_ydata(ydata)

        self._carn_count_line = self._animal_count.plot(xdata,
                                                        np.full_like(xdata,
                                                                     np.nan,
                                                                     dtype=float),
                                                        color='red')[0]

        ydata = self._carn_count_line.get_ydata()
        ydata[0] = 0
        self._carn_count_line.set_ydata(ydata)

        row2 = self._subfigs[1].subplots(1, 2)

        cmax_h = 200
        cmax_c = 100
        if self._cmax_animals is not None:
            cmax_h = self._cmax_animals["Herbivore"]
            cmax_c = self._cmax_animals["Carnivore"]

        self._herb_heat = row2[0]
        self._herb_heat.set_title("Herbivore Distribution")
        self._herb_heat.axis("off")

        self._herb_heat_image = self._herb_heat.imshow(animal_distribution["herb"],
                                                       interpolation='nearest',
                                                       cmap=self._ylgn)
        plt.colorbar(self._herb_heat_image,
                     ax=self._herb_heat,
                     orientation='vertical',
                     location="right")
        self._herb_heat_image.set_clim(10, cmax_h)

        self._carn_heat = row2[1]
        self._carn_heat.set_title("Carnivore Distribution")
        self._carn_heat.axis("off")

        self._carn_heat_image = self._carn_heat.imshow(animal_distribution["carn"],
                                                       interpolation='nearest',
                                                       cmap=self._oranges)
        plt.colorbar(self._carn_heat_image,
                     ax=self._carn_heat,
                     orientation='vertical',
                     location="right")
        self._carn_heat_image.set_clim(10, cmax_c)

        row3 = self._subfigs[2].subplots(1, len(self._hist_specs))

        for col, key in enumerate(self._hist_specs):
            row3[col].set_title(key.capitalize())
            self._hists[key.capitalize()] = row3[col]

    def save_frame(self, ymax, cmax, hist_specs, img_file_name):
        """
        Makes a single visual frame and saves it to disk as per the img_file_name, if it is present.
        """
        pass

    def set_island(self, island_map):

        map_rgba = [[self._rgba_value[column] for column in row]
                    for row in island_map.splitlines()]

        self._island.imshow(map_rgba)

        for ix, name in enumerate(('W', 'L', 'H', 'D')):
            self._island_legend.add_patch(plt.Rectangle((0., ix * 0.2), 0.3, 0.1,
                                                        edgecolor='none',
                                                        facecolor=self._rgba_value[name]))
            self._island_legend.text(0.35, ix * 0.2, name, transform=self._island_legend.transAxes)

    def refresh(self, year, max_years, animal_distr):
        self._set_year(year)
        self._refresh_animal_count_graph(Herbivore.count(), Carnivore.count(), year)
        self._refresh_heatmaps(animal_distr)
        self._refresh_histograms()
        self._flush_it()
        plt.pause(1e-6)

    def _set_year(self, year):
        self._year.set_text(f"Year: {year}")

    def _refresh_animal_count_graph(self, hcount, ccount, current_year):
        hline = self._herb_count_line.get_ydata()
        hline[current_year] = hcount
        self._herb_count_line.set_ydata(hline)

        cline = self._carn_count_line.get_ydata()
        cline[current_year] = ccount
        self._carn_count_line.set_ydata(cline)

        if self._ymax_animals is None:
            self._animal_count.set_ylim(0, max(max(hline), max(cline)) * 1.10)

    def _refresh_heatmaps(self, animal_distr: {}):
        self._herb_heat_image.set_data(np.ma.masked_where(animal_distr["herb"] == -1,
                                                          animal_distr["herb"]))
        self._carn_heat_image.set_data(np.ma.masked_where(animal_distr["carn"] == -1,
                                                          animal_distr["carn"]))

    def _refresh_histograms(self):
        pass
    def _flush_it(self):
        self._subfigs[0].canvas.draw()
        self._subfigs[1].canvas.draw()
        self._subfigs[2].canvas.draw()
        self._subfigs[0].canvas.flush_events()
        self._subfigs[1].canvas.flush_events()
        self._subfigs[2].canvas.flush_events()


