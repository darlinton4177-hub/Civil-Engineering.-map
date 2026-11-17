"""
Cross-section geometry and structural properties for 1D and 2D/3D beam and frame elements.
"""

from typing import Dict, Any, Optional
import math


class Section:
    """Structural cross-section property model."""

    def __init__(
        self,
        id: str,
        name: str,
        area_m2: float,
        I_strong_m4: float,
        I_weak_m4: Optional[float] = None,
        torsional_constant_j_m4: Optional[float] = None,
        depth_m: float = 0.2,
        width_m: float = 0.1,
    ):
        if area_m2 <= 0:
            raise ValueError(f"Cross-sectional area must be strictly positive for {name}.")
        if I_strong_m4 <= 0:
            raise ValueError(f"Moment of inertia I_strong must be positive for {name}.")

        self.id = id
        self.name = name
        self.A = float(area_m2)
        self.Iz = float(I_strong_m4)
        self.Iy = float(I_weak_m4) if I_weak_m4 else self.Iz
        self.J = float(torsional_constant_j_m4) if torsional_constant_j_m4 else (self.Iz + self.Iy)
        self.depth = float(depth_m)
        self.width = float(width_m)

        # Section modulus: W_el = I / (depth / 2)
        self.Wel_z = self.Iz / (self.depth / 2.0)
        self.Wel_y = self.Iy / (self.width / 2.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "area_cm2": round(self.A * 1e4, 2),
            "I_strong_cm4": round(self.Iz * 1e8, 2),
            "I_weak_cm4": round(self.Iy * 1e8, 2),
            "torsion_j_cm4": round(self.J * 1e8, 2),
            "depth_mm": round(self.depth * 1000, 1),
            "width_mm": round(self.width * 1000, 1),
            "section_modulus_cm3": round(self.Wel_z * 1e6, 2),
        }

    @classmethod
    def create_rectangular(cls, id: str, name: str, width_m: float, depth_m: float) -> "Section":
        """Generate rectangular solid section (timber, concrete, steel plate)."""
        b = float(width_m)
        h = float(depth_m)
        A = b * h
        Iz = (b * h**3) / 12.0
        Iy = (h * b**3) / 12.0
        # St. Venant torsion approximation for rectangle:
        a_dim = max(b, h)
        b_dim = min(b, h)
        J = a_dim * (b_dim**3) * (1.0 / 3.0 - 0.21 * (b_dim / a_dim) * (1.0 - (b_dim**4) / (12.0 * a_dim**4)))
        return cls(id=id, name=name, area_m2=A, I_strong_m4=Iz, I_weak_m4=Iy, torsional_constant_j_m4=J, depth_m=h, width_m=b)

    @classmethod
    def create_i_beam(
        cls, id: str, name: str, depth_m: float, flange_width_m: float, flange_thickness_m: float, web_thickness_m: float
    ) -> "Section":
        """Generate I-beam / W-flange section."""
        d = float(depth_m)
        bf = float(flange_width_m)
        tf = float(flange_thickness_m)
        tw = float(web_thickness_m)
        hw = d - 2.0 * tf

        A = 2.0 * bf * tf + hw * tw
        # Strong axis Iz
        Iz = (bf * d**3 - (bf - tw) * hw**3) / 12.0
        # Weak axis Iy
        Iy = (2.0 * tf * bf**3 + hw * tw**3) / 12.0
        # Torsion J ~ sum(b * t^3 / 3)
        J = (2.0 * bf * tf**3 + hw * tw**3) / 3.0
        return cls(id=id, name=name, area_m2=A, I_strong_m4=Iz, I_weak_m4=Iy, torsional_constant_j_m4=J, depth_m=d, width_m=bf)


# Standard Section Library Presets
STANDARD_SECTIONS: Dict[str, Section] = {
    "ub-305x127x42": Section.create_i_beam(
        id="ub-305x127x42",
        name="Universal Beam UB 305x127x42",
        depth_m=0.3072,
        flange_width_m=0.1243,
        flange_thickness_m=0.0107,
        web_thickness_m=0.0069,
    ),
    "ub-406x178x60": Section.create_i_beam(
        id="ub-406x178x60",
        name="Universal Beam UB 406x178x60",
        depth_m=0.4064,
        flange_width_m=0.1778,
        flange_thickness_m=0.0128,
        web_thickness_m=0.0078,
    ),
    "concrete-300x500": Section.create_rectangular(
        id="concrete-300x500",
        name="RC Rectangular Beam 300x500 mm",
        width_m=0.30,
        depth_m=0.50,
    ),
    "timber-100x200": Section.create_rectangular(
        id="timber-100x200",
        name="Solid Timber Joist 100x200 mm",
        width_m=0.10,
        depth_m=0.20,
    ),
}
