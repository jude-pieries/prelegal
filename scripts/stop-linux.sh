#!/bin/bash
cd "$(dirname "$0")/.."
echo "Stopping PreLegal..."
docker compose down
echo "PreLegal stopped."
