#!/usr/bin/env python3
"""Normalize compact tool summaries into BioProspector evidence ledgers."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from bioprospector_schema import ledger_headers


BLAST6_COLUMNS = [
    "qseqid",
    "sseqid",
    "pident",
    "length",
    "mismatch",
    "gapopen",
    "qstart",
    "qend",
    "sstart",
    "send",
    "evalue",
    "bitscore",
]


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return "REPLACE_ME_EXTERNAL_PATH"


def reject_raw_input(path: Path) -> None:
    raw_suffixes = {".fa", ".faa", ".fasta", ".fna", ".ffn", ".fq", ".fastq", ".gb", ".gbk", ".gff", ".gff3"}
    if path.suffix.lower() in raw_suffixes:
        raise ValueError("FASTA/raw sequence input is not allowed; provide compact tabular search output")
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        first = handle.readline()
    if first.lstrip().startswith(">"):
        raise ValueError("FASTA/raw sequence input is not allowed; provide compact tabular search output")


def read_rows(path: Path, fmt: str) -> list[dict[str, str]]:
    reject_raw_input(path)
    if fmt in {"tsv", "domain-tsv"}:
        with path.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle, delimiter="\t"))
    if fmt in {"blast6", "diamond", "mmseqs"}:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle, delimiter="\t")
            rows = []
            for values in reader:
                if not values or values[0].startswith("#"):
                    continue
                if len(values) >= 12:
                    rows.append({column: values[index] if index < len(values) else "" for index, column in enumerate(BLAST6_COLUMNS)})
                else:
                    raise ValueError(f"{fmt} rows must have at least 12 tab-separated compact columns")
            return rows
    if fmt == "hmmer-domtbl":
        rows = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip() or line.startswith("#"):
                    continue
                values = line.split()
                if len(values) < 23:
                    raise ValueError("hmmer-domtbl rows must be compact domtblout rows, not raw sequence data")
                rows.append(
                    {
                        "target": values[0],
                        "target_accession": values[1],
                        "query": values[3],
                        "query_accession": values[4],
                        "evalue": values[6],
                        "bitscore": values[7],
                        "domain_ievalue": values[12],
                        "domain_score": values[13],
                        "hmm_from": values[15],
                        "hmm_to": values[16],
                        "ali_from": values[17],
                        "ali_to": values[18],
                        "description": " ".join(values[22:]),
                    }
                )
        return rows
    raise ValueError(f"unsupported format: {fmt}")


def as_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def as_int(value: str, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}"


def compact_json(payload: dict[str, str | float | int]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def write_tsv(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({header: row.get(header, "") for header in headers})


def subject_id(hit: dict[str, str], index: int) -> str:
    return hit.get("sseqid") or hit.get("target") or hit.get("subject") or hit.get("accession") or f"hit_{index}"


def identity(hit: dict[str, str]) -> float:
    return as_float(hit.get("pident", hit.get("identity", "0")))


def evalue(hit: dict[str, str]) -> float:
    return as_float(hit.get("evalue", hit.get("domain_ievalue", "1")))


def bitscore(hit: dict[str, str]) -> float:
    return as_float(hit.get("bitscore", hit.get("domain_score", "0")))


def sequence_hits(
    rows: list[dict[str, str]],
    *,
    fmt: str,
    step_id: str,
    run_id: str,
    campaign_id: str,
    source_scope: str,
    source_tool_id: str,
    adapter_id: str,
    query_id: str,
    hits_name: str,
    max_candidates: int,
    min_identity: float,
    max_evalue: float,
) -> dict[str, list[dict[str, str]]]:
    filtered = [hit for hit in rows if identity(hit) >= min_identity and evalue(hit) <= max_evalue]
    selected = sorted(filtered, key=bitscore, reverse=True)[:max_candidates]

    candidates: list[dict[str, str]] = []
    evidence: list[dict[str, str]] = []
    sequences: list[dict[str, str]] = []
    graph: list[dict[str, str]] = []
    events: list[dict[str, str]] = []

    for index, hit in enumerate(selected, start=1):
        subject = subject_id(hit, index)
        candidate_id = stable_id(f"{run_id}-{step_id}-E", step_id, subject)
        metrics = {
            "format": fmt,
            "identity": identity(hit),
            "evalue": hit.get("evalue", ""),
            "bitscore": bitscore(hit),
            "alignment_length": as_int(hit.get("length", "0")),
        }
        candidates.append(
            {
                "candidate_id": candidate_id,
                "step_id": step_id,
                "candidate_name": subject,
                "source_organism": source_scope,
                "accession_or_source": subject,
                "enzyme_family": "review_after_ingest",
                "domain_architecture": "not_mapped",
                "evidence_classes": "sequence_similarity",
                "claim_level": "hypothesis",
                "substrate_fit": "unknown",
                "host_fit": "unknown",
                "rejection_risk": "medium",
                "verdict": "review",
                "notes": f"identity={metrics['identity']}; evalue={metrics['evalue']}; bitscore={metrics['bitscore']}",
            }
        )
        evidence.append(
            {
                "evidence_id": f"TE-{stable_id(run_id, candidate_id, 'target-evidence')}",
                "candidate_id": candidate_id,
                "step_id": step_id,
                "organism_id": "ORG_REVIEW",
                "dataset_id": "DS_REVIEW",
                "evidence_type": "homolog_hit",
                "evidence_pointer": f"compact_table:{hits_name}#{index}",
                "join_status": "pending",
                "claim_level": "hypothesis",
                "notes": "Search similarity is ranking input only until joined to source context, controls, and claim audit.",
            }
        )
        sequences.append(
            {
                "candidate_id": candidate_id,
                "step_id": step_id,
                "sequence_type": "provider_pointer",
                "sequence_pointer": f"provider_side_candidate_sequence_pending:{subject}",
                "aa_length": "0",
                "checksum_or_version": "provider_side_checksum_pending",
                "source_database": source_scope,
                "license_boundary": "accession_summary_only",
                "domain_map_status": "planned",
                "notes": "No raw sequence copied into repo; provider-side full AA pack must materialize this pointer.",
            }
        )
        graph.append(
            {
                "edge_id": stable_id("EDGE", step_id, candidate_id, "step_candidate"),
                "source_id": step_id,
                "target_id": candidate_id,
                "edge_type": "step_candidate",
                "step_id": step_id,
                "evidence_class": "sequence_similarity",
                "weight": f"{min(bitscore(hit) / 500.0, 1.0):.3f}",
                "claim_level": "hypothesis",
                "notes": "Derived from compact adapter ingest.",
            }
        )
        events.append(
            {
                "event_id": stable_id("EV", campaign_id, run_id, step_id, candidate_id, subject),
                "event_type": "sequence_hit",
                "campaign_id": campaign_id,
                "run_id": run_id,
                "step_id": step_id,
                "candidate_id": candidate_id,
                "query_id": query_id,
                "source_tool_id": source_tool_id,
                "adapter_id": adapter_id,
                "source_scope": source_scope,
                "evidence_class": "sequence_similarity",
                "evidence_type": "homolog_hit",
                "evidence_pointer": f"compact_table:{hits_name}#{index}",
                "metrics_json": compact_json(metrics),
                "claim_level": "hypothesis",
                "join_status": "pending",
                "license_boundary": "accession_summary_only",
                "checksum_or_version": "compact_input",
                "raw_data_retained": "false",
                "private_data_status": "none",
                "notes": "Normalized compact hit; not biological validation.",
            }
        )

    funnel_row = {
        "step_id": step_id,
        "raw_hits": str(len(rows)),
        "quality_filtered": str(len(filtered)),
        "domain_valid": "0",
        "clustered_representatives": str(len(selected)),
        "evidence_reviewed": "0",
        "shortlisted": "0",
        "final_picks": "0",
        "funnel_status": "derived_compact_hits",
        "notes": "Derived from compact tabular output only; no raw sequence evidence ingested.",
    }
    return {
        "candidate_funnels": [funnel_row],
        "enzyme_draft_board": candidates,
        "target_evidence_ledger": evidence,
        "candidate_sequence_ledger": sequences,
        "candidate_graph_ledger": graph,
        "evidence_event_ledger": events,
    }


def domain_hits(
    rows: list[dict[str, str]],
    *,
    fmt: str,
    step_id: str,
    run_id: str,
    campaign_id: str,
    source_scope: str,
    source_tool_id: str,
    adapter_id: str,
    query_id: str,
    hits_name: str,
) -> dict[str, list[dict[str, str]]]:
    annotations: list[dict[str, str]] = []
    events: list[dict[str, str]] = []
    for index, row in enumerate(rows, start=1):
        candidate = row.get("candidate_id") or row.get("target") or row.get("sseqid") or f"candidate_review_{index}"
        domain_accession = row.get("domain_accession") or row.get("query_accession") or row.get("target_accession") or "review_domain"
        domain_name = row.get("domain_name") or row.get("query") or row.get("description") or "review_domain"
        domain_start = row.get("domain_start") or row.get("ali_from") or "0"
        domain_end = row.get("domain_end") or row.get("ali_to") or "0"
        confidence = row.get("confidence") or ("high" if evalue(row) <= 1e-10 else "medium")
        annotation_id = stable_id("DOM", step_id, candidate, domain_accession, domain_start, domain_end)
        metrics = {
            "format": fmt,
            "evalue": row.get("evalue", row.get("domain_ievalue", "")),
            "bitscore": bitscore(row),
            "domain_start": domain_start,
            "domain_end": domain_end,
        }
        annotations.append(
            {
                "annotation_id": annotation_id,
                "candidate_id": candidate,
                "step_id": step_id,
                "domain_source": source_tool_id,
                "domain_accession": domain_accession,
                "domain_name": domain_name,
                "domain_start": str(as_int(domain_start)),
                "domain_end": str(as_int(domain_end)),
                "motif_or_active_site": row.get("motif_or_active_site", "review_required"),
                "confidence": confidence,
                "notes": "Derived from compact domain summary only.",
            }
        )
        events.append(
            {
                "event_id": stable_id("EV", campaign_id, run_id, step_id, candidate, annotation_id),
                "event_type": "domain_hit",
                "campaign_id": campaign_id,
                "run_id": run_id,
                "step_id": step_id,
                "candidate_id": candidate,
                "query_id": query_id,
                "source_tool_id": source_tool_id,
                "adapter_id": adapter_id,
                "source_scope": source_scope,
                "evidence_class": "domain",
                "evidence_type": "domain_hit",
                "evidence_pointer": f"compact_domain_table:{hits_name}#{index}",
                "metrics_json": compact_json(metrics),
                "claim_level": "hypothesis",
                "join_status": "pending",
                "license_boundary": "summary_only",
                "checksum_or_version": "compact_input",
                "raw_data_retained": "false",
                "private_data_status": "none",
                "notes": "Normalized compact domain hit; not validation.",
            }
        )
    return {"domain_annotation_ledger": annotations, "evidence_event_ledger": events}


def ingest(
    *,
    hits_path: Path,
    out_dir: Path,
    step_id: str,
    run_id: str,
    campaign_id: str,
    source_scope: str,
    fmt: str,
    max_candidates: int,
    min_identity: float,
    max_evalue: float,
    source_tool_id: str,
    adapter_id: str,
    query_id: str,
) -> None:
    headers = ledger_headers()
    rows = read_rows(hits_path, fmt)
    if fmt in {"hmmer-domtbl", "domain-tsv"}:
        ledgers = domain_hits(
            rows,
            fmt=fmt,
            step_id=step_id,
            run_id=run_id,
            campaign_id=campaign_id,
            source_scope=source_scope,
            source_tool_id=source_tool_id,
            adapter_id=adapter_id,
            query_id=query_id,
            hits_name=hits_path.name,
        )
    else:
        ledgers = sequence_hits(
            rows,
            fmt=fmt,
            step_id=step_id,
            run_id=run_id,
            campaign_id=campaign_id,
            source_scope=source_scope,
            source_tool_id=source_tool_id,
            adapter_id=adapter_id,
            query_id=query_id,
            hits_name=hits_path.name,
            max_candidates=max_candidates,
            min_identity=min_identity,
            max_evalue=max_evalue,
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    filenames = {
        "candidate_funnels": "candidate-funnels.tsv",
        "enzyme_draft_board": "enzyme-draft-board.tsv",
        "target_evidence_ledger": "target-evidence-ledger.tsv",
        "candidate_sequence_ledger": "candidate-sequence-ledger.tsv",
        "candidate_graph_ledger": "candidate-graph-ledger.tsv",
        "domain_annotation_ledger": "domain-annotation-ledger.tsv",
        "evidence_event_ledger": "evidence-event-ledger.tsv",
    }
    for key, rows_for_ledger in ledgers.items():
        if rows_for_ledger:
            write_tsv(out_dir / filenames[key], headers[key], rows_for_ledger)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hits", required=True, type=Path, help="Compact tabular hit file; FASTA is rejected")
    parser.add_argument("--out", required=True, type=Path, help="Output directory for derived ledgers")
    parser.add_argument("--step-id", required=True)
    parser.add_argument("--run-id", default="INGEST")
    parser.add_argument("--campaign-id", default="CAMPAIGN_REVIEW")
    parser.add_argument("--source-scope", default="public_or_provider_summary")
    parser.add_argument("--source-tool-id", default="tool_review")
    parser.add_argument("--adapter-id", default="adapter_review")
    parser.add_argument("--query-id", default="")
    parser.add_argument("--format", choices=["blast6", "diamond", "mmseqs", "tsv", "hmmer-domtbl", "domain-tsv"], default="blast6")
    parser.add_argument("--max-candidates", default=25, type=int)
    parser.add_argument("--min-identity", default=30.0, type=float)
    parser.add_argument("--max-evalue", default=1e-5, type=float)
    args = parser.parse_args()

    try:
        ingest(
            hits_path=args.hits.resolve(),
            out_dir=args.out.resolve(),
            step_id=args.step_id,
            run_id=args.run_id,
            campaign_id=args.campaign_id,
            source_scope=args.source_scope,
            fmt=args.format,
            max_candidates=args.max_candidates,
            min_identity=args.min_identity,
            max_evalue=args.max_evalue,
            source_tool_id=args.source_tool_id,
            adapter_id=args.adapter_id,
            query_id=args.query_id,
        )
    except ValueError as exc:
        print(f"FAIL {exc}")
        return 1
    print(f"Wrote derived evidence ledgers to {display_path(args.out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
