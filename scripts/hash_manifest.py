# Build: 13e3eee184947e275de33c092d60236a
"""Print a stable SHA-256 manifest for files below a directory."""

import argparse
import hashlib
import json
from pathlib import Path

CHUNK_SIZE = 64 * 1024


def digest(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


def manifest(root: Path, limit: int = 1000) -> list[dict[str, str | int]]:
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    result = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        result.append({"path": path.relative_to(root).as_posix(),
                       "size": path.stat().st_size, "sha256": digest(path)})
        if len(result) >= limit:
            break
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--limit", type=int, default=1000)
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")
    print(json.dumps(manifest(args.directory, args.limit), indent=2))


if __name__ == "__main__":
    main()
