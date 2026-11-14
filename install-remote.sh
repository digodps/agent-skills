#!/usr/bin/env bash
# Install skills from a remote repository URL.
# Usage: ./install-remote.sh <agent> <repo-url> [skill ...]
# Example:
#   ./install-remote.sh opencode https://github.com/digodps/agent-skills commit create-skill
#   ./install-remote.sh claude https://github.com/digodps/agent-skills --tag python
set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <agent> <repo-url> [skills...] [--tag tags]" >&2
    exit 1
fi

AGENT="$1"
REPO_URL="$2"
shift 2

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "Cloning $REPO_URL ..."
git clone --depth 1 "$REPO_URL" "$TMP/repo" >/dev/null 2>&1

exec python3 "$TMP/repo/install.py" "$AGENT" "$@"