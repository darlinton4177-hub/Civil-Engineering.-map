# Engineering & Science Hub
**Advanced Engineering Problem-Solving and Scientific Computation Platform**

A modular platform for university-level engineering and scientific problem solving. It combines:
- Course and topic library
- Verified formula catalogue
- Guided, step-by-step calculation workflows
- Interactive 2D/3D visualisation
- Engineering analysis modules
- Exportable calculations, graphs and reports

> The platform is an educational and analytical aid. It must never imply that an unverified result is an approved professional design.

## Product principles

1. **Advanced problems, clear explanations.** Keep the mathematics rigorous but explain each step in accessible language.
2. **Traceable calculations.** Every result must show inputs, units, assumptions, equations, substitutions, intermediate values and final results.
3. **Verified methods.** Every formula and engineering workflow must cite an authoritative textbook, standard or technical reference, including edition/year where relevant.
4. **No hidden assumptions.** Ask for missing design inputs or clearly state conservative/illustrative assumptions. Never silently invent loads, material grades, boundary conditions or code factors.
5. **Reactive visualisations.** Input changes update charts and diagrams; users can toggle loads, supports, result curves, labels, scales and units.
6. **Export everything useful.** Export calculation sheets, charts, data tables and reports independently.
7. **Modular growth.** New disciplines and problem types plug into shared calculation, graphing, units, validation and reporting services.

## Initial implementation focus

Build Civil/Structural Engineering first, with these vertical slices:
1. Simply supported beam: reactions, SFD, BMD and deflection (where the model assumptions are satisfied).
2. Strength of materials: axial stress/strain, bending stress, torsion and Mohr's circle.
3. Timber member checks: only after a selected design standard, material grade, load-duration/service class and all required inputs are specified.
4. Surveying: levelling/height of instrument and field-book checks.
5. Highway: chainage/elevation profile, horizontal and vertical alignment, sight distance and earthwork workflows.

Then expand to reinforced concrete, steel, geotechnics, hydraulics, transport, mechanical/electrical/chemical engineering, mathematics, physics and chemistry.

## Repository layout

```text
engineering-science-hub/
├── apps/
│   ├── web/                 # Next.js frontend
│   └── api/                 # FastAPI backend
├── packages/
│   ├── domain/              # Shared domain types and schemas
│   ├── formula-catalog/     # Versioned formula metadata
│   └── ui/                  # Shared UI components (later)
├── modules/
│   ├── civil/
│   │   ├── structural/
│   │   ├── strength-of-materials/
│   │   ├── timber/
│   │   ├── surveying/
│   │   ├── highway/
│   │   ├── geotechnical/
│   │   └── hydraulics/
│   ├── mechanical/
│   ├── electrical/
│   ├── chemical/
│   ├── mathematics/
│   ├── physics/
│   └── chemistry/
├── docs/
│   ├── PRODUCT_SPEC.md
│   ├── ARCHITECTURE.md
│   ├── CALCULATION_CONTRACT.md
│   ├── VISUALISATION_SPEC.md
│   ├── CONTENT_AND_STANDARDS.md
│   ├── TESTING_AND_SAFETY.md
│   └── ANTIGRAVITY_BUILD_GUIDE.md
├── examples/
│   ├── formula-record.example.json
│   └── problem-module.example.json
├── infra/
├── scripts/
├── .gitignore
└── README.md
```

## Local development (planned stack)

- Frontend: Next.js, React, TypeScript
- Backend: Python, FastAPI, Pydantic
- Numerical computation: NumPy, SciPy, SymPy
- Units: Pint
- Interactive charts: Plotly
- Custom 3D scenes: Three.js
- Database: PostgreSQL
- Formula rendering: KaTeX or MathJax

Pin dependency versions and use lockfiles before production deployment.

## Important

This repository is a **project blueprint and starter specification**, not a completed engineering solver. Each calculation module must be implemented, independently tested and reviewed against its declared method and reference before being published.
