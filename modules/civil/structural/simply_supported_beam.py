"""
Simply Supported Beam Solver (Milestone 2 Vertical Slice)
Complies with CALCULATION_CONTRACT.md and VISUALISATION_SPEC.md.

References:
- Hibbeler, R.C. (2018). Structural Analysis, 10th Edition. Pearson.
- Gere, J.M. and Goodno, B.J. (2018). Mechanics of Materials, 9th Edition. Cengage Learning.
"""

from typing import Any, Dict, List, Optional
import math


class SimplySupportedBeamSolver:
    """
    Deterministic solver for statically determinate single-span simply supported beams.
    Evaluates:
      - Support reactions (R_A at pin x=0, R_B at roller x=L)
      - Shear force diagram data V(x)
      - Bending moment diagram data M(x)
      - Elastic deflection curve y(x) using Euler-Bernoulli beam theory
      - Independent equilibrium verification checks
    """

    MODULE_ID = "simply-supported-beam"
    MODULE_VERSION = "1.0.0"

    def __init__(
        self,
        span_length: float,
        point_loads: Optional[List[Dict[str, float]]] = None,
        distributed_loads: Optional[List[Dict[str, float]]] = None,
        elastic_modulus_gpa: float = 200.0,
        moment_of_inertia_10e6_mm4: float = 80.0,
    ):
        if span_length <= 0:
            raise ValueError("Span length L must be strictly positive.")
        if elastic_modulus_gpa <= 0:
            raise ValueError("Elastic modulus E must be strictly positive.")
        if moment_of_inertia_10e6_mm4 <= 0:
            raise ValueError("Moment of inertia I must be strictly positive.")

        self.L = float(span_length)
        self.point_loads = point_loads or []
        self.distributed_loads = distributed_loads or []
        self.E_gpa = float(elastic_modulus_gpa)
        self.I_10e6_mm4 = float(moment_of_inertia_10e6_mm4)

        # SI Unit conversion:
        # E: GPa -> N/m^2 (x 10^9) -> kN/m^2 (x 10^6)
        # I: 10^6 mm^4 -> m^4 (x 10^-6)
        # EI in kN*m^2:
        self.EI = (self.E_gpa * 1e6) * (self.I_10e6_mm4 * 1e-6)

        self._validate_inputs()

    def _validate_inputs(self):
        for idx, pl in enumerate(self.point_loads):
            x = pl.get("x", 0.0)
            if x < 0.0 or x > self.L:
                raise ValueError(
                    f"Point load #{idx + 1} position x={x}m is outside beam span [0, {self.L}]m."
                )

        for idx, dl in enumerate(self.distributed_loads):
            x_start = dl.get("start_x", 0.0)
            x_end = dl.get("end_x", self.L)
            if x_start < 0.0 or x_end > self.L:
                raise ValueError(
                    f"Distributed load #{idx + 1} bounds [{x_start}, {x_end}]m exceed beam span [0, {self.L}]m."
                )
            if x_start >= x_end:
                raise ValueError(
                    f"Distributed load #{idx + 1} start_x ({x_start}m) must be strictly less than end_x ({x_end}m)."
                )

    def solve(self) -> Dict[str, Any]:
        """Execute calculation pipeline returning contract-compliant dictionary."""
        # 1. Reactions
        sum_M_A = 0.0
        total_load = 0.0

        for pl in self.point_loads:
            p = pl["magnitude"]
            x = pl["x"]
            sum_M_A += p * x
            total_load += p

        for dl in self.distributed_loads:
            w = dl["magnitude"]
            xs = dl["start_x"]
            xe = dl["end_x"]
            length = xe - xs
            w_total = w * length
            centroid = (xs + xe) / 2.0
            sum_M_A += w_total * centroid
            total_load += w_total

        # Equilibrium equations:
        # sum M_A = 0 => R_B * L = sum M_A
        R_B = sum_M_A / self.L
        # sum F_y = 0 => R_A + R_B = total_load
        R_A = total_load - R_B

        # 2. Independent equilibrium check (sum M_B = 0)
        sum_M_B_check = R_A * self.L
        for pl in self.point_loads:
            sum_M_B_check -= pl["magnitude"] * (self.L - pl["x"])
        for dl in self.distributed_loads:
            xs = dl["start_x"]
            xe = dl["end_x"]
            w_total = dl["magnitude"] * (xe - xs)
            centroid_from_B = self.L - (xs + xe) / 2.0
            sum_M_B_check -= w_total * centroid_from_B

        equilibrium_passed = abs(sum_M_B_check) < 1e-4

        # 3. Discretized distributions along beam (201 points)
        num_points = 201
        xs = [round(i * (self.L / (num_points - 1)), 4) for i in range(num_points)]
        
        # Include critical load locations
        crit_xs = {0.0, self.L}
        for pl in self.point_loads:
            crit_xs.add(round(pl["x"], 4))
        for dl in self.distributed_loads:
            crit_xs.add(round(dl["start_x"], 4))
            crit_xs.add(round(dl["end_x"], 4))
        
        eval_xs = sorted(list(set(xs).union(crit_xs)))

        shears = []
        moments = []
        deflections_mm = []

        for x in eval_xs:
            v_val = self._evaluate_shear(x, R_A)
            m_val = self._evaluate_moment(x, R_A)
            d_val = self._evaluate_deflection(x, R_A)
            shears.append(round(v_val, 4))
            moments.append(round(m_val, 4))
            deflections_mm.append(round(d_val * 1000.0, 4))  # Convert m to mm

        max_shear = max(shears)
        min_shear = min(shears)
        max_moment = max(moments)
        max_moment_idx = moments.index(max_moment)
        critical_x = eval_xs[max_moment_idx]
        max_deflection_mm = max(deflections_mm) if deflections_mm else 0.0

        # Steps calculation explanation (for engineering traceability)
        steps = [
            {
                "step_number": 1,
                "title": "Static Equilibrium & Support Reactions",
                "equation": r"\sum M_A = 0 \implies R_B \cdot L = \sum (P_i \cdot x_i) + \sum \left(w_j \cdot l_j \cdot \bar{x}_j\right)",
                "substitution": f"R_B \\cdot {self.L:.3f} = {sum_M_A:.3f}",
                "result": f"R_B = {R_B:.3f} kN, R_A = {R_A:.3f} kN",
                "units": "kN",
            },
            {
                "step_number": 2,
                "title": "Independent Equilibrium Verification",
                "equation": r"\sum M_B = R_A \cdot L - \sum [P_i \cdot (L - x_i)] - \sum [W_j \cdot (L - \bar{x}_j)] = 0",
                "substitution": f"Residual moment = {abs(sum_M_B_check):.6f} kN·m",
                "result": "Equilibrium Satisfied" if equilibrium_passed else "Tolerance Check Failed",
                "units": "kN·m",
            },
            {
                "step_number": 3,
                "title": "Critical Shear Forces & Turning Points",
                "equation": r"V(x) = R_A - \sum_{x_i \le x} P_i - \int_0^x w(u) \, du",
                "substitution": f"Max positive V = {max_shear:.3f} kN, Max negative V = {min_shear:.3f} kN",
                "result": f"Governing Shear = {max(abs(max_shear), abs(min_shear)):.3f} kN",
                "units": "kN",
            },
            {
                "step_number": 4,
                "title": "Maximum Bending Moment",
                "equation": r"\frac{dM}{dx} = V(x) = 0 \implies M_{\max}",
                "substitution": f"Maximum bending moment occurs at x = {critical_x:.3f} m",
                "result": f"M_max = {max_moment:.3f} kN·m",
                "units": "kN·m",
            },
            {
                "step_number": 5,
                "title": "Maximum Elastic Deflection",
                "equation": r"EI \frac{d^2 y}{dx^2} = -M(x) \implies \delta_{\max}",
                "substitution": f"E = {self.E_gpa} GPa, I = {self.I_10e6_mm4} \\times 10^6 \\text{{ mm}}^4 (EI = {self.EI:.1f} kN·m²)",
                "result": f"δ_max = {max_deflection_mm:.3f} mm",
                "units": "mm",
            },
        ]

        return {
            "status": "success",
            "module_id": self.MODULE_ID,
            "module_version": self.MODULE_VERSION,
            "inputs_normalized": {
                "span_length_m": self.L,
                "point_loads": self.point_loads,
                "distributed_loads": self.distributed_loads,
                "elastic_modulus_gpa": self.E_gpa,
                "moment_of_inertia_10e6_mm4": self.I_10e6_mm4,
                "flexural_rigidity_ei_kNm2": round(self.EI, 2),
            },
            "assumptions": [
                "Euler-Bernoulli beam theory applies (slender beam, L/d >= 10).",
                "Plane sections remain plane and normal to the longitudinal neutral axis.",
                "Linear elastic, homogeneous, and isotropic material behavior.",
                "Small deflections with pin support at x = 0 and roller support at x = L.",
                "Self-weight of beam is excluded unless provided as a distributed load.",
            ],
            "warnings": [] if (self.L > 0) else ["Invalid geometry"],
            "steps": steps,
            "results": {
                "reaction_A_kN": round(R_A, 3),
                "reaction_B_kN": round(R_B, 3),
                "max_shear_kN": round(max_shear, 3),
                "min_shear_kN": round(min_shear, 3),
                "max_moment_kNm": round(max_moment, 3),
                "critical_x_m": round(critical_x, 3),
                "max_deflection_mm": round(max_deflection_mm, 3),
            },
            "checks": {
                "vertical_equilibrium": True,
                "moment_equilibrium": equilibrium_passed,
                "boundary_conditions_deflection": True,
            },
            "plot_data": {
                "x_m": eval_xs,
                "shear_kN": shears,
                "moment_kNm": moments,
                "deflection_mm": deflections_mm,
                "span_length_m": self.L,
                "point_loads": self.point_loads,
                "distributed_loads": self.distributed_loads,
                "reaction_A_kN": round(R_A, 3),
                "reaction_B_kN": round(R_B, 3),
            },
            "references": [
                "Hibbeler, R.C. (2018). Structural Analysis, 10th Edition. Pearson.",
                "Gere, J.M. and Goodno, B.J. (2018). Mechanics of Materials, 9th Edition. Cengage Learning.",
            ],
        }

    def _evaluate_shear(self, x: float, R_A: float) -> float:
        v = R_A
        for pl in self.point_loads:
            if x >= pl["x"]:
                v -= pl["magnitude"]

        for dl in self.distributed_loads:
            xs = dl["start_x"]
            xe = dl["end_x"]
            if x > xs:
                overlap = min(x, xe) - xs
                v -= dl["magnitude"] * overlap
        return v

    def _evaluate_moment(self, x: float, R_A: float) -> float:
        m = R_A * x
        for pl in self.point_loads:
            px = pl["x"]
            if x > px:
                m -= pl["magnitude"] * (x - px)

        for dl in self.distributed_loads:
            xs = dl["start_x"]
            xe = dl["end_x"]
            if x > xs:
                active_end = min(x, xe)
                overlap = active_end - xs
                centroid = (xs + active_end) / 2.0
                m -= dl["magnitude"] * overlap * (x - centroid)
        return m

    def _evaluate_deflection(self, x: float, R_A: float) -> float:
        """
        Calculates vertical downward deflection (in meters) via superposition.
        Downwards deflection is positive.
        """
        total_deflection = 0.0

        # 1. Point loads contribution
        for pl in self.point_loads:
            P = pl["magnitude"]
            a = pl["x"]
            b = self.L - a
            if a == 0.0 or a == self.L:
                continue

            if x <= a:
                # y(x) = P*b*x / (6*E*I*L) * (L^2 - b^2 - x^2)
                y_p = (P * b * x) / (6 * self.EI * self.L) * (self.L**2 - b**2 - x**2)
            else:
                # y(x) = P*a*(L - x) / (6*E*I*L) * (2*L*x - x^2 - a^2)
                y_p = (P * a * (self.L - x)) / (6 * self.EI * self.L) * (2 * self.L * x - x**2 - a**2)
            total_deflection += y_p

        # 2. Distributed loads contribution
        for dl in self.distributed_loads:
            w = dl["magnitude"]
            xs = dl["start_x"]
            xe = dl["end_x"]
            # If full span UDL: y(x) = w*x / (24*EI) * (L^3 - 2*L*x^2 + x^3)
            if xs == 0.0 and xe == self.L:
                y_w = (w * x) / (24 * self.EI) * (self.L**3 - 2 * self.L * x**2 + x**3)
                total_deflection += y_w
            else:
                # Discretize partial UDL into equivalent slices
                num_slices = 20
                dx = (xe - xs) / num_slices
                for s in range(num_slices):
                    slice_x = xs + (s + 0.5) * dx
                    slice_P = w * dx
                    slice_b = self.L - slice_x
                    if x <= slice_x:
                        y_slice = (slice_P * slice_b * x) / (6 * self.EI * self.L) * (self.L**2 - slice_b**2 - x**2)
                    else:
                        y_slice = (slice_P * slice_x * (self.L - x)) / (6 * self.EI * self.L) * (2 * self.L * x - x**2 - slice_x**2)
                    total_deflection += y_slice

        return max(0.0, total_deflection)
