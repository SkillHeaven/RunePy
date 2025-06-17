# PowerShell entry point for RunePyv3.1

# Try the py launcher first
$launcher = Get-Command py -ErrorAction SilentlyContinue
if ($launcher) {
    & py -3 TileMap.py
    return
}

# Fall back to python on PATH
$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    & python TileMap.py
    return
}

Write-Host "Python 3 is required but was not found in PATH." -ForegroundColor Red
