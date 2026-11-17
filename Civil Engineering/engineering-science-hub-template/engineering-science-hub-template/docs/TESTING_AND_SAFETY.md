# Testing, Validation and Safety

## 1. Required test layers

- Unit tests for equations and helper functions
- Dimensional/unit tests
- Input validation tests
- Regression tests using published textbook/code examples
- Property-based tests where useful
- API contract tests
- Frontend interaction tests
- Export integrity tests
- Performance tests for expensive simulations

## 2. Engineering test cases

Each module must include:
- At least one normal case
- Boundary cases
- Invalid/missing input cases
- Unit conversion cases
- Independent verification case
- Expected tolerance and source

For structural analysis, test equilibrium and consistency between loads, reactions, shear and moment. For surveying, test arithmetic closure. For highway profiles, test chainage ordering, grade calculations and curve constraints.

## 3. Safety-critical warnings

Show a warning when results may affect life safety, public infrastructure or property. Clearly identify:
- Educational example vs preliminary analysis vs code-based design check
- Missing data
- Simplifications
- Load combinations and factors used
- Code/edition
- Required independent professional review

Never produce an unqualified statement that a structure, road, foundation or component is safe based on incomplete inputs.

## 4. Security

- Validate and limit input size/ranges.
- Never execute user-provided source code.
- Restrict symbolic expression parsing to an allowlisted grammar.
- Apply request rate limits.
- Use authentication and authorisation for saved projects.
- Keep secrets in environment variables.
- Scan dependencies and generated files.
