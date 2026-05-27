.PHONY: help first-look release-check switch-check test build package-smoke wheel-smoke doctor docs-check metadata-check version-check examples capabilities local-demo capability-demo demo-artifacts campaign-status-demo handoff-demo agent-brief-demo retrospective-demo provider-demo audit runtime-audit clean-runtime

help:
	@echo "BioProspector local commands"
	@echo "  make first-look            Run doctor, local demo, and point at the resulting dossier"
	@echo "  make doctor                Check checkout, schema, optional tools, and public audit"
	@echo "  make local-demo            Generate local-only demo artifacts under .runtime/"
	@echo "  make campaign-status-demo  Write compact campaign status snapshots"
	@echo "  make handoff-demo          Write review-only worker/reviewer handoff packets"
	@echo "  make agent-brief-demo      Write Codex/Claude/goal-ready campaign briefs"
	@echo "  make release-check         Run tests, docs, examples, demos, tree audit, and runtime audit"
	@echo "  make switch-check          Alias for release-check before any public switch"
	@echo "  make wheel-smoke           Build/install the wheel into an isolated target and run CLI smoke"
	@echo "  make provider-demo         Review-only provider bundle smoke; no resource creation"
	@echo "  make retrospective-demo    Write a public-safe retrospective ledger over local demo runs"

first-look: doctor local-demo
	@echo ""
	@echo "BioProspector first look complete."
	@echo "Open the dossier:"
	@echo "  .runtime/local-demo/huperzine/dossier.md"
	@echo "Other useful outputs live under .runtime/local-demo/."

release-check: test package-smoke doctor docs-check metadata-check examples capabilities audit runtime-audit

switch-check: release-check

