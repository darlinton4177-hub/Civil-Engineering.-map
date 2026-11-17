# Product Specification

## 1. Mission

Create a high-quality, browser-based advanced engineering and scientific problem-solving environment. A university student should be able to select a recognised problem type, enter data, follow a transparent solution, interact with the resulting graph/diagram and download the outputs.

## 2. Audience

- Undergraduate engineering students
- Postgraduate students and researchers
- Engineering educators
- Practising engineers using the platform for learning, preliminary analysis and checking

## 3. Academic level

The platform focuses on higher-institution and advanced technical content. Do not create a secondary-school mathematics track. Explain advanced mathematics clearly without lowering the technical standard.

## 4. Main experience

A user journey should be:

1. Choose discipline → course → topic → problem type.
2. Read the problem definition, applicability and required inputs.
3. Enter values with units and choose a supported method/design standard.
4. Validate inputs and identify missing data.
5. Run the calculation.
6. Review the worked solution, assumptions and checks.
7. Explore reactive diagrams/graphs.
8. Change inputs or display options and recalculate.
9. Export the calculation report, graph, diagram and data table separately.

## 5. Required departments

### Engineering
- Civil: structural, geotechnical, transportation/highway, water resources, environmental, construction, surveying/geomatics, materials, bridge/tunnel and infrastructure
- Mechanical
- Electrical and electronic
- Chemical
- Agricultural and biosystems
- Computer
- Materials
- Industrial
- Marine/offshore
- Mining and petroleum (where appropriate)

### Mathematical and scientific disciplines
- Advanced engineering mathematics
- Numerical methods and computational mathematics
- Classical physics
- Quantum physics
- Relativity and astrophysics
- Astronomy and cosmology, including Big Bang cosmology
- General, organic, inorganic, physical and analytical chemistry

## 6. Priority problem families

### Structural analysis
- Support reactions
- Simply supported and cantilever beams
- Shear force diagrams (SFD)
- Bending moment diagrams (BMD)
- Slope and deflection
- Trusses and frames
- Influence lines
- Indeterminate structures (later milestone)

### Strength of materials
- Axial stress and strain
- Thermal stress
- Torsion
- Bending stress
- Shear stress
- Combined stress
- Principal stresses and Mohr's circle
- Strain energy and buckling

### Timber engineering
- Member classification and material properties
- Bending, tension and compression checks
- Stability/buckling
- Deflection/serviceability
- Connection design
- Duration, moisture/service class and modification factors
- Standard-specific checks

Timber design is code-dependent. The user must select the applicable standard and edition. Do not mix factors or clauses from different standards.

### Highway engineering
- Survey data and chainage
- Existing/proposed longitudinal profiles
- Horizontal and vertical curves
- Gradients and superelevation
- Sight distance
- Cross-sections
- Pavement design
- Cut/fill and earthwork quantities
- Traffic flow and capacity

### Surveying
- Height of instrument (HI) method
- Rise-and-fall method
- Reduced levels and arithmetic checks
- Traverse calculations
- Coordinate geometry
- Setting out
- Contouring and profile levelling

### Other civil modules
- Reinforced concrete and steel design
- Geotechnical/foundation engineering
- Hydraulics and hydrology
- Water/wastewater
- Construction planning, estimating and quantity take-off
- Materials testing

## 7. Learning and explanation design

Every worked solution should include:
- What the problem asks
- Given data
- Required unknowns
- Diagram and sign convention
- Applicable assumptions
- Why the selected method applies
- Governing equations
- Variable definitions and units
- Step-by-step substitution
- Intermediate results
- Final answer with units and sensible precision
- Independent equilibrium/consistency checks where applicable
- Interpretation of the result
- Common mistakes
- Further practice problem

Use plain language around rigorous mathematics. Define technical terms at first use. Provide optional deeper theory.

## 8. Non-functional requirements

- Responsive desktop/tablet/mobile UI
- Accessible keyboard controls and readable contrast
- Secure input validation
- Reproducible calculations
- Versioned formula and standards content
- Fast common calculations
- Background jobs for computationally expensive simulations
- Clear error states and loading states
- Automated test coverage
- Audit trail for published calculation modules
