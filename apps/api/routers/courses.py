from typing import List, Optional
from fastapi import APIRouter, Query
from apps.api.supabase_client import supabase

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("", response_model=List[dict])
def list_courses(
    department: Optional[str] = Query(None, description="Filter by department code, e.g. 'civil'")
):
    """List available courses with optional department filter."""
    return supabase.get_courses(department_code=department)
