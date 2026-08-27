# git-snapshot

Repository: https://github.com/eitanben-ami/git-snapshot

A minimal CLI for capturing a reproducible repository snapshot manifest.

## About

`git-snapshot` writes a JSON manifest with the current branch, commit SHA, status summary, and changed files. It is useful for release audits, CI traceability, and quick debugging contexts where you need machine-readable repo state.

## Features

- Emits a single manifest file with high-signal git metadata.
- Defaults to `snapshot.json` in the current directory.
- Exposes a JSON manifest via stdout when reading input.
- Supports an optional output path override.
- Pure standard-library implementation with no runtime dependencies.

## Installation

Requires Python 3.10 or newer.

```bash
python -m pip install .
```

## Usage

```bash
# Create a snapshot manifest in the current repo
git-snapshot

# Write the manifest to a custom path
git-snapshot --output build/snapshot.json

# Preview a manifest in stdout
git-snapshot --print
```

## Project structure

```
git-snapshot/
  pyproject.toml
  README.md
  src/
    git_snapshot/
      __init__.py
      cli.py
      manifest.py
  tests/
    test_manifest.py
    test_cli.py
```

## License

MIT
