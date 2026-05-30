#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HERMES_DIR="${HOME}/.hermes"
SKILLS_DIR="${HERMES_DIR}/skills"
CONFIG="${HERMES_DIR}/config.yaml"
GODOT_BIN="${GODOT_BIN:-godot-4}"
HERMES_PIP="${HOME}/.hermes/hermes-agent/venv/bin/pip3"

echo "=== agent-tools install ==="
echo "Repo: ${REPO_DIR}"
echo ""

# 1. Copy skills
echo "[1/4] Copying skills..."
for skill_dir in "${REPO_DIR}/skills"/*/; do
    skill_name="$(basename "${skill_dir}")"
    # Skip empty skill directories (e.g. task-poller before migration)
    if [ -z "$(ls -A "${skill_dir}" 2>/dev/null)" ]; then
        echo "  skipping empty skill dir: ${skill_name}"
        continue
    fi
    dest="${SKILLS_DIR}/${skill_name}"
    mkdir -p "${dest}"
    cp -r "${skill_dir}"* "${dest}/"
    echo "  copied skill: ${skill_name}"
done

# 2. Install Godot MCP into Hermes venv
echo "[2/4] Installing Godot MCP into Hermes venv..."
"${HERMES_PIP}" install -e "${REPO_DIR}/mcps/godot/" --quiet
echo "  godot-mcp installed"

# 3. Register MCP in ~/.hermes/config.yaml
echo "[3/4] Registering Godot MCP in config.yaml..."
if [ ! -f "${CONFIG}" ]; then
    echo "  WARNING: ${CONFIG} not found — skipping MCP registration"
elif grep -q 'name: godot' "${CONFIG}" 2>/dev/null; then
    echo "  godot MCP already registered — skipping"
else
    if grep -q '^mcps:' "${CONFIG}"; then
        python3 - << 'PYEOF'
import re, os
config_path = os.path.expanduser("~/.hermes/config.yaml")
entry = """  - name: godot
    transport: stdio
    command: python
    args: ["-m", "godot_mcp.server"]
"""
content = open(config_path).read()
content = re.sub(r'^(mcps:\s*\n)', r'\1' + entry, content, flags=re.MULTILINE)
open(config_path, 'w').write(content)
print("  godot MCP registered in config.yaml")
PYEOF
    else
        cat >> "${CONFIG}" << 'YAMLEOF'

mcps:
  - name: godot
    transport: stdio
    command: python
    args: ["-m", "godot_mcp.server"]
YAMLEOF
        echo "  added mcps section with godot MCP"
    fi
fi

# 4. Verify Godot binary
echo "[4/4] Verifying Godot binary (${GODOT_BIN})..."
if "${GODOT_BIN}" --version >/dev/null 2>&1; then
    echo "  Godot OK: $("${GODOT_BIN}" --version 2>/dev/null)"
else
    echo "  WARNING: '${GODOT_BIN} --version' failed. Install Godot 4 or set GODOT_BIN."
fi

echo ""
echo "=== install complete ==="