test:
	python3 -m py_compile skills/bioprospector/scripts/*.py src/biosymphony_bioprospector/*.py
	python3 -m pytest -q

build:
	rm -rf .runtime/package-smoke/dist
	mkdir -p .runtime/package-smoke/dist
	python3 -m pip wheel . --no-deps -w .runtime/package-smoke/dist

package-smoke: wheel-smoke

wheel-smoke: build
	rm -rf .runtime/package-smoke/install
	python3 -m pip install --no-index --find-links .runtime/package-smoke/dist --target .runtime/package-smoke/install biosymphony-bioprospector
	cd .runtime/package-smoke && BIOPROSPECTOR_REPO_ROOT="$(CURDIR)" PYTHONPATH=install python3 -m biosymphony_bioprospector.cli --help >/dev/null
	cd .runtime/package-smoke && BIOPROSPECTOR_REPO_ROOT="$(CURDIR)" PYTHONPATH=install python3 -m biosymphony_bioprospector.cli commands --json >/dev/null
	cd .runtime/package-smoke && BIOPROSPECTOR_REPO_ROOT="$(CURDIR)" PYTHONPATH=install python3 -m biosymphony_bioprospector.cli doctor --json >/dev/null
	cd .runtime/package-smoke && BIOPROSPECTOR_REPO_ROOT="$(CURDIR)" PYTHONPATH=install python3 -m biosymphony_bioprospector.cli agent-brief --help >/dev/null
	cd .runtime/package-smoke && BIOPROSPECTOR_REPO_ROOT="$(CURDIR)" PYTHONPATH=install python3 -m biosymphony_bioprospector.cli campaign-handoff --help >/dev/null
	cd .runtime/package-smoke && BIOPROSPECTOR_REPO_ROOT="$(CURDIR)" PYTHONPATH=install python3 -m biosymphony_bioprospector.cli campaign-status --help >/dev/null
	cd .runtime/package-smoke && BIOPROSPECTOR_REPO_ROOT="$(CURDIR)" PYTHONPATH=install python3 -m biosymphony_bioprospector.cli genecluster-atlas-plan --help >/dev/null
	cd .runtime/package-smoke && BIOPROSPECTOR_REPO_ROOT="$(CURDIR)" PYTHONPATH=install python3 -m biosymphony_bioprospector.cli stage-contract --help >/dev/null
	cd .runtime/package-smoke && BIOPROSPECTOR_REPO_ROOT="$(CURDIR)" PYTHONPATH=install python3 -m biosymphony_bioprospector.cli retrospective --help >/dev/null
	rm -rf /tmp/bioprospector-wheel-no-checkout-install
	python3 -m pip install --no-index --find-links .runtime/package-smoke/dist --target /tmp/bioprospector-wheel-no-checkout-install biosymphony-bioprospector >/dev/null
	cd /tmp && PYTHONPATH=/tmp/bioprospector-wheel-no-checkout-install python3 -m biosymphony_bioprospector.cli --version >/dev/null
	cd /tmp && if PYTHONPATH=/tmp/bioprospector-wheel-no-checkout-install python3 -m biosymphony_bioprospector.cli doctor >/tmp/bioprospector-wheel-no-checkout.out 2>&1; then cat /tmp/bioprospector-wheel-no-checkout.out; exit 1; else grep -q "Could not locate a BioProspector checkout" /tmp/bioprospector-wheel-no-checkout.out; fi

doctor:
	python3 skills/bioprospector/scripts/bioprospector_doctor.py --include-runtime

docs-check:
	python3 scripts/check_docs_links.py .
	python3 scripts/check_docs_index.py .

metadata-check: version-check

version-check:
	python3 scripts/check_release_metadata.py .

examples:
	python3 skills/bioprospector/scripts/bioprospector_preflight.py --campaign skills/bioprospector/examples/vanillin-yeast-v0/campaign-manifest.json
	python3 skills/bioprospector/scripts/bioprospector_preflight.py --campaign skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json --repo-root . --scan-local-artifacts
	python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py --campaign skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json
	python3 skills/bioprospector/scripts/bioprospector_stage_contract.py --campaign skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json
	python3 skills/bioprospector/scripts/bioprospector_preflight.py --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json --repo-root . --scan-local-artifacts
	python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json
	python3 skills/bioprospector/scripts/bioprospector_stage_contract.py --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json

capabilities: local-demo

local-demo: capability-demo

capability-demo: demo-artifacts retrospective-demo
	python3 skills/bioprospector/scripts/bioprospector_public_demo_smoke.py --campaign skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json --prefix NOOTKATONE --out .runtime/public-demo-smoke/nootkatone --skip-provider-bundles
	python3 skills/bioprospector/scripts/bioprospector_public_demo_smoke.py --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json --prefix HUPERZINE --out .runtime/public-demo-smoke/huperzine --skip-provider-bundles

provider-demo:
	python3 skills/bioprospector/scripts/bioprospector_public_demo_smoke.py --campaign skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json --prefix NOOTKATONE --out .runtime/provider-demo-smoke/nootkatone
	python3 skills/bioprospector/scripts/bioprospector_public_demo_smoke.py --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json --prefix HUPERZINE --out .runtime/provider-demo-smoke/huperzine

demo-artifacts: campaign-status-demo handoff-demo agent-brief-demo
	python3 skills/bioprospector/scripts/bioprospector_campaign_graph.py --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json --out .runtime/local-demo/huperzine/campaign-plan.json
	python3 skills/bioprospector/scripts/bioprospector_genecluster_atlas_plan.py --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json --out .runtime/local-demo/huperzine/genecluster-atlas
	python3 skills/bioprospector/scripts/bioprospector_genecluster_atlas_normalizers.py all --annotation-direct skills/bioprospector/examples/genecluster-synthetic-v0/compact-clusters.tsv --pfam skills/bioprospector/examples/genecluster-synthetic-v0/compact-pfam.tsv --out-dir .runtime/local-demo/genecluster-synthetic/atlas
	python3 skills/bioprospector/scripts/bioprospector_genecluster_atlas_contracts.py --cluster-calls .runtime/local-demo/genecluster-synthetic/atlas/cluster_calls.tsv --bgc-consensus .runtime/local-demo/genecluster-synthetic/atlas/bgc_consensus.tsv --protein-function-votes .runtime/local-demo/genecluster-synthetic/atlas/protein_function_votes.tsv --protein-function-jury .runtime/local-demo/genecluster-synthetic/atlas/protein_function_jury.tsv
	python3 skills/bioprospector/scripts/bioprospector_candidate_package.py --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json --out .runtime/local-demo/huperzine/candidate-package
	python3 skills/bioprospector/scripts/bioprospector_pareto_rank.py --campaign skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json --out .runtime/local-demo/nootkatone/ranking
	python3 skills/bioprospector/scripts/bioprospector_dossier_export.py --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json --sidecar-dir .runtime/local-demo/huperzine/candidate-package --out .runtime/local-demo/huperzine/dossier.md

campaign-status-demo:
	mkdir -p .runtime/local-demo/huperzine .runtime/local-demo/nootkatone
	python3 skills/bioprospector/scripts/bioprospector_campaign_status.py --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json --out .runtime/local-demo/huperzine/campaign-status.md --format markdown
	python3 skills/bioprospector/scripts/bioprospector_campaign_status.py --campaign skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json --out .runtime/local-demo/nootkatone/campaign-status.json

handoff-demo:
	python3 skills/bioprospector/scripts/bioprospector_handoff_packet.py --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json --out .runtime/local-demo/huperzine/handoff --prefix HUPERZINE --profile public-demo

agent-brief-demo:
	python3 skills/bioprospector/scripts/bioprospector_agent_brief.py --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json --out .runtime/local-demo/huperzine/agent-brief --prefix HUPERZINE --profile public-demo --mode goal --agent codex

retrospective-demo:
	mkdir -p .runtime/local-demo
	python3 skills/bioprospector/scripts/bioprospector_retrospective.py --root .runtime/local-demo --out .runtime/local-demo/retrospective-ledger.tsv --quiet

audit:
	python3 scripts/public_audit.py .

runtime-audit:
	if [ -d .runtime ]; then python3 scripts/public_audit.py .runtime; else echo "No .runtime directory to audit"; fi

clean-runtime:
	rm -rf .runtime
