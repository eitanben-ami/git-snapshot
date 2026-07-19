from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def seed_repo(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / "note.txt").write_text("x", encoding="utf-8")
    subprocess.run(["git", "add", "note.txt"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "seed"], cwd=tmp_path, check=True, capture_output=True)


def test_cli_print() -> None:
    tmp_path = Path("/tmp/git-snapshot-cli-test-repo")
    if tmp_path.exists():
        import shutil
        shutil.rmtree(tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    seed_repo(tmp_path)

    outputs = subprocess.run(
        [sys.executable, "-m", "git_snapshot.cli", "--print", "--manifest", str(tmp_path)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(outputs.stdout)
    assert payload["branch"] == "main"
    assert payload["dirty"] is False
