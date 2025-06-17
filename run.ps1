# PowerShell entry point for RunePyv3.1
# Sets working directory to the script's location and runs the game client.

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

# Prefer py launcher if available, fallback to python
if (Get-Command py -ErrorAction SilentlyContinue) {
    py client.py
} else {
    python client.py
}
