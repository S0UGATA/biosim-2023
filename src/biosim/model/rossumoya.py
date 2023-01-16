# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
from biosim.model.fauna import Herbivore, Carnivore
from biosim.model.unit_area import UnitArea


class Rossumoya:
    """
    Class that defines the island, Rossumøya, where the simulation takes place.
    It encapsulates a 2d array of cells of type UnitArea.
    """

    def __init__(self, island_map):
        """
        Initializes an island as per the input parameters.

        Parameters
        ----------
        island_map
        """

        if island_map is None:
            raise ValueError("No Island")
        island_cells = []
        island_cells.extend(
            [UnitArea((r + 1, c + 1), geo) for c, geo in enumerate(rows)]
            for r, rows in enumerate(island_map.splitlines())
        )
        self._cells = island_cells

    def __str__(self):
        return '\n'.join(['\t|\t'.join([str(col) for col in row]) for row in self._cells])

    @property
    def cells(self):
        """ Returns the underlying 2d array of UnitAreas. """
        return self._cells

    def populate_island(self, population: [{}], initial=False):
        """
        Resets the population count for each species.
        Populates the island with the amount of animals in the parameters.
        Loops through all the cells of the island, and populates them accordingly.
        Error is raised if an undefined species is being sent in.
        """

        if population is None:
            raise ValueError("No Input population.")

        if initial is True:
            Herbivore.reset_count()
            Carnivore.reset_count()

        for cell_info in population:
            row, col = cell_info.get("loc")
            unit_area: UnitArea = self._cells[row - 1][col - 1]
            for pop in cell_info.get("pop"):
                match pop.get("species"):
                    case "Herbivore":
                        unit_area.add_herb(Herbivore(pop.get("age"), pop.get("weight")))
                    case "Carnivore":
                        unit_area.add_carn(Carnivore(pop.get("age"), pop.get("weight")))
                    case _:
                        raise ValueError("Unknown species.")
