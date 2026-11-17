from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runs", tags=["Calculation Runs"])

# In-memory storage for active session calculation runs
_RUNS_DB: List[Dict[str, Any]] = []


class CreateRunPayload(BaseModel):
    module_slug: str
    title: str = "Untitled Calculation"
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = None


@router.get("", response_model=List[Dict[str, Any]])
def list_runs():
    """List recent calculation runs."""
    return _RUNS_DB


@router.post("", status_code=201)
def create_run(payload: CreateRunPayload):
    """Save a calculation run."""
    run_record = {
        "id": f"run-{len(_RUNS_DB) + 1}",
        "module_slug": payload.module_slug,
        "title": payload.title,
        "inputs": payload.inputs,
        "outputs": payload.outputs,
        "notes": payload.notes,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _RUNS_DB.insert(0, run_record)
    return run_record
