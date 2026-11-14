#!/usr/bin/env bash
# Install skills to Claude Code (~/.claude/skills)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="$(cd "$SCRIPT_DIR/../skills" && pwd)"
TARGET="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"

mkdir -p "$TARGET"

if [[ $# -eq 0 ]]; then
    echo "Installing all skills to $TARGET"
    cp -r "$SOURCE"/* "$TARGET/"
else
    for skill in "$@"; do
        if [[ -d "$SOURCE/$skill" ]]; then
            echo "  → $skill"
            rm -rf "$TARGET/$skill"
            cp -r "$SOURCE/$skill" "$TARGET/$skill"
        else
            echo "  ! skill '$skill' not found" >&2
        fi
    done
fi

echo "Done. Skills installed to $TARGET"