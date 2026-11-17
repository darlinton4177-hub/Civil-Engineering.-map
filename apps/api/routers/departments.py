from typing import List
from fastapi import APIRouter
from apps.api.supabase_client import supabase

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("", response_model=List[dict])
def list_departments():
    """List all supported academic departments."""
    return supabase.get_departments()
