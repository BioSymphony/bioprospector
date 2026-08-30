#!/usr/bin/env python3
"""Generate dry-run Linear issue bodies for a BioProspector campaign."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


HEAVY_SEARCH_WIDTHS = {"wide", "frontier"}
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return "REPLACE_ME_EXTERNAL_PATH"


def declared_path(base: Path, value: object) -> Path | None:
    rel = Path(str(value or ""))
    if not str(value or "").strip() or rel.is_absolute():
        return None
    resolved_base = base.resolve()
    resolved = (resolved_base / rel).resolve()
    try:
        resolved.relative_to(resolved_base)
    except ValueError:
        return None
    return resolved

INCLUDE_FLAG_ATTRS = (
    "include_evidence_lanes",
    "include_runpod_prep",
    "include_elasticblast_prep",
    "include_literature_lanes",
    "include_ambiguity_lanes",
    "include_enzyme_family_sweeps",
    "include_genome_mining_lanes",
    "include_structure_risk_lanes",
    "include_host_comparison_lanes",
    "include_assay_handoff_lanes",
    "include_monitoring_lanes",
    "include_stage_contract_lanes",
    "include_input_audit_lanes",
    "include_operator_intake_lanes",
    "include_maturity_lanes",
    "include_target_evidence_lanes",
    "include_decoy_control_lanes",
    "include_self_check_lanes",
    "include_provider_lanes",
    "include_provider_preflight_lanes",
    "include_framework_lanes",
    "include_sequence_search_lanes",
    "include_candidate_package_lanes",
    "include_candidate_intelligence_lanes",
    "include_genecluster_atlas_lanes",
    "include_scale_control_lanes",
    "include_self_learning_lanes",
    "include_tool_execution_proof_lanes",
    "include_template_design_lanes",
    "include_ledger_schema_lanes",
    "include_supply_chain_lanes",
    "include_active_site_audit_lanes",
    "include_route_rule_lanes",
    "include_thermodynamics_lanes",
    "include_metabolic_model_lanes",
    "include_strain_design_lanes",
    "include_chemoenzymatic_fallback_lanes",
    "include_bgc_context_lanes",
    "include_metagenome_context_lanes",
    "include_metabolomics_handoff_lanes",
    "include_compound_source_lanes",
    "include_review_surface_lanes",
)

DEFAULT_INCLUDE_FLAGS = {
    "include_candidate_intelligence_lanes",
}

INCLUDE_PROFILES = {
    "core-evidence": {
        "include_evidence_lanes",
        "include_literature_lanes",
        "include_decoy_control_lanes",
    },
    "full-frontier": set(INCLUDE_FLAG_ATTRS),
}


def resolve_include_options(profile: str | None, explicit: dict[str, bool]) -> dict[str, bool]:
    options = {name: name in DEFAULT_INCLUDE_FLAGS for name in INCLUDE_FLAG_ATTRS}
    if profile:
        try:
            profile_flags = INCLUDE_PROFILES[profile]
        except KeyError as exc:
            choices = ", ".join(sorted(INCLUDE_PROFILES))
            raise ValueError(f"unknown include profile {profile!r}; expected one of: {choices}") from exc
        for name in profile_flags:
            options[name] = True
    for name in INCLUDE_FLAG_ATTRS:
        if explicit.get(name):
            options[name] = True
    return options


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_optional_tsv(base: Path, ledgers: dict, key: str) -> list[dict[str, str]]:
    rel = ledgers.get(key)
    if not rel:
        return []
    path = declared_path(base, rel)
    if path is None or not path.exists():
        return []
    return read_tsv(path)


def slug(value: str) -> str:
    cleaned = []
    for char in value.lower():
        if char.isalnum():
            cleaned.append(char)
        elif char in {" ", "_", "-", "/", ":"}:
            cleaned.append("-")
    out = "".join(cleaned).strip("-")
    while "--" in out:
        out = out.replace("--", "-")
    return out or "issue"


def issue_body(
    *,
    title: str,
    role: str,
    goal: str,
    inputs: list[str],
    artifacts: list[str],
    acceptance: list[str],
    search_budget: list[str] | None = None,
    continuation_criteria: list[str] | None = None,
    kill_criteria: list[str] | None = None,
    validation_command: str,
    dependencies: list[str],
    touched_areas: list[str] | None = None,
    review_gate: str | None = None,
    claim_boundary: str,
    requires_heavy_compute: bool = False,
) -> str:
    def bullets(values: list[str]) -> str:
        return "\n".join(f"- {value}" for value in values)

    search_budget = search_budget or [
        "Use the provided campaign manifest, target contract, and ledgers first.",
        "Do not copy private sequences, raw reads, large databases, model weights, or restricted data into this repo.",
    ]
    continuation_criteria = continuation_criteria or [
        "Continue only when required artifacts are written in structured ledgers or dossier notes.",
        "Downstream issues remain blocked until the review gate and claim boundary are satisfied.",
    ]
    kill_criteria = kill_criteria or [
        "Stop or park the issue if required evidence cannot be represented within the claim boundary.",
        "Stop if the work requires private, unpublished, restricted, or large biological data inside this repo.",
    ]
    touched_areas = touched_areas or ["ledgers", "dossier"]
    review_gate = review_gate or (
        "The orchestrator should verify structured outputs, evidence level, continuation criteria, "
        "kill criteria, touched areas, and claim boundary before unlocking downstream issues."
    )
    schema_touched_areas = "\n".join(f"  - {area}" for area in touched_areas)
    heavy = "true" if requires_heavy_compute else "false"
    return f"""# {title}

## Agent Role

{role}

## Scientific Goal

{goal}

## Inputs

{bullets(inputs)}

## Artifact Contract

{bullets(artifacts)}

## Acceptance Criteria

{bullets(acceptance)}

## Search Budget

{bullets(search_budget)}

## Continuation Criteria

{bullets(continuation_criteria)}

## Kill Criteria

{bullets(kill_criteria)}

## Validation Commands

```bash
{validation_command}
```

## Dependencies

{bullets(dependencies)}

## Review Gate

{review_gate}

## Touched Areas

{bullets(touched_areas)}

## Claim Boundary

{claim_boundary}

