#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
metadata = json.loads((root / "project.json").read_text(encoding="utf-8"))
required = ["README.md", "LICENSE", "project.json", "docs/wiring.md", "docs/test-plan.md", metadata["entrypoint"]]
missing = [item for item in required if not (root / item).is_file()]
if missing:
    raise SystemExit("Missing required files: " + ", ".join(missing))
if metadata["id"] <= 0 or not metadata["title"] or not metadata["repository_slug"]:
    raise SystemExit("Invalid project metadata")
if metadata["repository_slug"] not in (root / "README.md").read_text(encoding="utf-8"):
    # The title is required; slug presence is optional in prose.
    if metadata["title"] not in (root / "README.md").read_text(encoding="utf-8"):
        raise SystemExit("README does not identify the project")
print(f"validated {metadata['repository_slug']}")
