# Generate Sample Context Files for Testing
# Creates representative sample context files demonstrating different migration scenarios

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Write-Host "Generating sample context files..."
Write-Host "Project root: $ProjectRoot"

# Change to project root
Set-Location $ProjectRoot

# Check if python is available
try {
    $null = Get-Command python -ErrorAction Stop
    $pythonCmd = "python"
} catch {
    try {
        $null = Get-Command python3 -ErrorAction Stop
        $pythonCmd = "python3"
    } catch {
        Write-Host "Error: python is not installed or not in PATH." -ForegroundColor Red
        exit 1
    }
}

# Run the generator script
& $pythonCmd tests/generate_sample_data.py $args

Write-Host ""
Write-Host "Sample files are in: examples/context_files/"
