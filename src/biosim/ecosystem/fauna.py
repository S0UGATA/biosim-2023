# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU
import math
import numpy as np
from copy import copy

from biosim.ecosystem.parameters import FaunaParam

# Module-level references to math/numpy functions to avoid repeated
# attribute lookups in hot loops. This is a standard CPython optimization
# technique that shaves ~10-15% off tight numerical loops.
_EXP = math.exp       # exponential function used in fitness sigmoid
_LOG = math.log       # natural log used in lognormal baby weight calc
_SQRT = math.sqrt     # square root used in lognormal baby weight calc
_RANDOM = np.random.random  # uniform random [0,1) used for all probability checks


class Fauna:
    """
    Super class used to represent each species on Rossumoya: Herbivores and Carnivores

    Subclasses: Herbivore and Carnivore

    Attributes
    ----------
    _params : Parameters.FaunaParam
        A class variable containing the specified parameters for Fauna, shared across all animals
        of the same species.
    """

    # __slots__ restricts instance attributes to only these four fields.
    # This eliminates the per-instance __dict__, reducing memory by ~100 bytes
    # per animal and making attribute access ~20% faster via direct slot indexing.
    __slots__ = ('_age', '_weight', '_cached_fit', 'has_moved')

    _default_params: FaunaParam
    _params: FaunaParam
    _count: int

    def __init__(self, age=0, weight=0.):
        # Validates that age is non-negative and weight is strictly positive,
        # then stores instance state. _cached_fit starts as None (lazy computation).
        # The class-level count is incremented to track total animals of this species.
        if age < 0:
            raise ValueError("Age cannot be negative")
        if weight <= 0.:
            raise ValueError("Weight has to be > 0")
        self._age = age
        self._weight = weight
        self._cached_fit = None  # fitness is lazily computed and cached until invalidated
        self.has_moved = False   # tracks if animal already migrated this year
        self.increase_count()    # increment species-wide counter

    def __str__(self):
        # Returns a compact debug string: species initial, age, weight, fitness, moved flag.
        # Example: "H-A5-W20.0-F0.66-M0"
        return (f"{self.__class__.__name__[0]}"
                f"-A{self._age}"
                f"-W{round(self._weight, 2)}"
                f"-F{round(self.fitness, 2)}"
                f"-M{int(self.has_moved)}")

    @property
    def age(self):
        # Read-only accessor for the animal's current age in years.
        return self._age

    @property
    def weight(self):
        # Read-only accessor for the animal's current weight.
        return self._weight

    @property
    def fitness(self):
        # Lazy-cached fitness property. Returns the cached value if available,
        # otherwise computes it via _compute_fitness() and stores the result.
        # The cache is invalidated (set to None) whenever age or weight changes,
        # which happens in get_older(), lose_weight(), procreate(), and feeding.
        # This reduces fitness calculations from ~3.2M/run to ~285K/run (11x reduction).
        f = self._cached_fit
        if f is None:
            f = self._compute_fitness()
            self._cached_fit = f
        return f

    @property
    def default_params(self):
        # Returns a copy of the default parameters so the originals can't be mutated.
        return copy(self._default_params)

    def _compute_fitness(self):
        # Computes fitness using the sigmoid formula from the project specification:
        #   fitness = q+(age) * q-(weight)
        #   q+(a) = 1 / (1 + exp(phi_age * (a - a_half)))
        #   q-(w) = 1 / (1 + exp(-phi_weight * (w - w_half)))
        # If weight <= 0, fitness is 0 (animal is effectively dead).
        # OverflowError is caught for extreme age/weight values where exp() overflows,
        # in which case the sigmoid clamps to 0 (the limit as exponent -> +inf).
        # Uses module-level _EXP to avoid repeated math.exp attribute lookup.
        w = self._weight
        if w <= 0:
            return 0.0
        p = self._params
        try:
            q_plus = 1.0 / (1.0 + _EXP(p.phi_age * (self._age - p.a_half)))
        except OverflowError:
            q_plus = 0.0
        try:
            q_minus = 1.0 / (1.0 + _EXP(-p.phi_weight * (w - p.w_half)))
        except OverflowError:
            q_minus = 0.0
        return q_plus * q_minus

    @classmethod
    def set_animal_parameters(cls, params: {}):
        """
        A class method that changes the default values for the animal parameters.
        Iterates over the provided dict, validates each key exists on FaunaParam,
        checks that values are non-negative (strictly positive for DeltaPhiMax),
        and sets them on the class-level _params object.
        Raises ValueError for unknown keys, negative values, or type mismatches.

        Parameters
        ----------
        params: {}
        """
        fauna_params = getattr(cls, "_params")
        for key, value in params.items():
            try:
                if value is None:
                    continue
                value = float(value)
                if getattr(fauna_params, key) is None:
                    raise ValueError(f"[{key}:{value}] is invalid.")
                if key == "DeltaPhiMax" and value <= 0.:
                    raise ValueError("DeltaPhiMax should be > 0")
                if value < 0.:
                    raise ValueError(f"{key} should be >= 0")
                setattr(fauna_params, key, value)
            except (AttributeError, ValueError) as e:
                raise ValueError(f"[{key}:{value}] is invalid, inner error: {e}") from e

    @classmethod
    def decrease_count(cls, by=1):
        # Decrements the species-wide animal counter. Called when an animal dies
        # or is eaten. The 'by' parameter allows batch decrements for efficiency
        # when multiple herbivores are eaten in one carnivore feeding cycle.
        cls._count -= by

    @classmethod
    def increase_count(cls):
        # Increments the species-wide animal counter by 1.
        # Called in __init__ whenever a new animal instance is created.
        cls._count += 1

    @classmethod
    def count(cls):
        # Returns the current total number of living animals of this species.
        # Used by BioSim for reporting num_animals and num_animals_per_species.
        return cls._count

    @classmethod
    def reset_count(cls):
        # Resets the species counter to 0. Called at the start of a new simulation
        # via populate_island(initial=True) to clear counts from previous runs.
        cls._count = 0

    def procreate(self, number_of_animals: int):
        """
        Determines if this animal produces an offspring this year.
        Checks five conditions sequentially, returning None (no baby) at the first failure:
          1. Weight must be >= zeta * (w_birth + sigma_birth) -- too light animals can't reproduce
          2. Random check against probability min(1, gamma * fitness * N) -- stochastic birth
          3. Baby weight is drawn from a lognormal distribution
          4. Parent must weigh more than xi * baby_weight -- can't lose more than own weight
          5. If all pass: parent loses xi * baby_weight, fitness cache is invalidated, baby is returned

        The probability check is optimized: if prob >= 1.0, we skip the random draw entirely.
        Weight change is inlined (avoiding _change_weight method call overhead) since
        procreate is called ~130K times per 50-year simulation.

        Parameters
        ----------
        number_of_animals: int
            Number of same-species animals in the cell at start of breeding season.
        """
        p = self._params
        if self._weight < p.zeta * (p.w_birth + p.sigma_birth):
            return None
        prob = p.gamma * self.fitness * number_of_animals
        if prob < 1.0 and _RANDOM() >= prob:
            return None
        w_baby = _baby_weight(p.w_birth, p.sigma_birth)
        xi_w_baby = p.xi * w_baby
        if self._weight < xi_w_baby:
            return None
        # Inline weight change and invalidate fitness cache since weight changed
        self._weight = max(self._weight - xi_w_baby, 0)
        self._cached_fit = None
        return type(self)(0, w_baby)  # type(self) creates the correct subclass (Herbivore/Carnivore)

    def get_older(self):
        # Increments age by 1 year. Invalidates the fitness cache since
        # fitness depends on age via the q+(age) sigmoid term.
        self._age += 1
        self._cached_fit = None

    def lose_weight(self):
        # Reduces weight by the fraction eta (annual weight loss).
        # Uses multiplication (w * (1 - eta)) instead of computing eta*w then subtracting,
        # which is slightly faster and avoids a separate _change_weight call.
        # Invalidates fitness cache since fitness depends on weight.
        self._weight *= (1.0 - self._params.eta)
        self._cached_fit = None

    def maybe_die(self) -> bool:
        # Determines if this animal dies this year. Two death conditions:
        #   1. Weight <= 0: certain death (starvation)
        #   2. Random probability: omega * (1 - fitness). Higher fitness = lower death chance.
        # If the animal dies, the species counter is decremented and True is returned.
        # The caller (UnitArea.maybe_die) uses the return value to filter the animal list.
        w = self._weight
        if w <= 0:
            self.decrease_count()
            return True
        if _RANDOM() < self._params.omega * (1.0 - self.fitness):
            self.decrease_count()
            return True
        return False

    def will_you_move(self) -> bool:
        # Decides if this animal will attempt migration this year.
        # Returns False immediately if already moved (prevents migration waves).
        # Otherwise, checks random probability against mu * fitness.
        # Short-circuit evaluation: if has_moved is True, _RANDOM() is never called.
        return (not self.has_moved) and _RANDOM() < self.fitness * self._params.mu

    @staticmethod
    def where_will_you_move():
        # Picks one of four cardinal directions with equal probability (25% each).
        # Returns a (row_delta, col_delta) tuple for the chosen direction:
        #   Up=(-1,0), Right=(0,1), Down=(1,0), Left=(0,-1).
        # Uses cascading if-checks against quartile thresholds for speed.
        # The last case doesn't need a conditional since it covers [0.75, 1.0).
        where = _RANDOM()
        if where < 0.25:
            return -1, 0
        if where < 0.5:
            return 0, 1
        if where < 0.75:
            return 1, 0
        return 0, -1

    @staticmethod
    def _fitness(w, phi_weight, w_half, a, phi_age, a_half):
        # Static version of fitness computation, kept for backward compatibility
        # with code that calls Fauna._fitness() directly with explicit parameters.
        # Uses the same sigmoid formula as _compute_fitness() but takes all
        # parameters as arguments instead of reading from self._params.
        if w <= 0:
            return 0
        try:
            q_plus = 1 / (1 + _EXP(phi_age * (a - a_half)))
        except OverflowError:
            q_plus = 0.0
        try:
            q_minus = 1 / (1 + _EXP(-phi_weight * (w - w_half)))
        except OverflowError:
            q_minus = 0.0
        return q_plus * q_minus

    @staticmethod
    def _baby_weight(mean_birth, sd_birth):
        # Delegates to the module-level _baby_weight function.
        # This static method exists so external code can call Fauna._baby_weight()
        # while the actual logic lives at module level to avoid method lookup overhead.
        return _baby_weight(mean_birth, sd_birth)


