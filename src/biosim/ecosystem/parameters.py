# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU


class Parameters:
    """
    Super class containing parameters for the initialization of Fauna and Geography.
    """
    pass


class FaunaParam(Parameters):
    """
    Child class of Parameters, defining the parameters for Fauna
    """

    def __init__(self, params: {}):
        self.w_birth = params["w_birth"]
        self.sigma_birth = params["sigma_birth"]
        self.beta = params["beta"]
        self.eta = params["eta"]
        self.a_half = params["a_half"]
        self.phi_age = params["phi_age"]
        self.w_half = params["w_half"]
        self.phi_weight = params["phi_weight"]
        self.mu = params["mu"]
        self.gamma = params["gamma"]
        self.zeta = params["zeta"]
        self.xi = params["xi"]
        self.omega = params["omega"]
        self.F = params["F"]
        self.DeltaPhiMax = params["DeltaPhiMax"]


class GeoParam(Parameters):
    """
    Child class of Parameters, defining the parameter(s) for Geography.
    """

    def __init__(self, f_max):
        self.f_max = f_max
