# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Tonje, Sougata / NMBU


class Parameters:
    pass


class Fauna(Parameters):
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
        self._w_birth = w_birth
        self._sigma_birth = sigma_birth
        self._beta = beta
        self._eta = eta
        self._a_half = a_half
        self._phi_age = phi_age
        self._w_half = w_half
        self._phi_weight = phi_weight
        self._mu = mu
        self._gamma = gamma
        self._zeta = zeta
        self._xi = xi
        self._omega = omega
        self._F = F
        self._DeltaPhiMax = DeltaPhiMax

    @property
    def phi_age(self):
        return self._phi_age

    @property
    def a_half(self):
        return self._a_half

    @property
    def phi_weight(self):
        return self._phi_weight

    @property
    def w_half(self):
        return self._w_half


class Geography(Parameters):
    def __init__(self, f_max):
        self._f_max = f_max

    @property
    def f_max(self):
        return self._f_max
