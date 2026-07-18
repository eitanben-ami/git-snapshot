from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from git_snapshot.cli import main


@pytest.fixture()
def git_repo(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "agent@test.local"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test Agent"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / "note.txt").write_text("hello", encoding="utf-8")
    subprocess.run(["git", "add", "note.txt"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "seed"], cwd=tmp_path, check=True, capture_output=True)
    return tmp_path


def test_help_prints_usage(git_repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    import os
    os.chdir(git_repo)
    code = main(["--help"])
    assert code == 0
    captured = capsys.readouterr()
    assert "Usage:" in captured.out


def test_print_outputs_json_manifest(git_repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    import os
    os.chdir(git_repo)
    code = main(["--print"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert isinstance(payload, dict)
    assert payload["branch"] == "main"
    assert payload["commit"] != "unknown"
    assert payload["dirty"] is False


def test_output_creates_file(git_repo: Path) -> None:
    import os
    os.chdir(git_repo)
    output_path = git_repo / "out" / "snapshot.json"
    code = main(["--output", str(output_path)])
    assert code == 0
    assert output_path.exists()
    assert json.loads(output_path.read_text(encoding="utf-8"))["dirty"] is False


def test_missing_output_argument_fails(git_repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    import os
    os.chdir(git_repo)
    code = main(["--output"])
    assert code == 1
    assert "path" in capsys.readouterr().err


def test_dirty_tree_returns_two(git_repo: Path) -> None:
    import os
    os.chdir(git_repo)
    (git_repo / "new.txt").write_text("new", encoding="utf-8")
    (git_repo / "note.txt").write_text("dirty", encoding="utf-8")
    code = main(["--print"])
    assert code == 2


def test_output_directory_fails(git_repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    import os
    os.chdir(git_repo)
    existing_dir = git_repo / "snapshot.json"
    existing_dir.mkdir(parents=True)
    code = main(["--output", str(existing_dir)])
    assert code == 1
    assert "directory" in capsys.readouterr().err
