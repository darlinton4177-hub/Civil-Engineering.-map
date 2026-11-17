# Technical Architecture

## 1. Architecture approach

Use a modular monolith initially, with clear boundaries. Do not start with microservices. Extract services only when operational scale justifies it.

## 2. Logical layers

### Frontend (Next.js + TypeScript)
- Department/course/topic browser
- Problem workbench
- Dynamic input forms generated from problem schemas
- Worked-solution viewer
- Plot/diagram panel
- Export controls
- User projects and saved runs

### API (FastAPI)
- Authentication/authorisation
- Course and formula catalogue endpoints
- Problem module registry
- Input validation
- Calculation orchestration
- Result serialization
- Export generation
- Background task submission/status

### Domain/calculation modules
Each problem module exposes a consistent interface:
- Metadata and version
- Input schema
- Validation
- Calculation function
- Result schema
- Diagram/plot data
- Reference and assumptions

### Persistence (PostgreSQL)
Store users, course content, formula metadata, module versions, saved projects, calculation runs, exports and review status. Store large generated artifacts in object storage, not database rows.

## 3. Recommended stack

- Next.js + React + TypeScript
- Tailwind CSS and an accessible component library
- FastAPI + Pydantic
- NumPy, SciPy, SymPy
- Pint for units
- Plotly for interactive charts
- Three.js for custom 3D scenes
- PostgreSQL
- Redis + a task queue only when background workloads are introduced
- S3-compatible object storage for exports

## 4. API conventions

Use versioned routes, for example `/api/v1`.

Suggested endpoints:
- `GET /api/v1/departments`
- `GET /api/v1/courses?department=civil`
- `GET /api/v1/problem-modules`
- `GET /api/v1/problem-modules/{module_id}`
- `POST /api/v1/problem-modules/{module_id}/validate`
- `POST /api/v1/problem-modules/{module_id}/solve`
- `GET /api/v1/runs/{run_id}`
- `POST /api/v1/runs/{run_id}/exports`
- `GET /api/v1/exports/{export_id}`

Do not expose an endpoint that evaluates arbitrary Python, JavaScript, shell commands or unrestricted symbolic input.

## 5. Calculation request lifecycle

1. Resolve module ID and exact module version.
2. Validate request schema.
3. Parse and normalise units.
4. Validate domain constraints and required assumptions.
5. Execute deterministic calculation.
6. Validate output and numerical tolerances.
7. Create graph/diagram-ready data.
8. Return result, steps, warnings, references and module version.
9. Save run if user requests or account policy requires it.

## 6. Frontend interaction

- Input controls must be typed and unit-aware.
- Graphs update when inputs change, with debouncing for expensive operations.
- Provide explicit Calculate/Reset buttons as well as optional live-update mode.
- Keep input values, result values and chart state synchronised.
- Allow toggling individual series, loads, reactions, labels, supports and annotations.
- Do not redraw a misleading graph when the calculation is invalid.

## 7. 2D and 3D

Use Plotly for most 2D/3D data plots. Use Three.js for interactive geometry and custom scenes. Keep numerical calculation separate from rendering. The solver returns structured data; the visualisation layer interprets it.