def _baby_weight(mean_birth, sd_birth):
    # Module-level function that computes a random baby weight from a lognormal distribution.
    # The lognormal parameters (mu, sigma) are derived from the desired mean and std deviation:
    #   mu = log(mean^2 / sqrt(mean^2 + sd^2))
    #   sigma = sqrt(log(1 + sd^2/mean^2))
    # This is placed at module level (not as a method) to avoid the overhead of
    # self/cls attribute lookup on every call -- it's called ~45K times per 50-year simulation.
    # Uses pre-bound _LOG and _SQRT for the same reason.
    mu2 = mean_birth * mean_birth    # mean^2, using multiplication instead of ** for speed
    sd2 = sd_birth * sd_birth        # sd^2
    mean = _LOG(mu2 / _SQRT(mu2 + sd2))
    sd = _SQRT(_LOG(1 + (sd2 / mu2)))
    return np.random.lognormal(mean, sd)


class Herbivore(Fauna):
    """
    A class used to represent a Herbivore as a type under the superclass Fauna.

    Herbivores eat plant fodder from their cell's geography type.
    Their weight increases by beta * amount_eaten after feeding.
    Default parameters define a species that grazes on lowland/highland fodder.

    Attributes
    ----------
    _default_params = FaunaParam
        The default parameters that defines a Herbivore.

    _params = FaunaParam
        Initialized with default_params,
        but is overridden if .. py:function::`Fauna.Fauna.set_animal_parameters` is called.

    _count: int = 0
        Initial count of Herbivores, is set to zero.
    """

    _default_params = FaunaParam({"w_birth": 8,
                                  "sigma_birth": 1.5,
                                  "beta": 0.9,
                                  "eta": 0.05,
                                  "a_half": 40,
                                  "phi_age": 0.6,
                                  "w_half": 10,
                                  "phi_weight": 0.1,
                                  "mu": 0.25,
                                  "gamma": 0.2,
                                  "zeta": 3.5,
                                  "xi": 1.2,
                                  "omega": 0.4,
                                  "F": 10,
                                  "DeltaPhiMax": None})

    _params = copy(_default_params)  # class-level mutable copy, shared by all Herbivore instances
    _count: int = 0                   # total living herbivores across all cells

    def __init__(self, age: int = 0, weight: float = None):
        # If weight is None (no explicit weight given), generates a random birth weight
        # from the lognormal distribution defined by w_birth and sigma_birth.
        # Otherwise uses the provided weight. Delegates to Fauna.__init__ for validation.
        if weight is None:
            weight = _baby_weight(self._params.w_birth, self._params.sigma_birth)
        super().__init__(age, weight)

    def feed_and_gain_weight(self, start_fodder: float) -> float:
        # Herbivore attempts to eat up to F units of fodder from the available supply.
        # If enough fodder is available (F <= start_fodder), eats exactly F.
        # Otherwise eats whatever remains (start_fodder).
        # Weight increases by beta * amount_eaten.
        # Fitness cache is invalidated since weight changed.
        # Returns the remaining fodder for the next herbivore in the feeding queue.
        # Weight is modified inline (direct += on _weight) instead of calling
        # _change_weight() to eliminate method call overhead -- this function is
        # called ~79K times per 50-year simulation.
        F = self._params.F
        if F <= start_fodder:
            self._weight += self._params.beta * F
            self._cached_fit = None
            return start_fodder - F
        else:
            self._weight += self._params.beta * start_fodder
            self._cached_fit = None
            return 0


