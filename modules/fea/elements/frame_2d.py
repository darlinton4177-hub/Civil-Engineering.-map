"""
2D Frame (Beam-Column) Element formulation with axial, shear, and bending interaction.
Formulated according to the Direct Stiffness Method (Przemieniecki / McGuire, Gallagher & Ziemian).
"""

from typing import Dict, Any
import numpy as np
from modules.fea.elements.base import Element
from modules.fea.core.node import Node
from modules.fea.core.material import Material
from modules.fea.core.section import Section


class Frame2DElement(Element):
    """
    2-Node 2D Frame Element with 6 Degrees of Freedom:
    [u1 (axial), v1 (transverse), theta1 (rotation), u2, v2, theta2]
    """

    def __init__(self, id: int, node_i: Node, node_j: Node, material: Material, section: Section):
        super().__init__(id, node_i, node_j, material, section)
        if self.length <= 1e-7:
            raise ValueError(f"Frame element #{id} has zero or degenerate length.")

    def local_stiffness_matrix(self) -> np.ndarray:
        """
        Calculates the 6x6 local stiffness matrix.
        [EA/L, 12EI/L^3, 6EI/L^2, 4EI/L, 2EI/L]
        """
        L = self.length
        E = self.material.E
        A = self.section.A
        I = self.section.Iz

        k_axial = (E * A) / L
        k_12 = (12.0 * E * I) / (L**3)
        k_6 = (6.0 * E * I) / (L**2)
        k_4 = (4.0 * E * I) / L
        k_2 = (2.0 * E * I) / L

        k = np.array([
            [k_axial,  0.0,   0.0, -k_axial,  0.0,   0.0],
            [ 0.0,    k_12,  k_6,   0.0,   -k_12,  k_6],
            [ 0.0,    k_6,   k_4,   0.0,   -k_6,   k_2],
            [-k_axial, 0.0,   0.0,  k_axial,  0.0,   0.0],
            [ 0.0,   -k_12, -k_6,   0.0,    k_12, -k_6],
            [ 0.0,    k_6,   k_2,   0.0,   -k_6,   k_4],
        ], dtype=float)
        return k

    def transformation_matrix(self) -> np.ndarray:
        """
        Calculates 6x6 transformation matrix [T] relating local to global coordinate systems.
        """
        theta = self.angle
        c = np.cos(theta)
        s = np.sin(theta)

        T = np.zeros((6, 6), dtype=float)
        # Node i block
        T[0, 0] = c
        T[0, 1] = s
        T[1, 0] = -s
        T[1, 1] = c
        T[2, 2] = 1.0
        # Node j block
        T[3, 3] = c
        T[3, 4] = s
        T[4, 3] = -s
        T[4, 4] = c
        T[5, 5] = 1.0
        return T

    def consistent_mass_matrix(self) -> np.ndarray:
        """
        Consistent 6x6 mass matrix for dynamic and modal eigenvalue analysis.
        rho * A * L / 420 * [CMM]
        """
        L = self.length
        rho = self.material.rho
        A = self.section.A
        factor = (rho * A * L) / 420.0

        m_local = factor * np.array([
            [140.0,   0.0,     0.0,   70.0,   0.0,     0.0],
            [  0.0, 156.0,  22.0*L,    0.0,  54.0, -13.0*L],
            [  0.0, 22.0*L, 4.0*L*L,   0.0, 13.0*L, -3.0*L*L],
            [ 70.0,   0.0,     0.0,  140.0,   0.0,     0.0],
            [  0.0,  54.0,  13.0*L,    0.0, 156.0, -22.0*L],
            [  0.0,-13.0*L,-3.0*L*L,   0.0,-22.0*L,  4.0*L*L],
        ], dtype=float)

        T = self.transformation_matrix()
        return T.T @ m_local @ T

    def geometric_stiffness_matrix(self, axial_force: float) -> np.ndarray:
        """
        Consistent 6x6 geometric stiffness matrix [k_g] for linear eigenvalue buckling analysis.
        P is axial force (Tension positive, compression negative).
        """
        L = self.length
        P = float(axial_force)
        factor = P / (30.0 * L)

        kg_local = factor * np.array([
            [0.0,   0.0,      0.0,  0.0,   0.0,      0.0],
            [0.0,  36.0,    3.0*L,  0.0, -36.0,    3.0*L],
            [0.0,  3.0*L, 4.0*L*L,  0.0, -3.0*L,   -L*L],
            [0.0,   0.0,      0.0,  0.0,   0.0,      0.0],
            [0.0, -36.0,   -3.0*L,  0.0,  36.0,   -3.0*L],
            [0.0,  3.0*L,   -L*L,   0.0, -3.0*L, 4.0*L*L],
        ], dtype=float)

        T = self.transformation_matrix()
        return T.T @ kg_local @ T

    def compute_internal_actions(self, global_displacements: np.ndarray) -> Dict[str, Any]:
        """
        Recovers local displacements, axial force (N), shear force (V), bending moments (M),
        and maximum normal, shear, and von Mises stresses along the element.
        """
        T = self.transformation_matrix()
        # Local displacements: u_local = [T] @ u_global
        u_local = T @ global_displacements
        k_local = self.local_stiffness_matrix()
        f_local = k_local @ u_local

        # Internal actions:
        # Node i: N1, V1, M1 (opposite of element end force on joint)
        N_i = -f_local[0]
        V_i = f_local[1]
        M_i = -f_local[2]

        N_j = f_local[3]
        V_j = -f_local[4]
        M_j = f_local[5]

        # Average axial force (positive = tension, negative = compression)
        N_avg = (N_j - N_i) / 2.0 if abs(N_j - N_i) > 1e-4 else N_j

        # Stresses:
        # Axial normal stress: sigma_axial = N / A
        sigma_axial = N_avg / self.section.A
        # Bending stress: sigma_bending = max(|M_i|, |M_j|) / Wel_z
        max_abs_M = max(abs(M_i), abs(M_j))
        sigma_bending = max_abs_M / self.section.Wel_z
        max_normal_stress = abs(sigma_axial) + sigma_bending

        # Shear stress: tau = 1.5 * V / A for rectangle, or V / Aw for I-beam
        tau_shear = 1.5 * max(abs(V_i), abs(V_j)) / self.section.A

        # von Mises equivalent stress: sigma_vm = sqrt(sigma^2 + 3 * tau^2)
        von_mises = np.sqrt(max_normal_stress**2 + 3.0 * tau_shear**2)

        return {
            "element_id": self.id,
            "length_m": round(self.length, 4),
            "local_displacements": u_local.tolist(),
            "axial_force_i_kN": round(N_i / 1e3, 3),
            "axial_force_j_kN": round(N_j / 1e3, 3),
            "shear_force_i_kN": round(V_i / 1e3, 3),
            "shear_force_j_kN": round(V_j / 1e3, 3),
            "bending_moment_i_kNm": round(M_i / 1e3, 3),
            "bending_moment_j_kNm": round(M_j / 1e3, 3),
            "max_bending_moment_kNm": round(max_abs_M / 1e3, 3),
            "sigma_axial_MPa": round(sigma_axial / 1e6, 2),
            "sigma_bending_MPa": round(sigma_bending / 1e6, 2),
            "max_normal_stress_MPa": round(max_normal_stress / 1e6, 2),
            "max_shear_stress_MPa": round(tau_shear / 1e6, 2),
            "von_mises_stress_MPa": round(von_mises / 1e6, 2),
            "stress_utilization": round(von_mises / self.material.fy, 3) if self.material.fy else None,
        }
