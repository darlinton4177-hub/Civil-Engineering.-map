"""
Abstract base class for finite elements.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple
import numpy as np
from modules.fea.core.node import Node
from modules.fea.core.material import Material
from modules.fea.core.section import Section


class Element(ABC):
    """Abstract Finite Element specification."""

    def __init__(self, id: int, node_i: Node, node_j: Node, material: Material, section: Section):
        self.id = int(id)
        self.node_i = node_i
        self.node_j = node_j
        self.material = material
        self.section = section

    @property
    def length(self) -> float:
        dx = self.node_j.x - self.node_i.x
        dy = self.node_j.y - self.node_i.y
        dz = self.node_j.z - self.node_i.z
        return float(np.sqrt(dx**2 + dy**2 + dz**2))

    @property
    def angle(self) -> float:
        """2D planar orientation angle in radians."""
        dx = self.node_j.x - self.node_i.x
        dy = self.node_j.y - self.node_i.y
        return float(np.arctan2(dy, dx))

    @abstractmethod
    def local_stiffness_matrix(self) -> np.ndarray:
        """Element stiffness matrix in local coordinate system."""
        pass

    @abstractmethod
    def transformation_matrix(self) -> np.ndarray:
        """Coordinate transformation matrix from local to global DOFs."""
        pass

    def global_stiffness_matrix(self) -> np.ndarray:
        """Element stiffness matrix transformed to global coordinate system: [K_g] = [T]^T [k_l] [T]."""
        T = self.transformation_matrix()
        k_local = self.local_stiffness_matrix()
        return T.T @ k_local @ T

    @abstractmethod
    def consistent_mass_matrix(self) -> np.ndarray:
        """Consistent element mass matrix in global coordinates."""
        pass

    @abstractmethod
    def geometric_stiffness_matrix(self, axial_force: float) -> np.ndarray:
        """Element geometric stiffness matrix for buckling eigenvalue analysis."""
        pass

    @abstractmethod
    def compute_internal_actions(self, global_displacements: np.ndarray) -> Dict[str, Any]:
        """Recovers local internal forces (N, V, M) and stress tensors."""
        pass
