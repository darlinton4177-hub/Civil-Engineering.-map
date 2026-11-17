"""
Unified Engineering Project Data Model for Engineer Realm.
Encapsulates geometry, materials, cross-sections, boundary conditions,
loads, solver configurations, and post-processed simulation results.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class MaterialModel(BaseModel):
    id: str
    name: str
    elastic_modulus_pa: float
    poissons_ratio: float = 0.3
    density_kg_m3: float = 7850.0
    yield_strength_pa: Optional[float] = None


class SectionModel(BaseModel):
    id: str
    name: str
    area_m2: float
    I_strong_m4: float
    I_weak_m4: Optional[float] = None
    torsional_constant_j_m4: Optional[float] = None
    depth_m: float = 0.2
    width_m: float = 0.1


class NodeModel(BaseModel):
    id: int
    x: float
    y: float
    z: float = 0.0
    restraints: List[bool] = Field(default_factory=lambda: [False, False, False])
    loads: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])


class ElementModel(BaseModel):
    id: int
    element_type: str = "frame"  # "frame" or "truss"
    node_i_id: int
    node_j_id: int
    material_id: str
    section_id: str


class ProjectMetadata(BaseModel):
    id: str = "proj-1"
    name: str = "Untitled Structural Project"
    description: str = "Engineer Realm Multiphysics Project"
    discipline: str = "Civil & Structural Engineering"
    academic_level: str = "University / Professional"  # ND, HND, University Year, Research
    version: str = "1.0.0"


class EngineeringProject(BaseModel):
    metadata: ProjectMetadata = Field(default_factory=ProjectMetadata)
    materials: List[MaterialModel] = Field(default_factory=list)
    sections: List[SectionModel] = Field(default_factory=list)
    nodes: List[NodeModel] = Field(default_factory=list)
    elements: List[ElementModel] = Field(default_factory=list)
    solver_settings: Dict[str, Any] = Field(default_factory=lambda: {"analysis_type": "linear_static"})
    results: Optional[Dict[str, Any]] = None
