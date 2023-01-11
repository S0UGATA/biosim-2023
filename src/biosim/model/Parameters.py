# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU


class Parameters:
    pass


class FaunaParam(Parameters):
    def __init__(self,
                 w_birth,
                 sigma_birth,
                 beta,
                 eta,
                 a_half,
                 phi_age,
                 w_half,
                 phi_weight,
                 mu,
                 gamma,
                 zeta,
                 xi,
                 omega,
                 F,
                 DeltaPhiMax):
        self.w_birth = w_birth
        self.sigma_birth = sigma_birth
        self.beta = beta
        self.eta = eta
        self.a_half = a_half
        self.phi_age = phi_age
        self.w_half = w_half
        self.phi_weight = phi_weight
        self.mu = mu
        self.gamma = gamma
        self.zeta = zeta
        self.xi = xi
        self.omega = omega
        self.F = F
        self.DeltaPhiMax = DeltaPhiMax


class GeoParam(Parameters):
    def __init__(self, f_max):
        self.f_max = f_max
