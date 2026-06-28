#!/usr/bin/env python3
"""Summarize a local BioProspector checkout with redacted local details."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]

KEY_FILES = [
    "README.md",
    "Makefile",
    "pyproject.toml",
    "docs/PUBLIC_RELEASE_PREP.md",
    "docs/PRIVACY_SECURITY_MODEL.md",
    "schemas/bioprospector-ledgers.json",
]


def run_git(path: Path, args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(
        ["git", *args],
        cwd=path,
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )
    return result.returncode, result.stdout, result.stderr


def display_path(path: Path, root: Path, *, show_absolute_paths: bool) -> str:
    resolved = path.resolve()
    if show_absolute_paths:
        return resolved.as_posix()
    for base in (root.resolve(), Path.cwd().resolve()):
        try:
            rel = resolved.relative_to(base)
        except ValueError:
            continue
        rendered = rel.as_posix()
        return rendered if rendered else "."
    return resolved.name


def parse_recent_commits(output: str, *, include_subjects: bool) -> list[dict[str, str]]:
    commits: list[dict[str, str]] = []
    for line in output.splitlines():
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        item = {"hash": parts[0], "date": parts[1]}
        if include_subjects:
            item["subject"] = parts[2]
        commits.append(item)
    return commits


def git_info(
    root: Path,
    *,
    max_commits: int,
    include_branch: bool,
    include_dirty_files: bool,
    include_commit_subjects: bool,
) -> dict[str, Any]:
    info: dict[str, Any] = {
        "exists": root.exists(),
        "is_git_repo": False,
        "branch": None,
        "head_hash": None,
        "clean": None,
        "dirty_count": None,
        "dirty_files": [],
        "ahead_main": None,
        "behind_main": None,
        "remote_count": None,
        "recent_commits": [],
        "warnings": [],
    }
    if not root.exists():
        info["warnings"].append("repo root does not exist")
        return info

    code, stdout, stderr = run_git(root, ["rev-parse", "--is-inside-work-tree"])
    if code != 0 or stdout.strip() != "true":
        info["warnings"].append(stderr.strip() or "not a git work tree")
        return info
    info["is_git_repo"] = True

    code, stdout, _ = run_git(root, ["rev-parse", "--abbrev-ref", "HEAD"])
    if code == 0 and include_branch:
        info["branch"] = stdout.strip()

    code, stdout, _ = run_git(root, ["rev-parse", "--short", "HEAD"])
    if code == 0:
        info["head_hash"] = stdout.strip()

    code, stdout, _ = run_git(root, ["status", "--porcelain"])
    if code == 0:
        dirty = [line for line in stdout.splitlines() if line.strip()]
        info["dirty_count"] = len(dirty)
        info["clean"] = len(dirty) == 0
        if include_dirty_files:
            info["dirty_files"] = dirty[:20]

    code, _, _ = run_git(root, ["rev-parse", "--verify", "main"])
    if code == 0:
        code, stdout, _ = run_git(root, ["rev-list", "--left-right", "--count", "main...HEAD"])
        if code == 0 and stdout.strip():
            pieces = stdout.strip().split()
            if len(pieces) == 2:
                info["behind_main"] = int(pieces[0])
                info["ahead_main"] = int(pieces[1])

    code, stdout, _ = run_git(root, ["remote"])
    if code == 0:
        info["remote_count"] = len([line for line in stdout.splitlines() if line.strip()])

    if max_commits > 0:
        code, stdout, _ = run_git(
            root,
            [
                "log",
                f"-n{max_commits}",
                "--date=iso-strict",
                "--pretty=format:%h\t%ad\t%s",
            ],
        )
        if code == 0:
            info["recent_commits"] = parse_recent_commits(stdout.strip(), include_subjects=include_commit_subjects)

    return info


def file_info(root: Path) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    for rel in KEY_FILES:
        path = root / rel
        item: dict[str, Any] = {"path": rel, "exists": path.exists()}
        if path.exists():
            item["size_bytes"] = path.stat().st_size
        files.append(item)
    return files


def runtime_info(root: Path, *, include_dirs: bool, max_dirs: int) -> dict[str, Any]:
    runtime = root / ".runtime"
    info: dict[str, Any] = {
        "exists": runtime.exists(),
        "top_level_dir_count": 0,
        "latest_dirs": [],
    }
    if not runtime.exists():
        return info
    dirs = [path for path in runtime.iterdir() if path.is_dir()]
    info["top_level_dir_count"] = len(dirs)
    if include_dirs:
        latest = sorted(dirs, key=lambda item: item.stat().st_mtime, reverse=True)[:max_dirs]
        info["latest_dirs"] = [
            {
                "path": path.relative_to(root).as_posix(),
                "modified_utc": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
            }
            for path in latest
        ]
    return info


def recommended_commands() -> list[dict[str, str]]:
    return [
        {
            "name": "doctor_with_runtime",
            "command": "python3 skills/bioprospector/scripts/bioprospector_doctor.py --include-runtime",
        },
        {
            "name": "release_check",
            "command": "make release-check",
        },
    ]


def compile_workspace_status(
    *,
    root: Path,
    max_commits: int = 3,
    max_runtime_dirs: int = 5,
    include_branch: bool = False,
    include_dirty_files: bool = False,
    include_runtime_dirs: bool = False,
    include_commit_subjects: bool = False,
    show_absolute_paths: bool = False,
) -> dict[str, Any]:
    root = root.resolve()
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "local_checkout_status",
        "remote_network_actions": "none",
        "redaction_defaults": {
            "absolute_paths": show_absolute_paths,
            "branch_name": include_branch,
            "dirty_file_names": include_dirty_files,
            "runtime_dir_names": include_runtime_dirs,
            "commit_subjects": include_commit_subjects,
        },
        "repo": {
            "root": display_path(root, root, show_absolute_paths=show_absolute_paths),
            "git": git_info(
                root,
                max_commits=max_commits,
                include_branch=include_branch,
                include_dirty_files=include_dirty_files,
                include_commit_subjects=include_commit_subjects,
            ),
            "runtime": runtime_info(root, include_dirs=include_runtime_dirs, max_dirs=max_runtime_dirs),
            "key_files": file_info(root),
        },
        "recommended_commands": recommended_commands(),
    }


def render_markdown(status: dict[str, Any]) -> str:
    repo = status["repo"]
    git = repo["git"]
    runtime = repo["runtime"]
    redaction = status["redaction_defaults"]
    lines = [
        "# BioProspector Workspace Status",
        "",
        f"- Generated UTC: `{status['generated_at_utc']}`",
        f"- Scope: `{status['scope']}`",
        f"- Remote/network actions: `{status['remote_network_actions']}`",
        f"- Absolute paths shown: `{redaction['absolute_paths']}`",
        f"- Branch name shown: `{redaction['branch_name']}`",
        f"- Dirty file names shown: `{redaction['dirty_file_names']}`",
        f"- Runtime directory names shown: `{redaction['runtime_dir_names']}`",
        f"- Commit subjects shown: `{redaction['commit_subjects']}`",
        "",
        "## Repository",
        "",
        f"- Root: `{repo['root']}`",
        f"- Git repo: `{git['is_git_repo']}`",
        f"- Branch: `{git.get('branch') or 'n/a'}`",
        f"- HEAD: `{git.get('head_hash') or 'n/a'}`",
        f"- Clean: `{git.get('clean')}`",
        f"- Dirty count: `{git.get('dirty_count')}`",
        f"- Ahead/behind main: `{git.get('ahead_main')}/{git.get('behind_main')}`",
        f"- Remotes configured: `{git.get('remote_count')}`",
    ]
    for warning in git.get("warnings") or []:
        lines.append(f"- Warning: {warning}")
    if git.get("dirty_files"):
        lines.append("- Dirty file preview:")
        for dirty_file in git["dirty_files"]:
            lines.append(f"  - `{dirty_file}`")

    lines.extend(["", "## Recent Commits", ""])
    commits = git.get("recent_commits") or []
    if not commits:
        lines.append("- none")
    for commit in commits:
        suffix = f" {commit['subject']}" if "subject" in commit else ""
        lines.append(f"- `{commit['hash']}` ({commit['date']}){suffix}")

    lines.extend(
        [
            "",
            "## Runtime Sidecars",
            "",
            f"- `.runtime` exists: `{runtime['exists']}`",
            f"- Top-level runtime dirs: `{runtime['top_level_dir_count']}`",
        ]
    )
    for item in runtime.get("latest_dirs") or []:
        lines.append(f"- `{item['path']}` ({item['modified_utc']})")

    lines.extend(["", "## Key Files", ""])
    for item in repo["key_files"]:
        suffix = f", {item['size_bytes']} bytes" if item.get("exists") else ""
        lines.append(f"- `{item['path']}` exists=`{item['exists']}`{suffix}")

    lines.extend(["", "## Suggested Commands", ""])
    for item in status["recommended_commands"]:
        lines.append(f"- `{item['name']}`: `{item['command']}`")
    lines.append("")
    return "\n".join(lines)


def write_output(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT, help="BioProspector checkout root")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    parser.add_argument("--out", type=Path, help="Optional output path; stdout is used when omitted")
    parser.add_argument("--max-commits", type=int, default=3)
    parser.add_argument("--max-runtime-dirs", type=int, default=5)
    parser.add_argument("--show-branch", action="store_true", help="Include the current git branch name")
    parser.add_argument("--show-dirty-files", action="store_true", help="Include git status filenames")
    parser.add_argument("--show-runtime-dirs", action="store_true", help="Include latest .runtime directory names")
    parser.add_argument("--show-commit-subjects", action="store_true", help="Include recent commit subjects")
    parser.add_argument("--show-absolute-paths", action="store_true", help="Include absolute checkout paths")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    status = compile_workspace_status(
        root=args.repo_root,
        max_commits=args.max_commits,
        max_runtime_dirs=args.max_runtime_dirs,
        include_branch=args.show_branch,
        include_dirty_files=args.show_dirty_files,
        include_runtime_dirs=args.show_runtime_dirs,
        include_commit_subjects=args.show_commit_subjects,
        show_absolute_paths=args.show_absolute_paths,
    )
    if args.format == "json":
        output = json.dumps(status, indent=2, sort_keys=True) + "\n"
    else:
        output = render_markdown(status)
    if args.out:
        write_output(args.out, output)
    else:
        print(output, end="" if output.endswith("\n") else "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
