#!/usr/bin/env bash
# Install skills to Cursor (.cursor/rules in current project)
# Cursor uses .cursor/rules/*.mdc files for rules
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="$(cd "$SCRIPT_DIR/../skills" && pwd)"
TARGET="${CURSOR_SKILLS_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.cursor/rules}"

mkdir -p "$TARGET"

convert_skill_to_mdc() {
    local skill_dir="$1"
    local skill_name="$2"
    local target_file="$TARGET/${skill_name}.mdc"

    # Read SKILL.md frontmatter and content
    local skill_file="$skill_dir/SKILL.md"
    if [[ ! -f "$skill_file" ]]; then
        return 1
    fi

    # Extract frontmatter
    local name=$(grep '^name:' "$skill_file" | head -1 | sed 's/name: *//')
    local description=$(grep '^description:' "$skill_file" | head -1 | sed 's/description: *//')
    local allowed_tools=$(grep '^allowed-tools:' "$skill_file" | head -1 | sed 's/allowed-tools: *//')

    # Generate .mdc file
    cat > "$target_file" <<EOF
---
description: $description
globs: []
alwaysApply: false
---
# Skill: $name

$(sed '1,/^---$/d' "$skill_file" | sed '1,/^---$/d')
EOF
}

if [[ $# -eq 0 ]]; then
    echo "Installing all skills to $TARGET"
    for skill_dir in "$SOURCE"/*/; do
        skill_name=$(basename "$skill_dir")
        echo "  → $skill_name"
        convert_skill_to_mdc "$skill_dir" "$skill_name"
    done
else
    for skill in "$@"; do
        if [[ -d "$SOURCE/$skill" ]]; then
            echo "  → $skill"
            convert_skill_to_mdc "$SOURCE/$skill" "$skill"
        else
            echo "  ! skill '$skill' not found" >&2
        fi
    done
fi

echo "Done. Skills installed as .mdc rules to $TARGET"