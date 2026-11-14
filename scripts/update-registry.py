#!/usr/bin/env python3
"""Generate registry.json from skills directory."""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
OUT = ROOT / "registry.json"

TAG_RULES = [
    (r"python", ["python", "backend"]),
    (r"typescript|javascript|nodejs", ["javascript", "frontend"]),
    (r"rust", ["rust", "backend"]),
    (r"go-|golang|go-concurrency", ["go", "backend"]),
    (r"java", ["java", "backend"]),
    (r"csharp|dotnet", ["csharp", "backend"]),
    (r"ruby", ["ruby", "backend"]),
    (r"php", ["php", "backend"]),
    (r"django|fastapi", ["python", "backend", "api"]),
    (r"flutter|react-native|ios|mobile", ["mobile", "frontend"]),
    (r"react|nextjs|frontend", ["frontend", "react"]),
    (r"backend|architect|api", ["backend", "architecture"]),
    (r"security", ["security"]),
    (r"test", ["testing"]),
    (r"deploy|docker|ci", ["devops", "deployment"]),
    (r"openspec|egm", ["openspec", "workflow"]),
    (r"mcp", ["mcp", "tools"]),
]


def frontmatter(text: str) -> dict:
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    data = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "\t", "-")):
            key, _, val = line.partition(":")
            data[key.strip()] = val.strip().strip('"').strip("'")
    return data


def infer_tags(name: str) -> list[str]:
    for pattern, tags in TAG_RULES:
        if re.search(pattern, name):
            return tags
    return ["general"]


def main() -> int:
    if not SKILLS.is_dir():
        print(f"missing skills dir: {SKILLS}", file=sys.stderr)
        return 1

    skills = []
    for d in sorted(SKILLS.iterdir()):
        skill_md = d / "SKILL.md"
        if not d.is_dir() or not skill_md.is_file():
            continue
        fm = frontmatter(skill_md.read_text(encoding="utf-8"))
        skills.append({
            "name": d.name,
            "display_name": fm.get("name", d.name),
            "description": fm.get("description", ""),
            "allowed_tools": fm.get("allowed-tools", "Bash(*)"),
            "license": fm.get("license", "MIT"),
            "author": fm.get("author", ""),
            "version": fm.get("version", "1.0"),
            "tags": infer_tags(d.name),
        })

    registry = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "count": len(skills),
        "skills": skills,
    }
    OUT.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Registry generated: {OUT}")
    print(f"Skills indexed: {len(skills)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())