import json
import logging
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.error

from apps.api.config import settings
from apps.api.data.seed_catalog import DEPARTMENTS, COURSES, PROBLEM_MODULES

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Lightweight Supabase REST client with seamless fallback to verified seed data."""

    def __init__(self):
        self.base_url = settings.SUPABASE_URL.rstrip("/")
        self.anon_key = settings.SUPABASE_ANON_KEY
        self.service_key = settings.SUPABASE_SERVICE_ROLE_KEY

    def _headers(self, use_service_key: bool = False) -> Dict[str, str]:
        key = self.service_key if use_service_key else self.anon_key
        return {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    def check_connection(self) -> bool:
        """Verify Supabase Auth / REST connectivity."""
        try:
            url = f"{self.base_url}/auth/v1/settings"
            req = urllib.request.Request(url, headers={"apikey": self.anon_key})
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status == 200
        except Exception as e:
            logger.warning(f"Supabase connection check failed: {e}")
            return False

    def get_departments(self) -> List[Dict[str, Any]]:
        """Fetch departments from Supabase, fallback to seed catalog."""
        try:
            url = f"{self.base_url}/rest/v1/departments?select=*"
            req = urllib.request.Request(url, headers=self._headers(use_service_key=True))
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    if data:
                        return data
        except Exception as e:
            logger.info(f"Using in-memory departments seed catalog ({e})")
        return DEPARTMENTS

    def get_courses(self, department_code: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch courses from Supabase, fallback to seed catalog."""
        try:
            query = "select=*"
            if department_code:
                query += f"&department_code=eq.{department_code}"
            url = f"{self.base_url}/rest/v1/courses?{query}"
            req = urllib.request.Request(url, headers=self._headers(use_service_key=True))
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    if data:
                        return data
        except Exception as e:
            logger.info(f"Using in-memory courses seed catalog ({e})")
        
        if department_code:
            return [c for c in COURSES if c["department_code"] == department_code]
        return COURSES

    def get_problem_modules(
        self,
        discipline: Optional[str] = None,
        category: Optional[str] = None,
        course_code: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch problem modules, fallback to seed catalog."""
        try:
            filters = ["select=*"]
            if discipline:
                filters.append(f"discipline=eq.{discipline}")
            if category:
                filters.append(f"category=eq.{category}")
            if course_code:
                filters.append(f"course_code=eq.{course_code}")
            
            url = f"{self.base_url}/rest/v1/problem_modules?{'&'.join(filters)}"
            req = urllib.request.Request(url, headers=self._headers(use_service_key=True))
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    if data:
                        return data
        except Exception as e:
            logger.info(f"Using in-memory problem modules catalog ({e})")
        
        res = PROBLEM_MODULES
        if discipline:
            res = [m for m in res if m.get("discipline") == discipline]
        if category:
            res = [m for m in res if m.get("category") == category]
        if course_code:
            res = [m for m in res if m.get("course_code") == course_code]
        return res

    def get_problem_module(self, slug: str) -> Optional[Dict[str, Any]]:
        """Fetch single module by slug."""
        try:
            url = f"{self.base_url}/rest/v1/problem_modules?slug=eq.{slug}&select=*"
            req = urllib.request.Request(url, headers=self._headers(use_service_key=True))
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    if data:
                        return data[0]
        except Exception as e:
            logger.info(f"Using seed catalog for module {slug} ({e})")
        
        for m in PROBLEM_MODULES:
            if m["slug"] == slug:
                return m
        return None


supabase = SupabaseClient()
