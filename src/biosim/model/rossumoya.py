# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
import logging

from prettytable import PrettyTable

from biosim.model.fauna import Herbivore, Carnivore
from biosim.model.geography import Highland, Lowland
from biosim.model.unit_area import UnitArea


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
        island_cells.extend(
            [UnitArea((r + 1, c + 1), geo) for c, geo in enumerate(row)]
            for r, row in enumerate(rows)
        )
        self._cells = island_cells

    def __str__(self):
        island = PrettyTable(header=False)
        [island.add_row(row) for row in self._cells]
        return str(island)

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

    def go_through_annual_cycle(self):
        self.reset_animal_move_flag()
        for r, rows in enumerate(self.cells):
            for c, cell in enumerate(rows):
                if not cell.can_animals_move_here():
                    continue
                logging.debug(f"  Cell:{cell}")
                cell.make_babies()
                cell.eat()
                cell.wander_away(r, c, self.cells)
                cell.grow_old()
                cell.get_thin()
                cell.maybe_die()
                logging.debug("-------------")

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
