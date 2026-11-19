# Made by: Hazzard
# FreeCodeCamp: PowerShell Automation and Scripting
# Project: System Inventory & Hardware Profile Generator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "       SYSTEM INVENTORY REPORT          " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$os = Get-CimInstance Win32_OperatingSystem
$cs = Get-CimInstance Win32_ComputerSystem

$profile = [PSCustomObject]@{
    ComputerName    = $cs.Name
    Manufacturer    = $cs.Manufacturer
    Model           = $cs.Model
    OperatingSystem = $os.Caption
    Architecture    = $os.OSArchitecture
    TotalRAM_GB     = [Math]::Round($cs.TotalPhysicalMemory / 1GB, 2)
    FreeRAM_GB      = [Math]::Round($os.FreePhysicalMemory / 1MB, 2)
    LastBootTime    = $os.LastBootUpTime
}

$profile | Format-List
Write-Host "Report generated at $(Get-Date)" -ForegroundColor Green
