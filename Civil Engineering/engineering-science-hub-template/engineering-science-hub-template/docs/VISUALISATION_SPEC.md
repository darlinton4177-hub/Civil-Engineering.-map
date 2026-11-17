# Interactive Visualisation and Export Specification

## 1. Core requirement

Visualisations must be generated from solver output, not from separately hard-coded example values. When inputs change and a new valid result is produced, the visualisation must reflect that result.

## 2. Graph controls

Provide relevant controls for each graph:
- Show/hide each data series
- Show/hide axes, grid, legend, labels and annotations
- Zoom, pan, reset view
- Change axis range and scale where mathematically valid
- Select units and display precision
- Toggle input loads, support symbols and reaction arrows
- Switch between graph and data table
- Compare multiple cases where supported

Do not expose controls that do not apply to the current plot.

## 3. Structural diagrams

For beam analysis, support:
- Beam geometry and supports
- Applied point loads and distributed loads
- Reaction arrows and values
- Shear force diagram
- Bending moment diagram
- Deflection curve where the solver supports it
- Key locations and values
- Sign convention legend

Keep diagrams aligned to a common horizontal coordinate and clearly distinguish units.

## 4. Highway plots

Support:
- Chainage/elevation longitudinal profile
- Existing ground and proposed formation
- Vertical curves and grade labels
- Cross-sections at selected chainages
- Cut/fill regions
- Tabular station data

## 5. 3D scenes

- Orbit/rotate, pan and zoom
- Reset camera
- Show/hide layers
- Display dimensions and axes
- Select components for metadata
- Responsive rendering and graceful fallback on low-powered devices

## 6. Downloads

Each result panel should have its own export actions:
- Graph: PNG, SVG where supported, PDF
- Data: CSV and XLSX
- Worked solution: PDF
- Full calculation report: PDF
- 3D scene: supported image snapshot and structured geometry/data export where implemented

Exports must include title, module/version, units, date/time, inputs, assumptions and reference information. Do not claim an export type is supported until it has been implemented and tested.
