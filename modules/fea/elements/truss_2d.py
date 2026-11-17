"""
2D Pin-jointed Truss element (axial member with zero moment capacity).
"""

from typing import Dict, Any
import numpy as np
from modules.fea.elements.base import Element
from modules.fea.core.node import Node
from modules.fea.core.material import Material
from modules.fea.core.section import Section


class Truss2DElement(Element):
    """
    2-Node 2D Pin-jointed Truss Element with 4 Degrees of Freedom:
    [u1 (global x), v1 (global y), u2, v2]
    """

    def __init__(self, id: int, node_i: Node, node_j: Node, material: Material, section: Section):
        super().__init__(id, node_i, node_j, material, section)

    def local_stiffness_matrix(self) -> np.ndarray:
        L = self.length
        k_axial = (self.material.E * self.section.A) / L
        return np.array([
            [ k_axial, 0.0, -k_axial, 0.0],
            [ 0.0,     0.0,  0.0,     0.0],
            [-k_axial, 0.0,  k_axial, 0.0],
            [ 0.0,     0.0,  0.0,     0.0],
        ], dtype=float)

    def transformation_matrix(self) -> np.ndarray:
        theta = self.angle
        c = np.cos(theta)
        s = np.sin(theta)
        return np.array([
            [ c, s, 0, 0],
            [-s, c, 0, 0],
            [ 0, 0, c, s],
            [ 0, 0,-s, c],
        ], dtype=float)

    def consistent_mass_matrix(self) -> np.ndarray:
        L = self.length
        m_total = self.material.rho * self.section.A * L
        m_local = (m_total / 6.0) * np.array([
            [2.0, 0.0, 1.0, 0.0],
            [0.0, 2.0, 0.0, 1.0],
            [1.0, 0.0, 2.0, 0.0],
            [0.0, 1.0, 0.0, 2.0],
        ], dtype=float)
        T = self.transformation_matrix()
        return T.T @ m_local @ T

    def geometric_stiffness_matrix(self, axial_force: float) -> np.ndarray:
        L = self.length
        P = float(axial_force)
        kg_local = (P / L) * np.array([
            [0.0,  0.0,  0.0,  0.0],
            [0.0,  1.0,  0.0, -1.0],
            [0.0,  0.0,  0.0,  0.0],
            [0.0, -1.0,  0.0,  1.0],
        ], dtype=float)
        T = self.transformation_matrix()
        return T.T @ kg_local @ T

    def compute_internal_actions(self, global_displacements: np.ndarray) -> Dict[str, Any]:
        """Recovers axial force N and axial stress."""
        T = self.transformation_matrix()
        u_local = T @ global_displacements
        delta_L = u_local[2] - u_local[0]
        strain = delta_L / self.length
        stress = self.material.E * strain
        axial_force = stress * self.section.A

        is_tension = axial_force >= 0
        von_mises = abs(stress)

        return {
            "element_id": self.id,
            "length_m": round(self.length, 4),
            "elongation_mm": round(delta_L * 1e3, 4),
            "strain": round(strain, 6),
            "axial_force_kN": round(axial_force / 1e3, 3),
            "state": "Tension" if is_tension else "Compression",
            "normal_stress_MPa": round(stress / 1e6, 2),
            "von_mises_stress_MPa": round(von_mises / 1e6, 2),
            "stress_utilization": round(von_mises / self.material.fy, 3) if self.material.fy else None,
        }
