#!/usr/bin/env python3
"""
Scan `tools/external/` and produce a categorized inventory of projects
and helper scripts. Output JSON and a human-readable markdown summary.

Usage:
  python scripts/tools_inventory.py --root tools/external --out tools/external_inventory.json

"""
import argparse
import json
from pathlib import Path


def detect_project_type(path: Path):
    names = {p.name for p in path.rglob("*") if p.is_file()}
    if any(n in names for n in ("flake.nix", "default.nix")):
        return "nix-project"
    if any("nvim" in n or "neovim" in n or n.endswith(".vim") for n in names):
        return "neovim-plugin"
    if any(n.endswith(".sh") or n.endswith(".py") or n.endswith(".pl") for n in names):
        return "script-collection"
    return "misc"


def summarize_repo(path: Path):
    return {
        "name": path.name,
        "path": str(path),
        "type": detect_project_type(path),
        "files": [str(p.relative_to(path)) for p in path.iterdir() if p.is_file()],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="tools/external")
    parser.add_argument("--out", default="tools/external_inventory.json")
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f"Root path does not exist: {root}")
        raise SystemExit(1)

    repos = [p for p in root.iterdir() if p.is_dir()]
    inventory = {"root": str(root), "repos": []}

    for repo in repos:
        try:
            inventory["repos"].append(summarize_repo(repo))
        except Exception as e:
            inventory["repos"].append({"name": repo.name, "path": str(repo), "error": str(e)})

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(inventory, indent=2))

    # Also produce a quick markdown summary
    md = [f"# Tools inventory for `{root}`\n"]
    for r in inventory["repos"]:
        md.append(f"## {r.get('name')} — {r.get('type', 'unknown')}\n")
        md.append(f"Path: `{r.get('path')}`\n")
        files = r.get("files") or []
        if files:
            md.append("Files:\n")
            for f in files[:20]:
                md.append(f"- {f}\n")
        md.append("\n")

    md_path = out_path.with_suffix(".md")
    md_path.write_text("\n".join(md))
    print(f"Wrote {out_path} and {md_path}")


if __name__ == "__main__":
    main()
