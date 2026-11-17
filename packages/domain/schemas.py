from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class DepartmentBase(BaseModel):
    code: str
    name: str
    description: str
    icon: str = "building-2"


class Department(DepartmentBase):
    id: Optional[str] = None
    created_at: Optional[datetime] = None


class CourseBase(BaseModel):
    department_code: str
    code: str
    title: str
    level: str = "Undergraduate"
    description: str
    order_index: int = 0


class Course(CourseBase):
    id: Optional[str] = None
    created_at: Optional[datetime] = None


class ProblemModuleBase(BaseModel):
    course_code: str
    slug: str
    title: str
    description: str
    discipline: str = "civil"
    category: str
    status: Literal["active", "beta", "planned"] = "planned"
    version: str = "0.1.0"
    icon: str = "calculator"


class ProblemModule(ProblemModuleBase):
    id: Optional[str] = None
    created_at: Optional[datetime] = None


class CalculationRunCreate(BaseModel):
    module_slug: str
    title: str = "Untitled Calculation"
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = None


class CalculationRun(CalculationRunCreate):
    id: Optional[str] = None
    user_id: Optional[str] = None
    created_at: Optional[datetime] = None


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "engineering-science-hub-api"
    version: str = "0.1.0"
    supabase_connected: bool
    timestamp: str
