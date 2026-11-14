# BioProspector Documentation

## Get Started

- [Quickstart](QUICKSTART.md) · Run the local demo and inspect its outputs.
- [Agent installation](AGENT_INSTALL.md) · Link the skill and install the CLI.
- [Agent playbook](AGENT_PLAYBOOK.md) · Prompts for review and planning.
- [First campaign](FIRST_CAMPAIGN.md) · Create a manifest and validate its inputs.
- [FAQ](FAQ.md) and [glossary](GLOSSARY.md) · Terms and common questions.

## Tools and Workflows

- [CLI reference](CLI_REFERENCE.md) · Commands and outputs.
- [Tool guide](tool-stack.md) · Tool roles, inputs, and outputs.
- [Integration guide](TOOL_INTEGRATIONS.md) · Supported result formats.
- [Optional tools](OPTIONAL_TOOLS.md) · Commands the doctor checks.
- [Tool review](opportunity-radar.md) · Releases and evaluation questions.
- [Workflows](WORKFLOWS.md), [modes](MODES.md), and [use cases](USE_CASES.md) · Campaign workflows and examples.
- [Capability overview](PUBLIC_LAUNCH_PAD.md) and [command and artifact map](capability-map.md) · Available toolkit components.
- [Architecture](architecture.md) and [product foundation](product-foundation.md) · Campaign and execution model.

## Campaign contracts

- [`dossier-schema.md`](dossier-schema.md): dossier, ledger, and artifact contracts.
- [`operator-intake.md`](operator-intake.md): short intake loop and `skip and go` boundary.
- [`no-false-success-gates.md`](no-false-success-gates.md): gates that block overclaiming.
- [`monitoring-provenance.md`](monitoring-provenance.md): provenance, heartbeat, and artifact proof.
- [`stage-progress-and-provider-preflight.md`](stage-progress-and-provider-preflight.md): long-run stage contracts.
- [`target-modularity.md`](target-modularity.md): target-swappable manifest conventions.
- [`self-learning-skill-runbook.md`](self-learning-skill-runbook.md): turn workflow hiccups into durable improvements.

## Search and evidence lanes

- [`ambiguity-workflows.md`](ambiguity-workflows.md): dark-step and unknown-gene handling.
- [`enzyme-family-search.md`](enzyme-family-search.md): family-level candidate expansion.
- [`genome-context-mining.md`](genome-context-mining.md): context mining without overclaiming.
- [`genecluster-atlas-public-lane.md`](genecluster-atlas-public-lane.md): metadata-only atlas planner.
- [`host-structure-risk.md`](host-structure-risk.md): host fit and structure-risk review.
- [`runpod-blast-candidate-package.md`](runpod-blast-candidate-package.md): high-detail search package contract.

## Provider readiness

- [`runpod-stack.md`](runpod-stack.md): RunPod readiness contract.
- [`aws-elasticblast-stack.md`](aws-elasticblast-stack.md): AWS ElasticBLAST readiness contract.
- [`compute-provider-strategy.md`](compute-provider-strategy.md): provider role and fallback policy.
- [`symphony-linear-sidecar.md`](symphony-linear-sidecar.md): portable Symphony + Linear sidecar.

## Release boundaries

- [`NON_CLAIMS.md`](../NON_CLAIMS.md): what the toolkit does and never claims by itself.
- [`BIOSAFETY.md`](../BIOSAFETY.md): operator-review boundary for biological work.
- [`SECURITY.md`](../SECURITY.md): sensitive-disclosure and data-handling policy.
- [`PRIVACY_SECURITY_MODEL.md`](PRIVACY_SECURITY_MODEL.md): data classes, threat model, and release controls.
- [`PUBLIC_RELEASE_PREP.md`](PUBLIC_RELEASE_PREP.md): local release gate and expected results.
- [`PUBLIC_SWITCH_CHECKLIST.md`](PUBLIC_SWITCH_CHECKLIST.md): checklist for every public release.

## Design and roadmap

- [`design-principles.md`](design-principles.md): durable design and evidence principles.
- [`roadmap.md`](roadmap.md): public product direction and adoption gates.
- [`future-campaigns.md`](future-campaigns.md): future public campaign ideas and boundaries.

## Examples

- [`../demos/public-nootkatone-demo.md`](../demos/public-nootkatone-demo.md): public frontier demo.
- [`../demos/public-huperzine-frontier-demo.md`](../demos/public-huperzine-frontier-demo.md): public dark-step/source-context demo.
- [`../demos/expected-outputs`](../demos/expected-outputs): compact output snapshots.
- [`../skills/bioprospector/examples/vanillin-yeast-v0`](../skills/bioprospector/examples/vanillin-yeast-v0): starter scaffold.
- [`../skills/bioprospector/examples/nootkatone-yeast-v0`](../skills/bioprospector/examples/nootkatone-yeast-v0): public frontier scaffold.
- [`../skills/bioprospector/examples/huperzine-frontier-public-v0`](../skills/bioprospector/examples/huperzine-frontier-public-v0): dark-step scaffold.
- [`../skills/bioprospector/examples/genecluster-synthetic-v0`](../skills/bioprospector/examples/genecluster-synthetic-v0): synthetic Atlas contract fixture.
- [`../templates/README.md`](../templates/README.md): issue template map.
