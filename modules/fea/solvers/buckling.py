"""
Linear Elastic Buckling Eigenvalue Solver (Pure NumPy Engine).
Evaluates critical buckling load factor lambda_cr and buckling mode shapes:
([K] - lambda_cr * [K_g]) {v} = 0
"""

from typing import Dict, Any, List
import numpy as np
from modules.fea.core.node import Node
from modules.fea.elements.base import Element
from modules.fea.elements.frame_2d import Frame2DElement
from modules.fea.solvers.linear_static import LinearStaticSolver


class BucklingSolver:
    """Calculates critical buckling multiplier and buckling mode shapes."""

    def __init__(self, nodes: List[Node], elements: List[Element], num_modes: int = 3):
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

    def solve(self) -> Dict[str, Any]:
        # Step 1: Pre-buckling linear static stress analysis
        static_solver = LinearStaticSolver(self.nodes, self.elements)
        static_results = static_solver.solve()
        elem_actions = {ea["element_id"]: ea for ea in static_results["elements"]}

        K = static_solver.assemble_global_stiffness()
        Kg = np.zeros((self.total_dofs, self.total_dofs), dtype=float)

        # Assemble global geometric stiffness matrix [Kg]
        for elem in self.elements:
            elem_dofs = self._get_element_dofs(elem)
            act = elem_actions.get(elem.id, {})
            N_kN = act.get("axial_force_j_kN", 0.0)
            P_axial = N_kN * 1e3
            kg_elem = elem.geometric_stiffness_matrix(P_axial)

            for r_idx, r in enumerate(elem_dofs):
                for c_idx, c in enumerate(elem_dofs):
                    Kg[r, c] += kg_elem[r_idx, c_idx]

        # Extract free DOFs
        free_dofs = []
        for n in self.nodes:
            idx = self.node_id_map[n.id]
            for d in range(self.dofs_per_node):
                if d >= len(n.restraints) or not n.restraints[d]:
                    free_dofs.append(idx * self.dofs_per_node + d)

        K_ff = K[np.ix_(free_dofs, free_dofs)]
        Kg_ff = -Kg[np.ix_(free_dofs, free_dofs)]

        # Check if compressive members exist
        diag_kg = np.diag(Kg_ff)
        if np.all(diag_kg <= 1e-12):
            return {
                "status": "inapplicable",
                "message": "No structural members are under compression under the applied loads.",
                "buckling_modes": [],
            }

        # Solve generalized eigenvalue problem via matrix inversion:
        # K_ff * v = lambda * Kg_ff * v  => (K_ff^-1 * Kg_ff) * v = (1 / lambda) * v
        try:
            K_inv = np.linalg.inv(K_ff)
            A = K_inv @ Kg_ff
            eigenvalues_mu, eigenvectors = np.linalg.eig(A)

            # mu = 1 / lambda => lambda = 1 / mu
            real_mask = np.isreal(eigenvalues_mu) & (np.real(eigenvalues_mu) > 1e-9)
            valid_mus = np.real(eigenvalues_mu[real_mask])
            valid_evecs = np.real(eigenvectors[:, real_mask])

            valid_lambdas = 1.0 / valid_mus
            sort_order = np.argsort(valid_lambdas)
            valid_lambdas = valid_lambdas[sort_order]
            valid_evecs = valid_evecs[:, sort_order]

            buckling_modes = []
            num_found = min(len(valid_lambdas), self.num_modes)

            for m_idx in range(num_found):
                lambda_cr = float(valid_lambdas[m_idx])
                full_shape = np.zeros(self.total_dofs, dtype=float)
                full_shape[free_dofs] = valid_evecs[:, m_idx]

                max_val = np.max(np.abs(full_shape))
                if max_val > 1e-12:
                    full_shape /= max_val

                node_shapes = []
                for n in self.nodes:
                    idx = self.node_id_map[n.id]
                    d_start = idx * self.dofs_per_node
                    node_shapes.append({
                        "node_id": n.id,
                        "x": n.x,
                        "y": n.y,
                        "dx": round(float(full_shape[d_start]), 4),
                        "dy": round(float(full_shape[d_start + 1]), 4),
                    })

                buckling_modes.append({
                    "mode_number": m_idx + 1,
                    "critical_load_factor": round(lambda_cr, 3),
                    "description": f"Buckling Load Multiplier: {lambda_cr:.2f}x applied reference load",
                    "buckling_shape": node_shapes,
                })

            return {
                "status": "success",
                "solver": "linear_buckling_fea",
                "critical_load_factor": buckling_modes[0]["critical_load_factor"] if buckling_modes else None,
                "buckling_modes": buckling_modes,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Buckling eigenvalue solver failed: {e}",
                "buckling_modes": [],
            }
