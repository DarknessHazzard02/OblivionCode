#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Deep weekly hardware, storage, OS integrity, OEM governance, and Windows Update routine (Admin Version).
#>
param(
    [switch]$DebloatOnly
)

$ErrorActionPreference = "SilentlyContinue"

$DesktopPath = [Environment]::GetFolderPath('Desktop')
$ScriptRoot  = Join-Path -Path $DesktopPath -ChildPath "DeviceMaintenance"
$LogDir      = Join-Path -Path $ScriptRoot -ChildPath "Logs"
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

# Rotate weekly logs older than 60 days
Get-ChildItem -Path $LogDir -Filter "Weekly_*.log" |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-60) } |
    Remove-Item -Force

$ComputerName = $env:COMPUTERNAME
$ModeTag      = if ($DebloatOnly) { "Debloat" } else { "Weekly" }
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
Write-Host " Device : $ComputerName ($Manufacturer $($CS.Model))" -ForegroundColor Cyan
Write-Host " RAM    : $FreeRAM_GB / $TotalRAM_GB GB free ($UsedRAM_Pct% used) | Free C: $FreeBefore GB" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# --- [1/7] OEM SERVICE GOVERNANCE & BLOAT TRIM ---
Write-Host "[1/7] Enforcing OEM service governance..." -ForegroundColor White
@("*McAfee*") | ForEach-Object {
    Get-AppxPackage -AllUsers $_ | Remove-AppxPackage -AllUsers
    Get-AppxProvisionedPackage -Online | Where-Object DisplayName -Like $_ | Remove-AppxProvisionedPackage -Online
}

if ($Manufacturer -like "*ASUS*") {
    @("ASUSSystemDiagnosis", "ASUSUpdateCheck", "ASUSLinkNear", "ASUSLinkRemote", "AsusCertService") | ForEach-Object {
        if (Get-Service -Name $_) {
            Stop-Service -Name $_ -Force
            Set-Service -Name $_ -StartupType Disabled
        }
    }
    @("ASUSSystemControlInterface", "ASUSSystemControlInterfaceV3", "ASUSOptimization", "ASUSAppService") | ForEach-Object {
        $Obj = Get-Service -Name $_
        if ($Obj) {
            Set-Service -Name $_ -StartupType Automatic
            if ($Obj.Status -ne "Running") { Start-Service -Name $_ }
        }
    }
    @("*GlideX*") | ForEach-Object {
        Get-AppxPackage -AllUsers $_ | Remove-AppxPackage -AllUsers
        Get-AppxProvisionedPackage -Online | Where-Object DisplayName -Like $_ | Remove-AppxProvisionedPackage -Online
    }
    Get-ScheduledTask -TaskPath "\ASUS\*" |
        Where-Object { $_.TaskName -match "Update|AppDeals|Diagnosis|GlideX" } |
        Disable-ScheduledTask | Out-Null
}
elseif ($Manufacturer -like "*Dell*") {
    Get-Service -Name "*Dell*" | Select-Object Name, Status, StartType | Format-Table -AutoSize
}

if ($DebloatOnly) {
    Write-Host "=== Initial OEM Debloat Completed ===" -ForegroundColor Green
    Stop-Transcript
    exit 0
}

# --- [2/7] SYSTEM RESTORE POINT ---
Write-Host "[2/7] Creating System Restore checkpoint..." -ForegroundColor White
Enable-ComputerRestore -Drive "C:\"
Checkpoint-Computer -Description "WeeklyMaintenance" -RestorePointType "MODIFY_SETTINGS"

# --- [3/7] STORAGE OPTIMIZATION (SSD TRIM / HDD DEFRAG) & SMART HEALTH ---
Write-Host "[3/7] Optimizing storage & auditing SMART health..." -ForegroundColor White
$Disks = Get-PhysicalDisk
foreach ($Disk in $Disks) {
    if ($Disk.MediaType -eq "SSD") {
        Optimize-Volume -DriveLetter C -ReTrim -Verbose
    } elseif ($Disk.MediaType -eq "HDD") {
        Optimize-Volume -DriveLetter C -Defrag -Verbose
    }
}
$Disks | Get-StorageReliabilityCounter |
    Select-Object DeviceId, Temperature, Wear, ReadErrorsTotal, WriteErrorsTotal |
    Format-Table -AutoSize

# --- [4/7] WINSXS CLEANUP & OS IMAGE REPAIR ---
Write-Host "[4/7] Cleaning WinSxS component store & repairing OS files..." -ForegroundColor White
Dism.exe /Online /Cleanup-Image /StartComponentCleanup
Repair-WindowsImage -Online -RestoreHealth
sfc /scannow

# --- [5/7] DEFENDER QUICKSCAN ---
Write-Host "[5/7] Running Microsoft Defender QuickScan..." -ForegroundColor White
Start-MpScan -ScanType QuickScan

# --- [6/7] WINDOWS OS, DRIVER & MICROSOFT STORE UPDATES (NO FORCED REBOOT) ---
Write-Host "[6/7] Triggering Store & Windows Updates..." -ForegroundColor White
Get-CimInstance -Namespace "Root\cimv2\mdm\dmmap" -ClassName "MDM_EnterpriseModernAppManagement_AppManagement01" |
    Invoke-CimMethod -MethodName UpdateScanMethod | Out-Null

if (Get-Module -ListAvailable -Name PSWindowsUpdate) {
    Import-Module PSWindowsUpdate
    Get-WindowsUpdate -MicrosoftUpdate -AcceptAll -Install -IgnoreReboot |
        Select-Object KB, Title, Result | Format-Table -AutoSize
    if (Get-WURebootStatus -Silent) {
        Write-Host "ACTION REQUIRED: Windows Update installed patches that require a reboot." -ForegroundColor Yellow
    }
} else {
    Start-Process -FilePath "UsoClient.exe" -ArgumentList "StartInteractiveScan" -NoNewWindow
}

# --- [7/7] RAM PRESSURE AUDIT & BATTERY REPORT ---
Write-Host "[7/7] Auditing RAM usage & generating battery report..." -ForegroundColor White
if ($UsedRAM_Pct -ge 80) {
    Write-Host "WARNING: High memory pressure detected ($UsedRAM_Pct% used on $TotalRAM_GB GB RAM)." -ForegroundColor Red
}
Get-Process | Sort-Object WorkingSet64 -Descending |
    Select-Object -First 10 Name, @{N='RAM_MB';E={[math]::Round($_.WorkingSet64/1MB,1)}} |
    Format-Table -AutoSize

if ($HasBattery) {
    $BatteryFile = Join-Path -Path $ScriptRoot -ChildPath "BatteryReport_${ComputerName}_$(Get-Date -Format 'yyyyMMdd').html"
    powercfg /batteryreport /output "$BatteryFile" | Out-Null
}

$FreeAfter = [math]::Round((Get-PSDrive C).Free / 1GB, 2)
$Reclaimed = [math]::Round($FreeAfter - $FreeBefore, 2)
Write-Host "=== Completed Weekly Maintenance | Free C: $FreeAfter GB (Delta: $Reclaimed GB) ===" -ForegroundColor Green
Stop-Transcript
