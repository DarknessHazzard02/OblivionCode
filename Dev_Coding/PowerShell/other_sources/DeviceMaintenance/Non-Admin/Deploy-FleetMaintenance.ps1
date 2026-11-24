<#
.SYNOPSIS
    Zero-elevation fleet installer (Standard Non-Admin User Version).
    Registers Limited-privilege user Scheduled Tasks (with Startup-folder fallback if GPO blocks Task Scheduler).
#>

$ErrorActionPreference = "SilentlyContinue"

$DesktopPath = [Environment]::GetFolderPath('Desktop')
$TargetDir   = Join-Path -Path $DesktopPath -ChildPath "DeviceMaintenanceUser"
$DailyScript = "Run-DailyOnRestart-User.ps1"
$WeekScript  = "Run-WeeklyMaintenance-User.ps1"

foreach ($File in @($DailyScript, $WeekScript)) {
    $Src = Join-Path -Path $PSScriptRoot -ChildPath $File
    if (-not (Test-Path $Src)) {
        Write-Error "Missing $File in $PSScriptRoot"
        exit 1
    }
}

# 1. Copy both scripts into Desktop\DeviceMaintenanceUser
New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
$DestDaily = Join-Path -Path $TargetDir -ChildPath $DailyScript
$DestWeek  = Join-Path -Path $TargetDir -ChildPath $WeekScript
Copy-Item -Path (Join-Path $PSScriptRoot $DailyScript) -Destination $DestDaily -Force
Copy-Item -Path (Join-Path $PSScriptRoot $WeekScript)  -Destination $DestWeek  -Force
Unblock-File -Path $DestDaily, $DestWeek

# 2. Run initial user-scope bloat removal immediately
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$DestWeek" -DebloatOnly

# 3. Register Limited-privilege Scheduled Tasks for the current standard user
$CurrentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$Settings    = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$Principal   = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive -RunLevel Limited

$RestartTrigger = New-ScheduledTaskTrigger -AtLogOn -User $CurrentUser
$RestartTrigger.Delay = "PT2M"
$DailyFallback  = New-ScheduledTaskTrigger -Daily -At 1:00PM

$DailyAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$DestDaily`""
$Task1 = Register-ScheduledTask -TaskName "User-Device-Maintenance-OnRestart" -Action $DailyAction -Trigger @($RestartTrigger, $DailyFallback) -Principal $Principal -Settings $Settings -Force

$WeeklyAction  = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$DestWeek`""
$WeeklyTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 3:00AM
$Task2 = Register-ScheduledTask -TaskName "User-Device-Maintenance-Weekly" -Action $WeeklyAction -Trigger $WeeklyTrigger -Principal $Principal -Settings $Settings -Force

# 4. Fallback: If corporate GPO blocks Scheduled Tasks for standard users, place a shortcut in shell:startup
if (-not $Task1) {
    $StartupDir = [Environment]::GetFolderPath('Startup')
    $WshShell   = New-Object -ComObject WScript.Shell
    $Shortcut   = $WshShell.CreateShortcut((Join-Path $StartupDir "DailyUserMaintenance.lnk"))
    $Shortcut.TargetPath       = "powershell.exe"
    $Shortcut.Arguments        = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$DestDaily`""
    $Shortcut.WorkingDirectory = $TargetDir
    $Shortcut.Save()
    Write-Host "Task Scheduler restricted by policy; configured Startup folder fallback instead." -ForegroundColor Yellow
}

Write-Host "`nNon-Admin Deployment complete in: $TargetDir" -ForegroundColor Green
Get-ScheduledTask -TaskName "User-Device-Maintenance-*" |
    Select-Object TaskName, State, @{N='NextRunTime';E={($_ | Get-ScheduledTaskInfo).NextRunTime}} |
    Format-Table -AutoSize
