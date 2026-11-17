import pytest
from modules.civil.structural.simply_supported_beam import SimplySupportedBeamSolver


def test_beam_point_load_center():
    """Hibbeler Benchmark: L=6m, P=30kN at center x=3m."""
    solver = SimplySupportedBeamSolver(
        span_length=6.0,
        point_loads=[{"x": 3.0, "magnitude": 30.0}],
        elastic_modulus_gpa=200.0,
        moment_of_inertia_10e6_mm4=80.0,
    )
    result = solver.solve()
    assert result["status"] == "success"
    res = result["results"]

    # Reactions: R_A = R_B = 15 kN
    assert pytest.approx(res["reaction_A_kN"], rel=1e-3) == 15.0
    assert pytest.approx(res["reaction_B_kN"], rel=1e-3) == 15.0

    # Max moment: PL/4 = 45 kNm at center x=3m
    assert pytest.approx(res["max_moment_kNm"], rel=1e-3) == 45.0
    assert pytest.approx(res["critical_x_m"], rel=1e-3) == 3.0

    # Max shear: +15 kN and -15 kN
    assert pytest.approx(res["max_shear_kN"], rel=1e-3) == 15.0
    assert pytest.approx(res["min_shear_kN"], rel=1e-3) == -15.0

    # Deflection: delta = PL^3 / (48 EI) = 30 * 6^3 / (48 * 16000) = 0.0084375 m = 8.438 mm
    assert pytest.approx(res["max_deflection_mm"], rel=1e-2) == 8.438

    # Equilibrium checks
    assert result["checks"]["vertical_equilibrium"] is True
    assert result["checks"]["moment_equilibrium"] is True


def test_beam_full_udl():
    """Gere & Goodno Benchmark: L=8m, w=12kN/m over full span."""
    solver = SimplySupportedBeamSolver(
        span_length=8.0,
        distributed_loads=[{"start_x": 0.0, "end_x": 8.0, "magnitude": 12.0}],
        elastic_modulus_gpa=200.0,
        moment_of_inertia_10e6_mm4=100.0,
    )
    result = solver.solve()
    assert result["status"] == "success"
    res = result["results"]

    # Reactions: R_A = R_B = wL/2 = 48 kN
    assert pytest.approx(res["reaction_A_kN"], rel=1e-3) == 48.0
    assert pytest.approx(res["reaction_B_kN"], rel=1e-3) == 48.0

    # Max moment: wL^2 / 8 = 12 * 64 / 8 = 96 kNm at center x=4m
    assert pytest.approx(res["max_moment_kNm"], rel=1e-3) == 96.0
    assert pytest.approx(res["critical_x_m"], rel=1e-3) == 4.0

    # Max shear: 48 kN and -48 kN
    assert pytest.approx(res["max_shear_kN"], rel=1e-3) == 48.0
    assert pytest.approx(res["min_shear_kN"], rel=1e-3) == -48.0

    # Deflection: 5 w L^4 / (384 EI) = 5 * 12 * 4096 / (384 * 20000) = 0.032 m = 32.0 mm
    assert pytest.approx(res["max_deflection_mm"], rel=1e-2) == 32.0

    assert result["checks"]["moment_equilibrium"] is True


def test_beam_asymmetric_point_load():
    """Asymmetric point load: L=5m, P=20kN at x=2m."""
    solver = SimplySupportedBeamSolver(
        span_length=5.0,
        point_loads=[{"x": 2.0, "magnitude": 20.0}],
    )
    result = solver.solve()
    res = result["results"]

    # R_B = 20 * 2 / 5 = 8 kN, R_A = 20 * 3 / 5 = 12 kN
    assert pytest.approx(res["reaction_A_kN"], rel=1e-3) == 12.0
    assert pytest.approx(res["reaction_B_kN"], rel=1e-3) == 8.0

    # M_max = P*a*b / L = 20 * 2 * 3 / 5 = 24 kNm
    assert pytest.approx(res["max_moment_kNm"], rel=1e-3) == 24.0
    assert pytest.approx(res["critical_x_m"], rel=1e-3) == 2.0


def test_beam_validation_errors():
    """Verify input domain checks."""
    with pytest.raises(ValueError, match="Span length L must be strictly positive"):
        SimplySupportedBeamSolver(span_length=-5.0)

    with pytest.raises(ValueError, match="outside beam span"):
        SimplySupportedBeamSolver(
            span_length=4.0, point_loads=[{"x": 6.0, "magnitude": 10.0}]
        )

    with pytest.raises(ValueError, match="exceed beam span"):
        SimplySupportedBeamSolver(
            span_length=4.0,
            distributed_loads=[{"start_x": 0.0, "end_x": 5.0, "magnitude": 5.0}],
        )
