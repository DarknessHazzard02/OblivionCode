<#
.SYNOPSIS
    Weekly user-scope maintenance, health audit, battery report & CSV tracker (Non-Admin Version).
#>
param(
    [switch]$DebloatOnly
)

$ErrorActionPreference = "SilentlyContinue"

$DesktopPath = [Environment]::GetFolderPath('Desktop')
$ScriptRoot  = Join-Path -Path $DesktopPath -ChildPath "DeviceMaintenanceUser"
$LogDir      = Join-Path -Path $ScriptRoot -ChildPath "Logs"
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

# Rotate weekly logs older than 60 days
Get-ChildItem -Path $LogDir -Filter "WeeklyUser_*.log" |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-60) } |
    Remove-Item -Force

$ComputerName = $env:COMPUTERNAME
$ModeTag      = if ($DebloatOnly) { "DebloatUser" } else { "WeeklyUser" }
$LogFile      = Join-Path -Path $LogDir -ChildPath "${ModeTag}_${ComputerName}_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
Start-Transcript -Path $LogFile -Append

$CS           = Get-CimInstance Win32_ComputerSystem
$OS           = Get-CimInstance Win32_OperatingSystem
$Manufacturer = $CS.Manufacturer
$TotalRAM_GB  = [math]::Round($CS.TotalPhysicalMemory / 1GB, 1)
$FreeRAM_GB   = [math]::Round(($OS.FreePhysicalMemory * 1KB) / 1GB, 2)
$UsedRAM_Pct  = [math]::Round((($TotalRAM_GB - $FreeRAM_GB) / $TotalRAM_GB) * 100, 1)
$HasBattery   = [bool](Get-CimInstance Win32_Battery)
$FreeBefore   = [math]::Round((Get-PSDrive C).Free / 1GB, 2)

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " Device : $ComputerName ($Manufacturer $($CS.Model)) [User Mode]" -ForegroundColor Cyan
Write-Host " RAM    : $FreeRAM_GB / $TotalRAM_GB GB free ($UsedRAM_Pct% used) | Free C: $FreeBefore GB" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# --- [1/5] USER-SCOPE BLOAT REMOVAL & STARTUP AUDIT ---
Write-Host "[1/5] Removing user-scoped consumer trialware & auditing user startup apps..." -ForegroundColor White
@("*McAfee*", "*GlideX*") | ForEach-Object {
    Get-AppxPackage $_ | Remove-AppxPackage
}

Write-Host "  -> Current User Startup Entries:" -ForegroundColor DarkGray
Get-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" |
    Select-Object * -ExcludeProperty PSPath, PSParentPath, PSChildName, PSDrive, PSProvider |
    Format-List

if ($DebloatOnly) {
    Write-Host "=== User-Scope Debloat Completed ===" -ForegroundColor Green
    Stop-Transcript
    exit 0
}

# --- [2/5] READ-ONLY CORE & OEM SERVICE HEALTH CHECK ---
Write-Host "[2/5] Auditing core Windows & OEM service statuses (read-only)..." -ForegroundColor White
Get-Service -Name "WinDefend", "wuauserv", "bits", "*ASUS*", "*Dell*" |
    Select-Object Name, Status, StartType |
    Format-Table -AutoSize

# --- [3/5] MICROSOFT STORE USER APP UPDATES ---
Write-Host "[3/5] Triggering user-scoped Microsoft Store updates..." -ForegroundColor White
if (Get-Command winget -ErrorAction SilentlyContinue) {
    winget upgrade --source msstore --scope user --silent --accept-package-agreements --accept-source-agreements
}

# --- [4/5] RAM PRESSURE AUDIT & BATTERY REPORT ---
Write-Host "[4/5] Auditing top RAM consumers & exporting Battery Report..." -ForegroundColor White
if ($UsedRAM_Pct -ge 80) {
    Write-Host "WARNING: High memory pressure ($UsedRAM_Pct% used on $TotalRAM_GB GB RAM)." -ForegroundColor Red
}
Get-Process | Sort-Object WorkingSet64 -Descending |
    Select-Object -First 10 Name, @{N='RAM_MB';E={[math]::Round($_.WorkingSet64/1MB,1)}} |
    Format-Table -AutoSize

if ($HasBattery) {
    $BatteryFile = Join-Path -Path $ScriptRoot -ChildPath "BatteryReport_${ComputerName}_$(Get-Date -Format 'yyyyMMdd').html"
    powercfg /batteryreport /output "$BatteryFile" | Out-Null
    Write-Host "  -> Exported Battery Report to $BatteryFile" -ForegroundColor Green
}

# --- [5/5] APPEND FLEET HEALTH CSV SUMMARY ---
Write-Host "[5/5] Recording health telemetry to FleetHealthSummary.csv..." -ForegroundColor White
$FreeAfter = [math]::Round((Get-PSDrive C).Free / 1GB, 2)
$SummaryCsv = Join-Path -Path $ScriptRoot -ChildPath "FleetHealthSummary.csv"
[PSCustomObject]@{
    Timestamp    = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    DeviceName   = $ComputerName
    Manufacturer = $Manufacturer
    Model        = $CS.Model
    TotalRAM_GB  = $TotalRAM_GB
    UsedRAM_Pct  = $UsedRAM_Pct
    FreeDriveC_GB = $FreeAfter
    UptimeDays   = [math]::Round(((Get-Date) - $OS.LastBootUpTime).TotalDays, 1)
} | Export-Csv -Path $SummaryCsv -NoTypeInformation -Append

Write-Host "=== Completed Non-Admin Weekly Maintenance | Free C: $FreeAfter GB ===" -ForegroundColor Green
Stop-Transcript