<!-- symphony:schema
complexity: medium
touched_areas:
{schema_touched_areas}
local_friendly: true
requires_private_data: false
requires_heavy_compute: {heavy}
-->
"""


def with_claude_lane(body: str) -> str:
    return f"{body}\n## Routing\n\n- lane:claude\n"


def step_search_budget(step: dict[str, str]) -> list[str]:
    width = step.get("candidate_search_width", "")
    budgets = {
        "tiny": [
            "Review known seed candidates only; cap the raw candidate universe at 10 records.",
            "Use existing ledgers and cited resources before any new database query.",
        ],
        "narrow": [
            "Cap the raw candidate universe at 25 records or 2 tightly scoped query families.",
            "Stop expansion once enough evidence exists for a route-stitching yes/no decision.",
        ],
        "medium": [
            "Cap the raw candidate universe at 75 records or 3 query families.",
            "Compress to at most 15 evidence-reviewed candidates before downstream stitching.",
        ],
        "wide": [
            "Cap the raw candidate universe at 500 records or 3 query families.",
            "Compress through domain, motif, substrate, host-fit, and provenance filters before shortlisting.",
            "Use RunPod/HPC only after a prep issue or equivalent query contract exists.",
        ],
        "frontier": [
            "Cap the raw candidate universe at 2,000 records or 5 query families before orchestrator review.",
            "Cluster and compress aggressively before manual evidence review; preserve rejected classes.",
            "Use RunPod/HPC only after a prep issue or equivalent query contract exists.",
        ],
    }
    return budgets.get(width, budgets["medium"])


def step_continuation_criteria(step: dict[str, str]) -> list[str]:
    return [
        f"Continue only if step {step['step_id']} has a candidate funnel update or a documented unknown-step split.",
        "Promote candidates only when evidence class, claim level, rejection risk, and provenance are explicit.",
        "Unlock route stitching only after route-critical gaps are represented in the ledgers.",
    ]


def step_kill_criteria(step: dict[str, str]) -> list[str]:
    return [
        "Kill or park the step if no credible enzyme family, chemistry class, or unknown-step hypothesis survives the search budget.",
        "Reject candidates that are broad family hits without domain, motif, substrate, or provenance support.",
        "Stop if executing the search requires private or restricted data that cannot be summarized safely.",
    ]


def evidence_lane_issue(
    *,
    prefix: str,
    step: dict[str, str],
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    step_id = step["step_id"]
    filename = f"{prefix}-evidence-step-{slug(step_id)}-{slug(step['enzyme_role'])}.md"
    body = issue_body(
        title=f"{prefix}: Evidence lane for step {step_id} {step['enzyme_role']}",
        role="Evidence Lane reviewer",
        goal=(
            f"Independently review the evidence trail for wide/frontier step {step_id}: "
            f"{step['substrate']} -> {step['product']}."
        ),
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            f"Parent step id: {step_id}",
            f"Route id: {step['route_id']}",
            f"Transformation: {step['transformation']}",
            f"Evidence need: {step['evidence_need']}",
            f"Candidate search width: {step['candidate_search_width']}",
        ],
        artifacts=[
            "candidate-funnels.tsv evidence_reviewed and shortlist updates",
            "enzyme-draft-board.tsv evidence_classes and claim_level updates",
            "rejected-candidates.tsv rows for weak, misleading, or unsupported hits",
            "claim-ledger.md caveats for promoted candidates",
            "provenance notes for databases, query versions, thresholds, and access modes",
        ],
        acceptance=[
            "Every promoted candidate has a defensible claim level and evidence class.",
            "Family-only or similarity-only hits remain caveated or rejected.",
            "Evidence gaps are explicit enough for route stitching and red-team review.",
            "No restricted database content, raw sequence dumps, or large search output is copied into this repo.",
        ],
        search_budget=[
            "Review at most 30 evidence-bearing candidates before asking the orchestrator to widen or split the lane.",
            "Prioritize characterized, accession-backed, motif/domain-supported, and host-compatible evidence.",
            "Summarize database and literature evidence; store only compact provenance and derived judgments in this repo.",
        ],
        continuation_criteria=[
            f"Continue parent step {step_id} only if at least one candidate class has evidence above raw similarity.",
            "Unlock stitching only when the evidence lane records why each promoted candidate is still only a candidate.",
        ],
        kill_criteria=[
            "Kill or park candidate classes that cannot cross the evidence threshold after the review budget.",
            "Stop if evidence depends on private, restricted, or unredistributable records that cannot be cited safely.",
        ],
        validation_command=validation,
        dependencies=[
            f"Child of generated step issue for {step_id}.",
            "Blocks Pathway Stitcher integration for routes using this step.",
            "Blocks Red-team claim audit for promoted candidates from this step.",
        ],
        touched_areas=["candidate-funnels", "enzyme-draft-board", "claim-ledger", "provenance", "dossier"],
        review_gate=(
            "The orchestrator should compare this evidence lane against the parent step draft, then unlock "
            "stitching only when promoted claims stay inside the claim boundary."
        ),
        claim_boundary=claim_boundary,
        requires_heavy_compute=False,
    )
    return filename, body


def campaign_runpod_prep_issue(
    *,
    prefix: str,
    manifest: dict,
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    execution = manifest.get("execution", {})
    remote_workdir = execution.get("remote_workdir", "/workspace/bioprospector/runs/<campaign_id>")
    filename = f"{prefix}-runpod-00-campaign-prep.md"
    body = issue_body(
        title=f"{prefix}: RunPod campaign prep",
        role="RunPod prep operator",
        goal="Prepare the remote search lane contract without launching pods or executing heavy biological search.",
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            "RunPod stack doc: docs/runpod-stack.md",
            "Resource ledger: resource-ledger.tsv",
            f"Remote workdir convention: {remote_workdir}",
            f"Artifact policy: {execution.get('artifact_policy', 'summaries_only')}",
        ],
        artifacts=[
            "RunPod readiness notes for image, tools, and database access modes",
            "provider-launch-preflight-ledger.tsv rows for image pull, registry auth, volume, snapshot, payload, secrets, and stage contracts",
            "stage-contract-ledger.tsv rows for long-run checkpoint, timeout, done marker, and resume behavior",
            "remote workdir layout checklist",
            "resource-ledger.tsv updates for public resources and license posture",
            "compact-output contract for ledgers, hashes, citations, and summaries",
        ],
        acceptance=[
            "No RunPod instance is created by this issue.",
            "The image/tool plan names only approved public-data tools and resources.",
            "Private registry images remain blocked until provider-side pull auth is verified outside repo and Linear.",
            "Provider desiredStatus/RUNNING is not treated as evidence that a container pulled or work progressed.",
            "The remote workdir, compact output policy, and cleanup expectations are explicit.",
            "Downstream heavy search issues can run without writing large artifacts into this repo.",
        ],
        search_budget=[
            "Inspect campaign docs, resource ledger, and RunPod stack guidance only.",
            "Do not download databases, model weights, raw reads, or private sequence data.",
            "Limit output to a readiness checklist and compact policy updates.",
        ],
        continuation_criteria=[
            "Continue to step-specific RunPod prep only when tool, resource, remote workdir, and artifact policies are explicit.",
            "Continue to heavy execution only after blocking provider preflight rows pass and an operator confirms budget and data-policy fit outside this dry run.",
        ],
        kill_criteria=[
            "Stop if the campaign requires private, unpublished, restricted, or unlicensed resources for the planned search lane.",
            "Stop if the output contract would return large search files instead of compact ledgers and provenance.",
            "Stop if the exact image cannot be pulled by the provider or the branch/snapshot does not contain the referenced bundle.",
        ],
        validation_command=validation,
        dependencies=[
            "Blocked by target contract review.",
            "Blocks step-specific RunPod prep drafts for wide/frontier steps.",
        ],
        touched_areas=["runpod", "provider-launch-preflight-ledger", "stage-contract-ledger", "resource-ledger", "dossier", "docs"],
        review_gate=(
            "The orchestrator should verify the prep issue is policy-only and does not imply pod creation, "
            "database mirroring, or biological validation."
        ),
        claim_boundary=claim_boundary,
        requires_heavy_compute=False,
    )
    return filename, body


def step_runpod_prep_issue(
    *,
    prefix: str,
    step: dict[str, str],
    manifest: dict,
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    execution = manifest.get("execution", {})
    remote_root = execution.get("remote_workdir", "/workspace/bioprospector/runs/<campaign_id>")
    step_id = step["step_id"]
    filename = f"{prefix}-runpod-step-{slug(step_id)}-{slug(step['enzyme_role'])}.md"
    body = issue_body(
        title=f"{prefix}: RunPod prep for step {step_id} {step['enzyme_role']}",
        role="RunPod step prep worker",
        goal=(
            f"Prepare a reproducible remote query contract for {step['candidate_search_width']} step {step_id} "
            "without launching pods or running the heavy search."
        ),
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            f"Step id: {step_id}",
            f"Route id: {step['route_id']}",
            f"Transformation: {step['transformation']}",
            f"Evidence need: {step['evidence_need']}",
            f"Remote step workdir: {remote_root}/work/{step_id}",
        ],
        artifacts=[
            "step query contract with tools, databases, query families, thresholds, and stop limits",
            "expected compact output manifest for candidate-funnels.tsv and enzyme-draft-board.tsv updates",
            "resource-ledger.tsv updates for database versions and license classes",
            "resume, cleanup, and kill checklist for remote execution",
        ],
        acceptance=[
            "The prep draft is sufficient for a later worker to execute the search reproducibly.",
            "Raw-hit caps, clustering strategy, evidence review cap, and compact output names are explicit.",
            "No pod is created and no heavy search is executed by this prep issue.",
            "The plan preserves rejected classes and provenance without copying large data into the repo.",
        ],
        search_budget=step_search_budget(step),
        continuation_criteria=[
            f"Continue to remote execution for {step_id} only after orchestrator approval of query budget and data policy.",
            "Continue only if expected outputs map back to ledgers and claim levels.",
        ],
        kill_criteria=[
            "Stop if the query plan depends on restricted databases or unpublished/private sequences.",
            "Stop if expected outputs cannot be compressed into ledgers, hashes, citations, and summaries.",
            "Stop if search width is too broad for a single worker and should be split by family, organism class, or query mode.",
        ],
        validation_command=validation,
        dependencies=[
            "Blocked by RunPod campaign prep.",
            f"Blocks heavy execution or evidence-lane review for step {step_id}.",
        ],
        touched_areas=["runpod", "resource-ledger", "candidate-funnels", "provenance", "dossier"],
        review_gate=(
            "The orchestrator should verify this is a prep-only issue, then approve or split remote execution "
            "before any heavy compute is used."
        ),
        claim_boundary=claim_boundary,
        requires_heavy_compute=False,
    )
    return filename, body


def sequence_search_lane_issue(
    *,
    prefix: str,
    step: dict[str, str],
    manifest: dict,
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    execution = manifest.get("execution", {})
    remote_root = execution.get("remote_workdir", "/workspace/bioprospector/runs/<campaign_id>")
    step_id = step["step_id"]
    requires_heavy = step["candidate_search_width"] in HEAVY_SEARCH_WIDTHS
    filename = f"{prefix}-sequence-search-step-{slug(step_id)}-{slug(step['enzyme_role'])}.md"
    body = issue_body(
        title=f"{prefix}: Sequence search and BLAST contract for step {step_id}",
        role="Sequence search planner",
        goal=(
            f"Prepare the BLAST/DIAMOND/MMseqs2/HMMER search contract for {step_id}: "
            f"{step['substrate']} -> {step['product']}, including AA-only candidate package outputs."
        ),
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            f"Step id: {step_id}",
            f"Candidate search width: {step['candidate_search_width']}",
            "query-set-ledger.tsv",
            "sequence-search-plan-ledger.tsv",
            f"Remote step workdir: {remote_root}/work/{step_id}",
        ],
        artifacts=[
            "sequence-search-plan-ledger.tsv rows with tool, database, query id, thresholds, caps, budget, and approval status",
            "candidate-sequence-ledger.tsv rows with protein AA sequence pointers only, checksums or versions, and license boundary",
            "domain-annotation-ledger.tsv rows for domain source, accession, mapped span, motif/active-site summary, and confidence",
            "candidate-intelligence-ledger.tsv placeholders for sequence-derived watchouts that need later SignalP/TMHMM/localization/PTM/literature review",
            "candidate-funnels.tsv updates for raw hits, clustered representatives, evidence-reviewed counts, and shortlist counts",
            "stage-progress.jsonl or stage-progress-ledger.tsv events when a later live run executes",
        ],
        acceptance=[
            "Every planned search names a query set, search tool, database, hit cap, thresholds, remote workdir, and budget.",
            "RunPod-local BLAST/DIAMOND/MMseqs/HMMER lanes are default; AWS ElasticBLAST remains a separate reviewed escalation.",
            "Raw BLAST output, database mirrors, and bulk FASTA stay on the provider volume, not in this repo.",
            "The return package is AA-sequence pointers plus compact domain maps, not raw all-hit dumps.",
            "No candidate is promoted from sequence similarity alone; domain, motif, literature, host-fit, and controls remain gates.",
        ],
        search_budget=step_search_budget(step),
        continuation_criteria=[
            f"Continue to candidate package generation for {step_id} only when query id, tool, database, and compact output contract are explicit.",
            "Continue to candidate-intelligence review only when candidate ids can join sequence/domain rows or public anchors.",
            "Continue to route stitching only after the candidate sequence rows join enzyme-draft-board rows and domain annotations.",
            "Continue to AWS ElasticBLAST only when local curated/search lanes are insufficient and cloud approval is recorded separately.",
        ],
        kill_criteria=[
            "Stop if the search needs private, unpublished, or restricted sequence upload without explicit approval.",
            "Stop if output cannot be compressed into ledgers, checksums, graph edges, and citations.",
            "Stop if the provider image, volume, budget, branch snapshot, or stage contract launch preflight is not green for live execution.",
        ],
        validation_command=validation,
        dependencies=[
            f"Blocked by step {step_id} review and RunPod campaign prep.",
            f"Blocks candidate package and graph edges for {step_id}.",
        ],
        touched_areas=[
            "sequence-search-plan-ledger",
            "candidate-sequence-ledger",
            "domain-annotation-ledger",
            "candidate-funnels",
            "stage-progress-ledger",
        ],
        review_gate=(
            "The orchestrator should verify this is still a search contract unless a separate live execution issue "
            "authorizes RunPod work and records stage progress."
        ),
        claim_boundary=claim_boundary,
        requires_heavy_compute=requires_heavy,
    )
    return filename, body


def candidate_package_lane_issue(
    *,
    prefix: str,
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    filename = f"{prefix}-candidate-package-80-graph-and-dossier.md"
    body = issue_body(
        title=f"{prefix}: Candidate graph and detailed data package",
        role="Candidate package integrator",
        goal="Assemble the conceptual enzyme graph, candidate evidence package, diversity spread, domain maps, candidate-intelligence summaries, literature search summaries, and output dossier boundaries.",
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            "sequence-search-plan-ledger.tsv",
            "candidate-sequence-ledger.tsv",
            "domain-annotation-ledger.tsv",
            "candidate-intelligence-ledger.tsv",
            "literature-search-ledger.tsv",
            "candidate-diversity-ledger.tsv",
            "candidate-graph-ledger.tsv",
            "run-output-package-ledger.tsv",
        ],
        artifacts=[
            "candidate-graph-ledger.tsv edges connecting route -> step -> candidate -> domain -> literature -> package",
            "run-output-package-ledger.tsv rows for graph pack, candidate data pack, literature pack, and final dossier",
            "candidate-diversity-ledger.tsv rows preserving canonical, close homolog, diverse homolog, remote homolog, and weird/novel picks",
            "candidate-intelligence-ledger.tsv rows summarizing publicly reported/reference enzymes, mutants or engineered variants, signal/transit peptides, transmembrane regions, PTMs, localization, cofactors, oligomers, motifs, expression watchouts, and canonical-match inferences",
            "AA-sequence-only candidate package pointers with domain spans, motifs, source database, checksum/version, and license boundary",
            "compact literature-search summaries with query terms, source list, search date/window, result cap, and claim boundary",
        ],
        acceptance=[
            "The enzyme graph is represented in structured edges and can be rendered later without re-parsing prose.",
            "Candidate package rows join back to steps and enzyme-draft-board candidates.",
            "Diversity selection keeps more than top similarity hits: canonical, host-fit, remote, unusual, and parked/rejected classes are represented.",
            "Candidate-intelligence rows explain ranking impact without requiring docking, assay protocols, or target-host validation.",
            "All sequence output is AA-only or provider-pointer based; raw all-hit files, BLAST databases, and unbounded FASTA dumps stay provider-side.",
            "The package distinguishes planning intelligence from real execution, target evidence, and target-host validation.",
        ],
        search_budget=[
            "Integrate compact search outputs and ledgers only; do not run new BLAST, install tools, launch RunPod, or fetch literature from this issue.",
            "Prefer graph edges, package indexes, citations, checksums, and summarized domain maps over freeform reports.",
            "Return Pareto views for minimal genes, highest evidence, best host fit, clearest validation handoff, ambitious route, and diversity library.",
        ],
        continuation_criteria=[
            "Continue to final self-check only when every output package row has a status and location/pointer.",
            "Continue to route stitching only when candidate graph edges are explicit enough to trace each recommendation to evidence and caveats.",
        ],
        kill_criteria=[
            "Stop if graph or package outputs cannot be joined to manifest-declared ledgers.",
            "Stop if a package would copy private sequences, raw BLAST output, large databases, model weights, or full-text literature into the repo.",
            "Downgrade any candidate whose evidence is reference-only, similarity-only, mock, or not joined to the declared package.",
        ],
        validation_command=validation,
        dependencies=[
            "Blocked by sequence search contracts and evidence lanes.",
            "Blocks Pathway Stitcher integration, Red-team audit, and final contract self-check.",
        ],
        touched_areas=[
            "candidate-graph-ledger",
            "run-output-package-ledger",
            "candidate-diversity-ledger",
            "candidate-intelligence-ledger",
            "candidate-sequence-ledger",
            "domain-annotation-ledger",
            "literature-search-ledger",
            "dossier",
        ],
        review_gate="The orchestrator should verify graph/package joinability before accepting high-detail candidate recommendations.",
        claim_boundary=claim_boundary,
        requires_heavy_compute=False,
    )
    return filename, body


def candidate_intelligence_lane_issue(
    *,
    prefix: str,
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    filename = f"{prefix}-candidate-intelligence-70-sequence-and-literature.md"
    body = issue_body(
        title=f"{prefix}: Candidate intelligence from sequence and public evidence",
        role="Candidate intelligence reviewer",
        goal=(
            "Extract high-value sequence and public-literature interpretation for candidate prioritization, "
            "without requiring docking, wet-lab assay design, or production claims."
        ),
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            "enzyme-draft-board.tsv",
            "candidate-sequence-ledger.tsv when present",
            "domain-annotation-ledger.tsv when present",
            "candidate-intelligence-ledger.tsv",
            "literature-search-ledger.tsv and literature-ledger.tsv when present",
            "template-design-ledger.tsv or campaign-specific design notes when present",
        ],
        artifacts=[
            "candidate-intelligence-ledger.tsv rows for publicly reported/reference enzymes, mutants or engineered variants, natural variants, and close canonical matches",
            "candidate-intelligence-ledger.tsv rows for signal peptides, transit peptides, transmembrane regions, PTM/glycosylation watchouts, localization, cofactors, oligomers, motifs, and expression-context risks",
            "provider-launch-preflight-ledger.tsv rows for candidate_intelligence_tools, public_api_access, provider_egress_policy, tool_execution_proof, data_policy, workdir, and stage_contract when the operator asks to run predictors or public lookups",
            "candidate downgrades or review notes when a finding is reference-only, inferred from a close canonical match, or not observed",
            "short list of missing intelligence that would materially change ranking, kept as review/park rows instead of blockers",
        ],
        acceptance=[
            "Useful candidate interpretation is captured even when no new search or assay work is needed.",
            "Publicly reported enzymes and engineered variants are treated as ranking anchors or literature context, not target-host validation.",
            "Sequence-derived watchouts are actionable for prioritization but remain caveated when predictor, source, or terminus evidence is missing.",
            "When explicitly requested, SignalP/TMHMM-style predictors or UniProt/PubMed-style mutant extraction run only after provider/tool/API preflight passes.",
            "Docking, wet-lab protocols, construct recipes, and actual assay design stay out of scope for this lane.",
            "Every row has confidence, claim level, actionability, and source scope so the lane stays flexible without becoming freeform prose.",
        ],
        search_budget=[
            "Use compact public citations, accession records, domain maps, candidate sequence pointers, and existing demo notes first.",
            "Do not launch RunPod/neocloud/cloud/HPC, submit ElasticBLAST, fetch raw FASTA dumps, run docking, or design assays from this issue unless a separate operator-approved execution handoff exists.",
            "If literature searching is needed, record query terms and citation identifiers rather than full-text content.",
        ],
        continuation_criteria=[
            "Continue to candidate package or route stitching when intelligence rows explain the ranking impact and remaining caveats.",
            "Continue to provider execution only when missing intelligence depends on materialized candidate sequences or a separately approved predictor/API lookup run.",
            "Continue to final dossier only when missing mutant/reference-enzyme/PTM/signal questions are recorded as answered, review-required, or not observed.",
        ],
        kill_criteria=[
            "Downgrade candidates whose apparent advantage is only a broad family label or close-match inference without motif/domain support.",
            "Park public mutant or engineered-variant claims that cannot be traced to a citation or accession-backed source.",
            "Stop if the lane would require private sequences, raw search artifacts, proprietary full text, docking archives, or assay protocols in the repo.",
        ],
        validation_command=validation,
        dependencies=[
            "Blocked by candidate sequence/domain summaries when this lane depends on sequence-derived features.",
            "Blocks high-detail candidate package and final candidate ranking claims.",
        ],
        touched_areas=[
            "candidate-intelligence-ledger",
            "enzyme-draft-board",
            "candidate-sequence-ledger",
            "domain-annotation-ledger",
            "literature-search-ledger",
            "candidate-diversity-ledger",
            "claim-ledger",
        ],
        review_gate=(
            "The orchestrator should verify the lane captured ranking-useful sequence and public-evidence insights "
            "without treating them as activity validation."
        ),
        claim_boundary=claim_boundary,
        requires_heavy_compute=False,
    )
    return filename, body


def genecluster_atlas_lane_issue(
    *,
    prefix: str,
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    filename = f"{prefix}-genecluster-atlas-60-source-route-and-jury.md"
    plan_command = (
        "python3 skills/bioprospector/scripts/bioprospector_genecluster_atlas_plan.py "
        f"--campaign {display_path(campaign_path)} --out .runtime/genecluster-atlas/{prefix.lower()}"
    )
    body = issue_body(
        title=f"{prefix}: GeneCluster atlas source, route, and jury plan",
        role="GeneCluster atlas planner",
        goal=(
            "Turn public campaign ledgers into a source scout, route decision, and cluster/function jury contract "
            "without downloading raw biological data or launching provider work."
        ),
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            "organism-sample-ledger.tsv when present",
            "target-dataset-ledger.tsv when present",
            "query-set-ledger.tsv when present",
            "decoy-control-ledger.tsv when present",
            "sequence-search-plan-ledger.tsv and genome-mining-plan.tsv when present",
        ],
        artifacts=[
            "genecluster-source-scout-ledger.tsv with metadata-only source availability",
            "genecluster-route-decision-ledger.tsv with recommended route, blockers, rejected routes, and claim ceiling",
            "genecluster-atlas-contract-ledger.tsv with Stage 0, provider-neutral search, cluster/function jury, and dossier contracts",
            "genecluster-atlas-plan.json with counts, warnings, and selected claim ceiling",
            "claim-ledger.md updates if any route ceiling changes downstream claims",
        ],
        acceptance=[
            "The atlas planner runs locally and performs no network calls, provider launches, or raw artifact materialization.",
            "Every source row preserves metadata-only acquisition policy and summary-only artifact policy.",
            "Route selection distinguishes annotation, transcript, genome, candidate-search, and next-experiment paths.",
            "Negative controls and query seeds are explicit before candidate promotion or route completion claims.",
            "Physical neighborhood or cluster claims stay blocked unless coordinate evidence is declared.",
        ],
        search_budget=[
            "Inspect compact ledgers only: organism, dataset, query, decoy, provider, stage, target evidence, and claim ledgers.",
            "Do not fetch FASTA/GFF/FASTQ/SRA, build databases, run BLAST, or launch provider jobs from this issue.",
            "Keep all generated artifacts under `.runtime/` unless the orchestrator intentionally copies public-safe ledgers into an example.",
        ],
        continuation_criteria=[
            "Continue to sequence search only when query seeds, provider policy, output contracts, and decoy controls are declared.",
            "Continue to genome context only when public coordinate or annotation inputs are declared and claim ceilings are preserved.",
            "Continue to dossier only when source, route, execution proof, and claim ledgers can be joined.",
        ],
        kill_criteria=[
            "Stop if a ledger points to local raw sequence, annotation, alignment, database, or model artifacts.",
            "Stop if a route would require private, restricted, or unpublished data without a public-safe pointer and summary policy.",
            "Do not promote BGC, physical cluster, or pathway-completion claims from transcript-only or literature-only evidence.",
        ],
        validation_command=f"{validation}\n{plan_command}",
        dependencies=[
            "Blocked by target contract review and input audit.",
            "Blocks sequence search, genome-context mining, and final dossier claims.",
        ],
        touched_areas=[
            "genecluster-source-scout-ledger",
            "genecluster-route-decision-ledger",
            "genecluster-atlas-contract-ledger",
            "organism-sample-ledger",
            "target-dataset-ledger",
            "query-set-ledger",
            "decoy-control-ledger",
            "claim-ledger",
        ],
        review_gate="The orchestrator should verify route ceilings and blockers before activating heavy search or atlas lanes.",
        claim_boundary=claim_boundary,
        requires_heavy_compute=False,
    )
    return filename, body


def scale_control_lane_issue(
    *,
    prefix: str,
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    filename = f"{prefix}-scale-control-00-fanout-and-partial-closeout.md"
    body = issue_body(
        title=f"{prefix}: Scale control and partial closeout",
        role="BioProspector scale-control reviewer",
        goal=(
            "Separate primary evidence from context lanes, estimate fanout before expensive annotation, "
            "and require partial summaries plus stale-output guards for resumable provider runs."
        ),
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            "lane-status-ledger.tsv",
            "fanout-estimate-ledger.tsv",
            "partial-summary-ledger.tsv",
            "stale-output-guard-ledger.tsv",
            "stage-contract-ledger.tsv",
            "execution-artifact-ledger.tsv",
        ],
        artifacts=[
            "lane-status-ledger.tsv rows for primary, context, control, and summary lane status",
            "fanout-estimate-ledger.tsv rows for expected expansion, mitigation, and decision",
            "partial-summary-ledger.tsv rows for failed, partial, deferred, blocked, fallback, or skipped lanes",
            "stale-output-guard-ledger.tsv rows joining done markers to input, code, and output hashes",
        ],
        acceptance=[
            "Context annotation partials are visible and do not masquerade as primary evidence.",
            "High fanout uses downsample, shard, annotate-once-join-many, defer, block, or operator review.",
            "Raw tool output is normalized into ledgers before downstream consumption.",
            "Native/control hits are labeled separately from discovery candidates.",
            "Persistent-volume outputs cannot close out as live evidence with stale or unknown guards.",
        ],
        search_budget=[
            "Inspect manifest-declared ledgers and compact summaries only.",
            "Do not launch pods, download databases, fetch raw sequences, submit jobs, or run biological searches from this issue.",
            "Cap fanout review to ledger estimates and ask the orchestrator to split or pause unresolved expansions.",
        ],
        continuation_criteria=[
            "Continue to execution or stitching only when fanout, partial summaries, and stale-output guards are explicit.",
            "Continue only when primary evidence, context annotations, controls, and summaries are separable in the lane status ledger.",
        ],
        kill_criteria=[
            "Stop if heavy biological data appears in the repo or would be consumed directly by downstream issues.",
            "Stop if stale-output guards are missing, stale, or unknown for provider-side outputs.",
            "Stop if raw all-hit output is being treated as joined evidence instead of normalized ledger rows.",
        ],
        validation_command=validation,
        dependencies=[
            "Blocked by target contract review.",
            "Blocks live execution, route stitching, candidate packaging, and final self-check.",
        ],
        touched_areas=[
            "lane-status-ledger",
            "fanout-estimate-ledger",
            "partial-summary-ledger",
            "stale-output-guard-ledger",
            "stage-contract-ledger",
            "execution-artifact-ledger",
        ],
        review_gate=(
            "The orchestrator should verify fanout controls, partial closeout rows, and stale-output guards "
            "before accepting provider outputs or increasing worker concurrency."
        ),
        claim_boundary=claim_boundary,
        requires_heavy_compute=False,
    )
    return filename, body


def campaign_elasticblast_prep_issue(
    *,
    prefix: str,
    manifest: dict,
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    filename = f"{prefix}-elasticblast-00-wide-search-prep.md"
    body = issue_body(
        title=f"{prefix}: AWS ElasticBLAST wide-search prep",
        role="AWS ElasticBLAST prep operator",
        goal=(
            "Prepare the NCBI-wide BLAST escalation lane without creating AWS resources, "
            "uploading queries, or submitting ElasticBLAST jobs."
        ),
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            "AWS ElasticBLAST stack doc: docs/aws-elasticblast-stack.md",
            "ElasticBLAST search plan ledger: elasticblast-search-plan.tsv",
            "AWS safety ledger: aws-safety-ledger.tsv",
            "ElasticBLAST run ledger: elasticblast-run-ledger.tsv",
            f"Target molecule: {manifest.get('target_molecule', '')}",
            f"Host: {manifest.get('host', '')}",
        ],
        artifacts=[
            "reviewable ElasticBLAST readiness notes",
            "search-plan updates for wide/frontier steps that truly need NCBI BLAST DB scale",
            "AWS safety ledger updates for budget, quota, S3, and cleanup controls",
            "compact-output contract for parsing S3 BLAST results into candidate ledgers",
        ],
        acceptance=[
            "No AWS credentials, access keys, session tokens, or MFA codes are written anywhere.",
            "No AWS resources are created and no ElasticBLAST job is submitted.",
            "Every planned search has a budget under $100 and operator_review_required status.",
            "Cleanup verification is explicit before any future live submit.",
        ],
        search_budget=[
            "Review only campaign ledgers, AWS docs, and ElasticBLAST bundle artifacts.",
            "Do not upload query FASTA, download results, create buckets, or call AWS APIs from this issue.",
            "Prefer RunPod Swiss-Prot, UniRef, Pfam, DIAMOND, MMseqs2, and HMMER lanes before NCBI-wide escalation.",
        ],
        continuation_criteria=[
            "Continue to step-specific ElasticBLAST prep only when AWS safety controls are represented in the ledger.",
            "Continue to live submit only after a separate operator approval records account, budget, bucket, and cleanup readiness.",
        ],
        kill_criteria=[
            "Stop if the query data is private, unpublished, or unapproved for cloud upload.",
            "Stop if the search can be satisfied by RunPod-local staged resources instead of NCBI-wide BLAST.",
            "Stop if budget, quota, S3, or cleanup controls cannot be verified.",
        ],
        validation_command=validation,
        dependencies=[
            "Blocked by target contract review.",
            "Blocks step-specific ElasticBLAST prep drafts for wide/frontier steps.",
        ],
        touched_areas=["elasticblast", "aws-safety-ledger", "resource-ledger", "provenance", "docs"],
        review_gate=(
            "The orchestrator should verify this remains prep-only and that ElasticBLAST is used only as "
            "a gated NCBI-wide escalation lane."
        ),
        claim_boundary=claim_boundary,
        requires_heavy_compute=False,
    )
    return filename, body


def step_elasticblast_prep_issue(
    *,
    prefix: str,
    step: dict[str, str],
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    step_id = step["step_id"]
    filename = f"{prefix}-elasticblast-step-{slug(step_id)}-{slug(step['enzyme_role'])}.md"
    body = issue_body(
        title=f"{prefix}: ElasticBLAST prep for step {step_id} {step['enzyme_role']}",
        role="AWS ElasticBLAST step prep worker",
        goal=(
            f"Prepare a capped NCBI-wide BLAST escalation plan for {step['candidate_search_width']} "
            f"step {step_id}: {step['substrate']} -> {step['product']}."
        ),
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            f"Step id: {step_id}",
            f"Route id: {step['route_id']}",
            f"Transformation: {step['transformation']}",
            f"Evidence need: {step['evidence_need']}",
            f"Candidate search width: {step['candidate_search_width']}",
        ],
        artifacts=[
            "elasticblast-search-plan.tsv row review or update",
            "expected query FASTA provenance and sensitivity review",
            "expected S3 result prefix and compact output parsing plan",
            "elasticblast-run-ledger.tsv planned row with cleanup_status not_started",
        ],
        acceptance=[
            "The planned search is justified as NCBI-wide escalation, not the default search lane.",
            "The query set, database, thresholds, result URI, max hits, node count, and budget are explicit.",
            "approval_status remains operator_review_required unless a human has approved live submit.",
            "No query FASTA, raw BLAST output, credentials, or cloud result archives are copied into this repo.",
        ],
        search_budget=[
            "Start from the existing step row and ElasticBLAST plan row.",
            "Keep first-run budget under $25 for this step unless the orchestrator explicitly raises it.",
            "Use one node and capped hit counts until cleanup has been proven.",
        ],
        continuation_criteria=[
            f"Continue to live ElasticBLAST for {step_id} only after operator approval of AWS safety controls.",
            "Continue only if returned outputs can be parsed into candidate-funnels, enzyme-draft-board, rejected-candidates, and provenance ledgers.",
        ],
        kill_criteria=[
            "Stop if cheaper RunPod-local lanes can answer the question.",
            "Stop if query sequences are private or unapproved for cloud upload.",
            "Stop if cleanup verification cannot be made part of the run ledger.",
        ],
        validation_command=validation,
        dependencies=[
            "Blocked by AWS ElasticBLAST campaign prep.",
            f"Blocks live NCBI-wide escalation or evidence-lane review for step {step_id}.",
        ],
        touched_areas=["elasticblast-search-plan", "elasticblast-run-ledger", "aws-safety-ledger", "provenance"],
        review_gate=(
            "The orchestrator should verify the step requires NCBI-wide BLAST scale and remains below the "
            "configured scout budget before approving live submit."
        ),
        claim_boundary=claim_boundary,
        requires_heavy_compute=False,
    )
    return filename, body


def literature_lane_issue(
    *,
    prefix: str,
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    filename = f"{prefix}-literature-00-evidence-ledger.md"
    body = issue_body(
        title=f"{prefix}: Literature and evidence ledger",
        role="Literature evidence reviewer",
        goal="Create a compact evidence trail for route, enzyme, host-fit, and ambiguity claims.",
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            "Resource ledger: resource-ledger.tsv",
            "Claim ledger: claim-ledger.md",
            "Optional output ledgers: literature-ledger.tsv and literature-search-ledger.tsv",
        ],
        artifacts=[
            "literature-search-ledger.tsv rows for topic, sources, query terms, recency window, result cap, status, and output contract",
            "literature-ledger.tsv rows for cited claims, evidence class, and license boundary",
            "claim-ledger.md updates when evidence changes claim language",
            "resource-ledger.tsv updates for source access mode and redistribution policy",
            "provenance notes for searches, dates, identifiers, and source APIs",
        ],
        acceptance=[
            "Every promoted claim points to at least one evidence record or an explicit gap.",
            "Latest-literature searches are represented as search plans or compact summaries; no full-text or large supplement mirrors enter the repo.",
            "Full-text, license, and redistribution boundaries are explicit.",
            "No article bodies, restricted database content, or large supplemental files are copied into the repo.",
        ],
        search_budget=[
            "Use PubMed, OpenAlex, UniProt, source papers, and resource ledgers as citation sources.",
            "Stop at compact citation and claim summaries; do not mirror papers or supplements.",
            "Prioritize evidence that changes candidate ranking, route survival, or claim level.",
        ],
        continuation_criteria=[
            "Continue downstream route or enzyme work only when claim-driving citations are represented compactly.",
            "Continue only if uncertain evidence is caveated rather than promoted.",
        ],
        kill_criteria=[
            "Stop if a claim depends on unavailable, restricted, or unredistributable evidence.",
            "Downgrade claims that cannot be backed by a citation, accession, or explicit hypothesis record.",
        ],
        validation_command=validation,
        dependencies=[
            "Blocked by target contract review.",
            "Blocks claim promotion, red-team closeout, and public demo writeups.",
        ],
        touched_areas=["literature-ledger", "resource-ledger", "claim-ledger", "provenance"],
        review_gate="The orchestrator should verify citations support only the language used in the claim ledger.",
        claim_boundary=claim_boundary,
        requires_heavy_compute=False,
    )
    return filename, body


def dark_step_resolver_issue(
    *,
    prefix: str,
    unknown: dict[str, str],
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    unknown_id = unknown["unknown_step_id"]
    parent_step_id = unknown["parent_step_id"]
    filename = f"{prefix}-ambiguity-{slug(unknown_id)}-{slug(parent_step_id)}.md"
    body = issue_body(
        title=f"{prefix}: Dark Step Resolver {unknown_id} for {parent_step_id}",
        role="Unknown-gene discovery worker",
        goal=(
            f"Resolve ambiguity for {unknown_id}: {unknown['substrate']} -> {unknown['product']} "
            "without assuming the missing activity is a single obvious homolog."
        ),
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            f"Unknown step id: {unknown_id}",
            f"Parent step id: {parent_step_id}",
            f"Route id: {unknown['route_id']}",
            f"Gap type: {unknown['gap_type']}",
            f"Transformation hypothesis: {unknown['transformation_hypothesis']}",
            f"Search strategy: {unknown['search_strategy']}",
        ],
        artifacts=[
            "pathway-inference-ledger.tsv hypothesis rows",
            "unknown-gene-hypothesis-ledger.tsv single-gene and multi-gene module hypotheses",
            "enzyme-family-sweep.tsv rows for plausible enzyme classes",
            "rejected-candidates.tsv rows for killed explanations",
            "experiment-priority notes in assay-handoff-ledger.tsv when a discriminating test is needed",
        ],
        acceptance=[
            "At least one enzyme-class, multi-gene, spontaneous, transport, or host-native hypothesis is evaluated.",
            "Counterevidence is recorded for weak hypotheses.",
            "Weird but plausible candidates are preserved separately from normal homolog hits.",
            "The next discriminating step is explicit and remains non-protocol planning.",
        ],
        search_budget=[
            "Do not BLAST harder by default; first decompose chemistry and infer plausible enzyme classes.",
            "Review at most 5 hypothesis families before asking the orchestrator to split the lane.",
            "Use coexpression, genomic context, domain architecture, side-product logic, and convergent taxa only as evidence sources.",
        ],
        continuation_criteria=[
            "Continue to enzyme-family or genome-context lanes only when a hypothesis row defines the search target.",
            "Continue to route stitching only when ambiguity is resolved, split, or explicitly carried as a bottleneck.",
        ],
        kill_criteria=[
            "Park the hypothesis if it depends only on broad family similarity.",
            "Kill claims that hide a multi-step transformation inside a single enzyme row.",
            "Stop if source data would require private or restricted sequence uploads.",
        ],
        validation_command=validation,
        dependencies=[
            f"Blocked by parent step {parent_step_id}.",
            "Blocks route stitching for routes that require this missing or ambiguous transformation.",
        ],
        touched_areas=[
            "pathway-inference-ledger",
            "unknown-gene-hypothesis-ledger",
            "enzyme-family-sweep",
            "rejected-candidates",
            "assay-handoff-ledger",
        ],
        review_gate="The orchestrator should verify the worker reasoned over alternatives rather than only extending homology search.",
        claim_boundary=claim_boundary,
        requires_heavy_compute=False,
    )
    return filename, body


def enzyme_family_sweep_issue(
    *,
    prefix: str,
    step: dict[str, str],
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    step_id = step["step_id"]
    filename = f"{prefix}-family-sweep-step-{slug(step_id)}-{slug(step['enzyme_role'])}.md"
    body = issue_body(
        title=f"{prefix}: Enzyme-family sweep for step {step_id}",
        role="Enzyme family sweep worker",
        goal=f"Compress broad family space for {step_id} into reviewable candidate classes before individual ranking.",
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            f"Step id: {step_id}",
            f"Transformation: {step['transformation']}",
            f"Enzyme role: {step['enzyme_role']}",
            f"Evidence need: {step['evidence_need']}",
        ],
        artifacts=[
            "enzyme-family-sweep.tsv rows for family scope, motifs, hit counts, and next lane",
            "candidate-funnels.tsv updates for raw-to-cluster compression",
            "rejected-candidates.tsv rows for family classes killed by motif, domain, or substrate evidence",
            "provenance notes for databases, model versions, and thresholds",
        ],
        acceptance=[
            "Raw family hits are compressed before manual candidate review.",
            "Motif, domain, substrate, and host-fit gates are explicit.",
            "Family-level risk is recorded before individual enzyme candidates are promoted.",
        ],
        search_budget=step_search_budget(step),
        continuation_criteria=[
            "Continue to individual candidate review only after representatives and killed classes are recorded.",
            "Continue to structure-risk or genome-context lanes only when family-level evidence justifies them.",
        ],
        kill_criteria=[
            "Stop if family scope is too broad and needs splitting by clade, motif, or substrate class.",
            "Reject family classes that lack required domains, motifs, or plausible chemistry.",
        ],
        validation_command=validation,
        dependencies=[
            f"Blocked by step {step_id}.",
            "Blocks broad candidate promotion for this step.",
        ],
        touched_areas=["enzyme-family-sweep", "candidate-funnels", "rejected-candidates", "provenance"],
        review_gate="The orchestrator should verify family compression before allowing individual candidate shortlists.",
        claim_boundary=claim_boundary,
        requires_heavy_compute=step["candidate_search_width"] in HEAVY_SEARCH_WIDTHS,
    )
    return filename, body


def genome_mining_lane_issue(
    *,
    prefix: str,
    step: dict[str, str],
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    step_id = step["step_id"]
    filename = f"{prefix}-genome-mining-step-{slug(step_id)}-{slug(step['enzyme_role'])}.md"
    body = issue_body(
        title=f"{prefix}: Genome-context mining for step {step_id}",
        role="Genome-context mining planner",
        goal="Plan anchor, neighborhood, and BGC-context searches without downloading raw genome artifacts into the repo.",
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            f"Step id: {step_id}",
            f"Route id: {step['route_id']}",
            f"Enzyme role: {step['enzyme_role']}",
            "Optional ledgers: genome-mining-plan.tsv and genome-hit-ledger.tsv",
        ],
        artifacts=[
            "genome-mining-plan.tsv rows with target taxa, source, anchor, window, budget, and approval status",
            "genome-hit-ledger.tsv compact hit rows with coordinates or secure pointers",
            "resource-ledger.tsv updates for antiSMASH, plantiSMASH, cblaster, GECCO, BiG-SCAPE, or MIBiG use",
            "claim-ledger.md caveats for neighborhood-supported candidates",
        ],
        acceptance=[
            "Raw genome, GFF, FASTA, and BGC output archives stay outside the repo.",
            "Hits preserve enough coordinate or accession context for review without copying source data.",
            "Neighborhood support is treated as evidence, not proof of function.",
        ],
        search_budget=[
            "Plan at most 3 taxa/source groups and 3 anchor families before orchestrator review.",
            "Prefer accession IDs, secure paths, checksums, and compact summaries over raw downloads.",
            "Use genome context only when it changes candidate ranking or unknown-gene hypotheses.",
        ],
        continuation_criteria=[
            "Continue to live genome mining only after data rights, source, budget, and output policy are explicit.",
            "Continue to candidate promotion only when genome-context evidence is combined with sequence, domain, or literature evidence.",
        ],
        kill_criteria=[
            "Stop if source data is private or cannot be referenced safely.",
            "Park hits that are neighborhood-supported but lack plausible domain or chemistry evidence.",
        ],
        validation_command=validation,
        dependencies=[
            f"Blocked by step {step_id} or a dark-step hypothesis.",
            "Blocks genome-context claims in route stitching.",
        ],
        touched_areas=["genome-mining-plan", "genome-hit-ledger", "resource-ledger", "claim-ledger"],
        review_gate="The orchestrator should verify genome context is compact, rights-aware, and not overclaimed.",
        claim_boundary=claim_boundary,
        requires_heavy_compute=True,
    )
    return filename, body


def structure_risk_lane_issue(
    *,
    prefix: str,
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    filename = f"{prefix}-structure-risk-00-triage.md"
    body = issue_body(
        title=f"{prefix}: Structure-risk triage",
        role="Structure-risk reviewer",
        goal="Triage candidate structural risks without bulk prediction, docking, or model-weight storage.",
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            "Enzyme draft board: enzyme-draft-board.tsv",
            "Optional output ledger: structure-risk-ledger.tsv",
        ],
        artifacts=[
            "structure-risk-ledger.tsv rows for active site, cofactor, membrane, substrate-access, and oligomerization risks",
            "enzyme-draft-board.tsv verdict updates only when structure evidence changes candidate status",
            "claim-ledger.md caveats for structure-supported or structure-risky candidates",
        ],
        acceptance=[
            "Only a small shortlist is triaged structurally.",
            "Structure evidence is treated as risk/support, not validation of activity.",
            "No AlphaFold caches, PDB/mmCIF bundles, model weights, or docking archives enter the repo.",
        ],
        search_budget=[
            "Triage at most 20 candidates before requesting a split.",
            "Use Foldseek, AlphaFoldDB, ESM/ColabFold-derived references, or secure external paths only as compact evidence.",
        ],
        continuation_criteria=[
            "Continue to deeper modeling only after a candidate survives evidence and host-fit review.",
            "Continue to route stitching only when structure risks are caveated in the scorecard.",
        ],
        kill_criteria=[
            "Reject candidates with incompatible active-site, cofactor, membrane, or oligomerization risk if no counterevidence exists.",
            "Stop if structure work would require large local artifacts or unlicensed models in the repo.",
        ],
        validation_command=validation,
        dependencies=["Blocked by enzyme-family sweeps or candidate shortlist review."],
        touched_areas=["structure-risk-ledger", "enzyme-draft-board", "claim-ledger"],
        review_gate="The orchestrator should verify structure-risk evidence does not become an activity claim.",
        claim_boundary=claim_boundary,
        requires_heavy_compute=False,
    )
    return filename, body


def host_comparison_lane_issue(
    *,
    prefix: str,
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    filename = f"{prefix}-host-comparison-00-fit-review.md"
    body = issue_body(
        title=f"{prefix}: Host comparison and fit review",
        role="Host-fit reviewer",
        goal="Compare host options and route burdens without claiming production or providing strain-construction guidance.",
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            "Target contract: target-contract.json",
            "Route stitching scorecard: route-stitching-scorecard.tsv",
            "Optional output ledger: host-comparison-ledger.tsv",
        ],
        artifacts=[
            "host-comparison-ledger.tsv rows for burden, precursor fit, compartment fit, toxicity, analytics fit, and verdict",
            "route-stitching-scorecard.tsv caveats where host fit changes route ranking",
            "claim-ledger.md updates for host-fit assumptions",
        ],
        acceptance=[
            "Yeast, plant transient, bacterial, cell-free, or other hosts are compared only when relevant.",
            "P450/CPR, compartment, toxicity, product recovery, and analytics risks are explicit.",
            "No construct automation, wet-lab protocol, or production claim is introduced.",
        ],
        search_budget=[
            "Review host constraints, route burdens, and candidate classes; do not run GEMs unless a later execution issue approves it.",
            "Use COBRApy/ModelSEED/CarveMe only as future tool references unless model artifacts are externally approved.",
        ],
        continuation_criteria=[
            "Continue to validation-readiness planning only when host-specific risks are scored.",
            "Continue to metabolic modeling only after a route shortlist exists.",
        ],
        kill_criteria=[
            "Block host recommendations that ignore compartment, cofactor, toxicity, or analytics constraints.",
            "Stop if host comparison would require unpublished constructs or private strain information in the repo.",
        ],
        validation_command=validation,
        dependencies=["Blocked by route and step review.", "Blocks validation-readiness recommendations."],
        touched_areas=["host-comparison-ledger", "route-stitching-scorecard", "claim-ledger"],
        review_gate="The orchestrator should verify host choice is a planning verdict, not a production claim.",
        claim_boundary=claim_boundary,
        requires_heavy_compute=False,
    )
    return filename, body


def assay_handoff_lane_issue(
    *,
    prefix: str,
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    filename = f"{prefix}-assay-handoff-00-validation-readiness.md"
    body = issue_body(
        title=f"{prefix}: Evidence handoff and validation readiness",
        role="Validation-readiness planner",
        goal="Convert route and candidate uncertainty into non-procedural evidence gaps, measurement categories, and control categories.",
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            "Route stitching scorecard: route-stitching-scorecard.tsv",
            "Claim ledger: claim-ledger.md",
            "Optional output ledger: assay-handoff-ledger.tsv",
        ],
        artifacts=[
            "assay-handoff-ledger.tsv rows for measurable product, readout category, control category, risk, and non-protocol boundary",
            "claim-ledger.md updates for unresolved validation gaps",
            "validation-readiness notes that remain non-procedural and planning-only",
        ],
        acceptance=[
            "Each proposed handoff names the uncertainty it resolves.",
            "Control categories are listed at a planning level only.",
            "No wet-lab recipe, construct sequence, dosage, timing, or procedural protocol is written.",
        ],
        search_budget=[
            "Use ledgers and claim gaps; do not design a detailed experiment protocol.",
            "Prioritize the clearest discriminating evidence gap for each route bottleneck.",
        ],
        continuation_criteria=[
            "Continue only when the route or candidate has a clear evidence gap and measurable readout.",
            "Continue to external handoff only after red-team claim audit passes.",
        ],
        kill_criteria=[
            "Stop if the handoff drifts into protocol detail.",
            "Park designs that cannot identify a measurable readout or control need.",
        ],
        validation_command=validation,
        dependencies=["Blocked by Pathway Stitcher and Red-team claim audit."],
        touched_areas=["assay-handoff-ledger", "claim-ledger", "validation-readiness"],
        review_gate="The orchestrator should verify the handoff is non-protocol and tied to a claim gap.",
        claim_boundary=claim_boundary,
        requires_heavy_compute=False,
    )
    return filename, body


def monitoring_lane_issue(
    *,
    prefix: str,
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    filename = f"{prefix}-monitoring-00-campaign-ledger.md"
    body = issue_body(
        title=f"{prefix}: Campaign monitoring and provenance",
        role="Campaign monitoring reviewer",
        goal="Define heartbeat, blocker, artifact, and closeout tracking for a Symphony + Linear BioProspector campaign.",
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            "Generated issue drafts",
            "Optional output ledger: monitoring-ledger.tsv",
            "Workflow draft: templates/symphony-workflow-bioprospector.WORKFLOW.md",
        ],
        artifacts=[
            "monitoring-ledger.tsv rows for lane, issue, expected artifact, heartbeat, blocker, next review, and owner",
            "provenance notes for run ids, generated issue sets, and validation commands",
            "closeout checklist aligned with Symphony outcome blocks",
        ],
        acceptance=[
            "Every active lane has an expected compact artifact and review point.",
            "Blocked, stale, and completed states are distinguishable without a daemon.",
            "Monitoring remains ledger/Linear based; no new service or dashboard is introduced.",
        ],
        search_budget=[
            "Inspect generated issues and workflow docs only.",
            "Do not start Symphony, seed Linear, or create monitoring automations from this issue.",
        ],
        continuation_criteria=[
            "Continue to worker dispatch only when first-wave lanes and stop checkpoints are explicit.",
            "Continue only when closeout validation commands are present.",
        ],
        kill_criteria=[
            "Stop if monitoring requires a new daemon, queue runner, or dashboard.",
            "Stop if worker outputs cannot be mapped to expected compact artifacts.",
        ],
        validation_command=validation,
        dependencies=["Blocked by issue-draft generation.", "Blocks multi-worker campaign dispatch."],
        touched_areas=["monitoring-ledger", "provenance", "workflow", "docs"],
        review_gate="The orchestrator should verify monitoring gives stop/check points before increasing concurrency.",
        claim_boundary=claim_boundary,
        requires_heavy_compute=False,
    )
    return filename, body


def self_learning_lane_issue(
    *,
    prefix: str,
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    filename = f"{prefix}-self-learning-00-skill-update-after-hiccup.md"
    body = issue_body(
        title=f"{prefix}: Self-learning skill update after hiccup",
        role="BioProspector learning reviewer",
        goal=(
            "Convert a stalled run, failed gate, ambiguous fallback, or repeated workflow hiccup "
            "into reusable process intelligence."
        ),
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            "Relevant ignored .runtime/learning-notes note or campaign closeout",
            "stage-progress-ledger.tsv, execution-artifact-ledger.tsv, monitoring-ledger.tsv, or compact provider status summary",
            "self-learning-skill-ledger.tsv when present",
            "docs/self-learning-skill-runbook.md",
        ],
        artifacts=[
            "self-learning-skill-ledger.tsv row with observation, hypothesis, probe, baseline/control, expected signal, stop-loss, result, and decision",
            "ignored local learning note if the context is not already recorded",
            "small runbook, skill, template, validator, or issue-generator update when the lesson is reusable",
        ],
        acceptance=[
            "The learning row distinguishes process improvement from biological validation.",
            "Any retry recommendation is separate from execution approval and names the provider preflight, budget, and stage-contract gates it needs.",
            "Repeated hiccups become durable guardrails when they can be encoded in docs, templates, validators, or skill instructions.",
            "No secrets, private data, raw outputs, full FASTA dumps, database mirrors, or full-text literature are copied into the repo.",
        ],
        search_budget=[
            "Inspect compact logs, ledgers, validator output, and provider summaries only.",
            "Do not launch pods, submit jobs, download databases, fetch sequences, or run biological searches from this issue.",
            "If a live retry is needed, open a separate execution issue with explicit operator approval.",
        ],
        continuation_criteria=[
            "Continue to campaign retry only after the hypothesis, expected signal, and stop-loss are explicit.",
            "Continue to skill/runbook update when the lesson would have changed agent behavior before the hiccup.",
            "Continue to validator/template work when the lesson can be enforced mechanically.",
        ],
        kill_criteria=[
            "Stop if the proposed learning depends on private data or raw provider artifacts in the repo.",
            "Stop if the row tries to convert a process lesson into a biological success claim.",
            "Park one-off observations that have no reusable guardrail and no effect on campaign risk.",
        ],
        validation_command=validation,
        dependencies=[
            "Triggered by monitoring, stage-progress, provider-preflight, control, evidence-join, or self-check hiccups.",
            "Blocks repeated retry of the same failure mode when the hiccup is unresolved.",
        ],
        touched_areas=[
            "self-learning-skill-ledger",
            "logs",
            "docs/self-learning-skill-runbook",
            "templates",
            "validators",
            "skills/bioprospector/SKILL.md",
        ],
        review_gate=(
            "The orchestrator should verify the row names a falsifiable process hypothesis "
            "and does not weaken normal evidence or provider gates."
        ),
        claim_boundary=claim_boundary,
        requires_heavy_compute=False,
    )
    return filename, body


OPPORTUNITY_LANE_SPECS = {
    "ledger_schema": {
        "slug": "ledger-schema-00-contract-hardening",
        "title": "Ledger schema contract hardening",
        "role": "BioProspector schema maintainer",
        "goal": "Keep Frictionless-style schemas, LinkML-ready semantic notes, and Python preflight validators aligned.",
        "artifacts": ["Frictionless schema parity notes", "LinkML readiness notes", "preflight failures for drift, invalid enums, booleans, and numeric bounds"],
        "tools": "Frictionless, LinkML",
        "touched": ["schemas", "preflight", "tests", "docs"],
    },
    "supply_chain": {
        "slug": "supply-chain-00-image-provenance",
        "title": "Supply-chain preflight for provider images",
        "role": "BioProspector provider supply-chain auditor",
        "goal": "Record SBOM, vulnerability, signature, and provenance proof as launch blockers, not scientific evidence.",
        "artifacts": ["supply-chain-preflight-ledger.tsv rows", "provider-launch-preflight-ledger.tsv blocker rows", "compact evidence pointers under ignored runtime paths"],
        "tools": "Syft, Grype, Cosign, SLSA",
        "touched": ["supply-chain-preflight-ledger", "provider-launch-preflight-ledger", "runpod", "docs"],
    },
    "active_site_audit": {
        "slug": "active-site-audit-00-structure-risk",
        "title": "Active-site and structure-risk audit",
        "role": "BioProspector active-site auditor",
        "goal": "Join curated catalytic-site, motif, pocket, ligand, benchmark, and pose sanity summaries into risk and candidate-intelligence ledgers.",
        "artifacts": ["structure-risk-ledger.tsv rows", "candidate-intelligence-ledger.tsv rows", "tool-execution-proof and provider-preflight rows before live predictors"],
        "tools": "M-CSA, PROSITE, ProRule, P2Rank, EnzyMM, PyJess, BioLiP2, PLINDER, PoseBusters",
        "touched": ["structure-risk-ledger", "candidate-intelligence-ledger", "tool-execution-proof-ledger", "claim-ledger"],
    },
    "route_rule": {
        "slug": "route-rule-00-retrosynthesis-expansion",
        "title": "Route-rule expansion and compression",
        "role": "BioProspector route-rule reviewer",
        "goal": "Use rule-based, biocatalytic, enzyme-ranking, and network-expansion outputs as opt-in route expansion intelligence.",
        "artifacts": ["route-rule-ledger.tsv rows", "route or step review notes", "over-expansion rejection notes"],
        "tools": "RetroRules, RetroBioCat, SelenzymeRF, Pickaxe",
        "touched": ["route-rule-ledger", "route-ledger", "reaction-step-ledger", "pathway-inference-ledger"],
    },
    "thermodynamics": {
        "slug": "thermodynamics-00-route-feasibility",
        "title": "Thermodynamics route feasibility",
        "role": "BioProspector thermodynamics reviewer",
        "goal": "Use thermodynamic summaries to rank reaction-step plausibility without treating thermodynamics as host proof.",
        "artifacts": ["thermodynamics-ledger.tsv rows", "route-stitching-scorecard caveats"],
        "tools": "eQuilibrator, component-contribution",
        "touched": ["thermodynamics-ledger", "route-stitching-scorecard", "claim-ledger"],
    },
    "metabolic_model": {
        "slug": "metabolic-model-00-host-fit",
        "title": "Metabolic-model host-fit review",
        "role": "BioProspector host-model reviewer",
        "goal": "Use metabolic-model summaries to review host context without claiming production.",
        "artifacts": ["metabolic-model-ledger.tsv rows", "host-comparison and route-stitching caveats"],
        "tools": "gapseq, COBRApy, ModelSEEDpy",
        "touched": ["metabolic-model-ledger", "host-comparison-ledger", "route-stitching-scorecard"],
    },
    "strain_design": {
        "slug": "host-fit-model-00-non-operational-review",
        "title": "Host-fit model perturbation review",
        "role": "BioProspector host-fit model reviewer",
        "goal": "Capture non-operational model perturbation summaries as prioritization intelligence.",
        "artifacts": ["strain-design-ledger.tsv rows with non-operational boundaries", "host-fit caveats"],
        "tools": "COBRApy, StrainDesign",
        "touched": ["strain-design-ledger", "host-comparison-ledger", "claim-ledger"],
    },
    "chemoenzymatic_fallback": {
        "slug": "chemoenzymatic-fallback-00-rescue-routes",
        "title": "Chemoenzymatic fallback and rescue-route review",
        "role": "BioProspector fallback reviewer",
        "goal": "Capture chemoenzymatic fallback ideas for blocked biosynthetic steps without treating them as BioProspector success.",
        "artifacts": ["chemoenzymatic-fallback-ledger.tsv rows", "partial/degraded route caveats"],
        "tools": "ASKCOS, manual chemoenzymatic review",
        "touched": ["chemoenzymatic-fallback-ledger", "route-stitching-scorecard", "claim-ledger"],
    },
    "bgc_context": {
        "slug": "bgc-context-00-natural-product-clusters",
        "title": "BGC context handoff",
        "role": "BioProspector BGC context reviewer",
        "goal": "Use biosynthetic gene cluster and neighborhood summaries as reference context.",
        "artifacts": ["bgc-context-ledger.tsv rows", "target-evidence joins only when target/sample evidence exists"],
        "tools": "SMC, plantiSMASH, GECCO, BiG-SLiCE, BiG-FAM, BGCFlow, cblaster, clinker",
        "touched": ["bgc-context-ledger", "genome-hit-ledger", "target-evidence-ledger", "claim-ledger"],
    },
    "metagenome_context": {
        "slug": "metagenome-context-00-contig-mag-gates",
        "title": "Metagenome context handoff",
        "role": "BioProspector metagenome context reviewer",
        "goal": "Capture metagenome, contig, MAG, and taxonomy summaries without storing raw reads or MAGs.",
        "artifacts": ["metagenome-context-ledger.tsv rows", "mag-quality-ledger.tsv rows"],
        "tools": "GECCO, BiG-MAP, BGCFlow, CheckM2, GTDB-Tk",
        "touched": ["metagenome-context-ledger", "mag-quality-ledger", "target-dataset-ledger", "decoy-control-ledger"],
    },
    "metabolomics_handoff": {
        "slug": "metabolomics-handoff-00-spectra-policy",
        "title": "Metabolomics evidence handoff",
        "role": "BioProspector metabolomics handoff reviewer",
        "goal": "Define metabolomics output contracts without uploading private spectra by default.",
        "artifacts": ["metabolomics-evidence-ledger.tsv rows", "upload/data-policy provider preflight rows"],
        "tools": "MZmine, GNPS2, matchms, MS2Query",
        "touched": ["metabolomics-evidence-ledger", "provider-launch-preflight-ledger", "target-evidence-ledger", "decoy-control-ledger"],
    },
    "compound_source": {
        "slug": "compound-source-00-reference-priors",
        "title": "Compound/source prior review",
        "role": "BioProspector compound-source reviewer",
        "goal": "Use natural-product source priors as reference context with explicit license boundaries.",
        "artifacts": ["compound-source-ledger.tsv rows", "resource-ledger.tsv license notes"],
        "tools": "LOTUS, Natural Products Atlas",
        "touched": ["compound-source-ledger", "resource-ledger", "literature-ledger", "claim-ledger"],
    },
    "review_surface": {
        "slug": "review-surface-00-graph-dossier",
        "title": "Candidate graph and review-surface contracts",
        "role": "BioProspector review-surface architect",
        "goal": "Define graph/export and review-surface contracts without implementing a UI yet.",
        "artifacts": ["candidate graph export contract", "review-surface package notes", "run-output-package-ledger.tsv rows"],
        "tools": "Quarto, marimo, Evidence.dev, Streamlit",
        "touched": ["candidate-graph-ledger", "run-output-package-ledger", "dossier", "docs"],
    },
    "tool_execution_proof": {
        "slug": "tool-execution-proof-00-callable-commands",
        "title": "Exact executable proof",
        "role": "BioProspector tool-proof reviewer",
        "goal": "Prove exact stage commands are callable before paid compute, live closeout, or scientific success language.",
        "artifacts": ["tool-execution-proof-ledger.tsv rows", "observed version or dry-invocation evidence pointers", "provider-preflight blocker rows when command proof gates launch"],
        "tools": "BLAST+, DIAMOND, MMseqs2, HMMER, seqkit, NCBI Datasets, SignalP, ElasticBLAST, and campaign-specific executable probes",
        "touched": ["tool-execution-proof-ledger", "stage-contract-ledger", "provider-launch-preflight-ledger", "claim-ledger"],
    },
    "template_design": {
        "slug": "template-design-00-curated-template-set",
        "title": "Curated template-design set",
        "role": "BioProspector template-design curator",
        "goal": "Compress raw sequence, domain, and literature hits into a dry-lab template set for pathway-stitching review.",
        "artifacts": ["template-design-ledger.tsv rows when present", "candidate-sequence/domain/diversity joins", "literature citation pointers for optimization notes"],
        "tools": "template-design ledger, candidate sequence/domain/diversity ledgers, literature identifiers",
        "touched": ["template-design-ledger", "candidate-sequence-ledger", "domain-annotation-ledger", "candidate-diversity-ledger", "candidate-intelligence-ledger"],
    },
}


def opportunity_contract_lane_issue(
    *,
    spec_key: str,
    prefix: str,
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    spec = OPPORTUNITY_LANE_SPECS[spec_key]
    filename = f"{prefix}-{spec['slug']}.md"
    body = issue_body(
        title=f"{prefix}: {spec['title']}",
        role=spec["role"],
        goal=spec["goal"],
        inputs=[f"Campaign manifest: {display_path(campaign_path)}", "docs/opportunity-radar.md", *spec["touched"]],
        artifacts=spec["artifacts"],
        acceptance=[
            f"Named tools/resources are handled as opt-in contract inputs only: {spec['tools']}.",
            "Outputs are compact ledgers, IDs, checksums, summaries, citations, or runtime pointers only.",
            "This lane cannot satisfy biological validation, target-host production, or claim closeout by itself.",
        ],
        search_budget=[
            "Contracts-first only: do not install tools, call paid providers, upload data, or run live external APIs.",
            "Add tool/API/provider execution proof rows before any future live wrapper uses this lane.",
        ],
        continuation_criteria=[
            "Continue only when ledger rows are joinable to manifest-declared inputs and claim boundaries are explicit.",
            "Downstream promotion still requires execution artifacts, target evidence, decoy controls, and self-check gates when applicable.",
        ],
        kill_criteria=[
            "Stop if the lane would copy private data, raw reads, full spectra, full text, large outputs, database mirrors, or model weights into the repo.",
            "Stop if evidence cannot be represented as planning, prioritization, reference context, target evidence, control evidence, or execution proof.",
        ],
        validation_command=validation,
        dependencies=["Blocked by target contract review and campaign preflight."],
        touched_areas=spec["touched"],
        review_gate="The orchestrator should verify this lane remains a contract/planning lane and does not weaken claim gates.",
        claim_boundary=claim_boundary,
    )
    return filename, body


def stage_contract_lane_issue(
    *,
    prefix: str,
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    filename = f"{prefix}-stage-contract-00-long-run-gates.md"
    body = issue_body(
        title=f"{prefix}: Stage contracts and progress ledger",
        role="BioProspector stage controller",
        goal="Define fail-closed stage contracts and progress events before any long local, RunPod, cloud, HPC, or ElasticBLAST run.",
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            "stage-contract-ledger.tsv",
            "stage-progress-ledger.tsv",
            "run-maturity-ledger.tsv",
            "execution-artifact-ledger.tsv",
        ],
        artifacts=[
            "stage-contract-ledger.tsv rows with stage id, expected artifact, timeout, checkpoint, done marker, resume command, and fail-closed behavior",
            "stage-progress-ledger.tsv rows or provider-side stage-progress.jsonl events for started, heartbeat, completed, failed, partial, fallback, skipped, and resumed",
            "run-maturity-ledger.tsv updates that do not promote L3/L4/L5 from RUNNING intent alone",
        ],
        acceptance=[
            "Every long-running stage has an expected artifact, timeout, checkpoint marker, done marker, and resume command.",
            "Provider RUNNING or desiredStatus is never accepted as stage completion.",
            "Fallback, partial, failed, or skipped stages degrade final status unless a separate review explicitly narrows the deliverable.",
            "Progress events include timestamps and compact artifact pointers without copying heavy data into the repo.",
        ],
        search_budget=[
            "Review only the planned campaign lanes and provider contracts.",
            "Do not launch pods, submit jobs, download databases, or run biological searches from this issue.",
        ],
        continuation_criteria=[
            "Continue to provider launch only after fail-closed stages and progress emission are defined.",
            "Continue to strict closeout only when required execution stages have completed progress events and execution artifacts.",
        ],
        kill_criteria=[
            "Stop if a stage lacks a checkpoint, done marker, timeout, or resume command.",
            "Stop if a worker can silently switch providers, data sources, or route scope without a degraded progress event.",
        ],
        validation_command=validation,
        dependencies=["Blocked by input audit and provider strategy.", "Blocks any long-running execution issue."],
        touched_areas=["stage-contract-ledger", "stage-progress-ledger", "run-maturity-ledger", "execution-artifact-ledger"],
        review_gate="The orchestrator should verify progress proof exists before treating any long run as completed.",
        claim_boundary=claim_boundary,
    )
    return filename, body


def input_audit_lane_issue(
    *,
    prefix: str,
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    filename = f"{prefix}-input-audit-00-known-inputs.md"
    audit_command = (
        "python3 skills/bioprospector/scripts/bioprospector_input_audit.py "
        f"--campaign {display_path(campaign_path)}"
    )
    body = issue_body(
        title=f"{prefix}: Input audit before operator questions",
        role="BioProspector input auditor",
        goal="Read all declared manifests and ledgers first, then identify only explicit missing_operator_items.",
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            "target-contract.json",
            "input-audit-ledger.tsv if present",
            "organism/sample, query-set, target-dataset, resource, and provenance ledgers if present",
        ],
        artifacts=[
            "input audit JSON summary",
            "input-audit-ledger.tsv updates for known inputs and missing operator items",
            "recommended hardening-ledger gaps without treating them as blockers unless campaign scope requires them",
        ],
        acceptance=[
            "Known inputs are summarized before asking any operator question.",
            "Only explicit missing_operator_items are escalated.",
            "No database, accession, sequence, or remote artifact is downloaded during input audit.",
        ],
        search_budget=[
            "Read local manifest, target contract, ledgers, and paths only.",
            "Do not infer missing biology from absent optional ledgers unless the campaign requires those ledgers.",
        ],
        continuation_criteria=[
            "Continue to planning or execution only when blocking missing_operator_items are empty.",
            "Continue only when absent recommended ledgers are explicitly accepted or added.",
        ],
        kill_criteria=[
            "Stop if a required input path is missing.",
            "Stop if the next step would require private data, credentials, or unapproved downloads.",
        ],
        validation_command=f"{validation}\n{audit_command}",
        dependencies=["Blocks first-wave worker dispatch."],
        touched_areas=["input-audit-ledger", "manifest", "target-contract", "provenance"],
        review_gate="The orchestrator should verify the worker read existing inputs before asking for anything new.",
        claim_boundary=claim_boundary,
    )
    return filename, body


def operator_intake_lane_issue(
    *,
    prefix: str,
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    filename = f"{prefix}-operator-intake-00-confirmation.md"
    audit_command = (
        "python3 skills/bioprospector/scripts/bioprospector_input_audit.py "
        f"--campaign {display_path(campaign_path)}"
    )
    body = issue_body(
        title=f"{prefix}: Operator intake and assumption confirmation",
        role="BioProspector intake lead",
        goal=(
            "Turn the input audit into a short operator interview only when true target, host, scope, "
            "data-policy, provider, budget, success, or claim-boundary gaps remain."
        ),
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            "input-audit JSON summary",
            "operator-intake-ledger.tsv if present",
            "target-contract.json",
            "campaign claim boundary and execution policy",
        ],
        artifacts=[
            "operator-intake-ledger.tsv rows for assumptions, answers, confirmation status, and skip policy",
            "explicit list of execution or claim-closeout blockers",
            "target-contract or claim-ledger updates only when operator answers change scope",
        ],
        acceptance=[
            "The worker asks zero questions when inputs are sufficient or the operator says skip and go.",
            "If questions are needed, they are grouped into at most three operator prompts.",
            "Every skipped or assumed answer records whether planning can proceed and what later gate it blocks.",
            "The worker never asks for secrets, private sequences, or raw biological data in chat or Linear.",
        ],
        search_budget=[
            "Run the input audit first; do not ask questions from memory or from a blank page.",
            "Ask only for decisions that materially change campaign scope, safety, provider choice, or claim language.",
            "Use reversible defaults for planning-only work and preserve unresolved items in the ledger.",
        ],
        continuation_criteria=[
            "Continue to planning when planning_can_proceed=true for all intake rows.",
            "Continue to execution only when rows with required_before=execution are confirmed or explicitly unblocked.",
            "Continue to claim closeout only when claim-boundary and success-criteria rows are confirmed.",
        ],
        kill_criteria=[
            "Stop before execution if data rights, provider, budget, or target inputs are blocked.",
            "Stop before claim closeout if the target, host, success criteria, or claim boundary remain assumed.",
            "Stop if the requested answer would require credentials or private sequence content in the repo or Linear.",
        ],
        validation_command=f"{validation}\n{audit_command}",
        dependencies=["Blocked by input audit.", "Blocks first-wave worker dispatch only when planning cannot proceed."],
        touched_areas=["operator-intake-ledger", "input-audit-ledger", "target-contract", "claim-ledger", "manifest"],
        review_gate=(
            "The orchestrator should verify the interview stayed short, captured assumptions, and separated "
            "planning blockers from execution and claim-closeout blockers."
        ),
        claim_boundary=claim_boundary,
    )
    return filename, body


def provider_launch_preflight_lane_issue(
    *,
    prefix: str,
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    filename = f"{prefix}-provider-preflight-00-no-launch-until-green.md"
    body = issue_body(
        title=f"{prefix}: Provider launch preflight",
        role="BioProspector provider launch auditor",
        goal="Fail before paid compute starts if image pull, registry auth, branch snapshot, payload, volume, budget, secrets, or stage contracts are not ready.",
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            "provider-launch-preflight-ledger.tsv",
            "compute-provider-ledger.tsv",
            "runpod-run-manifest.json or equivalent provider bundle",
            "stage-contract-ledger.tsv",
        ],
        artifacts=[
            "provider-launch-preflight-ledger.tsv rows for image digest, registry auth, image pull, network volume, workdir, cost guardrail, secrets boundary, branch snapshot, provider payload size, issue body, data policy, and stage contract checks",
            "explicit launch blocker list",
            "claim-ledger or maturity notes when the run remains readiness-only",
        ],
        acceptance=[
            "Private registry images are blocked unless provider-side pull auth is verified outside the repo and Linear.",
            "Digest-pinned images are preferred; install-at-boot is recorded as a dev/emergency risk, not production readiness.",
            "Rendered issue bodies, provider payloads, branch/snapshot references, and bundle paths are checked before launch.",
            "No API key, token, private sequence, or credential material is written to the repo or Linear.",
        ],
        search_budget=[
            "Validate only manifests, generated bundles, issue bodies, and compact preflight rows.",
            "Do not create pods, submit AWS jobs, call provider APIs, or test credentials from this issue.",
        ],
        continuation_criteria=[
            "Continue to launch only when every blocking_before_launch row has status=pass.",
            "Continue only when the exact bundle exists in the branch or snapshot the worker will clone.",
        ],
        kill_criteria=[
            "Stop if desired provider state is RUNNING but container or stage progress proof is absent.",
            "Stop if a private image cannot be pulled by the provider.",
            "Stop if a worker would need to fall back silently to local compute, mock data, reference-only data, or a rescue route.",
        ],
        validation_command=validation,
        dependencies=["Blocked by provider strategy and stage contract review.", "Blocks any paid provider launch."],
        touched_areas=["provider-launch-preflight-ledger", "compute-provider-ledger", "runpod", "stage-contract-ledger"],
        review_gate="The orchestrator should verify provider readiness proof before starting anything that can burn money.",
        claim_boundary=claim_boundary,
    )
    return filename, body


def maturity_lane_issue(
    *,
    prefix: str,
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    filename = f"{prefix}-maturity-00-run-ladder.md"
    body = issue_body(
        title=f"{prefix}: Run maturity ladder",
        role="BioProspector maturity reviewer",
        goal="Separate plan, tools, materialized inputs, execution, evidence joins, and claim-audited dossier status.",
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            "run-maturity-ledger.tsv",
            "execution-artifact-ledger.tsv",
            "target-evidence-ledger.tsv",
            "claim-ledger.md",
        ],
        artifacts=[
            "run-maturity-ledger.tsv rows for L0 through L5",
            "blocking gaps that prevent promotion to the next maturity level",
            "review notes explaining which levels are planning-only versus evidence-backed",
        ],
        acceptance=[
            "L0 plan, L1 tools, L2 inputs, L3 execution, L4 evidence join, and L5 claim audit are distinct.",
            "No level is marked pass unless its evidence artifact exists.",
            "L3 cannot pass on dry-run or mock artifacts.",
        ],
        search_budget=[
            "Inspect local ledgers and compact execution summaries only.",
            "Do not launch cloud resources or run searches from maturity review.",
        ],
        continuation_criteria=[
            "Continue to execution only after L0-L2 are pass or explicitly blocked.",
            "Continue to claims only after L3-L4 pass with non-mock evidence.",
        ],
        kill_criteria=[
            "Downgrade any maturity level whose artifact proof is absent.",
            "Stop if a mock/dry-run artifact is being used as real execution evidence.",
        ],
        validation_command=validation,
        dependencies=["Blocked by input audit.", "Blocks campaign success closeout."],
        touched_areas=["run-maturity-ledger", "execution-artifact-ledger", "target-evidence-ledger", "claim-ledger"],
        review_gate="The orchestrator should refuse campaign-success language until the maturity ladder proves it.",
        claim_boundary=claim_boundary,
    )
    return filename, body


def target_evidence_lane_issue(
    *,
    prefix: str,
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    filename = f"{prefix}-target-evidence-00-join-gate.md"
    self_check = (
        "python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py "
        f"--campaign {display_path(campaign_path)} --require-target-evidence"
    )
    body = issue_body(
        title=f"{prefix}: Target evidence join gate",
        role="BioProspector evidence join reviewer",
        goal="Prevent public/reference hits from masquerading as target organism or sample evidence.",
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            "organism-sample-ledger.tsv",
            "target-dataset-ledger.tsv",
            "target-evidence-ledger.tsv",
            "enzyme-draft-board.tsv",
        ],
        artifacts=[
            "target-evidence-ledger.tsv rows joining candidate -> step -> organism/sample -> dataset",
            "candidate downgrade notes for records that only have reference/public hits",
            "self-check JSON showing target evidence joins pass or fail",
        ],
        acceptance=[
            "Every promoted candidate is joined to target evidence or explicitly downgraded.",
            "Reference-only hits remain labeled as reference context, not target evidence.",
            "Target organism/sample and dataset identities are explicit.",
        ],
        search_budget=[
            "Use compact target evidence summaries, accessions, hashes, or remote pointers only.",
            "Do not copy raw FASTA/GFF/spectra or private data into this repo.",
        ],
        continuation_criteria=[
            "Continue to L4 evidence-joined maturity only when promoted candidates have joined target evidence.",
            "Continue to route stitching only when reference-only candidates remain caveated.",
        ],
        kill_criteria=[
            "Downgrade candidate claims when target evidence is missing.",
            "Stop if the candidate cannot be tied to target organism/sample evidence required by the campaign.",
        ],
        validation_command=f"{validation}\n{self_check}",
        dependencies=["Blocked by candidate evidence review.", "Blocks L4 evidence-joined maturity."],
        touched_areas=["target-evidence-ledger", "organism-sample-ledger", "target-dataset-ledger", "enzyme-draft-board"],
        review_gate="The orchestrator should verify target joins before accepting promoted candidate claims.",
        claim_boundary=claim_boundary,
    )
    return filename, body


def decoy_control_lane_issue(
    *,
    prefix: str,
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    filename = f"{prefix}-decoy-control-00-negative-gate.md"
    self_check = (
        "python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py "
        f"--campaign {display_path(campaign_path)} --require-decoy-controls"
    )
    body = issue_body(
        title=f"{prefix}: Decoy and negative-control search gate",
        role="BioProspector control reviewer",
        goal="Require decoy or negative-control evidence before wide/frontier search lanes promote candidates.",
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            "reaction-step-ledger.tsv",
            "decoy-control-ledger.tsv",
            "candidate-funnels.tsv",
            "enzyme-draft-board.tsv",
        ],
        artifacts=[
            "decoy-control-ledger.tsv rows for wide/frontier steps",
            "control failure downgrade notes",
            "self-check JSON showing blocking controls pass or fail",
        ],
        acceptance=[
            "Every wide/frontier step has at least one passed blocking control before promotion.",
            "Failed controls block candidate promotion until resolved.",
            "Controls are represented as compact summaries, not raw search dumps.",
        ],
        search_budget=[
            "Use small decoy summaries or provider-side result pointers only.",
            "Do not start new searches from this review issue.",
        ],
        continuation_criteria=[
            "Continue to promotion only when blocking controls pass.",
            "Continue to rerun only through a separate approved execution issue.",
        ],
        kill_criteria=[
            "Kill or downgrade candidate families that also score strongly against decoys.",
            "Stop if control results cannot be joined to the step they are supposed to guard.",
        ],
        validation_command=f"{validation}\n{self_check}",
        dependencies=["Blocked by wide/frontier search result summaries.", "Blocks candidate promotion."],
        touched_areas=["decoy-control-ledger", "candidate-funnels", "enzyme-draft-board", "claim-ledger"],
        review_gate="The orchestrator should treat controls as promotion gates, not optional notes.",
        claim_boundary=claim_boundary,
    )
    body = with_claude_lane(body)
    return filename, body


def contract_self_check_lane_issue(
    *,
    prefix: str,
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    filename = f"{prefix}-contract-self-check-99-final-join.md"
    self_check = (
        "python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py "
        f"--campaign {display_path(campaign_path)} --require-real-execution --require-target-evidence "
        "--require-decoy-controls --require-maturity L5"
    )
    body = issue_body(
        title=f"{prefix}: Final contract self-check",
        role="BioProspector contract auditor",
        goal="Join inputs, materialized data, commands/results, evidence, controls, and claims before declaring success.",
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            "input-audit-ledger.tsv",
            "operator-intake-ledger.tsv",
            "run-maturity-ledger.tsv",
            "stage-contract-ledger.tsv",
            "stage-progress-ledger.tsv",
            "execution-artifact-ledger.tsv",
            "provider-launch-preflight-ledger.tsv",
            "target-evidence-ledger.tsv",
            "decoy-control-ledger.tsv",
            "claim-ledger.md",
        ],
        artifacts=[
            "contract self-check JSON",
            "claim downgrades for anything without joined proof",
            "final gap list split into missing input, missing execution, missing target evidence, failed controls, and overclaims",
        ],
        acceptance=[
            "Runner flags are not treated as proof.",
            "Dry-run and mock artifacts cannot satisfy real evidence requirements.",
            "Candidate and route claims are bounded by joined artifacts and target evidence.",
        ],
        search_budget=[
            "Read compact ledgers, manifests, summaries, and provenance only.",
            "Do not create new evidence inside the final self-check; return blockers instead.",
        ],
        continuation_criteria=[
            "Continue to success language only when the self-check passes under required flags.",
            "Continue to another execution wave only through a new issue if blockers remain.",
        ],
        kill_criteria=[
            "Fail the closeout if any required join is missing.",
            "Fail the closeout if mock/dry-run artifacts are being used as real proof.",
        ],
        validation_command=f"{validation}\n{self_check}",
        dependencies=["Blocked by all execution, evidence, control, and claim-audit lanes."],
        touched_areas=[
            "input-audit-ledger",
            "operator-intake-ledger",
            "run-maturity-ledger",
            "stage-contract-ledger",
            "stage-progress-ledger",
            "execution-artifact-ledger",
            "provider-launch-preflight-ledger",
            "target-evidence-ledger",
            "decoy-control-ledger",
            "claim-ledger",
        ],
        review_gate="The orchestrator should not mark the campaign successful unless this joined self-check passes.",
        claim_boundary=claim_boundary,
    )
    body = with_claude_lane(body)
    return filename, body


def provider_strategy_lane_issue(
    *,
    prefix: str,
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    filename = f"{prefix}-provider-strategy-00-compute-contract.md"
    body = issue_body(
        title=f"{prefix}: Compute provider strategy",
        role="BioProspector provider strategist",
        goal="Keep RunPod as one reviewed optional heavy-search pattern while allowing AWS ElasticBLAST and compatible neocloud/HPC/cloud paths only as role-specific, contract-preserving escalations.",
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            "compute-provider-ledger.tsv",
            "provider-launch-preflight-ledger.tsv",
            "stage-contract-ledger.tsv",
            "workflow-framework-ledger.tsv",
            "docs/compute-provider-strategy.md",
            "docs/runpod-stack.md",
        ],
        artifacts=[
            "compute-provider-ledger.tsv rows for approved, review-required, blocked, and future provider options",
            "provider-launch-preflight-ledger.tsv rows for launch blockers",
            "stage-contract-ledger.tsv expectations for long-running provider work",
            "provider-specific stop gates and cost/data boundaries",
            "notes mapping each provider to the same input audit, execution-artifact, target-evidence, and self-check contracts",
        ],
        acceptance=[
            "RunPod remains a reviewed optional pattern for controlled heavy search lanes.",
            "AWS ElasticBLAST may be marked reviewed only for official NCBI-wide BLAST escalation.",
            "Neocloud, cloud VM, SSH HPC, local-full, and managed workflow options may be marked reviewed only for a specific compatible/escalation role with the same ledger contracts.",
            "No provider-specific path is allowed to bypass no-false-success gates.",
            "No paid provider launch proceeds while blocking launch-preflight rows remain unpassed.",
        ],
        search_budget=[
            "Review provider docs, manifest execution policy, and provider ledger only.",
            "Do not launch instances, create buckets, upload queries, or download databases.",
        ],
        continuation_criteria=[
            "Continue to execution prep only after provider class, workdir, storage root, secrets boundary, and cost boundary are explicit.",
            "Continue to launch only after image pull, registry auth, payload, branch/snapshot, volume, and stage-contract checks pass.",
            "Continue only if the provider can return compact summaries and execution-artifact rows.",
        ],
        kill_criteria=[
            "Block providers that require secrets in repo/Linear or cannot preserve external heavy-data storage.",
            "Block providers that cannot emit stage-progress rows or prove container/workflow progress independently of provider desired state.",
            "Block providers that cannot emit the same self-check artifacts.",
        ],
        validation_command=validation,
        dependencies=["Blocked by input audit.", "Blocks provider-specific execution prep."],
        touched_areas=["compute-provider-ledger", "provider-launch-preflight-ledger", "stage-contract-ledger", "workflow-framework-ledger", "docs", "manifest"],
        review_gate="The orchestrator should verify the provider choice does not change the scientific or evidence contract.",
        claim_boundary=claim_boundary,
    )
    return filename, body


def workflow_framework_lane_issue(
    *,
    prefix: str,
    campaign_path: Path,
    validation: str,
    claim_boundary: str,
) -> tuple[str, str]:
    filename = f"{prefix}-workflow-framework-00-runner-contract.md"
    body = issue_body(
        title=f"{prefix}: Workflow framework compatibility",
        role="BioProspector workflow framework reviewer",
        goal="Define how shell scripts, Python CLIs, Nextflow, Snakemake, CWL, WDL, or managed workflows can all satisfy the same BioProspector output contract.",
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            "workflow-framework-ledger.tsv",
            "execution-artifact-ledger.tsv",
            "run-maturity-ledger.tsv",
            "docs/compute-provider-strategy.md",
        ],
        artifacts=[
            "workflow-framework-ledger.tsv rows for supported and deferred frameworks",
            "framework-specific provenance and resume requirements",
            "runner output requirements for execution-artifact, target-evidence, decoy-control, and self-check summaries",
        ],
        acceptance=[
            "Framework choice is independent of campaign semantics.",
            "Every live framework path can emit execution artifacts with dry-run/mock flags.",
            "Resumable frameworks are preferred for real campaigns, but shell/Python remains acceptable for readiness and smoke checks.",
        ],
        search_budget=[
            "Review framework contract only.",
            "Do not implement full Nextflow/Snakemake/CWL/WDL workflows from this issue.",
        ],
        continuation_criteria=[
            "Continue to live runner implementation only after provider storage, provenance, and output ledgers are defined.",
            "Continue only if the framework can write compact summaries without copying heavy data to the repo.",
        ],
        kill_criteria=[
            "Defer frameworks that cannot preserve provenance or resume state.",
            "Block frameworks that require private data or credentials in tracked files.",
        ],
        validation_command=validation,
        dependencies=["Blocked by compute provider strategy.", "Blocks live workflow implementation."],
        touched_areas=["workflow-framework-ledger", "execution-artifact-ledger", "docs", "templates"],
        review_gate="The orchestrator should verify framework portability before assigning implementation work.",
        claim_boundary=claim_boundary,
    )
    return filename, body


def build_issues(
    campaign_path: Path,
    prefix: str,
    *,
    include_evidence_lanes: bool = False,
    include_runpod_prep: bool = False,
    include_elasticblast_prep: bool = False,
    include_literature_lanes: bool = False,
    include_ambiguity_lanes: bool = False,
    include_enzyme_family_sweeps: bool = False,
    include_genome_mining_lanes: bool = False,
    include_structure_risk_lanes: bool = False,
    include_host_comparison_lanes: bool = False,
    include_assay_handoff_lanes: bool = False,
    include_monitoring_lanes: bool = False,
    include_stage_contract_lanes: bool = False,
    include_input_audit_lanes: bool = False,
    include_operator_intake_lanes: bool = False,
    include_maturity_lanes: bool = False,
    include_target_evidence_lanes: bool = False,
    include_decoy_control_lanes: bool = False,
    include_self_check_lanes: bool = False,
    include_provider_lanes: bool = False,
    include_provider_preflight_lanes: bool = False,
    include_framework_lanes: bool = False,
    include_sequence_search_lanes: bool = False,
    include_candidate_package_lanes: bool = False,
    include_candidate_intelligence_lanes: bool = True,
    include_genecluster_atlas_lanes: bool = False,
    include_scale_control_lanes: bool = False,
    include_self_learning_lanes: bool = False,
    include_tool_execution_proof_lanes: bool = False,
    include_template_design_lanes: bool = False,
    include_ledger_schema_lanes: bool = False,
    include_supply_chain_lanes: bool = False,
    include_active_site_audit_lanes: bool = False,
    include_route_rule_lanes: bool = False,
    include_thermodynamics_lanes: bool = False,
    include_metabolic_model_lanes: bool = False,
    include_strain_design_lanes: bool = False,
    include_chemoenzymatic_fallback_lanes: bool = False,
    include_bgc_context_lanes: bool = False,
    include_metagenome_context_lanes: bool = False,
    include_metabolomics_handoff_lanes: bool = False,
    include_compound_source_lanes: bool = False,
    include_review_surface_lanes: bool = False,
) -> dict[str, str]:
    manifest = load_json(campaign_path)
    base = campaign_path.parent
    ledgers = manifest["ledgers"]
    route_path = declared_path(base, ledgers.get("route_ledger"))
    step_path = declared_path(base, ledgers.get("reaction_step_ledger"))
    if route_path is None or step_path is None:
        raise ValueError("required ledger paths must stay inside the campaign directory")
    routes = read_tsv(route_path)
    steps = read_tsv(step_path)
    unknown_steps = read_optional_tsv(base, ledgers, "unknown_step_ledger")
    sequence_searches = read_optional_tsv(base, ledgers, "sequence_search_plan_ledger")
    sequence_search_steps = {row.get("step_id", "").strip() for row in sequence_searches if row.get("step_id", "").strip()}

    validation = (
        "python3 skills/bioprospector/scripts/bioprospector_preflight.py "
        f"--campaign {display_path(campaign_path)}"
    )
    claim_boundary = manifest["claim_boundary"]

    issues: dict[str, str] = {}
    campaign_id = manifest["campaign_id"]
    target = manifest["target_molecule"]
    host = manifest["host"]

    issues[f"{prefix}-00-target-contract.md"] = issue_body(
        title=f"{prefix}: Target contract and campaign ledger",
        role="BioProspector orchestrator",
        goal=f"Review and freeze the campaign contract for {target} in {host}.",
        inputs=[
            f"Campaign manifest: {display_path(campaign_path)}",
            f"Target contract: {display_path(base / manifest['target_contract'])}",
            f"Campaign id: {campaign_id}",
        ],
        artifacts=[
            "campaign decision notes",
            "updated claim-ledger.md rows if the scope changes",
            "review notes for route and step issue activation",
        ],
        acceptance=[
            "Target, host, scope, boundaries, ledgers, and execution policy are explicit.",
            "No downstream issue is activated if claim boundary or data policy is unclear.",
        ],
        search_budget=[
            "Inspect the manifest, target contract, current ledgers, and repo policy docs only.",
            "Do not start route expansion or candidate mining from this issue.",
        ],
        continuation_criteria=[
            "Continue to route issues only when the target, host, scope, claim boundary, and artifact policy are frozen.",
            "Continue only if all campaign ledgers referenced by the manifest validate.",
        ],
        kill_criteria=[
            "Stop if scope is not planning_only or if claim boundaries are ambiguous.",
            "Stop if the campaign depends on private or restricted data that lacks a safe reference path.",
        ],
        validation_command=validation,
        dependencies=["Blocks all route, step, integration, and red-team issues."],
        touched_areas=["manifest", "target-contract", "ledgers", "dossier"],
        review_gate="The orchestrator should freeze the target contract before activating any route or step issue.",
        claim_boundary=claim_boundary,
    )

    if include_runpod_prep:
        filename, body = campaign_runpod_prep_issue(
            prefix=prefix,
            manifest=manifest,
            campaign_path=campaign_path,
            validation=validation,
            claim_boundary=claim_boundary,
        )
        issues[filename] = body

    if include_elasticblast_prep:
        filename, body = campaign_elasticblast_prep_issue(
            prefix=prefix,
            manifest=manifest,
            campaign_path=campaign_path,
            validation=validation,
            claim_boundary=claim_boundary,
        )
        issues[filename] = body

    if include_candidate_package_lanes:
        filename, body = candidate_package_lane_issue(
            prefix=prefix,
            campaign_path=campaign_path,
            validation=validation,
            claim_boundary=claim_boundary,
        )
        issues[filename] = body

    if include_candidate_intelligence_lanes:
        filename, body = candidate_intelligence_lane_issue(
            prefix=prefix,
            campaign_path=campaign_path,
            validation=validation,
            claim_boundary=claim_boundary,
        )
        issues[filename] = body

    if include_genecluster_atlas_lanes:
        filename, body = genecluster_atlas_lane_issue(
            prefix=prefix,
            campaign_path=campaign_path,
            validation=validation,
            claim_boundary=claim_boundary,
        )
        issues[filename] = body

    if include_scale_control_lanes:
        filename, body = scale_control_lane_issue(
            prefix=prefix,
            campaign_path=campaign_path,
            validation=validation,
            claim_boundary=claim_boundary,
        )
        issues[filename] = body

    if include_self_learning_lanes:
        filename, body = self_learning_lane_issue(
            prefix=prefix,
            campaign_path=campaign_path,
            validation=validation,
            claim_boundary=claim_boundary,
        )
        issues[filename] = body

    opportunity_options = {
        "tool_execution_proof": include_tool_execution_proof_lanes,
        "template_design": include_template_design_lanes,
        "ledger_schema": include_ledger_schema_lanes,
        "supply_chain": include_supply_chain_lanes,
        "active_site_audit": include_active_site_audit_lanes,
        "route_rule": include_route_rule_lanes,
        "thermodynamics": include_thermodynamics_lanes,
        "metabolic_model": include_metabolic_model_lanes,
        "strain_design": include_strain_design_lanes,
        "chemoenzymatic_fallback": include_chemoenzymatic_fallback_lanes,
        "bgc_context": include_bgc_context_lanes,
        "metagenome_context": include_metagenome_context_lanes,
        "metabolomics_handoff": include_metabolomics_handoff_lanes,
        "compound_source": include_compound_source_lanes,
        "review_surface": include_review_surface_lanes,
    }
    for spec_key, enabled in opportunity_options.items():
        if not enabled:
            continue
        filename, body = opportunity_contract_lane_issue(
            spec_key=spec_key,
            prefix=prefix,
            campaign_path=campaign_path,
            validation=validation,
            claim_boundary=claim_boundary,
        )
        issues[filename] = body

    if include_literature_lanes:
        filename, body = literature_lane_issue(
            prefix=prefix,
            campaign_path=campaign_path,
            validation=validation,
            claim_boundary=claim_boundary,
        )
        issues[filename] = body

    if include_structure_risk_lanes:
        filename, body = structure_risk_lane_issue(
            prefix=prefix,
            campaign_path=campaign_path,
            validation=validation,
            claim_boundary=claim_boundary,
        )
        issues[filename] = body

    if include_host_comparison_lanes:
        filename, body = host_comparison_lane_issue(
            prefix=prefix,
            campaign_path=campaign_path,
            validation=validation,
            claim_boundary=claim_boundary,
        )
        issues[filename] = body

    if include_assay_handoff_lanes:
        filename, body = assay_handoff_lane_issue(
            prefix=prefix,
            campaign_path=campaign_path,
            validation=validation,
            claim_boundary=claim_boundary,
        )
        issues[filename] = body

    if include_monitoring_lanes:
        filename, body = monitoring_lane_issue(
            prefix=prefix,
            campaign_path=campaign_path,
            validation=validation,
            claim_boundary=claim_boundary,
        )
        issues[filename] = body

    if include_stage_contract_lanes:
        filename, body = stage_contract_lane_issue(
            prefix=prefix,
            campaign_path=campaign_path,
            validation=validation,
            claim_boundary=claim_boundary,
        )
        issues[filename] = body

    if include_input_audit_lanes:
        filename, body = input_audit_lane_issue(
            prefix=prefix,
            campaign_path=campaign_path,
            validation=validation,
            claim_boundary=claim_boundary,
        )
        issues[filename] = body

    if include_operator_intake_lanes:
        filename, body = operator_intake_lane_issue(
            prefix=prefix,
            campaign_path=campaign_path,
            validation=validation,
            claim_boundary=claim_boundary,
        )
        issues[filename] = body

    if include_maturity_lanes:
        filename, body = maturity_lane_issue(
            prefix=prefix,
            campaign_path=campaign_path,
            validation=validation,
            claim_boundary=claim_boundary,
        )
        issues[filename] = body

    if include_target_evidence_lanes:
        filename, body = target_evidence_lane_issue(
            prefix=prefix,
            campaign_path=campaign_path,
            validation=validation,
            claim_boundary=claim_boundary,
        )
        issues[filename] = body

    if include_decoy_control_lanes:
        filename, body = decoy_control_lane_issue(
            prefix=prefix,
            campaign_path=campaign_path,
            validation=validation,
            claim_boundary=claim_boundary,
        )
        issues[filename] = body

    if include_provider_lanes:
        filename, body = provider_strategy_lane_issue(
            prefix=prefix,
            campaign_path=campaign_path,
            validation=validation,
            claim_boundary=claim_boundary,
        )
        issues[filename] = body

    if include_provider_preflight_lanes:
        filename, body = provider_launch_preflight_lane_issue(
            prefix=prefix,
            campaign_path=campaign_path,
            validation=validation,
            claim_boundary=claim_boundary,
        )
        issues[filename] = body

    if include_framework_lanes:
        filename, body = workflow_framework_lane_issue(
            prefix=prefix,
            campaign_path=campaign_path,
            validation=validation,
            claim_boundary=claim_boundary,
        )
        issues[filename] = body

    if include_ambiguity_lanes:
        for unknown in unknown_steps:
            filename, body = dark_step_resolver_issue(
                prefix=prefix,
                unknown=unknown,
                campaign_path=campaign_path,
                validation=validation,
                claim_boundary=claim_boundary,
            )
            issues[filename] = body

    for route in routes:
        route_id = route["route_id"]
        title = f"{prefix}: Route {route_id} {route['route_name']}"
        route_steps = [step for step in steps if step["route_id"] == route_id]
        route_heavy_steps = [step for step in route_steps if step.get("candidate_search_width") in HEAVY_SEARCH_WIDTHS]
        issues[f"{prefix}-route-{slug(route_id)}-{slug(route['route_name'])}.md"] = issue_body(
            title=title,
            role="Route cartographer",
            goal=(
                f"Expand and review route {route_id} for {target} in {host}, "
                f"with status `{route['route_status']}` and evidence level `{route['evidence_level']}`."
            ),
            inputs=[
                f"Route id: {route_id}",
                f"Route class: {route['route_class']}",
                f"Feedstock mode: {route['feedstock_mode']}",
                f"Primary risk: {route['primary_risk']}",
                f"Step ids: {', '.join(step['step_id'] for step in route_steps) or 'none'}",
            ],
            artifacts=[
                "route-ledger.tsv row updates",
                "reaction-step-ledger.tsv row updates if route decomposition changes",
                "unknown-step-ledger.tsv rows for missing chemistry",
                "route kill or continuation recommendation",
            ],
            acceptance=[
                "Route steps are explicit enough for step-level candidate mining.",
                "Missing or uncertain transformations are captured as unknown-step entries.",
                "Route is not promoted without a primary risk and evidence level.",
            ],
            search_budget=[
                "Review the route row, associated step rows, target contract, and at most 10 route-neighbor hypotheses.",
                "Do not start broad enzyme search from the route issue; split those into step or evidence-lane drafts.",
                f"Wide/frontier steps on this route: {', '.join(step['step_id'] for step in route_heavy_steps) or 'none'}.",
            ],
            continuation_criteria=[
                "Continue to step issues only when route steps, primary risk, and missing chemistry are explicit.",
                "Continue only if route-level caveats can be represented in the claim ledger.",
            ],
            kill_criteria=[
                "Kill or park the route if its core chemistry cannot be decomposed into reviewable steps.",
                "Kill or park the route if the primary risk cannot be bounded for downstream candidate mining.",
            ],
            validation_command=validation,
            dependencies=[
                "Blocked by target contract review.",
                "Blocks step-level Enzyme Frontier issues for its route steps.",
            ],
            touched_areas=["route-ledger", "reaction-step-ledger", "unknown-step-ledger", "claim-ledger"],
            review_gate=(
                "The orchestrator should verify the route decomposition and route-specific risks before activating "
                "step-level candidate mining."
            ),
            claim_boundary=claim_boundary,
        )

    for step in steps:
        step_id = step["step_id"]
        requires_heavy = step["candidate_search_width"] in HEAVY_SEARCH_WIDTHS
        issues[f"{prefix}-step-{slug(step_id)}-{slug(step['enzyme_role'])}.md"] = issue_body(
            title=f"{prefix}: Step {step_id} {step['enzyme_role']}",
            role="Enzyme Frontier worker",
            goal=(
                f"Mine, filter, and score candidate enzymes for step {step_id}: "
                f"{step['substrate']} -> {step['product']}."
            ),
            inputs=[
                f"Route id: {step['route_id']}",
                f"Transformation: {step['transformation']}",
                f"Evidence need: {step['evidence_need']}",
                f"Candidate search width: {step['candidate_search_width']}",
                f"Required output: {step['required_output']}",
            ],
            artifacts=[
                "candidate-funnels.tsv row update",
                "enzyme-draft-board.tsv candidate rows if candidates are reviewed",
                "rejected-candidates.tsv rows for failures",
                "provenance notes for databases, queries, and thresholds",
            ],
            acceptance=[
                "Candidate counts move through the raw-to-shortlist funnel.",
                "Every candidate has a claim level before route stitching.",
                "Rejected candidates include a rejection reason.",
                "Frontier searches include explicit budget and continuation criteria.",
            ],
            search_budget=step_search_budget(step),
            continuation_criteria=step_continuation_criteria(step),
            kill_criteria=step_kill_criteria(step),
            validation_command=validation,
            dependencies=[
                f"Blocked by route {step['route_id']} review.",
                "Blocks Pathway Stitcher integration for any route using this step.",
            ],
            touched_areas=["candidate-funnels", "enzyme-draft-board", "rejected-candidates", "provenance", "claim-ledger"],
            review_gate=(
                "The orchestrator should compare raw-to-shortlist compression, evidence level, and rejected classes "
                "before route stitching consumes this step."
            ),
            claim_boundary=claim_boundary,
            requires_heavy_compute=requires_heavy,
        )

        if include_evidence_lanes and requires_heavy:
            filename, body = evidence_lane_issue(
                prefix=prefix,
                step=step,
                campaign_path=campaign_path,
                validation=validation,
                claim_boundary=claim_boundary,
            )
            issues[filename] = body

        if include_runpod_prep and requires_heavy:
            filename, body = step_runpod_prep_issue(
                prefix=prefix,
                step=step,
                manifest=manifest,
                campaign_path=campaign_path,
                validation=validation,
                claim_boundary=claim_boundary,
            )
            issues[filename] = body

        if include_elasticblast_prep and requires_heavy:
            filename, body = step_elasticblast_prep_issue(
                prefix=prefix,
                step=step,
                campaign_path=campaign_path,
                validation=validation,
                claim_boundary=claim_boundary,
            )
            issues[filename] = body

        if include_sequence_search_lanes and (requires_heavy or step_id in sequence_search_steps):
            filename, body = sequence_search_lane_issue(
                prefix=prefix,
                step=step,
                manifest=manifest,
                campaign_path=campaign_path,
                validation=validation,
                claim_boundary=claim_boundary,
            )
            issues[filename] = body

        if include_enzyme_family_sweeps and requires_heavy:
            filename, body = enzyme_family_sweep_issue(
                prefix=prefix,
                step=step,
                campaign_path=campaign_path,
                validation=validation,
                claim_boundary=claim_boundary,
            )
            issues[filename] = body

        if include_genome_mining_lanes and requires_heavy:
            filename, body = genome_mining_lane_issue(
                prefix=prefix,
                step=step,
                campaign_path=campaign_path,
                validation=validation,
                claim_boundary=claim_boundary,
            )
            issues[filename] = body

    issues[f"{prefix}-90-pathway-stitcher.md"] = issue_body(
        title=f"{prefix}: Pathway Stitcher integration review",
        role="Pathway Stitcher",
        goal="Combine reviewed step candidates into coherent route designs and score integrated feasibility.",
        inputs=[
            "route-ledger.tsv",
            "reaction-step-ledger.tsv",
            "candidate-funnels.tsv",
            "enzyme-draft-board.tsv",
            "route-stitching-scorecard.tsv",
        ],
        artifacts=[
            "route-stitching-scorecard.tsv updates",
            "host-fit-scorecard.tsv if host burdens are reviewed",
            "minimal-designs.md",
            "Pareto route recommendations",
        ],
        acceptance=[
            "No route advances on individual enzyme scores alone.",
            "Intermediate compatibility, cofactors, toxicity, host precursor fit, and missing steps are reviewed.",
            "At least minimal-gene, highest-evidence, and clearest-validation-handoff options are considered.",
        ],
        search_budget=[
            "Review only candidates that passed step-level gates or are explicitly carried as caveated alternatives.",
            "Compare all seeded routes, but keep final Pareto recommendations to compact route designs.",
            "Do not introduce new broad enzyme searches from the stitcher issue.",
        ],
        continuation_criteria=[
            "Continue to red-team only when integrated route bottlenecks and missing steps are explicit.",
            "Continue only when Pareto options include evidence, host-fit, validation-speed, and diversity tradeoffs.",
        ],
        kill_criteria=[
            "Kill or park any route that depends on unreviewed step candidates for a route-critical transformation.",
            "Kill claims of pathway completion unless direct evidence supports that exact target-host claim.",
        ],
        validation_command=validation,
        dependencies=["Blocked by candidate shortlists for all route-critical steps."],
        touched_areas=["route-stitching-scorecard", "host-fit-scorecard", "claim-ledger", "dossier"],
        review_gate=(
            "The orchestrator should verify route-level feasibility is not inferred from isolated enzyme scores "
            "before red-team review."
        ),
        claim_boundary=claim_boundary,
    )

    red_team_body = issue_body(
        title=f"{prefix}: Red-team claim audit",
        role="Red-team reviewer",
        goal="Attack route, candidate, and host-fit claims before downstream planning.",
        inputs=[
            "claim-ledger.md",
            "enzyme-draft-board.tsv",
            "route-stitching-scorecard.tsv",
            "candidate-funnels.tsv",
        ],
        artifacts=[
            "red-team-report.md",
            "claim-ledger.md updates",
            "rejected-candidates.tsv rows",
            "route-kill-list.md rows if needed",
        ],
        acceptance=[
            "Broad family hits are not promoted without evidence.",
            "Route completion is not claimed without direct validation.",
            "Weak links and missing validation evidence are explicit.",
        ],
        search_budget=[
            "Review every promoted route and candidate claim, plus a representative sample of rejected classes.",
            "Do not perform new search except to verify a disputed claim boundary or provenance citation.",
        ],
        continuation_criteria=[
            "Continue to downstream planning only when all claims have approved language and caveats.",
            "Continue only when killed routes, parked candidates, and unresolved validation gaps are preserved.",
        ],
        kill_criteria=[
            "Kill or downgrade any claim that exceeds the evidence in the ledgers.",
            "Kill route recommendations that hide missing chemistry, host-fit risk, or evidence gaps.",
        ],
        validation_command=validation,
        dependencies=["Blocked by Pathway Stitcher integration review."],
        touched_areas=["red-team-report", "claim-ledger", "rejected-candidates", "route-kill-list", "dossier"],
        review_gate=(
            "The orchestrator should treat this as the final claim-boundary gate before any external handoff "
            "or validation-readiness plan."
        ),
        claim_boundary=claim_boundary,
    )
    issues[f"{prefix}-99-red-team.md"] = with_claude_lane(red_team_body)

    if include_self_check_lanes:
        filename, body = contract_self_check_lane_issue(
            prefix=prefix,
            campaign_path=campaign_path,
            validation=validation,
            claim_boundary=claim_boundary,
        )
        issues[filename] = body

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", required=True, type=Path, help="Path to campaign-manifest.json")
    parser.add_argument("--prefix", default="BIOPROSPECTOR", help="Issue filename/title prefix")
    parser.add_argument("--out", required=True, type=Path, help="Output directory for issue markdown files")
    parser.add_argument(
        "--include-profile",
        choices=sorted(INCLUDE_PROFILES),
        help="Enable a named bundle of include flags.",
    )
    parser.add_argument(
        "--include-evidence-lanes",
        action="store_true",
        help="Also draft evidence-lane child issues for wide/frontier reaction steps.",
    )
    parser.add_argument(
        "--include-runpod-prep",
        action="store_true",
        help="Also draft RunPod campaign and step prep issues without creating pods or Linear issues.",
    )
    parser.add_argument(
        "--include-elasticblast-prep",
        action="store_true",
        help="Also draft AWS ElasticBLAST campaign and step prep issues without touching AWS.",
    )
    parser.add_argument(
        "--include-literature-lanes",
        action="store_true",
        help="Also draft literature/evidence ledger issues.",
    )
    parser.add_argument(
        "--include-ambiguity-lanes",
        action="store_true",
        help="Also draft Dark Step Resolver issues for unknown-step rows.",
    )
    parser.add_argument(
        "--include-enzyme-family-sweeps",
        action="store_true",
        help="Also draft family-level compression issues for wide/frontier steps.",
    )
    parser.add_argument(
        "--include-genome-mining-lanes",
        action="store_true",
        help="Also draft genome-context mining prep issues for wide/frontier steps.",
    )
    parser.add_argument(
        "--include-structure-risk-lanes",
        action="store_true",
        help="Also draft structure-risk triage issues.",
    )
    parser.add_argument(
        "--include-host-comparison-lanes",
        action="store_true",
        help="Also draft host-fit comparison issues.",
    )
    parser.add_argument(
        "--include-assay-handoff-lanes",
        action="store_true",
        help="Also draft non-procedural evidence handoff and validation-readiness issues.",
    )
    parser.add_argument(
        "--include-monitoring-lanes",
        action="store_true",
        help="Also draft campaign monitoring and provenance ledger issues.",
    )
    parser.add_argument(
        "--include-stage-contract-lanes",
        action="store_true",
        help="Also draft stage contract and progress ledger issues for long runs.",
    )
    parser.add_argument(
        "--include-input-audit-lanes",
        action="store_true",
        help="Also draft no-false-success input audit issues.",
    )
    parser.add_argument(
        "--include-operator-intake-lanes",
        action="store_true",
        help="Also draft short operator interview and assumption-confirmation issues.",
    )
    parser.add_argument(
        "--include-maturity-lanes",
        action="store_true",
        help="Also draft run maturity ladder issues.",
    )
    parser.add_argument(
        "--include-target-evidence-lanes",
        action="store_true",
        help="Also draft target-evidence join gate issues.",
    )
    parser.add_argument(
        "--include-decoy-control-lanes",
        action="store_true",
        help="Also draft decoy and negative-control gate issues.",
    )
    parser.add_argument(
        "--include-self-check-lanes",
        action="store_true",
        help="Also draft final contract self-check issues.",
    )
    parser.add_argument(
        "--include-provider-lanes",
        action="store_true",
        help="Also draft compute provider strategy issues for local, RunPod, cloud, neocloud, and HPC paths.",
    )
    parser.add_argument(
        "--include-provider-preflight-lanes",
        action="store_true",
        help="Also draft provider launch preflight issues for image, auth, bundle, payload, and stage gates.",
    )
    parser.add_argument(
        "--include-framework-lanes",
        action="store_true",
        help="Also draft workflow framework compatibility issues.",
    )
    parser.add_argument(
        "--include-sequence-search-lanes",
        action="store_true",
        help="Also draft step-specific BLAST/DIAMOND/MMseqs/HMMER search-contract issues.",
    )
    parser.add_argument(
        "--include-candidate-package-lanes",
        action="store_true",
        help="Also draft candidate graph, AA-sequence package, domain-map, diversity, and dossier issues.",
    )
    parser.add_argument(
        "--include-candidate-intelligence-lanes",
        action="store_true",
        help="Draft sequence/public-evidence intelligence issues for publicly reported/reference enzymes, mutants, signal peptides, PTMs, localization, and canonical-match inferences. This lane is default-on; the flag is accepted for compatibility.",
    )
    parser.add_argument(
        "--include-genecluster-atlas-lanes",
        action="store_true",
        help="Also draft the metadata-only GeneCluster atlas source scout, route decision, cluster/function jury, and dossier contract issue.",
    )
    parser.add_argument(
        "--include-scale-control-lanes",
        action="store_true",
        help="Also draft fanout, partial closeout, lane-status, and stale-output guard issues.",
    )
    parser.add_argument(
        "--include-self-learning-lanes",
        action="store_true",
        help="Also draft a self-learning skill issue for turning hiccups into durable runbook, skill, template, or validator updates.",
    )
    for flag, help_text in (
        ("--include-tool-execution-proof-lanes", "Also draft exact executable proof contract issues."),
        ("--include-template-design-lanes", "Also draft curated template-design contract issues."),
        ("--include-ledger-schema-lanes", "Also draft ledger schema hardening issues."),
        ("--include-supply-chain-lanes", "Also draft provider image supply-chain preflight issues."),
        ("--include-active-site-audit-lanes", "Also draft active-site and structure-risk audit issues."),
        ("--include-route-rule-lanes", "Also draft route-rule expansion and compression issues."),
        ("--include-thermodynamics-lanes", "Also draft route thermodynamics feasibility issues."),
        ("--include-metabolic-model-lanes", "Also draft metabolic-model host-fit issues."),
        ("--include-strain-design-lanes", "Also draft non-operational host-fit model perturbation review issues."),
        ("--include-chemoenzymatic-fallback-lanes", "Also draft chemoenzymatic fallback and rescue-route issues."),
        ("--include-bgc-context-lanes", "Also draft BGC context handoff issues."),
        ("--include-metagenome-context-lanes", "Also draft metagenome context handoff issues."),
        ("--include-metabolomics-handoff-lanes", "Also draft metabolomics evidence handoff issues."),
        ("--include-compound-source-lanes", "Also draft compound/source prior review issues."),
        ("--include-review-surface-lanes", "Also draft candidate graph and review-surface contract issues."),
    ):
        parser.add_argument(flag, action="store_true", help=help_text)
    args = parser.parse_args()

    campaign = args.campaign
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    include_options = resolve_include_options(
        args.include_profile,
        {name: getattr(args, name) for name in INCLUDE_FLAG_ATTRS},
    )

    try:
        issues = build_issues(campaign, args.prefix, **include_options)
    except ValueError as exc:
        print(f"FAIL issue draft generation: {exc}")
        return 1
    for filename, body in issues.items():
        (out / filename).write_text(body, encoding="utf-8")

    print(f"Wrote {len(issues)} issue drafts to {display_path(out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
