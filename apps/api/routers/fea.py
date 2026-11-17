"""
FastAPI FEA Simulation Router for Engineer Realm.
Exposes Linear Static, Modal Dynamic, Buckling Eigenvalue, and Mesh Convergence Endpoints.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from packages.domain.project_model import EngineeringProject
from modules.fea.core.material import Material, STANDARD_MATERIALS
from modules.fea.core.section import Section, STANDARD_SECTIONS
from modules.fea.core.node import Node
from modules.fea.elements.frame_2d import Frame2DElement
from modules.fea.elements.truss_2d import Truss2DElement
from modules.fea.solvers.linear_static import LinearStaticSolver
from modules.fea.solvers.modal import ModalSolver
from modules.fea.solvers.buckling import BucklingSolver
from modules.fea.mesh.mesh_generator import MeshGenerator

router = APIRouter(prefix="/fea", tags=["FEA Simulation Laboratory"])


def _build_fea_model(project: EngineeringProject):
    """Instantiates runtime domain objects from serialized project model."""
    # 1. Materials map
    mat_map: Dict[str, Material] = {}
    for pm in project.materials:
        mat_map[pm.id] = Material(
            id=pm.id,
            name=pm.name,
            elastic_modulus_pa=pm.elastic_modulus_pa,
            poissons_ratio=pm.poissons_ratio,
            density_kg_m3=pm.density_kg_m3,
            yield_strength_pa=pm.yield_strength_pa,
        )
    # Include standard materials if referenced
    for k, v in STANDARD_MATERIALS.items():
        if k not in mat_map:
            mat_map[k] = v

    # 2. Sections map
    sec_map: Dict[str, Section] = {}
    for ps in project.sections:
        sec_map[ps.id] = Section(
            id=ps.id,
            name=ps.name,
            area_m2=ps.area_m2,
            I_strong_m4=ps.I_strong_m4,
            I_weak_m4=ps.I_weak_m4,
            torsional_constant_j_m4=ps.torsional_constant_j_m4,
            depth_m=ps.depth_m,
            width_m=ps.width_m,
        )
    for k, v in STANDARD_SECTIONS.items():
        if k not in sec_map:
            sec_map[k] = v

    # 3. Nodes map
    node_map: Dict[int, Node] = {}
    for pn in project.nodes:
        node_map[pn.id] = Node(
            id=pn.id,
            x=pn.x,
            y=pn.y,
            z=pn.z,
            restraints=pn.restraints,
            loads=pn.loads,
        )

    # 4. Elements list
    elements = []
    for pe in project.elements:
        if pe.node_i_id not in node_map or pe.node_j_id not in node_map:
            raise HTTPException(
                status_code=422,
                detail=f"Element #{pe.id} connects undefined node IDs ({pe.node_i_id}, {pe.node_j_id})."
            )
        ni = node_map[pe.node_i_id]
        nj = node_map[pe.node_j_id]

        mat = mat_map.get(pe.material_id)
        if not mat:
            mat = STANDARD_MATERIALS["steel-s355"]

        sec = sec_map.get(pe.section_id)
        if not sec:
            sec = STANDARD_SECTIONS["ub-305x127x42"]

        if pe.element_type == "truss":
            elem = Truss2DElement(id=pe.id, node_i=ni, node_j=nj, material=mat, section=sec)
        else:
            elem = Frame2DElement(id=pe.id, node_i=ni, node_j=nj, material=mat, section=sec)
        elements.append(elem)

    return list(node_map.values()), elements


@router.post("/solve")
def run_linear_static_analysis(project: EngineeringProject):
    """Executes linear static FEA simulation and recovers displacements and stress fields."""
    try:
        nodes, elements = _build_fea_model(project)
        solver = LinearStaticSolver(nodes, elements)
        results = solver.solve()
        return results
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err))


@router.post("/modal")
def run_modal_analysis(project: EngineeringProject, num_modes: int = 5):
    """Calculates natural frequencies, periods, and modal vibration shapes."""
    try:
        nodes, elements = _build_fea_model(project)
        solver = ModalSolver(nodes, elements, num_modes=num_modes)
        results = solver.solve()
        return results
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err))


@router.post("/buckling")
def run_buckling_analysis(project: EngineeringProject):
    """Calculates critical elastic buckling load multiplier lambda_cr and buckling shapes."""
    try:
        nodes, elements = _build_fea_model(project)
        solver = BucklingSolver(nodes, elements)
        results = solver.solve()
        return results
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err))


@router.post("/mesh-convergence")
def run_mesh_convergence_study(span_length_m: float = 6.0, point_load_kN: float = 30.0):
    """Executes mesh refinement convergence study verifying FEA vs exact analytical solution."""
    mat = STANDARD_MATERIALS["steel-s355"]
    sec = STANDARD_SECTIONS["ub-305x127x42"]
    res = MeshGenerator.run_convergence_study(
        span_length_m=span_length_m,
        point_load_N=point_load_kN * 1e3,
        material=mat,
        section=sec,
    )
    return res


@router.get("/library/materials")
def list_materials():
    """Returns standard verified materials."""
    return [m.to_dict() for m in STANDARD_MATERIALS.values()]


@router.get("/library/sections")
def list_sections():
    """Returns standard verified cross-sections."""
    return [s.to_dict() for s in STANDARD_SECTIONS.values()]


@router.get("/presets/{preset_id}")
def get_benchmark_preset(preset_id: str):
    """Returns verified textbook benchmarks for portal frames, continuous beams, and trusses."""
    if preset_id == "portal-frame":
        # 2D Portal Frame: 2 columns 4m high, 1 beam 6m wide
        # Node 1: (0, 0) fixed, Node 2: (0, 4), Node 3: (6, 4), Node 4: (6, 0) fixed
        # Lateral wind load 20 kN at Node 2, gravity load 30 kN at Node 3
        return {
            "metadata": {"name": "Industrial Portal Frame", "discipline": "Structural Frame"},
            "materials": [STANDARD_MATERIALS["steel-s355"].to_dict()],
            "sections": [STANDARD_SECTIONS["ub-305x127x42"].to_dict()],
            "nodes": [
                {"id": 1, "x": 0.0, "y": 0.0, "restraints": [True, True, True], "loads": [0.0, 0.0, 0.0]},
                {"id": 2, "x": 0.0, "y": 4.0, "restraints": [False, False, False], "loads": [20000.0, 0.0, 0.0]},
                {"id": 3, "x": 6.0, "y": 4.0, "restraints": [False, False, False], "loads": [0.0, -30000.0, 0.0]},
                {"id": 4, "x": 6.0, "y": 0.0, "restraints": [True, True, True], "loads": [0.0, 0.0, 0.0]},
            ],
            "elements": [
                {"id": 1, "element_type": "frame", "node_i_id": 1, "node_j_id": 2, "material_id": "steel-s355", "section_id": "ub-305x127x42"},
                {"id": 2, "element_type": "frame", "node_i_id": 2, "node_j_id": 3, "material_id": "steel-s355", "section_id": "ub-305x127x42"},
                {"id": 3, "element_type": "frame", "node_i_id": 3, "node_j_id": 4, "material_id": "steel-s355", "section_id": "ub-305x127x42"},
            ]
        }
    elif preset_id == "cantilever-beam":
        return {
            "metadata": {"name": "Cantilever Beam", "discipline": "Beam Mechanics"},
            "materials": [STANDARD_MATERIALS["steel-s355"].to_dict()],
            "sections": [STANDARD_SECTIONS["ub-305x127x42"].to_dict()],
            "nodes": [
                {"id": 1, "x": 0.0, "y": 0.0, "restraints": [True, True, True], "loads": [0.0, 0.0, 0.0]},
                {"id": 2, "x": 3.0, "y": 0.0, "restraints": [False, False, False], "loads": [0.0, 0.0, 0.0]},
                {"id": 3, "x": 6.0, "y": 0.0, "restraints": [False, False, False], "loads": [0.0, -40000.0, 0.0]},
            ],
            "elements": [
                {"id": 1, "element_type": "frame", "node_i_id": 1, "node_j_id": 2, "material_id": "steel-s355", "section_id": "ub-305x127x42"},
                {"id": 2, "element_type": "frame", "node_i_id": 2, "node_j_id": 3, "material_id": "steel-s355", "section_id": "ub-305x127x42"},
            ]
        }
    elif preset_id == "pratt-truss":
        # 2D Pratt Bridge Truss
        return {
            "metadata": {"name": "Pratt Bridge Truss", "discipline": "Truss Structures"},
            "materials": [STANDARD_MATERIALS["steel-s355"].to_dict()],
            "sections": [STANDARD_SECTIONS["ub-305x127x42"].to_dict()],
            "nodes": [
                {"id": 1, "x": 0.0, "y": 0.0, "restraints": [True, True, False], "loads": [0.0, 0.0, 0.0]},
                {"id": 2, "x": 3.0, "y": 0.0, "restraints": [False, False, False], "loads": [0.0, -50000.0, 0.0]},
                {"id": 3, "x": 6.0, "y": 0.0, "restraints": [False, True, False], "loads": [0.0, 0.0, 0.0]},
                {"id": 4, "x": 3.0, "y": 2.5, "restraints": [False, False, False], "loads": [0.0, 0.0, 0.0]},
            ],
            "elements": [
                {"id": 1, "element_type": "truss", "node_i_id": 1, "node_j_id": 2, "material_id": "steel-s355", "section_id": "ub-305x127x42"},
                {"id": 2, "element_type": "truss", "node_i_id": 2, "node_j_id": 3, "material_id": "steel-s355", "section_id": "ub-305x127x42"},
                {"id": 3, "element_type": "truss", "node_i_id": 1, "node_j_id": 4, "material_id": "steel-s355", "section_id": "ub-305x127x42"},
                {"id": 4, "element_type": "truss", "node_i_id": 2, "node_j_id": 4, "material_id": "steel-s355", "section_id": "ub-305x127x42"},
                {"id": 5, "element_type": "truss", "node_i_id": 3, "node_j_id": 4, "material_id": "steel-s355", "section_id": "ub-305x127x42"},
            ]
        }
    raise HTTPException(status_code=404, detail=f"Preset '{preset_id}' not found.")
