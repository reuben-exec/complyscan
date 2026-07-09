#!/usr/bin/env bash
# Render build script — frontend + backend
# Render Python image has nvm pre-installed in $HOME/.nvm
set -euo pipefail

echo "--- Installing Node.js via nvm ---"
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

nvm install 20
nvm use 20
echo "Node.js $(node --version), npm $(npm --version)"

echo "--- Building frontend ---"
cd frontend-next
npm ci
npm run build
cd ..

echo "--- Installing Python dependencies ---"
pip install -r requirements.txt

echo "--- Build complete ---"
