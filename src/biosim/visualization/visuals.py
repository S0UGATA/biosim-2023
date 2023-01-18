# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU


class Visuals:

    def __init__(self,
                 vis_years=1,
                 ymax_animals=None,
                 cmax_animals=None,
                 hist_specs=None,
                 img_years=None,
                 img_dir=None,
                 img_base=None,
                 img_fmt='png'):
        self._vis_years = vis_years
        self._ymax_animals = ymax_animals
        self._cmax_animals = cmax_animals
        self._hist_specs = hist_specs
        self._img_years = img_years
        self._img_dir = img_dir
        self._img_base = img_base
        self._img_fmt = img_fmt

        if (img_dir is None) ^ (img_base is None):
            raise ValueError("img_dir and img_base must both be None or str")

    def make_frame(self, ymax, cmax, hist_specs, img_file_name):
        """
        Makes a single visual frame and saves it to disk as per the img_file_name, if it is present.
        """
