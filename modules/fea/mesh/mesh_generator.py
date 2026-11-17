"""
Interactive Mesh Generation Laboratory & Convergence Engine.
Complies with Section 3: Interactive Mesh Generation Laboratory.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
from modules.fea.core.node import Node
from modules.fea.core.material import Material
from modules.fea.core.section import Section
from modules.fea.elements.frame_2d import Frame2DElement
from modules.fea.elements.truss_2d import Truss2DElement
from modules.fea.solvers.linear_static import LinearStaticSolver


class MeshGenerator:
    """Discretizes geometric frame/truss lines into finite element meshes."""

    @staticmethod
    def discretize_member(
        start_node: Node,
        end_node: Node,
        num_subdivisions: int,
        material: Material,
        section: Section,
        start_node_id: int,
        start_elem_id: int,
        element_type: str = "frame",
    ) -> Tuple[List[Node], List[Any]]:
        """
        Subdivides a physical member between start_node and end_node into N finite elements.
        """
        if num_subdivisions < 1:
            raise ValueError("Number of subdivisions must be at least 1.")

        x0, y0 = start_node.x, start_node.y
        x1, y1 = end_node.x, end_node.y

        generated_nodes = [start_node]
        generated_elements = []

        current_node_id = start_node_id

        # Create intermediate internal nodes
        for i in range(1, num_subdivisions):
            fraction = i / float(num_subdivisions)
            xi = x0 + fraction * (x1 - x0)
            yi = y0 + fraction * (y1 - y0)
            node = Node(
                id=current_node_id,
                x=round(xi, 4),
                y=round(yi, 4),
                restraints=[False, False, False],
                loads=[0.0, 0.0, 0.0],
            )
            generated_nodes.append(node)
            current_node_id += 1

        generated_nodes.append(end_node)

        # Create elements connecting consecutive nodes
        for i in range(num_subdivisions):
            ni = generated_nodes[i]
            nj = generated_nodes[i + 1]
            elem_id = start_elem_id + i
            if element_type == "truss":
                elem = Truss2DElement(id=elem_id, node_i=ni, node_j=nj, material=material, section=section)
            else:
                elem = Frame2DElement(id=elem_id, node_i=ni, node_j=nj, material=material, section=section)
            generated_elements.append(elem)

        # Remove start and end from generated_nodes list to return strictly new intermediate nodes if requested,
        # or return full node chain:
        return generated_nodes, generated_elements

    @staticmethod
    def run_convergence_study(
        span_length_m: float,
        point_load_N: float,
        material: Material,
        section: Section,
        mesh_densities: List[int] = [1, 2, 4, 8, 16, 32],
    ) -> Dict[str, Any]:
        """
        Executes a formal mesh refinement convergence study for a cantilever or simply-supported beam.
        Compares numerical FEA solution against exact theoretical closed-form continuum solution:
        Exact tip deflection delta_exact = P * L^3 / (3 * E * I)
        """
        L = float(span_length_m)
        P = float(point_load_N)
        EI = material.E * section.Iz
        delta_exact = (P * (L**3)) / (3.0 * EI)

        study_data = []

        for div in mesh_densities:
            # Create cantilever fixed at x=0, tip load at x=L
            n_start = Node(id=1, x=0.0, y=0.0, restraints=[True, True, True])
            n_end = Node(id=div + 1, x=L, y=0.0, restraints=[False, False, False], loads=[0.0, -P, 0.0])

            nodes, elements = MeshGenerator.discretize_member(
                start_node=n_start,
                end_node=n_end,
                num_subdivisions=div,
                material=material,
                section=section,
                start_node_id=2,
                start_elem_id=1,
                element_type="frame",
            )

            solver = LinearStaticSolver(nodes, elements)
            res = solver.solve()
            tip_node = [nr for nr in res["nodes"] if nr["node_id"] == n_end.id][0]
            tip_disp = abs(tip_node["dy_mm"]) / 1e3  # in meters
            error_percent = abs(tip_disp - delta_exact) / delta_exact * 100.0

            study_data.append({
                "subdivisions": div,
                "num_nodes": len(nodes),
                "num_elements": len(elements),
                "tip_deflection_mm": round(tip_disp * 1e3, 4),
                "exact_deflection_mm": round(delta_exact * 1e3, 4),
                "relative_error_percent": round(error_percent, 4),
                "max_stress_MPa": res["summary_results"]["max_von_mises_stress_MPa"],
            })

        return {
            "status": "success",
            "study_type": "cantilever_mesh_refinement_convergence",
            "exact_theoretical_deflection_mm": round(delta_exact * 1e3, 4),
            "convergence_table": study_data,
        }
