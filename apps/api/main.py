from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.api.config import settings
from apps.api.routers import health, departments, courses, modules, runs

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=(
        "Engineering & Science Hub API: Modular platform for university-level "
        "engineering problem solving and scientific computation."
    ),
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# Enable CORS for frontend clients (Next.js web & future mobile)
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


@app.get("/")
def root():
    return {
        "service": settings.API_TITLE,
        "version": settings.API_VERSION,
        "docs": "/docs",
        "api_v1": settings.API_PREFIX,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("apps.api.main:app", host="0.0.0.0", port=8000, reload=True)
