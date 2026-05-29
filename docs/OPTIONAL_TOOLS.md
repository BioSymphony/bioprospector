# Optional Tools

BioProspector itself depends only on Python 3.11+ and a POSIX shell. The
local doctor reports the availability of several optional tools that the
skill can use when present. None of them are required for the planning path
or release checks; they unlock more lanes when an operator decides to run
real local or cloud searches.

The doctor checks for these eight tools:

| Tool | What it enables in BioProspector |
| --- | --- |
| `aws` | AWS ElasticBLAST readiness review and bucket auth checks |
| `blastp` | Local NCBI BLAST sequence searches |
| `docker` | Containerized local workflows |
| `foldseek` | Structure-neighbor searches over predicted folds |
| `git` | Release hygiene and tracked-file checks |
| `hmmscan` | HMMER domain scans |
| `mmseqs` | Local sequence clustering and search |
| `runpodctl` | Operator-reviewed RunPod workflows |

## Install Hints

### macOS (Homebrew)

```bash
brew install git awscli docker
brew install blast hmmer mmseqs2 foldseek
# runpodctl: see https://github.com/runpod/runpodctl
```

### Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install -y git awscli docker.io ncbi-blast+ hmmer
# mmseqs2: see https://github.com/soedinglab/MMseqs2
# foldseek: see https://github.com/steineggerlab/foldseek
# runpodctl: see https://github.com/runpod/runpodctl
```

### Conda / Mamba

```bash
mamba install -c bioconda blast hmmer mmseqs2 foldseek
```

## Verifying

After install, run the doctor:

```bash
python3 skills/bioprospector/scripts/bioprospector_doctor.py --include-runtime
```

The doctor reports the count of available optional tools and which ones it
found on `PATH`. Missing tools are reported as optional and do not block
release checks.
