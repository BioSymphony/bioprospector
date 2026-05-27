#!/usr/bin/env python3
"""Run the BioProspector route stitcher and Pareto ranking pass."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from bioprospector_candidate_package import build_candidate_package, display_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path, help="Output directory for ranking and package index ledgers")
    parser.add_argument("--run-id", default="RANK")
    parser.add_argument(
        "--provider-pointer",
        default="provider-output://review-before-run/candidate-package",
        help="External pointer used for package-index joins; no raw sequences are written",
    )
    args = parser.parse_args()

    counts = build_candidate_package(
        args.campaign,
        out_dir=args.out,
        run_id=args.run_id,
        provider_pointer=args.provider_pointer,
        package_status="planned",
    )
    selected = {
        key: value
        for key, value in counts.items()
        if key in {"candidate_ranking_ledger", "pareto_frontier_ledger", "candidate_graph_ledger", "run_output_package_ledger"}
    }
    print(json.dumps({"out": display_path(args.out), "ranking_counts": selected}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
