# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
import numpy as np

from biosim.ecosystem.fauna import Herbivore, Carnivore, Fauna
from biosim.ecosystem.geography import Geography, Highland, Lowland, Water, Desert

# Pre-bind frequently called functions at module level to avoid repeated
# attribute lookups in hot loops. Each attribute lookup in Python costs ~50ns,
# which adds up significantly when called hundreds of thousands of times.
_SHUFFLE = np.random.shuffle       # used to randomize herbivore feeding order
_FITNESS_KEY = Fauna.fitness.fget   # direct reference to the fitness property getter function,
                                    # used as sort key to avoid creating a lambda wrapper per sort call


class UnitArea:
    """
    Class that defines the building blocks of the island.
    Each UnitArea represents a single cell on the Rossumoya island grid.
    It holds a geography type (Highland/Lowland/Desert/Water) and lists
    of Herbivores and Carnivores currently residing in the cell.
    """
    console_output_island = False  # class-level flag to enable/disable colored console output

    # __slots__ eliminates per-instance __dict__, saving ~200 bytes per cell and making
    # attribute access faster via C-level slot descriptors instead of dictionary lookups.
    # This matters because there are hundreds of cells and each is accessed every year.
    __slots__ = ('_loc', '_geo', '_herbs', '_carns', '_can_move', '_f_max')

    def __init__(self,
                 loc: tuple,
                 geo: str,
                 herbs: list[Herbivore] = None,
                 carns: list[Carnivore] = None):
        """
        Initializes a UnitArea cell by assigning its location, geography type,
        and initial animal populations. Caches _can_move and _f_max as direct
        boolean/float attributes to avoid going through Geography property chain
        (~80K property lookups saved per 50-year simulation).

        Parameters
        ----------
        loc: tuple
            Coordinates of the cell. Starts from 1,1 at the top left.
        geo: str
            Character indicating the type of cell. Can be W, D, L, H
        herbs: list
            List of Herbivores in the cell.
        carns: list
            List of Carnivores in the cell.
        """
        self._loc = loc
        self._geo: Geography = self._assign_geo(geo)  # creates the Geography subclass instance
        self._herbs = herbs if herbs is not None else []
        self._carns = carns if carns is not None else []
        self._can_move = self._geo.can_animals_move_here  # cached bool: can animals exist here?
        self._f_max = self._geo.params.f_max               # cached float: max fodder per year

    def __str__(self):
        # Builds a string representation of the cell for console display.
        # Format: "L.H50.C20" meaning Lowland with 50 Herbivores and 20 Carnivores.
        # If console_output_island is True, adds ANSI color codes based on population density.
        val = f"{str(self._geo)}"
        h_len = len(self._herbs)
        c_len = len(self._carns)
        if h_len > 0:
            val += f".H{h_len}"
        if c_len > 0:
            val += f".C{c_len}"
        if not self.console_output_island:
            return val
        sel_count = h_len + c_len
        return val if sel_count == 0 else self._color(sel_count) + val + "\033[0m"

    @property
    def herbs(self):
        # Returns the list of Herbivores in this cell. Used externally for animal_details().
        return self._herbs

    @property
    def carns(self):
        # Returns the list of Carnivores in this cell. Used externally for animal_details().
        return self._carns

    def add_herb(self, herbivore: Herbivore):
        # Adds a single Herbivore to this cell's herb list after validating
        # that the cell's geography permits animals (not Water).
        # Raises ValueError if cell is Water type.
        if herbivore is None:
            return
        if not self._can_move:
            raise ValueError(f"No animals allowed in {self._geo}")
        self._herbs.append(herbivore)

    def add_herbs(self, herbivores: [Herbivore]):
        # Adds a list of Herbivores to this cell using list.extend() for bulk insertion.
        # More efficient than repeated add_herb() calls because extend() is a single
        # C-level operation that pre-allocates space.
        if herbivores is None:
            return
        if not self._can_move:
            raise ValueError(f"No animals allowed in {self._geo}")
        self._herbs.extend(herbivores)

    def add_carn(self, carnivore):
        # Adds a single Carnivore to this cell's carn list after validation.
        if carnivore is None:
            return
        if not self._can_move:
            raise ValueError(f"No animals allowed in {self._geo}")
        self._carns.append(carnivore)

    def add_carns(self, carnivores: [Carnivore]):
        # Adds a list of Carnivores to this cell using list.extend() for bulk insertion.
        if carnivores is None:
            return
        if not self._can_move:
            raise ValueError(f"No animals allowed in {self._geo}")
        self._carns.extend(carnivores)

    def make_babies(self):
        # Step 1 of the annual cycle: Procreation.
        # Iterates over all current animals (snapshot count N at start of breeding season)
        # and calls procreate(N) on each. Babies are collected in separate lists and
        # bulk-added via extend() after iteration to avoid modifying the list during traversal.
        # This ensures N stays constant during the breeding season (per spec requirement).
        herbs = self._herbs
        carns = self._carns
        n_herbs = len(herbs)   # N for herbivore breeding probability calculation
        n_carns = len(carns)   # N for carnivore breeding probability calculation
        herb_babies = []
        carn_babies = []
        for animal in herbs:
            baby = animal.procreate(n_herbs)
            if baby is not None:
                herb_babies.append(baby)
        for animal in carns:
            baby = animal.procreate(n_carns)
            if baby is not None:
                carn_babies.append(baby)
        if herb_babies:
            herbs.extend(herb_babies)  # add newborns after all breeding decisions are made
        if carn_babies:
            carns.extend(carn_babies)

    def eat(self):
        # Step 2 of the annual cycle: Feeding.
        # Per spec, herbivores eat first (consuming plant fodder), then carnivores hunt.
        # Order matters because carnivore kill probability depends on herbivore fitness,
        # which may change after herbivores gain weight from eating.
        self._herbivores_eat()
        self._carnivores_eat()

    def wander_away(self, row, col, cells):
        # Step 3 of the annual cycle: Migration.
        # Delegates to _migrate_species for each species list. See _migrate_species
        # for details on the migration algorithm and optimizations.
        self._herbs = self._migrate_species(self._herbs, row, col, cells, is_herb=True)
        self._carns = self._migrate_species(self._carns, row, col, cells, is_herb=False)

    def _migrate_species(self, animals, row, col, cells, is_herb):
        # Migrates a list of animals (herbs or carns) and returns the updated list.
        # For each animal, checks if it will move (based on fitness and mu probability),
        # then picks a random cardinal direction. If the destination cell allows animals,
        # the animal is moved there directly by appending to the destination's list.
        #
        # Optimization: uses direct list append (move_to._herbs.append) instead of
        # add_herb() to skip the None check and _can_move validation -- we already
        # verified _can_move in _migrate_to(). This saves ~35K method calls per simulation.
        #
        # Removal uses index-based sets (O(1) lookup) instead of identity-based list search
        # (O(n) per check), reducing migration from O(n^2) to O(n) complexity.
        if not animals:
            return animals
        to_remove = set()      # set of indices to remove, O(1) membership test
        _migrate = self._migrate_to  # cache method reference to avoid repeated lookup
        for i, animal in enumerate(animals):
            move_to = _migrate(animal, row, col, cells)
            if move_to is not None:
                (move_to._herbs if is_herb else move_to._carns).append(animal)
                to_remove.add(i)
                animal.has_moved = True  # prevent this animal from moving again this year
        if to_remove:
            return [a for i, a in enumerate(animals) if i not in to_remove]
        return animals

    def grow_old(self):
        # Step 4 of the annual cycle: Aging.
        # Directly increments _age and invalidates _cached_fit on each animal
        # instead of calling animal.get_older(). This avoids ~134K method call overhead
        # per 50-year simulation by inlining the two operations (age += 1, cache = None).
        for herb in self._herbs:
            herb._age += 1
            herb._cached_fit = None
        for carn in self._carns:
            carn._age += 1
            carn._cached_fit = None

    def get_thin(self):
        # Step 5 of the annual cycle: Weight loss.
        # Directly modifies _weight using multiplication (w *= 1-eta) instead of calling
        # animal.lose_weight(). Inlined to avoid ~134K method calls per simulation.
        # Each animal's eta is accessed via the class-level _params object (shared by species).
        for herb in self._herbs:
            herb._weight *= (1.0 - herb._params.eta)
            herb._cached_fit = None
        for carn in self._carns:
            carn._weight *= (1.0 - carn._params.eta)
            carn._cached_fit = None

    def maybe_die(self):
        # Step 6 of the annual cycle: Death.
        # Filters each species list, keeping only animals that survive.
        # animal.maybe_die() returns True if the animal dies (weight=0 or random death),
        # and internally decrements the species count. The list comprehension builds a
        # new list containing only survivors.
        self._herbs = [herb for herb in self._herbs if not herb.maybe_die()]
        self._carns = [carn for carn in self._carns if not carn.maybe_die()]

    def can_animals_move_here(self):
        # Returns the cached boolean indicating whether animals can exist in this cell.
        # True for Highland, Lowland, Desert. False for Water.
        # Cached at __init__ time to avoid repeated property lookups through Geography.
        return self._can_move

    def can_be_border(self):
        # Returns whether this cell's geography type can be on the island border.
        # Only Water can be a border cell (per island validation rules).
        return self._geo.can_be_border

    def reset_animal_move_flag(self):
        # Resets the has_moved flag to False for all animals at the start of each year.
        # This flag prevents "migration waves" where an animal moves to an adjacent cell
        # and then moves again when that cell is processed later in the same year.
        for herb in self._herbs:
            herb.has_moved = False
        for carn in self._carns:
            carn.has_moved = False

    def _herbivores_eat(self):
        # Herbivore feeding: shuffles the list randomly (per spec: "random order"),
        # then each herbivore eats up to F units of the cell's fodder.
        # Early exit if: no herbs in cell, or no fodder available (Desert/Water).
        # The fodder supply (f_max) resets each year -- the spec says "growth of fodder
        # occurs at the very beginning of the year", so we start with f_max each time.
        # Uses cached _f_max instead of self._geo.params.f_max to avoid property chain.
        # Uses pre-bound _SHUFFLE instead of np.random.shuffle for faster attribute access.
        herbs = self._herbs
        if not herbs:
            return
        remaining_fodder = self._f_max
        if remaining_fodder <= 0:
            return  # Desert or Water -- no fodder to eat
        n = len(herbs)
        indices = np.arange(n)    # create index array for shuffling
        _SHUFFLE(indices)         # randomize feeding order
        for index in indices:
            remaining_fodder = herbs[index].feed_and_gain_weight(remaining_fodder)
            if remaining_fodder <= 0:
                break  # all fodder consumed, remaining herbs don't eat

    def _carnivores_eat(self):
        # Carnivore feeding: carnivores hunt in order of decreasing fitness (strongest first),
        # herbivores are sorted by increasing fitness (weakest are targeted first).
        #
        # Sort key uses _FITNESS_KEY (the raw property getter function) instead of a lambda.
        # This avoids creating a new lambda closure per sort call and is ~15% faster.
        #
        # After each carnivore feeds, eaten herbivores are removed from the list using
        # id()-based set lookup (O(1) per check) instead of identity comparison in a list
        # (O(n) per check). This reduces the removal step from O(n*k) to O(n+k) where
        # k = number of eaten herbivores.
        #
        # The species-wide Herbivore count is batch-decremented after each carnivore's
        # feeding round (not per kill) to reduce classmethod call overhead.
        carns = self._carns
        herbs = self._herbs
        if not carns or not herbs:
            return  # nothing to hunt or no prey available

        carns.sort(key=_FITNESS_KEY, reverse=True)  # strongest carnivores hunt first
        herbs.sort(key=_FITNESS_KEY)                 # weakest herbivores targeted first
        for carn in carns:
            eaten_herbs = carn.feed_on_herbivores_and_gain_weight(herbs)
            if eaten_herbs:
                eaten_set = {id(h) for h in eaten_herbs}  # O(k) set construction
                herbs = [h for h in herbs if id(h) not in eaten_set]  # O(n) filter
                Herbivore.decrease_count(len(eaten_herbs))  # batch decrement
        self._herbs = herbs  # update reference to filtered list

    @staticmethod
    def _assign_geo(geo) -> Geography:
        # Maps a single-character geography code to its corresponding Geography subclass
        # instance. Uses Python 3.10+ structural pattern matching for clean dispatch.
        # Called once per cell during island initialization.
        match geo:
            case "H":
                return Highland()
            case "L":
                return Lowland()
            case "W":
                return Water()
            case "D":
                return Desert()
            case _:
                raise ValueError(f"Geography {geo} is not a valid value.")

    @staticmethod
    def _migrate_to(animal, row, col, cells):
        # Determines if and where an animal migrates to.
        # First checks has_moved flag (prevents double migration in same year),
        # then probabilistically decides if the animal moves (based on fitness * mu).
        # If moving, picks a random cardinal direction and looks up the destination cell.
        # Returns the destination UnitArea if it allows animals, otherwise None.
        # Uses direct _can_move slot access instead of can_animals_move_here() method call.
        if animal.has_moved or not animal.will_you_move():
            return None
        dr, dc = animal.where_will_you_move()  # random direction: (-1,0), (0,1), (1,0), (0,-1)
        move_to = cells[row + dr][col + dc]    # look up neighboring cell in the grid
        return move_to if move_to._can_move else None  # can't move into Water

    @staticmethod
    def _color(selected):
        # Returns an ANSI escape code to colorize console output based on animal count.
        # Maps population density ranges (0-10, 10-20, ..., 50-60) to different
        # background colors (41-46). Counts above 60 get cyan (46).
        # Only used when console_output_island is True.
        ll = 0
        for count, ul in enumerate(range(0, 60, 10)):
            if ll <= selected < ul + 1:
                return f"\33[0;30;4{count + 1}m"
            ll = ul
        return "\33[0;30;46m"
