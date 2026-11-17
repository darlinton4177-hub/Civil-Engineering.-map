from datetime import datetime, timezone
from fastapi import APIRouter
from apps.api.config import settings
from apps.api.supabase_client import supabase

router = APIRouter(prefix="", tags=["Health"])


@router.get("/health")
def get_health():
    supabase_ok = supabase.check_connection()
    return {
        "status": "healthy" if supabase_ok else "degraded",
        "service": settings.API_TITLE,
        "version": settings.API_VERSION,
        "supabase_connected": supabase_ok,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
