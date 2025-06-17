# PowerShell entry point for RunePyv3.1
# Sets working directory to the script's location and runs the main TileMap program.

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

# Prefer py launcher if available, fallback to python
if (Get-Command py -ErrorAction SilentlyContinue) {
    py TileMap.py
} else {
    python TileMap.py
}
