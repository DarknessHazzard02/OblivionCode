#Requires -RunAsAdministrator
param(
    [switch]$InstallPSWindowsUpdate
)

$DesktopPath = [Environment]::GetFolderPath('Desktop')
$TargetDir   = Join-Path -Path $DesktopPath -ChildPath "DeviceMaintenance"
$DailyScript = "Run-DailyOnRestart.ps1"
$WeekScript  = "Run-WeeklyMaintenance.ps1"

foreach ($File in @($DailyScript, $WeekScript)) {
    $Src = Join-Path -Path $PSScriptRoot -ChildPath $File
    if (-not (Test-Path $Src)) {
        Write-Error "Missing $File in $PSScriptRoot"
        exit 1
    }
}

# 1. Copy both scripts into Desktop\DeviceMaintenance
New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
$DestDaily = Join-Path -Path $TargetDir -ChildPath $DailyScript
$DestWeek  = Join-Path -Path $TargetDir -ChildPath $WeekScript
Copy-Item -Path (Join-Path $PSScriptRoot $DailyScript) -Destination $DestDaily -Force
Copy-Item -Path (Join-Path $PSScriptRoot $WeekScript)  -Destination $DestWeek  -Force
Unblock-File -Path $DestDaily, $DestWeek

# 2. Optional: Install PSWindowsUpdate for full KB logging
if ($InstallPSWindowsUpdate) {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force -ErrorAction SilentlyContinue | Out-Null
    Install-Module -Name PSWindowsUpdate -Force -AllowClobber -ErrorAction SilentlyContinue
}

# 3. Run initial OEM bloat trim immediately
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$DestWeek" -DebloatOnly

# 4. Adapt Task Scheduler logon type for Windows Home vs. Pro
$CurrentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$OsSku       = (Get-CimInstance Win32_OperatingSystem).OperatingSystemSKU
$LogonType   = if ($OsSku -in @(100, 101)) { "Interactive" } else { "S4U" }

$Settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$Principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType $LogonType -RunLevel Highest

# Task 1: Runs 2 minutes after PC restart/sign-in (+ 1:00 PM fallback if PC only sleeps)
$RestartTrigger = New-ScheduledTaskTrigger -AtLogOn -User $CurrentUser
$RestartTrigger.Delay = "PT2M"
$DailyFallback  = New-ScheduledTaskTrigger -Daily -At 1:00PM

$DailyAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$DestDaily`""
Register-ScheduledTask -TaskName "Device-Maintenance-OnRestart" -Action $DailyAction -Trigger @($RestartTrigger, $DailyFallback) -Principal $Principal -Settings $Settings -Force | Out-Null

# Task 2: Runs Weekly on Sundays at 3:00 AM (catches up on next boot if off)
$WeeklyAction  = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$DestWeek`""
$WeeklyTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 3:00AM
Register-ScheduledTask -TaskName "Device-Maintenance-Weekly" -Action $WeeklyAction -Trigger $WeeklyTrigger -Principal $Principal -Settings $Settings -Force | Out-Null

Write-Host "`nDeployed to: $TargetDir" -ForegroundColor Green
Get-ScheduledTask -TaskName "Device-Maintenance-*" |
    Select-Object TaskName, State, @{N='NextRunTime';E={($_ | Get-ScheduledTaskInfo).NextRunTime}} |
    Format-Table -AutoSize
