"""Closed-form Kirchhoff-Love plate model and the piezoresistive signal chain.

Every quantity the laboratories compute numerically has a counterpart here.
Laboratory 3 compares the two.

Reference: Timoshenko, S. P., & Woinowsky-Krieger, S. (1959).
Theory of plates and shells (2nd ed.). McGraw-Hill.
"""
from dataclasses import dataclass

# Clamped square plate coefficients (Timoshenko & Woinowsky-Krieger, Table 35).
ALPHA = 0.00126   # central deflection
BETA = 0.0513     # edge-midpoint bending moment

# p-type piezoresistive coefficients, <110> on a (100) wafer [Pa^-1].
PI_L = +71.8e-11
PI_T = -66.3e-11

# Single-crystal silicon, isotropic approximation used throughout the sequence.
E_SI = 169e9      # Young's modulus [Pa]
NU_SI = 0.28      # Poisson ratio


@dataclass(frozen=True)
class Diaphragm:
    """A clamped square silicon diaphragm carrying a full Wheatstone bridge.

    a : side length [m]
    h : thickness [m]
    E : Young's modulus [Pa]
    nu: Poisson ratio
    """
    a: float
    h: float
    E: float = E_SI
    nu: float = NU_SI

    @property
    def D(self) -> float:
        """Flexural rigidity [N m], Equation (2)."""
        return self.E * self.h ** 3 / (12.0 * (1.0 - self.nu ** 2))

    def w_max(self, q: float) -> float:
        """Central deflection under uniform pressure q [Pa], Equation (3)."""
        return ALPHA * q * self.a ** 4 / self.D

    def m_max(self, q: float) -> float:
        """Edge-midpoint bending moment per unit width [N], Equation (4)."""
        return BETA * q * self.a ** 2

    def edge_stress(self, q: float) -> tuple[float, float]:
        """Surface stress at an edge midpoint, Equation (5).

        Returns (sigma_L, sigma_T) in Pa: the component normal to the edge and
        the in-plane component parallel to it.
        """
        sigma_l = 6.0 * self.m_max(q) / self.h ** 2
        return sigma_l, self.nu * sigma_l

    def small_deflection_ok(self, q: float, limit: float = 0.2) -> bool:
        """Thin-plate validity check: w_max / h must stay below `limit`."""
        return self.w_max(q) / self.h < limit

    def resistance_change(self, q: float) -> tuple[float, float]:
        """Fractional resistance change of the two bridge arms, Equation (6).

        The `long` arm carries current normal to the edge, the `trans` arm
        parallel to it, so the two respond with opposite sign.
        """
        s_l, s_t = self.edge_stress(q)
        return (PI_L * s_l + PI_T * s_t,      # long
                PI_L * s_t + PI_T * s_l)      # trans

    def bridge_output(self, q: float) -> float:
        """Normalised full-bridge output V_out / V_in [V/V], Equation (7)."""
        dr_long, dr_trans = self.resistance_change(q)
        return 0.5 * (dr_long - dr_trans)

    def sensitivity(self, q: float) -> float:
        """Pressure sensitivity [V/V/Pa], Equation (8)."""
        return self.bridge_output(q) / q


#: The reference design used throughout the notebooks and the paper.
REFERENCE = Diaphragm(a=1000e-6, h=20e-6)
REFERENCE_PRESSURE = 100e3  # Pa
