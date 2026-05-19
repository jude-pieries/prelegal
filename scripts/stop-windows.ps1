$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot
Write-Host "Stopping PreLegal..."
docker compose down
Write-Host "PreLegal stopped."
