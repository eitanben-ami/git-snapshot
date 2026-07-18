from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from git_snapshot.manifest import collect


def _resolve_output(path: str | None) -> Path | None:
    if path is None:
        return Path.cwd() / "snapshot.json"
    return Path(path).expanduser().resolve()


def print_manifest(manifest_path: Path | None = None) -> int:
    manifest = collect(manifest_path)
    print(json.dumps(manifest.to_dict(), indent=2))
    return 0 if not manifest.dirty else 2


def save_manifest(output: str | None = None, manifest_path: Path | None = None) -> int:
    path = _resolve_output(output)
    if path.exists() and path.is_dir():
        print(f"output is a directory: {path}", file=sys.stderr)
        return 1

    manifest = collect(manifest_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest.to_dict(), indent=2) + os.linesep, encoding="utf-8")
    print(path)
    return 0 if not manifest.dirty else 2


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    output: str | None = None
    do_print = False
    manifest_path: Path | None = None

    args = argv[:]
    while args:
        arg = args.pop(0)
        if arg in {"-h", "--help"}:
            print("Usage: git-snapshot [--output PATH] [--print] [--manifest PATH]")
            return 0
        if arg == "--print":
            do_print = True
        elif arg == "--output":
            if not args:
                print("--output requires a path", file=sys.stderr)
                return 1
            output = args.pop(0)
        elif arg == "--manifest":
            if not args:
                print("--manifest requires a path", file=sys.stderr)
                return 1
            manifest_path = Path(args.pop(0)).expanduser().resolve()
        elif arg.startswith("-"):
            print(f"unknown option: {arg}", file=sys.stderr)
            return 1
        else:
            print(f"unexpected positional argument: {arg}", file=sys.stderr)
            return 1

    if do_print:
        return print_manifest(manifest_path)
    return save_manifest(output, manifest_path)


if __name__ == "__main__":
    raise SystemExit(main())
