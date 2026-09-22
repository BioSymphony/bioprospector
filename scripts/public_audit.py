#!/usr/bin/env python3
"""Dependency-free public-release audit for the BioProspector foundation."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from html import unescape
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlsplit


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
    re.compile(r"(?i)(?:^|/)\.env(?:$|[._-])"),
    re.compile(r"(?i)(?:^|/)(?:\.envrc|\.netrc|\.pypirc|\.npmrc|\.git-credentials)$"),
    re.compile(r"(?i)(?:^|/)(?:id_(?:rsa|dsa|ecdsa|ed25519)|[^/]+\.(?:pem|key|p12|pfx|jks|keystore))$"),
    re.compile(
        r"(?i)(?:^|/)(?:credentials?|service[-_]?account|auth[-_]?export)[^/]*\.(?:json|ya?ml|ini|toml)$"
    ),
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

MODEL_SUFFIXES = {
    ".safetensors", ".pt", ".pth", ".ckpt", ".onnx", ".gguf",
    ".bin", ".h5", ".hdf5", ".msgpack", ".tflite", ".index",
}
ARCHIVE_SUFFIXES = {".gz", ".bz2", ".xz", ".zst", ".zip", ".tar", ".7z", ".bgz", ".lz4", ".tgz"}
URL_PATTERN = re.compile(
    r"(?:(?:https?|s3|gs|file):)?/" r"/(?!Users/|home/)[^\s<>\"'`]+", re.IGNORECASE
)
SENSITIVE_QUERY_KEYS = {
    "access_token", "api_key", "apikey", "token", "password",
    "jwt", "auth_token", "credential", "credentials", "bearer",
    "x-amz-signature", "x-amz-credential", "x-amz-security-token",
    "x-goog-signature", "x-goog-credential", "signature", "sig",
}

FORBIDDEN_TEXT = [
    "local" + "-notes",
    "demo" + "-runs",
    "pod" + "-id",
    "network volume " + "id",
    "volume " + "id:",
    "elastic" + "-blast.log",
    "proxy" + ".runpod.net",
]

FORBIDDEN_TEXT_CASE_INSENSITIVE = [
    "s" + "crub",
    "s" + "anitiz",
    "clean" + "-room",
    "clean" + " room",
]

PRIVATE_PATH_PATTERNS = [
    (
        "absolute POSIX user-home path",
        re.compile(r"(?<![A-Za-z0-9])/(?:Users|home)/[^/\s\"'<>]+(?:/|(?=$|[\s\"'<>),.;:]))"),
    ),
    (
        "absolute Windows user-home path",
        re.compile(r"(?i)\b[A-Z]:\\Users\\[^\\\s\"'<>]+\\"),
    ),
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
ALLOWED_S3_BUCKETS = {"REPLACE_ME_OPERATOR_APPROVED_BUCKET", "TODO-", "example", "bucket-name", "your-bucket"}

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
    if path.is_symlink():
        issues.append(f"symbolic link is not allowed in public artifacts: {rel}")
        return issues
    lower_name = path.name.lower()
    suffixes = set(Path(lower_name).suffixes)
    if suffixes & ARCHIVE_SUFFIXES:
        issues.append(f"archive requires external storage: {rel}")
    if suffixes & HEAVY_SUFFIXES:
        issues.append(f"heavy/raw biological file extension: {rel}")
    if suffixes & MODEL_SUFFIXES:
        issues.append(f"model artifact extension: {rel}")
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
    url_text = unescape(text.replace(r"\/", "/"))
    non_url_text = URL_PATTERN.sub(" ", url_text)
    for label, pattern in PRIVATE_PATH_PATTERNS:
        if pattern.search(non_url_text):
            issues.append(f"possible private path ({label}): {rel}")
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            issues.append(f"possible secret pattern {pattern.pattern!r}: {rel}")
    for label, pattern in PROVIDER_IDENTIFIER_PATTERNS:
        if pattern.search(text):
            issues.append(f"possible provider identifier ({label}): {rel}")
    for match in S3_URI_PATTERN.finditer(text):
        uri = match.group(0)
        try:
            allowed = urlsplit(uri).netloc in ALLOWED_S3_BUCKETS
        except ValueError:
            allowed = False
        if not allowed:
            issues.append(f"non-placeholder S3 URI: {rel}")
    for match in URL_PATTERN.finditer(url_text):
        try:
            parsed = urlsplit(match.group(0))
            if parsed.username is not None or parsed.password is not None:
                issues.append(f"URL contains credentials: {rel}")
            fields = parse_qsl(parsed.query.replace(";", "&"), keep_blank_values=True)
            fields += parse_qsl(parsed.fragment.replace(";", "&"), keep_blank_values=True)
            keys = {key.lower() for key, _ in fields}
            if keys & SENSITIVE_QUERY_KEYS:
                issues.append(f"URL contains authentication or signature parameters: {rel}")
            decoded_path = unquote(parsed.path)
            # /home is also a common public website route, unlike a file URL.
            locations = [unquote(value) for _, value in fields]
            if parsed.scheme == "file" or not decoded_path.startswith("/home/"):
                locations.append(decoded_path)
            if any(pattern.search(value) for value in locations for _, pattern in PRIVATE_PATH_PATTERNS):
                issues.append(f"URL contains a private path: {rel}")
        except ValueError:
            issues.append(f"malformed URL requires review: {rel}")
    return issues


def scan(root: Path) -> list[str]:
    issues: list[str] = []

    for dirpath, dirnames, _filenames in os.walk(root):
        current = Path(dirpath)
        all_dirnames = sorted(dirnames)
        for name in all_dirnames:
            part = current / name
            issues.extend(scan_path_name(root, part, tracked=False))
            if name in FORBIDDEN_DIR_NAMES:
                issues.append(f"forbidden directory: {part.relative_to(root)}")
        dirnames[:] = [
            name for name in all_dirnames if name not in SKIP_DIRS and not (current / name).is_symlink()
        ]

    for path in iter_files(root):
        issues.extend(scan_path_name(root, path, tracked=False))
        if not path.is_symlink():
            issues.extend(scan_file_content(root, path))

    for path in git_tracked_files(root):
        issues.extend(scan_path_name(root, path, tracked=True))
        if path.exists() and not path.is_symlink():
            issues.extend(scan_file_content(root, path))

    return sorted(set(issues))


def main(argv: list[str]) -> int:
    root_arg = Path(argv[1] if len(argv) > 1 else ".")
    if root_arg.is_symlink():
        print("FAIL public audit")
        print("- audit root is a symbolic link; pass a real directory")
        return 1
    root = root_arg.resolve()
    issues = scan(root)
    if issues:
        print("FAIL public audit")
        for issue in issues:
            print(f"- {issue}")
        print("Remove or replace every listed item, then rerun the audit.")
        return 1
    print("PASS public audit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
