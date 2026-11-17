"""
Node definition for finite element discretizations.
"""

from typing import Dict, Any, List, Optional


class Node:
    """Represents a discrete joint/node in the finite element mesh."""

    def __init__(
        self,
        id: int,
        x: float,
        y: float,
        z: float = 0.0,
        restraints: Optional[List[bool]] = None,
        loads: Optional[List[float]] = None,
        prescribed_displacements: Optional[Dict[int, float]] = None,
    ):
        self.id = int(id)
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

        # 2D default DOFs: [Tx, Ty, Rz]
        # True = restrained (fixed), False = free
        self.restraints = restraints if restraints is not None else [False, False, False]
        # Applied loads [Fx (N), Fy (N), Mz (N*m)]
        self.loads = loads if loads is not None else [0.0, 0.0, 0.0]
        # Prescribed displacements {local_dof_index: value_in_meters_or_radians}
        self.prescribed_displacements = prescribed_displacements or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "restraints": self.restraints,
            "loads": self.loads,
            "prescribed_displacements": self.prescribed_displacements,
        }
