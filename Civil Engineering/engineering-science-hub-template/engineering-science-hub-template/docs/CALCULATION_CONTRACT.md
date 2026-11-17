# Calculation Module Contract

Every published calculation must implement this contract.

## 1. Required metadata

- `module_id`: stable unique identifier
- `name`
- `discipline`, `course`, `topic`
- `module_version`
- `academic_level`
- `description`
- `applicability`
- `limitations`
- `references`: title, author/organisation, edition/year, clause/page/URL where licensed and available
- `design_standard`: exact standard and edition if code-based

## 2. Input requirements

For each input define:
- key and display label
- data type
- unit
- allowed range/domain
- whether required
- validation message
- help text
- default only if it is clearly an illustrative example

Never silently assume unknown loads, support conditions, material grades, exposure/service class, safety factors or design code.

## 3. Output requirements

Return:
- `status`
- `module_id` and `module_version`
- `inputs_normalized`
- `assumptions`
- `warnings`
- `steps[]`
- `results{}`
- `checks[]`
- `plot_data{}`
- `references[]`

Each step contains a title, explanation, equation (LaTeX), substituted values, result and units.

## 4. Numerical quality

- Use SI units internally unless a module explicitly declares another convention.
- Preserve unit dimensions through conversion.
- Avoid premature rounding.
- Define sign conventions.
- Handle singular, invalid and out-of-domain cases.
- Use tolerances appropriate to the method.
- State whether values are exact, approximate or numerical.
- Include independent checks where possible (e.g. equilibrium).

## 5. Formula governance

A formula record must identify its source and applicability. Record corrections and version history. A formula without a trustworthy source and test cases must remain draft/unpublished.

## 6. Safety and professional boundary

The platform is educational and supports preliminary analysis. It does not replace competent professional review, site investigation, authority approval or a complete code-compliant design. Display a clear notice for safety-critical structural, geotechnical, transport and building calculations.
