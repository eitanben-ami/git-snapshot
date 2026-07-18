from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from git_snapshot.manifest import collect


@pytest.fixture()
def git_repo(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "agent@test.local"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test Agent"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / "note.txt").write_text("x", encoding="utf-8")
    subprocess.run(["git", "add", "note.txt"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "seed"], cwd=tmp_path, check=True, capture_output=True)
    return tmp_path


def test_clean_tree(git_repo: Path) -> None:
    manifest = collect(git_repo)
    assert manifest.branch == "main"
    assert manifest.commit != "unknown"
    assert manifest.dirty is False
    assert manifest.added == []
    assert manifest.removed == []
    assert manifest.modified == []
    assert manifest.staged == []
    assert manifest.untracked == []


def test_dirty_tree_has_changes(git_repo: Path) -> None:
    target = git_repo / "note.txt"
    target.write_text("mutated", encoding="utf-8")
    (git_repo / "fresh.txt").write_text("untracked", encoding="utf-8")

    manifest = collect(git_repo)
    assert manifest.dirty is True
    assert "note.txt" in manifest.modified
    assert "fresh.txt" in manifest.untracked


def test_added_and_removed_files(git_repo: Path) -> None:
    (git_repo / "added.txt").write_text("new", encoding="utf-8")
    subprocess.run(["git", "add", "added.txt"], cwd=git_repo, check=True, capture_output=True)
    target = git_repo / "note.txt"
    target.unlink()

    manifest = collect(git_repo)
    assert "added.txt" in manifest.added
    assert "note.txt" in manifest.removed


def test_manifest_serialization(git_repo: Path) -> None:
    manifest = collect(git_repo)
    payload = manifest.to_dict()
    assert set(payload) == {
        "path",
        "branch",
        "commit",
        "dirty",
        "added",
        "removed",
        "modified",
        "staged",
        "untracked",
    }


def test_output_is_deduplicated(git_repo: Path) -> None:
    subprocess.run(["git", "add", "note.txt"], cwd=git_repo, check=True, capture_output=True)
    (git_repo / "fresh.txt").write_text("untracked", encoding="utf-8")
    (git_repo / "also.txt").write_text("untracked also", encoding="utf-8")
    manifest = collect(git_repo)
    values = manifest.untracked
    assert len(values) == len(set(values))
    assert set(values) == {"also.txt", "fresh.txt"}
