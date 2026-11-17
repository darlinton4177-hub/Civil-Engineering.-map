"""
Direct Stiffness Linear Static FEA Solver for 2D Frames and Trusses.
Complies with CALCULATION_CONTRACT.md.
"""

from typing import Dict, Any, List
import numpy as np
from modules.fea.core.node import Node
from modules.fea.elements.base import Element
from modules.fea.elements.frame_2d import Frame2DElement
from modules.fea.elements.truss_2d import Truss2DElement


class LinearStaticSolver:
    """Solves [K]{U} = {F} for arbitrary 2D structural networks."""

    def __init__(self, nodes: List[Node], elements: List[Element]):
        if not nodes:
            raise ValueError("FEA model must contain at least 1 node.")
        if not elements:
            raise ValueError("FEA model must contain at least 1 element.")

        self.nodes = sorted(nodes, key=lambda n: n.id)
        self.elements = sorted(elements, key=lambda e: e.id)
        self.node_id_map = {n.id: idx for idx, n in enumerate(self.nodes)}

        # Determine DOFs per node (3 for frames, 2 for trusses)
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

    def assemble_global_stiffness(self) -> np.ndarray:
        """Assembles the global structural stiffness matrix [K]."""
        K = np.zeros((self.total_dofs, self.total_dofs), dtype=float)
        for elem in self.elements:
            k_elem = elem.global_stiffness_matrix()
            elem_dofs = self._get_element_dofs(elem)
            for r_idx, r in enumerate(elem_dofs):
                for c_idx, c in enumerate(elem_dofs):
                    K[r, c] += k_elem[r_idx, c_idx]
        return K

    def assemble_global_forces(self) -> np.ndarray:
        """Assembles the global applied load vector {F}."""
        F = np.zeros(self.total_dofs, dtype=float)
        for n in self.nodes:
            idx = self.node_id_map[n.id]
            for d in range(self.dofs_per_node):
                if d < len(n.loads):
                    F[idx * self.dofs_per_node + d] += n.loads[d]
        return F

    def solve(self) -> Dict[str, Any]:
        """Executes direct stiffness solution and post-processes internal actions."""
        K = self.assemble_global_stiffness()
        F = self.assemble_global_forces()

        # Identify boundary conditions
        restrained_dofs = []
        free_dofs = []

        for n in self.nodes:
            idx = self.node_id_map[n.id]
            for d in range(self.dofs_per_node):
                global_dof = idx * self.dofs_per_node + d
                if d < len(n.restraints) and n.restraints[d]:
                    restrained_dofs.append(global_dof)
                else:
                    free_dofs.append(global_dof)

        if not restrained_dofs:
            raise ValueError("Structure is unstable: no supports or boundary conditions defined.")
        if len(free_dofs) == 0:
            raise ValueError("All degrees of freedom are fully fixed.")

        # Partition matrix:
        # [K_ff  K_fr] [U_f]   [F_f]
        # [K_rf  K_rr] [U_r] = [F_r + R]
        K_ff = K[np.ix_(free_dofs, free_dofs)]
        F_f = F[free_dofs]

        # Check conditioning / singularity
        cond = np.linalg.cond(K_ff)
        if cond > 1e16 or np.isnan(cond):
            raise ValueError("Stiffness matrix is singular. The structure contains unconstrained rigid body mechanisms.")

        # Solve for free displacements
        U_f = np.linalg.solve(K_ff, F_f)

        # Full global displacement vector
        U = np.zeros(self.total_dofs, dtype=float)
        U[free_dofs] = U_f

        # Compute support reactions: R = K_rf @ U_f - F_r
        reactions = np.zeros(self.total_dofs, dtype=float)
        if restrained_dofs:
            K_rf = K[np.ix_(restrained_dofs, free_dofs)]
            F_r = F[restrained_dofs]
            R_vals = K_rf @ U_f - F_r
            reactions[restrained_dofs] = R_vals

        # Post-process nodal results
        node_results = []
        for n in self.nodes:
            idx = self.node_id_map[n.id]
            d_start = idx * self.dofs_per_node
            u_x = U[d_start]
            u_y = U[d_start + 1]
            theta_z = U[d_start + 2] if self.dofs_per_node >= 3 else 0.0

            r_x = reactions[d_start]
            r_y = reactions[d_start + 1]
            r_mz = reactions[d_start + 2] if self.dofs_per_node >= 3 else 0.0

            node_results.append({
                "node_id": n.id,
                "x": n.x,
                "y": n.y,
                "dx_mm": round(u_x * 1e3, 4),
                "dy_mm": round(u_y * 1e3, 4),
                "rotation_mrad": round(theta_z * 1e3, 4),
                "total_disp_mm": round(np.sqrt(u_x**2 + u_y**2) * 1e3, 4),
                "Rx_kN": round(r_x / 1e3, 3),
                "Ry_kN": round(r_y / 1e3, 3),
                "R_Mz_kNm": round(r_mz / 1e3, 3),
            })

        # Post-process element internal actions and stresses
        element_results = []
        max_von_mises = 0.0
        max_disp_mm = max(nr["total_disp_mm"] for nr in node_results)

        for elem in self.elements:
            elem_dofs = self._get_element_dofs(elem)
            u_elem = U[elem_dofs]
            actions = elem.compute_internal_actions(u_elem)
            element_results.append(actions)
            if actions.get("von_mises_stress_MPa", 0.0) > max_von_mises:
                max_von_mises = actions["von_mises_stress_MPa"]

        # Global Equilibrium Verification
        total_applied_Fx = sum(n.loads[0] for n in self.nodes)
        total_applied_Fy = sum(n.loads[1] for n in self.nodes)
        total_reaction_Fx = sum(reactions[idx * self.dofs_per_node] for idx in range(len(self.nodes)))
        total_reaction_Fy = sum(reactions[idx * self.dofs_per_node + 1] for idx in range(len(self.nodes)))

        equilibrium_Fx = bool(abs(total_applied_Fx + total_reaction_Fx) < 1e-2)
        equilibrium_Fy = bool(abs(total_applied_Fy + total_reaction_Fy) < 1e-2)

        return {
            "status": "success",
            "solver": "linear_static_fea",
            "model_summary": {
                "num_nodes": len(self.nodes),
                "num_elements": len(self.elements),
                "total_dofs": self.total_dofs,
                "free_dofs": len(free_dofs),
                "restrained_dofs": len(restrained_dofs),
                "matrix_condition_number": float(f"{cond:.2e}"),
            },
            "summary_results": {
                "max_displacement_mm": round(max_disp_mm, 4),
                "max_von_mises_stress_MPa": round(max_von_mises, 2),
                "total_vertical_reaction_kN": round(total_reaction_Fy / 1e3, 3),
                "total_horizontal_reaction_kN": round(total_reaction_Fx / 1e3, 3),
            },
            "checks": {
                "global_Fx_equilibrium": equilibrium_Fx,
                "global_Fy_equilibrium": equilibrium_Fy,
                "no_rigid_body_mechanisms": True,
            },
            "nodes": node_results,
            "elements": element_results,
        }
