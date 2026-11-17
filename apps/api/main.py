from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.api.config import settings
from apps.api.routers import health, departments, courses, modules, runs, fea

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=(
        "Engineer Realm Multiphysics API: Unified environment for engineering computation, "
        "finite element analysis (FEA), 3D structural simulation, and scientific intelligence."
    ),
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register versioned API routers
app.include_router(health.router, prefix=settings.API_PREFIX)
app.include_router(departments.router, prefix=settings.API_PREFIX)
app.include_router(courses.router, prefix=settings.API_PREFIX)
app.include_router(modules.router, prefix=settings.API_PREFIX)
app.include_router(runs.router, prefix=settings.API_PREFIX)
app.include_router(fea.router, prefix=settings.API_PREFIX)


@app.get("/")
def root():
    return {
        "service": "Engineer Realm — Engineering & Science Hub API",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "api_v1": settings.API_PREFIX,
        "capabilities": [
            "Linear Static FEA",
            "Modal Dynamics",
            "Eigenvalue Buckling",
            "Mesh Convergence",
            "Structural Design Detailing",
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("apps.api.main:app", host="0.0.0.0", port=8000, reload=True)
