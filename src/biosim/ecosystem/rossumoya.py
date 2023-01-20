# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
import numpy as np
from prettytable import PrettyTable, ALL

from biosim.ecosystem.fauna import Herbivore, Carnivore
from biosim.ecosystem.geography import Highland, Lowland
from biosim.ecosystem.unit_area import UnitArea


class Rossumoya:
    """
    Class that defines the island, Rossumøya, where the simulation takes place.
    It encapsulates a 2d array of cells of type UnitArea.
    """

    def __init__(self, island_map):
        """
        Initializes an island as per the input parameters.
        Validates Island shape.

        Parameters
        ----------
        island_map
        """

        if island_map is None:
            raise ValueError("No Island")

        rows = island_map.splitlines()
        if len({len(cell) for cell in rows}) > 1:
            raise ValueError("Rossumøya is non rectangular")

        island_cells = []
        max_rows_idx = len(rows) - 1
        max_col_idx = len(rows[0]) - 1
        for r, row in enumerate(rows):
            island_row = []
            for c, geo in enumerate(row):
                cell = UnitArea((r + 1, c + 1), geo)
                if not cell.can_be_border() and (r in (0, max_rows_idx) or c in (0, max_col_idx)):
                    raise ValueError(f"{geo} cannot be a border")
                island_row.append(cell)
            island_cells.append(island_row)
        self._cells = island_cells

        self._hlist = np.zeros((len(self._cells), len(self._cells[0])))
        self._clist = np.copy(self._hlist)

    def __str__(self):
        island = PrettyTable(header=False, preserve_internal_border=True, hrules=ALL)
        [island.add_row(row) for row in self._cells]
        return str(island)

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

    def go_through_annual_cycle(self):
        self.reset_animal_move_flag()
        for r, rows in enumerate(self._cells):
            for c, cell in enumerate(rows):
                if not cell.can_animals_move_here():
                    continue
                cell.make_babies()
                cell.eat()
                cell.wander_away(r, c, self._cells)
        for rows in self._cells:
            for cell in rows:
                if not cell.can_animals_move_here():
                    continue
                cell.grow_old()
                cell.get_thin()
                cell.maybe_die()

    def reset_animal_move_flag(self):
        [[cell.reset_animal_move_flag() for cell in rows] for rows in self._cells]

    @staticmethod
    def set_island_params(landscape, params):
        """
        Set parameters for landscape type.
        Validates input.

        Parameters
        ----------
        self
        landscape
        params

        Returns
        -------

        """
        if landscape is None or params is None:
            raise ValueError(f"Empty landscape: {landscape} or params: {params}")

        f_max = params.get("f_max")
        if f_max is None:
            raise ValueError(f"param : {params} does not contain f_max")
        try:
            f_max = float(f_max)
            if f_max < 0.:
                raise ValueError("Fodder cannot be negative.")
        except ValueError as e:
            raise ValueError(f"f_max cannot be {f_max}, inner error: {e}") from e

        match landscape:
            case "H":
                Highland.initialize_fodder_max(f_max)
            case "L":
                Lowland.initialize_fodder_max(f_max)
            case "W":
                if f_max > 0:
                    raise ValueError(f"Water cannot have fodder {f_max}")
            case "D":
                if f_max > 0:
                    raise ValueError(f"Desert cannot have fodder {f_max}")
            case _:
                raise ValueError(f"Invalid geography: {landscape}")

    @staticmethod
    def set_animal_params(species, params):
        if species is None or params is None:
            raise ValueError(f"Empty species: {species} or params: {params}")
        match species:
            case "Herbivore":
                Herbivore.set_animal_parameters(params)
            case "Carnivore":
                Carnivore.set_animal_parameters(params)
            case _:
                raise ValueError(f"Invalid species: {species}")

    @staticmethod
    def console_output_island(param):
        UnitArea.console_output_island = param

    def animal_details(self) -> {}:
        age_h, age_c = [], []
        weight_h, weight_c = [], []
        fit_h, fit_c = [], []
        for r, rows in enumerate(self._cells):
            for c, cell in enumerate(rows):
                if cell.can_animals_move_here():
                    self._hlist[r, c] = len(cell.herbs)
                    self._clist[r, c] = len(cell.carns)
                    for herb in cell.herbs:
                        age_h.append(herb.age)
                        weight_h.append(herb.weight)
                        fit_h.append(herb.fitness)
                    for carn in cell.carns:
                        age_c.append(carn.age)
                        weight_c.append(carn.weight)
                        fit_c.append(carn.fitness)
                else:
                    self._hlist[r, c] = -1
                    self._clist[r, c] = -1
        return {"count_herbivore": self._hlist, "age_herbivore": age_h,
                "weight_herbivore": weight_h, "fitness_herbivore": fit_h,
                "count_carnivore": self._clist, "age_carnivore": age_c,
                "weight_carnivore": weight_c, "fitness_carnivore": fit_c}
