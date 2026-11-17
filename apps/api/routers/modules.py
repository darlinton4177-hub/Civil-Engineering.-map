from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from apps.api.supabase_client import supabase
from modules.civil.structural.simply_supported_beam import SimplySupportedBeamSolver

router = APIRouter(prefix="/problem-modules", tags=["Problem Modules"])


class ValidationRequest(BaseModel):
    inputs: Dict[str, Any]


class SolveRequest(BaseModel):
    inputs: Dict[str, Any] = Field(default_factory=dict)


@router.get("", response_model=List[dict])
def list_problem_modules(
    discipline: Optional[str] = Query(None, description="Discipline filter, e.g. 'civil'"),
    category: Optional[str] = Query(None, description="Category filter, e.g. 'structural', 'materials'"),
    course_code: Optional[str] = Query(None, description="Course filter, e.g. 'CE-201'"),
):
    """List problem modules with optional filters."""
    return supabase.get_problem_modules(
        discipline=discipline, category=category, course_code=course_code
    )


@router.get("/{module_slug}")
def get_problem_module(module_slug: str):
    """Retrieve metadata and schema for a specific problem module."""
    module = supabase.get_problem_module(module_slug)
    if not module:
        raise HTTPException(status_code=404, detail=f"Module '{module_slug}' not found")
    return module


@router.post("/{module_slug}/validate")
def validate_module_inputs(module_slug: str, payload: ValidationRequest):
    """Validate user inputs against module constraints before solving."""
    module = supabase.get_problem_module(module_slug)
    if not module:
        raise HTTPException(status_code=404, detail=f"Module '{module_slug}' not found")

    if module_slug == "simply-supported-beam":
        span = payload.inputs.get("span_length", 6.0)
        errors = []
        warnings = []
        if span <= 0:
            errors.append("Span length must be greater than 0.")
        if span > 100:
            warnings.append("Span length exceeds standard single-span beam limits (> 100m).")
        return {
            "valid": len(errors) == 0,
            "module_slug": module_slug,
            "warnings": warnings,
            "errors": errors,
        }

    return {
        "valid": True,
        "module_slug": module_slug,
        "warnings": [],
        "errors": [],
    }


@router.post("/{module_slug}/solve")
def solve_problem_module(module_slug: str, payload: SolveRequest):
    """Execute engineering computation for the given module."""
    module = supabase.get_problem_module(module_slug)
    if not module:
        raise HTTPException(status_code=404, detail=f"Module '{module_slug}' not found")

    if module_slug == "simply-supported-beam":
        try:
            span = float(payload.inputs.get("span_length", 6.0))
            point_loads = payload.inputs.get("point_loads", [{"x": 3.0, "magnitude": 20.0}])
            distributed_loads = payload.inputs.get("distributed_loads", [])
            e_gpa = float(payload.inputs.get("elastic_modulus", 200.0))
            i_mm4 = float(payload.inputs.get("moment_of_inertia", 80.0))

            solver = SimplySupportedBeamSolver(
                span_length=span,
                point_loads=point_loads,
                distributed_loads=distributed_loads,
                elastic_modulus_gpa=e_gpa,
                moment_of_inertia_10e6_mm4=i_mm4,
            )
            return solver.solve()
        except ValueError as err:
            raise HTTPException(status_code=422, detail=str(err))

    return {
        "status": "planned",
        "module_slug": module_slug,
        "version": module.get("version", "1.0.0"),
        "inputs": payload.inputs,
        "message": f"Calculation engine for {module.get('title')} is scheduled for subsequent milestone.",
    }
