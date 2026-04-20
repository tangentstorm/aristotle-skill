# Build aristotle-lean.plugin from the repo root.
# Produces .\aristotle-lean.plugin (a zip of .claude-plugin/ + skills/ + README.md + LICENSE).
$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$manifest = Get-Content ".claude-plugin\plugin.json" -Raw | ConvertFrom-Json
$name = $manifest.name
$out = "$name.plugin"

if (Test-Path $out) { Remove-Item $out }

Compress-Archive -Path ".claude-plugin", "skills", "README.md", "LICENSE" -DestinationPath $out

Write-Host "Built: $out"
