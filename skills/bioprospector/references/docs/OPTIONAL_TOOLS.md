# Optional tools

BioProspector itself depends only on Python 3.11+ and a POSIX shell. The
local doctor reports the availability of several optional tools that the
skill can use when present. None of them are required for the planning path
or release checks. Operators can use them for optional local or cloud search
lanes.

The doctor checks for these eight tools:

| Tool | What it enables in BioProspector |
| --- | --- |
| `aws` | AWS ElasticBLAST readiness review |
| `blastp` | Local NCBI BLAST sequence searches |
| `docker` | Containerized local workflows |
| `foldseek` | Structure-neighbor searches over predicted folds |
| `git` | Release hygiene and tracked-file checks |
| `hmmscan` | HMMER domain scans |
| `mmseqs` | Local sequence clustering and search |
| `runpodctl` | Operator-reviewed RunPod workflows |

These are starting points, not pinned environment specifications. Check each
project's current installation guide before use and record the installed
version in the campaign's execution proof.

## Install hints

### macOS

Install [Docker Desktop](https://docs.docker.com/desktop/setup/install/mac-install/)
if you need a local container engine. Then install the remaining tools with
Homebrew:

```bash
brew install git awscli
brew install blast hmmer mmseqs2 foldseek
brew install runpod/runpodctl/runpodctl
```

### Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install -y git awscli docker.io ncbi-blast+ hmmer
# mmseqs2: see https://github.com/soedinglab/MMseqs2
# foldseek: see https://github.com/steineggerlab/foldseek
# runpodctl: follow https://docs.runpod.io/runpodctl/overview
```

### Conda / Mamba

```bash
mamba install -c bioconda blast hmmer mmseqs2 foldseek
mamba install -c conda-forge runpodctl
```

Installing a provider CLI does not authorize credential configuration, resource
creation, or job submission from this repository.

## Verifying

After install, run the doctor:

```bash
python3 scripts/bioprospector_doctor.py --include-runtime
```

The doctor reports the count of available optional tools and which ones it
found on `PATH`. Missing tools are reported as optional and do not block
release checks.
