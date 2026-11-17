#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT=8088

echo "[*] Iniciando INDD Forensic Studio & Converter (Offline Edition)..."
python3 "${SCRIPT_DIR}/web/server.py"
