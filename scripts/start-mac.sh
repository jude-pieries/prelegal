#!/bin/bash
set -e
cd "$(dirname "$0")/.."
echo "Building and starting PreLegal..."
docker compose up --build -d
echo "PreLegal is running at http://localhost:8000"
