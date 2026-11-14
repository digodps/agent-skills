#!/usr/bin/env bash
# Generate registry.json from skills directory
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/update-registry.py" "$@"