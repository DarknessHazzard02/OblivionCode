<#
.SYNOPSIS
    Lightweight post-restart & daily maintenance routine (Standard Non-Admin User Version).
    Runs with zero UAC prompts and resolves Desktop dynamically via GetFolderPath.
#>
param(
    [switch]$Force
)

$ErrorActionPreference = "SilentlyContinue"

# Resolve Desktop dynamically (handles local Desktop and OneDrive-redirected Desktop)
$DesktopPath = [Environment]::GetFolderPath('Desktop')
$ScriptRoot  = Join-Path -Path $DesktopPath -ChildPath "DeviceMaintenanceUser"
$LogDir      = Join-Path -Path $ScriptRoot -ChildPath "Logs"
$StampFile   = Join-Path -Path $LogDir -ChildPath "LastDailyUserRun.txt"
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

# Cooldown guard: skip if already executed within the last 12 hours (unless -Force is passed)
if (-not $Force -and (Test-Path $StampFile)) {
    $LastRun = [datetime](Get-Content $StampFile -Raw)
    if (((Get-Date) - $LastRun).TotalHours -lt 12) {
        exit 0
    }
}

# Rotate logs older than 30 days
Get-ChildItem -Path $LogDir -Filter "DailyUser_*.log" |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } |
    Remove-Item -Force

$ComputerName = $env:COMPUTERNAME
$LogFile      = Join-Path -Path $LogDir -ChildPath "DailyUser_${ComputerName}_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
Start-Transcript -Path $LogFile -Append

$FreeBefore = [math]::Round((Get-PSDrive C).Free / 1GB, 2)
Write-Host "=== Post-Restart Daily Maintenance (Non-Admin User) | $ComputerName | Free C: $FreeBefore GB ===" -ForegroundColor Cyan

# 1. Purge user-scoped temporary files & CrashDumps
Write-Host "[1/4] Purging user temp files and local crash dumps..." -ForegroundColor White
Remove-Item -Path "$env:TEMP\*" -Recurse -Force
Remove-Item -Path "$env:LOCALAPPDATA\CrashDumps\*" -Recurse -Force

# 2. Clear user Recycle Bin
Write-Host "[2/4] Emptying user Recycle Bin..." -ForegroundColor White
Clear-RecycleBin -Force

# 3. Clean user-profile browser & WebView2 GPU/shader caches (safe while closed)
Write-Host "[3/4] Clearing user-level WebView2 and GPU shader caches..." -ForegroundColor White
$UserCachePaths = @(
    "$env:LOCALAPPDATA\Microsoft\Windows\INetCache\*",
    "$env:LOCALAPPDATA\D3DSCache\*"
)
foreach ($CachePath in $UserCachePaths) {
    Remove-Item -Path $CachePath -Recurse -Force
}

# 4. Upgrade user-scoped apps silently via Winget (avoids UAC elevation prompts)
Write-Host "[4/4] Upgrading user-scoped applications via Winget..." -ForegroundColor White
if (Get-Command winget -ErrorAction SilentlyContinue) {
    winget upgrade --all --scope user --silent --accept-package-agreements --accept-source-agreements
} else {
    Write-Host "  -> Winget not available; skipping." -ForegroundColor DarkGray
}

Set-Content -Path $StampFile -Value (Get-Date).ToString("o")
$FreeAfter = [math]::Round((Get-PSDrive C).Free / 1GB, 2)
$Reclaimed = [math]::Round($FreeAfter - $FreeBefore, 2)
Write-Host "=== Completed Non-Admin Daily Maintenance | Free C: $FreeAfter GB (Reclaimed: $Reclaimed GB) ===" -ForegroundColor Green
Stop-Transcript
