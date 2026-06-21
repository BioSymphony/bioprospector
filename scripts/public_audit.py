#!/usr/bin/env python3
"""Dependency-free public-release audit for the BioProspector foundation."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


SKIP_DIRS = {
    ".git",
    ".runtime",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
}

FORBIDDEN_DIR_NAMES = {
    "internal",
    "private",
    "local" + "-notes",
    "demo" + "-runs",
    "runs",
    "databases",
    "checkpoints",
    "cache",
}

FORBIDDEN_TRACKED_DIR_NAMES = FORBIDDEN_DIR_NAMES | {
    ".runtime",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "logs",
    "node_modules",
    "venv",
}

FORBIDDEN_TRACKED_NAME_PATTERNS = [
    re.compile(r"(?i)(?:^|[-_.])pod[-_]?id(?:[-_.]|$)"),
    re.compile(r"(?i)(?:create|pod|runpod).*response"),
    re.compile(r"(?i)(?:signed|presigned)[-_]?url"),
    re.compile(r"(?i)(?:secret|token|credential|registry[-_]?auth)"),
]

HEAVY_SUFFIXES = {
    ".fastq",
    ".fq",
    ".sra",
    ".bam",
    ".sam",
    ".cram",
    ".bt2",
    ".bt2l",
    ".dmnd",
    ".fa",
    ".faa",
    ".fasta",
    ".ffn",
    ".fna",
    ".pep",
    ".domtbl",
    ".gb",
    ".gbff",
    ".gbk",
    ".gff",
    ".gff3",
    ".gtf",
    ".aln",
    ".hmm",
    ".sto",
    ".pdb",
    ".cif",
    ".bcif",
    ".pin",
    ".phr",
    ".psq",
    ".nin",
    ".nhr",
    ".nsq",
}

FORBIDDEN_TEXT = [
    "/" + "Users" + "/",
    "github" + "_2",
    "jacob" + "vogan",
    "j" + "vogan",
    "local" + "-notes",
    "demo" + "-runs",
    "pod" + "-id",
    "network volume " + "id",
    "volume " + "id:",
    "elastic" + "-blast.log",
    "stricto" + "sidine",
    "Mitra" + "gyna",
    "symphony" + "-claude",
    "jacob" + "-cli",
    "vogan" + "linear",
    "linear" + ".app",
    "VO" + "G-",
    "proxy" + ".runpod.net",
    "s3" + "://jacob" + "vogan",
    "quarantined" + "_local_pointer_only",
    "huper" + "zine-heavy-artifacts",
]

FORBIDDEN_TEXT_CASE_INSENSITIVE = [
    "s" + "crub",
    "s" + "anitiz",
    "clean" + "-room",
    "clean" + " room",
]

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bASIA[0-9A-Z]{16}\b"),
    re.compile(r"\b" + "AIDA" + r"[0-9A-Z]{12,}\b"),
    re.compile(r"\b" + "AROA" + r"[0-9A-Z]{12,}\b"),
    re.compile(r"arn:aws:[^:\s]+::" + r"[0-9]{12}[:/]"),
    re.compile(r"(?i)\baws[_ -]?account(?:[_ -]?id)?\s*[:=]\s*['\"]?" + r"[0-9]{12}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"(?i)\b(?:aws_secret_access_key|secret_access_key)\s*=\s*[^ \n#<>{}$][^ \n#]*"),
    re.compile(r"(?i)\b(?:api[_-]?key|token|password)\s*=\s*['\"]?[A-Za-z0-9_./+=-]{24,}['\"]?"),
    re.compile(r"(?i)\bapi[_-]?key\s*:\s*(?!\$|<|REPLACE_ME|TRACKER_AUTH_ENV|env:)[A-Za-z0-9_./+=-]{8,}"),
]

S3_SCHEME = "s3" + "://"
S3_URI_PATTERN = re.compile(re.escape(S3_SCHEME) + r"[^ \t\r\n\"'<>),]+")
ALLOWED_S3_PREFIXES = (
    S3_SCHEME + "REPLACE_ME_OPERATOR_APPROVED_BUCKET",
    S3_SCHEME + "TODO-",
    S3_SCHEME + "example",
    S3_SCHEME + "bucket-name",
    S3_SCHEME + "your-bucket",
)

PROVIDER_IDENTIFIER_PATTERNS = [
    (
        "aws account id",
        re.compile(r"(?<![0-9A-Za-z])[0-9]{12}(?![0-9A-Za-z])"),
    ),
    (
        "provider id assignment",
        re.compile(
            r"(?i)\b(?:pod_id|pod[-_ ]id|runpod_pod_id|volume_id|volume[-_ ]id|"
            r"network_volume_id|network[-_ ]volume[-_ ]id)\b['\"]?\s*[:=]\s*['\"]?"
            r"(?!(?:<|REPLACE_ME|example|operator|redacted|unknown|null|none|not_|no_))"
            r"[A-Za-z0-9][A-Za-z0-9_-]{6,}"
        ),
    ),
    (
        "runpod proxy url",
        re.compile(r"(?i)\b[a-z0-9][a-z0-9-]*\.proxy\.runpod\.net\b"),
    ),
    (
        "private registry image assignment",
        re.compile(
            r"(?i)\b(?:image|image_ref|container_image|registry_image)\b\s*[:=]\s*['\"]?"
            r"(?!(?:REPLACE_ME|TODO|example|public|docker\.io/library|ghcr\.io/OWNER|<))"
            r"[a-z0-9][a-z0-9.-]+(?::[0-9]+)?/[a-z0-9_./-]+(?:[@:][a-z0-9_.:-]+)?"
        ),
    ),
]

MAX_FILE_BYTES = 1_000_000


def relpath(root: Path, path: Path) -> Path:
    try:
        return path.relative_to(root)
    except ValueError:
        return path


def iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        current = Path(dirpath)
        for name in sorted(filenames):
            yield current / name


def is_text(path: Path) -> bool:
    try:
        chunk = path.read_bytes()[:4096]
    except OSError:
        return False
    return b"\0" not in chunk


def git_tracked_files(root: Path) -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            check=False,
            capture_output=True,
        )
    except (OSError, ValueError):
        return []
    if result.returncode != 0 or not result.stdout:
        return []
    return [root / item.decode("utf-8", errors="replace") for item in result.stdout.split(b"\0") if item]


def scan_path_name(root: Path, path: Path, *, tracked: bool) -> list[str]:
    issues: list[str] = []
    rel = relpath(root, path)
    lower_name = path.name.lower()
    if any(lower_name.endswith(suffix) for suffix in HEAVY_SUFFIXES):
        issues.append(f"heavy/raw biological file extension: {rel}")
    if tracked:
        parts = set(rel.parts)
        forbidden_parts = sorted(parts & FORBIDDEN_TRACKED_DIR_NAMES)
        for part in forbidden_parts:
            issues.append(f"tracked forbidden directory component {part!r}: {rel}")
        for pattern in FORBIDDEN_TRACKED_NAME_PATTERNS:
            if pattern.search(str(rel)):
                issues.append(f"tracked forbidden filename pattern {pattern.pattern!r}: {rel}")
    return issues


def scan_file_content(root: Path, path: Path) -> list[str]:
    issues: list[str] = []
    rel = relpath(root, path)
    try:
        size = path.stat().st_size
    except OSError as exc:
        return [f"cannot stat {rel}: {exc}"]
    if size > MAX_FILE_BYTES:
        issues.append(f"file exceeds {MAX_FILE_BYTES} bytes: {rel} ({size} bytes)")
    if not is_text(path):
        return issues
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        issues.append(f"non-utf8 text-like file: {rel}")
        return issues
    for token in FORBIDDEN_TEXT:
        if token in text:
            issues.append(f"forbidden text {token!r}: {rel}")
    lower_text = text.lower()
    for token in FORBIDDEN_TEXT_CASE_INSENSITIVE:
        if token.lower() in lower_text:
            issues.append(f"forbidden text {token!r}: {rel}")
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            issues.append(f"possible secret pattern {pattern.pattern!r}: {rel}")
    for label, pattern in PROVIDER_IDENTIFIER_PATTERNS:
        if pattern.search(text):
            issues.append(f"possible provider identifier ({label}): {rel}")
    for match in S3_URI_PATTERN.finditer(text):
        uri = match.group(0)
        if not uri.startswith(ALLOWED_S3_PREFIXES):
            issues.append(f"non-placeholder S3 URI {uri!r}: {rel}")
    return issues


def scan(root: Path) -> list[str]:
    issues: list[str] = []

    for dirpath, dirnames, _filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        current = Path(dirpath)
        for name in dirnames:
            part = current / name
            if name in FORBIDDEN_DIR_NAMES:
                issues.append(f"forbidden directory: {part.relative_to(root)}")

    for path in iter_files(root):
        issues.extend(scan_path_name(root, path, tracked=False))
        issues.extend(scan_file_content(root, path))

    for path in git_tracked_files(root):
        issues.extend(scan_path_name(root, path, tracked=True))
        if path.exists():
            issues.extend(scan_file_content(root, path))

    return sorted(set(issues))


def main(argv: list[str]) -> int:
    root = Path(argv[1] if len(argv) > 1 else ".").resolve()
    issues = scan(root)
    if issues:
        print("FAIL public audit")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("PASS public audit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
