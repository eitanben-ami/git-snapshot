from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class SnapshotManifest:
    path: Path
    branch: str
    commit: str
    dirty: bool
    added: List[str]
    removed: List[str]
    modified: List[str]
    staged: List[str]
    untracked: List[str]

    def to_dict(self) -> dict:
        return {
            "path": str(self.path),
            "branch": self.branch,
            "commit": self.commit,
            "dirty": self.dirty,
            "added": self.added,
            "removed": self.removed,
            "modified": self.modified,
            "staged": self.staged,
            "untracked": self.untracked,
        }


def _run(args: List[str], cwd: Path, check: bool = True) -> str:
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=check)
    return result.stdout


def _safe_run(args: List[str], cwd: Path) -> str:
    try:
        return _run(args, cwd=cwd)
    except subprocess.CalledProcessError:
        return ""


def _normalize(paths: List[str]) -> List[str]:
    seen: set[str] = set()
    normalized: List[str] = []
    for path in paths:
        if path not in seen:
            seen.add(path)
            normalized.append(path)
    return normalized


def collect(working_dir: Path | None = None) -> SnapshotManifest:
    cwd = working_dir or Path.cwd()
    branch = (
        _safe_run(["git", "branch", "--show-current"], cwd=cwd) or "unknown"
    ).strip()
    commit = (
        _safe_run(["git", "rev-parse", "--short=12", "HEAD"], cwd=cwd) or "unknown"
    ).strip()

    raw = _safe_run(["git", "status", "--porcelain"], cwd=cwd)
    diff_lines = raw.splitlines()

    added: List[str] = []
    removed: List[str] = []
    modified: List[str] = []
    staged: List[str] = []
    untracked: List[str] = []

    for line in diff_lines:
        if not line:
            continue
        status = line[:2]
        path = line[3:].strip()
        xy = status.strip()
        for symbol in xy:
            if symbol == "?":
                untracked.append(path)
            elif symbol == "A":
                added.append(path)
            elif symbol == "D":
                removed.append(path)
            elif symbol == "M":
                modified.append(path)
        if status == "M ":
            staged.append(path)
        if status == "A ":
            staged.append(path)
        if status == "R ":
            pass
        if status == "D ":
            staged.append(path)
        if status == "C ":
            pass

    dirty = bool(added or removed or modified or staged or untracked)
    return SnapshotManifest(
        path=cwd,
        branch=branch,
        commit=commit,
        dirty=dirty,
        added=_normalize(added),
        removed=_normalize(removed),
        modified=_normalize(modified),
        staged=_normalize(staged),
        untracked=_normalize(untracked),
    )
