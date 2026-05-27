# BioProspector Contract Template

Every Symphony-dispatched BioProspector issue should answer:

1. What route, step, candidate family, host-fit question, or review gate is this issue responsible for?
2. What structured outputs must it write?
3. What search budget applies?
4. What evidence level is required to continue?
5. What kill criteria stop downstream work?
6. What validation command should be run?

## Required Sections

- Agent Role
- Scientific Goal
- Inputs
- Artifact Contract
- Search Budget
- Continuation Criteria
- Kill Criteria
- Acceptance Criteria
- Validation Commands
- Dependencies
- Review Gate
- Claim Boundary
- `<!-- symphony:schema -->` block

## Search Budget Examples

Use explicit budgets:

- raw hits: max 20,000
- clustered representatives: max 1,000
- evidence-reviewed representatives: max 100
- shortlist: max 20
- final picks: max 5

Budgets should vary by step type. Broad enzyme families get wider searches and stricter compression. Narrow characterized families get deeper evidence review.
