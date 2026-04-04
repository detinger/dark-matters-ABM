#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

cd "$BACKEND_DIR"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

cd "$FRONTEND_DIR"
npm install

if [[ -f .env.example && ! -f .env ]]; then
  cp .env.example .env
fi

if grep -q '^VITE_API_BASE=' .env 2>/dev/null; then
  sed -i '' 's#^VITE_API_BASE=.*#VITE_API_BASE=http://localhost:8000/api#' .env
else
  echo 'VITE_API_BASE=http://localhost:8000/api' >> .env
fi

echo "Local setup complete."