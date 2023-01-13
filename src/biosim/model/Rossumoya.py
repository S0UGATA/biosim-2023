# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
from biosim.model.Fauna import Herbivore, Carnivore
from biosim.model.UnitArea import UnitArea


class Rossumoya:

    def __init__(self, island_map):
        if island_map is None:
            raise ValueError("No Island")
        island_cells = []
        island_cells.extend(
            [UnitArea((r + 1, c + 1), value) for c, value in enumerate(rows)]
            for r, rows in enumerate(island_map.splitlines())
        )
        self._cells = island_cells

    def __str__(self):
        return '\n'.join(['\t|\t'.join([str(col) for col in row]) for row in self._cells])

    @property
    def cells(self):
        return self._cells

    def initial_populate_island(self, population: [{}]):
        if population is None:
            raise ValueError("No Input population.")

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
