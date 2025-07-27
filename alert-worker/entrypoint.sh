#!/usr/bin/env sh
set -e

echo "[INFO] Initialisation de la base..."
uv run python -m app.init_db || echo "[WARN] DB déjà initialisée"

echo "[INFO] Démarrage du worker..."
uv run python -u app/worker.py
