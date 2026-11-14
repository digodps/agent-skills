#!/usr/bin/env python3
"""Universal skill installer for AI coding agents."""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILLS = ROOT / "skills"
REGISTRY = ROOT / "registry.json"

AGENTS = {
    "opencode": Path.home() / ".config" / "opencode" / "skills",
    "claude": Path.home() / ".claude" / "skills",
    "copilot": None,  # project-local
    "cursor": None,   # project-local
}


def get_project_root() -> Path:
    try:
        return Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
    except subprocess.CalledProcessError:
        return Path.cwd()


def resolve_target(agent: str) -> Path:
    target = AGENTS.get(agent)
    if target:
        return target
    if agent == "copilot":
        return get_project_root() / ".github" / "skills"
    if agent == "cursor":
        return get_project_root() / ".cursor" / "rules"
    return get_project_root() / agent / "skills"


def load_registry() -> dict:
    if not REGISTRY.exists():
        subprocess.run([sys.executable, ROOT / "scripts" / "update-registry.py"], check=True)
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def filter_skills(registry: dict, skills: list[str], tags: list[str]) -> list[str]:
    if skills:
        return [s for s in skills if any(s == sk["name"] for sk in registry["skills"])]
    if tags:
        tag_set = set(tags)
        return [sk["name"] for sk in registry["skills"] if tag_set & set(sk["tags"])]
    return [sk["name"] for sk in registry["skills"]]


def install_opencode(target: Path, skill_names: list[str]):
    target.mkdir(parents=True, exist_ok=True)
    for name in skill_names:
        src = SKILLS / name
        if src.exists():
            dst = target / name
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"  → {name}")
        else:
            print(f"  ! {name} not found", file=sys.stderr)


def install_claude(target: Path, skill_names: list[str]):
    target.mkdir(parents=True, exist_ok=True)
    for name in skill_names:
        src = SKILLS / name
        if src.exists():
            dst = target / name
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"  → {name}")
        else:
            print(f"  ! {name} not found", file=sys.stderr)


def install_copilot(target: Path, skill_names: list[str]):
    target.mkdir(parents=True, exist_ok=True)
    for name in skill_names:
        src = SKILLS / name
        if src.exists():
            dst = target / name
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"  → {name}")
        else:
            print(f"  ! {name} not found", file=sys.stderr)
    print(f"  Add to .github/copilot-instructions.md or reference in prompts")


def install_cursor(target: Path, skill_names: list[str]):
    target.mkdir(parents=True, exist_ok=True)
    for name in skill_names:
        src = SKILLS / name
        skill_md = src / "SKILL.md"
        if not src.exists() or not skill_md.exists():
            print(f"  ! {name} not found", file=sys.stderr)
            continue
        text = skill_md.read_text(encoding="utf-8")
        fm = {}
        m = __import__("re").match(r"---\s*\n(.*?)\n---", text, __import__("re").S)
        if m:
            for line in m.group(1).splitlines():
                if ":" in line and not line.startswith((" ", "\t", "-")):
                    k, _, v = line.partition(":")
                    fm[k.strip()] = v.strip().strip('"').strip("'")
        desc = fm.get("description", "")
        content = text[m.end():] if m else text
        mdc = target / f"{name}.mdc"
        mdc.write_text(
            f"---\ndescription: {desc}\nglobs: []\nalwaysApply: false\n---\n# Skill: {name}\n\n{content}",
            encoding="utf-8",
        )
        print(f"  → {name}.mdc")


def main():
    parser = argparse.ArgumentParser(description="Install skills to AI coding agents")
    parser.add_argument("agent", choices=["opencode", "claude", "copilot", "cursor", "all"])
    parser.add_argument("skills", nargs="*", help="Specific skills to install")
    parser.add_argument("--tag", action="append", help="Filter by tag (repeatable)")
    parser.add_argument("--list", action="store_true", help="List available skills")
    parser.add_argument("--list-tags", action="store_true", help="List all tags")
    args = parser.parse_args()

    registry = load_registry()

    if args.list:
        for sk in registry["skills"]:
            print(f"{sk['name']:30} {sk['description'][:60]}  tags: {', '.join(sk['tags'])}")
        return

    if args.list_tags:
        all_tags = set()
        for sk in registry["skills"]:
            all_tags.update(sk["tags"])
        print("\n".join(sorted(all_tags)))
        return

    targets = []
    if args.agent == "all":
        targets = ["opencode", "claude", "copilot", "cursor"]
    else:
        targets = [args.agent]

    skill_names = filter_skills(registry, args.skills, args.tag or [])

    if not skill_names:
        print("No skills matched", file=sys.stderr)
        return 1

    for agent in targets:
        target = resolve_target(agent)
        print(f"\n=== {agent} -> {target} ===")
        if agent == "opencode":
            install_opencode(target, skill_names)
        elif agent == "claude":
            install_claude(target, skill_names)
        elif agent == "copilot":
            install_copilot(target, skill_names)
        elif agent == "cursor":
            install_cursor(target, skill_names)

    print(f"\nDone. Installed {len(skill_names)} skills to {len(targets)} agent(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())