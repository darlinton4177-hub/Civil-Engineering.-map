from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from apps.api.supabase_client import supabase

router = APIRouter(prefix="/problem-modules", tags=["Problem Modules"])


class ValidationRequest(BaseModel):
    inputs: Dict[str, Any]


class SolveRequest(BaseModel):
    inputs: Dict[str, Any]


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
    
    # Milestone 1: contract validation check
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
    
    # Milestone 1: endpoint stub adhering to CALCULATION_CONTRACT.md
    return {
        "status": "ready",
        "module_slug": module_slug,
        "version": module.get("version", "1.0.0"),
        "inputs": payload.inputs,
        "message": f"Calculation pipeline contract initialized for {module.get('title')}. Full numerical solver active in Milestone 2.",
    }
