"""
Material models for linear and nonlinear finite element analysis.
Complies with CALCULATION_CONTRACT.md and ISO/Eurocode material specifications.
"""

from typing import Dict, Any, Optional


class Material:
    """Isotropic linear elastic material model."""

    def __init__(
        self,
        id: str,
        name: str,
        elastic_modulus_pa: float,
        poissons_ratio: float = 0.3,
        density_kg_m3: float = 7850.0,
        yield_strength_pa: Optional[float] = None,
        thermal_expansion_coeff: float = 1.2e-5,
    ):
        if elastic_modulus_pa <= 0:
            raise ValueError(f"Elastic modulus E must be positive for material {name}.")
        if not (-1.0 < poissons_ratio < 0.5):
            raise ValueError(f"Poisson's ratio must be in (-1, 0.5) for isotropic material {name}.")
        if density_kg_m3 <= 0:
            raise ValueError(f"Density must be positive for material {name}.")

        self.id = id
        self.name = name
        self.E = float(elastic_modulus_pa)
        self.nu = float(poissons_ratio)
        self.rho = float(density_kg_m3)
        self.fy = float(yield_strength_pa) if yield_strength_pa else None
        self.alpha = float(thermal_expansion_coeff)

        # Derived elastic constants:
        # Shear modulus: G = E / (2 * (1 + nu))
        self.G = self.E / (2.0 * (1.0 + self.nu))
        # Bulk modulus: K = E / (3 * (1 - 2 * nu))
        self.K = self.E / (3.0 * (1.0 - 2.0 * self.nu))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "elastic_modulus_gpa": round(self.E / 1e9, 2),
            "poissons_ratio": self.nu,
            "density_kg_m3": self.rho,
            "shear_modulus_gpa": round(self.G / 1e9, 2),
            "bulk_modulus_gpa": round(self.K / 1e9, 2),
            "yield_strength_mpa": round(self.fy / 1e6, 2) if self.fy else None,
            "thermal_expansion_coeff": self.alpha,
        }


# Standard Material Library
STANDARD_MATERIALS: Dict[str, Material] = {
    "steel-s355": Material(
        id="steel-s355",
        name="Structural Steel S355",
        elastic_modulus_pa=210e9,
        poissons_ratio=0.30,
        density_kg_m3=7850.0,
        yield_strength_pa=355e6,
        thermal_expansion_coeff=1.2e-5,
    ),
    "steel-s275": Material(
        id="steel-s275",
        name="Structural Steel S275",
        elastic_modulus_pa=205e9,
        poissons_ratio=0.30,
        density_kg_m3=7850.0,
        yield_strength_pa=275e6,
        thermal_expansion_coeff=1.2e-5,
    ),
    "concrete-c30": Material(
        id="concrete-c30",
        name="Concrete C30/37",
        elastic_modulus_pa=33e9,
        poissons_ratio=0.20,
        density_kg_m3=2400.0,
        yield_strength_pa=30e6,
        thermal_expansion_coeff=1.0e-5,
    ),
    "timber-c24": Material(
        id="timber-c24",
        name="Structural Timber C24",
        elastic_modulus_pa=11e9,
        poissons_ratio=0.35,
        density_kg_m3=420.0,
        yield_strength_pa=24e6,
        thermal_expansion_coeff=0.5e-5,
    ),
    "aluminum-6061": Material(
        id="aluminum-6061",
        name="Aluminum Alloy 6061-T6",
        elastic_modulus_pa=68.9e9,
        poissons_ratio=0.33,
        density_kg_m3=2700.0,
        yield_strength_pa=276e6,
        thermal_expansion_coeff=2.3e-5,
    ),
}
