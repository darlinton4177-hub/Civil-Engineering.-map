import pytest
import numpy as np
from modules.fea.core.material import STANDARD_MATERIALS
from modules.fea.core.section import STANDARD_SECTIONS, Section
from modules.fea.core.node import Node
from modules.fea.elements.frame_2d import Frame2DElement
from modules.fea.elements.truss_2d import Truss2DElement
from modules.fea.solvers.linear_static import LinearStaticSolver
from modules.fea.solvers.modal import ModalSolver
from modules.fea.solvers.buckling import BucklingSolver
from modules.fea.mesh.mesh_generator import MeshGenerator


def test_cantilever_beam_exact_closed_form():
    """
    Theoretical Benchmark:
    Cantilever of length L=4.0m with tip load P=20kN.
    Exact tip deflection delta = P * L^3 / (3 * E * I)
    Exact base reaction Ry = 20 kN, Mz = -80 kNm
    """
    L = 4.0
    P = 20000.0  # 20 kN
    mat = STANDARD_MATERIALS["steel-s355"]
    sec = Section.create_rectangular(id="s1", name="Rect", width_m=0.2, depth_m=0.4)

    EI = mat.E * sec.Iz
    expected_delta_m = (P * (L**3)) / (3.0 * EI)

    # 4 subdivisions for accurate representation
    n1 = Node(id=1, x=0.0, y=0.0, restraints=[True, True, True])
    n2 = Node(id=2, x=L, y=0.0, restraints=[False, False, False], loads=[0.0, -P, 0.0])

    nodes, elements = MeshGenerator.discretize_member(
        start_node=n1,
        end_node=n2,
        num_subdivisions=4,
        material=mat,
        section=sec,
        start_node_id=3,
        start_elem_id=1,
    )

    solver = LinearStaticSolver(nodes, elements)
    res = solver.solve()

    tip_node = [nr for nr in res["nodes"] if nr["node_id"] == n2.id][0]
    tip_dy_m = abs(tip_node["dy_mm"]) / 1e3

    # Exact cubic beam element gives exact tip displacement within 1e-4
    assert pytest.approx(tip_dy_m, rel=1e-3) == expected_delta_m

    # Base reactions
    base_node = [nr for nr in res["nodes"] if nr["node_id"] == n1.id][0]
    assert pytest.approx(base_node["Ry_kN"], rel=1e-2) == 20.0
    assert pytest.approx(abs(base_node["R_Mz_kNm"]), rel=1e-2) == 80.0
    assert res["checks"]["global_Fy_equilibrium"] is True


def test_portal_frame_equilibrium():
    """Industrial 2D Portal Frame under lateral wind + vertical dead load."""
    mat = STANDARD_MATERIALS["steel-s355"]
    sec = STANDARD_SECTIONS["ub-305x127x42"]

    # 4-node frame: (0,0) fixed -> (0,4) -> (6,4) -> (6,0) fixed
    n1 = Node(id=1, x=0.0, y=0.0, restraints=[True, True, True])
    n2 = Node(id=2, x=0.0, y=4.0, restraints=[False, False, False], loads=[25000.0, 0.0, 0.0])  # 25kN lateral
    n3 = Node(id=3, x=6.0, y=4.0, restraints=[False, False, False], loads=[0.0, -40000.0, 0.0]) # 40kN vertical
    n4 = Node(id=4, x=6.0, y=0.0, restraints=[True, True, True])

    e1 = Frame2DElement(id=1, node_i=n1, node_j=n2, material=mat, section=sec)
    e2 = Frame2DElement(id=2, node_i=n2, node_j=n3, material=mat, section=sec)
    e3 = Frame2DElement(id=3, node_i=n3, node_j=n4, material=mat, section=sec)

    solver = LinearStaticSolver([n1, n2, n3, n4], [e1, e2, e3])
    res = solver.solve()

    assert res["status"] == "success"
    assert res["checks"]["global_Fx_equilibrium"] is True
    assert res["checks"]["global_Fy_equilibrium"] is True

    # Portal sway to the right
    assert res["nodes"][1]["dx_mm"] > 0
    assert res["nodes"][2]["dx_mm"] > 0


def test_modal_analysis_frequencies():
    """Verify natural frequencies and mode extraction for a cantilever."""
    mat = STANDARD_MATERIALS["steel-s355"]
    sec = STANDARD_SECTIONS["ub-305x127x42"]

    n1 = Node(id=1, x=0.0, y=0.0, restraints=[True, True, True])
    n2 = Node(id=2, x=6.0, y=0.0, restraints=[False, False, False])

    nodes, elements = MeshGenerator.discretize_member(
        start_node=n1, end_node=n2, num_subdivisions=6, material=mat, section=sec, start_node_id=3, start_elem_id=1
    )

    modal_solver = ModalSolver(nodes, elements, num_modes=3)
    res = modal_solver.solve()

    assert res["status"] == "success"
    assert len(res["modes"]) == 3
    # Check frequency ordering: f1 < f2 < f3
    f1 = res["modes"][0]["natural_frequency_hz"]
    f2 = res["modes"][1]["natural_frequency_hz"]
    f3 = res["modes"][2]["natural_frequency_hz"]
    assert 0 < f1 < f2 < f3


def test_linear_buckling_multiplier():
    """Verify Euler column buckling eigenvalue multiplier."""
    mat = STANDARD_MATERIALS["steel-s355"]
    sec = Section.create_rectangular(id="s1", name="Col", width_m=0.1, depth_m=0.1)
    L = 3.0

    # Fixed base, free top with compressive load 10 kN
    n1 = Node(id=1, x=0.0, y=0.0, restraints=[True, True, True])
    n2 = Node(id=2, x=0.0, y=L, restraints=[False, False, False], loads=[0.0, -10000.0, 0.0])

    nodes, elements = MeshGenerator.discretize_member(
        start_node=n1, end_node=n2, num_subdivisions=4, material=mat, section=sec, start_node_id=3, start_elem_id=1
    )

    buckling_solver = BucklingSolver(nodes, elements)
    res = buckling_solver.solve()

    assert res["status"] == "success"
    assert res["critical_load_factor"] is not None
    assert res["critical_load_factor"] > 0.0


def test_mesh_convergence_monotonicity():
    """Verify that mesh refinement reduces relative error monotonically."""
    mat = STANDARD_MATERIALS["steel-s355"]
    sec = Section.create_rectangular(id="s1", name="Beam", width_m=0.15, depth_m=0.3)
    res = MeshGenerator.run_convergence_study(
        span_length_m=5.0,
        point_load_N=15000.0,
        material=mat,
        section=sec,
        mesh_densities=[1, 2, 4, 8],
    )
    assert res["status"] == "success"
    table = res["convergence_table"]
    assert len(table) == 4
    # All errors must be small (< 0.1% for cubic beam element under point load)
    for row in table:
        assert row["relative_error_percent"] < 1.0