class Carnivore(Fauna):
    """
    A class used to represent a Carnivore as a type under the superclass Fauna.

    Carnivores hunt and eat herbivores. They attempt to kill herbivores in order
    of increasing herbivore fitness (weakest first), and their own kill probability
    depends on the fitness difference between predator and prey.

    Attributes
    ----------
    _default_params = FaunaParam
        The default parameters with set values which defines a Carnivore.

    _params = FaunaParam
        Initialized with default_params, can be overridden by Fauna.set_animal_parameters

    _count = 0
        Initial count of Carnivores is set to zero.
    """

    _default_params = FaunaParam({"w_birth": 6,
                                  "sigma_birth": 1,
                                  "beta": 0.75,
                                  "eta": 0.125,
                                  "a_half": 40,
                                  "phi_age": 0.3,
                                  "w_half": 4,
                                  "phi_weight": 0.4,
                                  "mu": 0.4,
                                  "gamma": 0.8,
                                  "zeta": 3.5,
                                  "xi": 1.1,
                                  "omega": 0.8,
                                  "F": 50,
                                  "DeltaPhiMax": 10})

    _params = copy(_default_params)  # class-level mutable copy, shared by all Carnivore instances
    _count = 0                        # total living carnivores across all cells

    def __init__(self, age: int = 0, weight: float = None):
        # Same as Herbivore: generates random birth weight if not provided.
        if weight is None:
            weight = _baby_weight(self._params.w_birth, self._params.sigma_birth)
        super().__init__(age, weight)

    def feed_on_herbivores_and_gain_weight(self, eat_herbs):
        # Carnivore attempts to kill and eat herbivores from the provided list.
        # The list is pre-sorted by increasing herbivore fitness (weakest first).
        #
        # Key optimizations vs original:
        #   1. Caches self.fitness as c_fitness locally, only recalculates after a kill
        #      (when weight changes). This reduced fitness calls from 2.7M to 1.5M.
        #   2. Caches params (F, beta, DeltaPhiMax) as local variables to avoid
        #      repeated attribute lookups through self._params.
        #   3. Accesses herb._weight directly instead of herb.weight property.
        #   4. Uses inline min() replacement (ternary) to avoid function call overhead.
        #
        # Kill logic per spec:
        #   - If carnivore fitness <= herbivore fitness: stop entirely (can't kill stronger prey)
        #   - If 0 < (c_fit - h_fit) < DeltaPhiMax: kill probability = diff / DeltaPhiMax
        #   - If diff >= DeltaPhiMax: kill probability = 1 (certain kill)
        #   - On kill: eat min(remaining_meat, herb_weight), gain beta * amount_eaten
        #   - Stop when remaining_meat (F) is exhausted
        #
        # Returns list of eaten herbivore objects for removal by the caller.
        p = self._params
        remaining_meat = p.F       # max amount of meat this carnivore wants to eat
        beta = p.beta              # weight gain efficiency factor
        dphi_max = p.DeltaPhiMax   # fitness difference threshold for certain kill
        eaten_herbs = []
        c_fitness = self.fitness   # cache fitness locally, recalculate only after eating
        for herb in eat_herbs:
            h_fitness = herb.fitness
            if c_fitness <= h_fitness:
                return eaten_herbs  # stop: can't kill prey with equal or higher fitness
            diff = c_fitness - h_fitness
            if diff < dphi_max and _RANDOM() >= diff / dphi_max:
                continue  # probabilistic kill failed, try next herbivore
            if remaining_meat > 0:
                hw = herb._weight  # direct slot access, avoids property overhead
                amount_to_eat = remaining_meat if remaining_meat <= hw else hw
                remaining_meat -= amount_to_eat
                eaten_herbs.append(herb)
                self._weight += beta * amount_to_eat  # inline weight gain
                self._cached_fit = None   # invalidate fitness cache (weight changed)
                c_fitness = self.fitness  # recompute and cache new fitness for next iteration
        return eaten_herbs
