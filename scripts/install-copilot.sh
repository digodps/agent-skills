#!/usr/bin/env bash
# Install skills to GitHub Copilot (.github/skills in current project)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="$(cd "$SCRIPT_DIR/../skills" && pwd)"
TARGET="${COPILOT_SKILLS_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.github/skills}"

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
echo "Add to .github/copilot-instructions.md or reference in prompts."