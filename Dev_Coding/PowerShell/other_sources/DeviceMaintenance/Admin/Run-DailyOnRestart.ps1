#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Lightweight post-restart & daily maintenance routine (Admin Version).
    Resolves Desktop dynamically (local or OneDrive) via GetFolderPath.
#>
param(
    [switch]$Force
)

$ErrorActionPreference = "SilentlyContinue"

# Resolve Desktop dynamically (handles local Desktop and OneDrive Known Folder Move)
$DesktopPath = [Environment]::GetFolderPath('Desktop')
$ScriptRoot  = Join-Path -Path $DesktopPath -ChildPath "DeviceMaintenance"
$LogDir      = Join-Path -Path $ScriptRoot -ChildPath "Logs"
$StampFile   = Join-Path -Path $LogDir -ChildPath "LastDailyRun.txt"
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

# Cooldown guard: skip if already executed within the last 12 hours (unless -Force is passed)
if (-not $Force -and (Test-Path $StampFile)) {
    $LastRun = [datetime](Get-Content $StampFile -Raw)
    if (((Get-Date) - $LastRun).TotalHours -lt 12) {
        exit 0
    }
}

# Rotate logs older than 30 days
Get-ChildItem -Path $LogDir -Filter "Daily_*.log" |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } |
    Remove-Item -Force

$ComputerName = $env:COMPUTERNAME
$LogFile      = Join-Path -Path $LogDir -ChildPath "Daily_${ComputerName}_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
Start-Transcript -Path $LogFile -Append

$FreeBefore = [math]::Round((Get-PSDrive C).Free / 1GB, 2)
Write-Host "=== Post-Restart Daily Maintenance (Admin) | $ComputerName | Free C: $FreeBefore GB ===" -ForegroundColor Cyan

# 1. Watchdog: Ensure core security & update services are running
foreach ($Svc in @("WinDefend", "wuauserv", "bits", "EventLog")) {
    $ServiceObj = Get-Service -Name $Svc
    if ($ServiceObj -and $ServiceObj.Status -ne "Running") {
        Start-Service -Name $Svc
        Write-Host "  -> Restarted stopped service: $Svc" -ForegroundColor Yellow
    }
}

# 2. Update Microsoft Defender definitions
Update-MpSignature

# 3. Purge Temp folders, Recycle Bin, DNS & Delivery Optimization caches
Remove-Item -Path "$env:TEMP\*", "C:\Windows\Temp\*" -Recurse -Force
Clear-RecycleBin -Force
Clear-DnsClientCache
Delete-DeliveryOptimizationCache -Force

# 4. Silent user & system app updates via Winget
if (Get-Command winget -ErrorAction SilentlyContinue) {
    winget upgrade --all --silent --accept-package-agreements --accept-source-agreements
}

Set-Content -Path $StampFile -Value (Get-Date).ToString("o")
$FreeAfter = [math]::Round((Get-PSDrive C).Free / 1GB, 2)
$Reclaimed = [math]::Round($FreeAfter - $FreeBefore, 2)
Write-Host "=== Completed Daily Maintenance | Free C: $FreeAfter GB (Reclaimed: $Reclaimed GB) ===" -ForegroundColor Green
Stop-Transcript
