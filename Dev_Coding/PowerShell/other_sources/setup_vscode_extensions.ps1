param(
    [string]$ExtensionsFile
)

$ErrorActionPreference = "Stop"

# Resolve extensions.txt relative to the script folder (or current directory if pasted interactively)
if (-not $ExtensionsFile) {
    $baseDir = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }
    $ExtensionsFile = Join-Path $baseDir "extensions.txt"
}

if (-not (Get-Command code -ErrorAction SilentlyContinue)) {
    Write-Error "The 'code' CLI is not available in PATH. Open VS Code, run 'Shell Command: Install code command in PATH', and retry."
    exit 1
}

if (-not (Test-Path -LiteralPath $ExtensionsFile)) {
    Write-Error "Extensions list not found at: $ExtensionsFile"
    exit 1
}

# 1. Remove ALL currently installed extensions (multi-pass to resolve dependency chains)
Write-Host "=== Step 1: Removing all installed VS Code extensions ===" -ForegroundColor Yellow
$maxPasses = 5
for ($pass = 1; $pass -le $maxPasses; $pass++) {
    $installed = @(code --list-extensions)
    if ($installed.Count -eq 0) {
        break
    }

    Write-Host "Pass $pass - Uninstalling $($installed.Count) extension(s)..." -ForegroundColor DarkYellow
    foreach ($ext in $installed) {
        code --uninstall-extension $ext | Out-Null
    }
}

$remaining = @(code --list-extensions)
if ($remaining.Count -gt 0) {
    Write-Warning "Some extensions could not be removed automatically: $($remaining -join ', ')"
} else {
    Write-Host "All existing extensions removed." -ForegroundColor Green
}

# 2. Install all extensions listed in extensions.txt
Write-Host "`n=== Step 2: Installing extensions from $ExtensionsFile ===" -ForegroundColor Cyan
$targetExtensions = Get-Content -LiteralPath $ExtensionsFile |
    ForEach-Object { $_.Trim() } |
    Where-Object { $_ -and -not $_.StartsWith("#") }

$total = $targetExtensions.Count
$index = 0

foreach ($ext in $targetExtensions) {
    $index++
    Write-Host "[$index/$total] Installing $ext..." -ForegroundColor Gray
    code --install-extension $ext --force | Out-Null
}

# 3. Verify final count
$finalInstalled = @(code --list-extensions)
Write-Host "`nDone! $($finalInstalled.Count) of $total extensions are now installed." -ForegroundColor Green
Write-Host "Reload VS Code (Ctrl+Shift+P -> 'Developer: Reload Window') to activate all extensions." -ForegroundColor Cyan