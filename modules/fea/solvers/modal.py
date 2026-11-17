"""
Modal Eigenvalue Solver for Natural Frequencies and Mode Shapes (Pure NumPy Engine).
Solves the generalized undamped eigenvalue problem: ([K] - omega^2 [M]) {phi} = 0
"""

from typing import Dict, Any, List
import numpy as np
from modules.fea.core.node import Node
from modules.fea.elements.base import Element
from modules.fea.elements.frame_2d import Frame2DElement


class ModalSolver:
    """Calculates natural frequencies, periods, and mode shapes."""

    def __init__(self, nodes: List[Node], elements: List[Element], num_modes: int = 5):
        self.nodes = sorted(nodes, key=lambda n: n.id)
        self.elements = sorted(elements, key=lambda e: e.id)
        self.node_id_map = {n.id: idx for idx, n in enumerate(self.nodes)}
        self.num_modes = int(num_modes)

        self.dofs_per_node = 3 if any(isinstance(e, Frame2DElement) for e in self.elements) else 2
        self.total_dofs = len(self.nodes) * self.dofs_per_node

    def _get_element_dofs(self, elem: Element) -> List[int]:
        idx_i = self.node_id_map[elem.node_i.id]
        idx_j = self.node_id_map[elem.node_j.id]
        dofs = []
        for i in range(self.dofs_per_node):
            dofs.append(idx_i * self.dofs_per_node + i)
        for j in range(self.dofs_per_node):
            dofs.append(idx_j * self.dofs_per_node + j)
        return dofs

    def assemble_matrices(self):
        K = np.zeros((self.total_dofs, self.total_dofs), dtype=float)
        M = np.zeros((self.total_dofs, self.total_dofs), dtype=float)

        for elem in self.elements:
            elem_dofs = self._get_element_dofs(elem)
            k_elem = elem.global_stiffness_matrix()
            m_elem = elem.consistent_mass_matrix()
            for r_idx, r in enumerate(elem_dofs):
                for c_idx, c in enumerate(elem_dofs):
                    K[r, c] += k_elem[r_idx, c_idx]
                    M[r, c] += m_elem[r_idx, c_idx]

        return K, M

    def solve(self) -> Dict[str, Any]:
        K, M = self.assemble_matrices()

        # Extract free DOFs
        free_dofs = []
        for n in self.nodes:
            idx = self.node_id_map[n.id]
            for d in range(self.dofs_per_node):
                if d >= len(n.restraints) or not n.restraints[d]:
                    free_dofs.append(idx * self.dofs_per_node + d)

        if len(free_dofs) == 0:
            raise ValueError("All degrees of freedom are restrained.")

        K_ff = K[np.ix_(free_dofs, free_dofs)]
        M_ff = M[np.ix_(free_dofs, free_dofs)]

        # Regularize diagonal of M if necessary (rotational DOFs with zero lumped mass)
        diag_m = np.diag(M_ff)
        zero_mass_indices = np.where(diag_m <= 1e-12)[0]
        if len(zero_mass_indices) > 0:
            avg_mass = np.mean(diag_m[diag_m > 1e-12]) if np.any(diag_m > 1e-12) else 1.0
            for idx in zero_mass_indices:
                M_ff[idx, idx] = avg_mass * 1e-4

        # Solve standard dynamic matrix: DynamicMatrix = M_ff^(-1) @ K_ff
        # (K_ff * phi = lambda * M_ff * phi) => (M_ff^-1 * K_ff) * phi = lambda * phi
        try:
            M_inv = np.linalg.inv(M_ff)
            Dyn = M_inv @ K_ff
            eigenvalues, eigenvectors = np.linalg.eig(Dyn)

            # Filter real, positive eigenvalues
            real_mask = np.isreal(eigenvalues) & (np.real(eigenvalues) > 1e-6)
            valid_evals = np.real(eigenvalues[real_mask])
            valid_evecs = np.real(eigenvectors[:, real_mask])

            sort_order = np.argsort(valid_evals)
            valid_evals = valid_evals[sort_order]
            valid_evecs = valid_evecs[:, sort_order]

            num_found = min(len(valid_evals), self.num_modes)
            modes = []

            for m_idx in range(num_found):
                omega = float(np.sqrt(valid_evals[m_idx]))
                freq_hz = float(omega / (2.0 * np.pi))
                period_s = float(1.0 / freq_hz) if freq_hz > 0 else 0.0

                full_mode_shape = np.zeros(self.total_dofs, dtype=float)
                full_mode_shape[free_dofs] = valid_evecs[:, m_idx]

                max_amp = np.max(np.abs(full_mode_shape))
                if max_amp > 1e-12:
                    full_mode_shape /= max_amp

                node_shapes = []
                for n in self.nodes:
                    idx = self.node_id_map[n.id]
                    d_start = idx * self.dofs_per_node
                    node_shapes.append({
                        "node_id": n.id,
                        "x": n.x,
                        "y": n.y,
                        "dx": round(float(full_mode_shape[d_start]), 4),
                        "dy": round(float(full_mode_shape[d_start + 1]), 4),
                        "rz": round(float(full_mode_shape[d_start + 2]), 4) if self.dofs_per_node >= 3 else 0.0,
                    })

                modes.append({
                    "mode_number": m_idx + 1,
                    "angular_frequency_rad_s": round(omega, 3),
                    "natural_frequency_hz": round(freq_hz, 3),
                    "period_seconds": round(period_s, 4),
                    "mode_shape": node_shapes,
                })

            return {
                "status": "success",
                "solver": "modal_eigenvalue_fea",
                "modes_calculated": len(modes),
                "modes": modes,
            }
        except Exception as e:
            raise ValueError(f"Modal eigenvalue extraction failed: {e}")
