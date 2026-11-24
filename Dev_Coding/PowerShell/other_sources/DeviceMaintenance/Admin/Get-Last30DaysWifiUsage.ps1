#Requires -RunAsAdministrator
# Updated by Haz
<#
.SYNOPSIS
    Extracts the last N days (default 30) of daily Wi-Fi data consumption (GB & Mbps) from Windows SRUM (SRUDB.dat).
.DESCRIPTION
    1. Snapshots C:\Windows\System32\sru\SRUDB.dat via Volume Shadow Copy (esentutl.exe).
    2. Exports hourly network counters with NirSoft NetworkUsageView, after checking its signature or hash.
    3. Filters Wi-Fi traffic for the last N calendar days (today included) and aggregates GB and Mbps per day.
    4. Writes Daily_Wifi_Last<N>Days_<PC>.csv and TopApps_Wifi_Last<N>Days_<PC>.csv to the Desktop and prints
       a sizing summary.
    The tool and every temporary file live under "<Program Files>\WifiUsageReport" (admin-only, local, never
    synced to OneDrive). The SRUM snapshot and the raw hourly export are deleted on every exit path.
    Units are decimal, like an ISP plan: 1 GB = 10^9 bytes, 1 Mbps = 10^6 bits per second.
.PARAMETER ToolSha256
    Expected SHA-256 of NetworkUsageView.exe. Without it the executable must carry a valid Authenticode
    signature from Nir Sofer; otherwise the script stops and prints the hash so you can pin it.
.PARAMETER AcknowledgeEdrRisk
    Required. Copying SRUDB.dat through VSS is the same technique used to steal credential databases, and
    NirSoft tools are flagged as potentially unwanted: on a managed (company) device this raises EDR alerts.
    Get IT approval before running it there.
.EXAMPLE
    .\Get-Last30DaysWifiUsage.ps1 -AcknowledgeEdrRisk -AllowDownload
#>
param(
    [ValidateRange(1, 60)][int]$Days = 30,
    [switch]$IncludeAllAdapters,
    [switch]$AllowDownload,
    [ValidatePattern('^[0-9A-Fa-f]{64}$')][string]$ToolSha256,
    [switch]$AcknowledgeEdrRisk
)

# ===============================================
# Settings and safety gate
# ===============================================
$ErrorActionPreference = "Stop"

Write-Warning ("This script copies SRUDB.dat through VSS and runs a NirSoft tool. On a managed device both " +
               "can raise EDR / antivirus alerts. Run it only on your own device or with IT approval.")
if (-not $AcknowledgeEdrRisk) {
    throw "Re-run with -AcknowledgeEdrRisk once you have read the warning above."
}

$ComputerName = $env:COMPUTERNAME
$TimestampTag = Get-Date -Format "yyyyMMdd_HHmmss"
$DesktopPath  = [Environment]::GetFolderPath('Desktop')          # final CSVs only: may be synced to OneDrive
$OutputDir    = Join-Path -Path $DesktopPath -ChildPath "WifiUsageReport"
# Known-folder API, not $env: a user-level ProgramFiles / SystemRoot variable would move work into a writable folder
$WorkRoot     = Join-Path -Path ([Environment]::GetFolderPath('ProgramFiles')) -ChildPath "WifiUsageReport"
$ToolsDir     = Join-Path -Path $WorkRoot -ChildPath "Tools"
$TempDir      = Join-Path -Path $WorkRoot -ChildPath "Temp_$TimestampTag"
$ExePath      = Join-Path -Path $ToolsDir -ChildPath "NetworkUsageView.exe"
$DailyCsv     = Join-Path -Path $OutputDir -ChildPath "Daily_Wifi_Last${Days}Days_${ComputerName}.csv"
$AppsCsv      = Join-Path -Path $OutputDir -ChildPath "TopApps_Wifi_Last${Days}Days_${ComputerName}.csv"
$SourceDb     = Join-Path -Path ([Environment]::GetFolderPath('System')) -ChildPath "sru\SRUDB.dat"
$SnapshotDb   = Join-Path -Path $TempDir -ChildPath "SRUDB_${TimestampTag}.dat"
$RawCsv       = Join-Path -Path $TempDir -ChildPath "raw_srum_${TimestampTag}.csv"
$ExpectedColumns = @('Timestamp', 'App Name', 'Network Adapter', 'Bytes Sent', 'Bytes Received')

New-Item -ItemType Directory -Path $OutputDir, $ToolsDir, $TempDir -Force | Out-Null
# The SRUM copy is readable only by SYSTEM and admins, like the original: Program Files would let Users read it
& icacls.exe $TempDir /inheritance:r /grant:r "*S-1-5-32-544:(OI)(CI)F" "*S-1-5-18:(OI)(CI)F" | Out-Null
if ($LASTEXITCODE -ne 0) {
    Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue
    throw "Could not restrict '$TempDir' to Administrators and SYSTEM (icacls exit code $LASTEXITCODE)."
}

function Assert-TrustedTool {
    param([string]$Path)
    $Hash = (Get-FileHash -Path $Path -Algorithm SHA256).Hash
    if ($ToolSha256) {
        if ($Hash -ne $ToolSha256.ToUpperInvariant()) {
            throw "NetworkUsageView.exe hash $Hash does not match -ToolSha256. The file was not run."
        }
        return
    }
    $Signature = Get-AuthenticodeSignature -FilePath $Path
    if ($Signature.Status -ne 'Valid' -or $Signature.SignerCertificate.Subject -notmatch 'Nir Sofer') {
        throw ("NetworkUsageView.exe has no valid Nir Sofer signature (status: $($Signature.Status)). " +
               "If you trust this copy, re-run with -ToolSha256 $Hash")
    }
}

function ConvertTo-SafeDateTime {
    param([string]$Text)
    if ([string]::IsNullOrWhiteSpace($Text)) { return $null }
    $Clean  = $Text.Trim()
    $Parsed = [datetime]::MinValue
    foreach ($Culture in @([System.Globalization.CultureInfo]::CurrentCulture, [System.Globalization.CultureInfo]::InvariantCulture)) {
        if ([datetime]::TryParse($Clean, $Culture, [System.Globalization.DateTimeStyles]::None, [ref]$Parsed)) {
            return $Parsed
        }
    }
    return $null
}

try {
    # ===============================================
    # [1/4] Locate, download (opt-in) and verify NetworkUsageView
    # ===============================================
    if (-not (Test-Path $ExePath)) {
        $ScriptDirCopy = if ($PSScriptRoot) { Join-Path -Path $PSScriptRoot -ChildPath "NetworkUsageView.exe" } else { "" }
        if ($ScriptDirCopy -and (Test-Path $ScriptDirCopy)) {
            Copy-Item -Path $ScriptDirCopy -Destination $ExePath -Force
        } elseif (-not $AllowDownload) {
            throw ("NetworkUsageView.exe not found. Place it in '$ToolsDir' (or next to this script), " +
                   "or re-run with -AllowDownload to fetch it from nirsoft.net.")
        } else {
            Write-Host "[1/4] Downloading NirSoft NetworkUsageView..." -ForegroundColor Cyan
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            $ZipUrl = if ($env:PROCESSOR_ARCHITECTURE -eq "AMD64") {
                "https://www.nirsoft.net/utils/networkusageview-x64.zip"
            } else {
                "https://www.nirsoft.net/utils/networkusageview.zip"
            }
            $ZipPath    = Join-Path -Path $TempDir -ChildPath "networkusageview.zip"
            $UnzipDir   = Join-Path -Path $TempDir -ChildPath "unzip"
            Invoke-WebRequest -Uri $ZipUrl -OutFile $ZipPath -Headers @{ "User-Agent" = "Mozilla/5.0" } -UseBasicParsing
            Expand-Archive -Path $ZipPath -DestinationPath $UnzipDir -Force
            $Extracted = Join-Path -Path $UnzipDir -ChildPath "NetworkUsageView.exe"
            if (-not (Test-Path $Extracted)) {
                throw "The downloaded archive did not contain NetworkUsageView.exe."
            }
            Assert-TrustedTool -Path $Extracted                    # verify before it reaches the tools folder
            Copy-Item -Path $Extracted -Destination $ExePath -Force # only the exe: no side-loadable extras
        }
    }
    Assert-TrustedTool -Path $ExePath                              # every run, also for a copy already there
    Unblock-File -Path $ExePath -ErrorAction SilentlyContinue

    # ===============================================
    # [2/4] Snapshot the locked SRUDB.dat via Volume Shadow Copy
    # ===============================================
    Write-Host "[2/4] Snapshotting Windows SRUM database (SRUDB.dat)..." -ForegroundColor Cyan
    if (-not (Test-Path $SourceDb)) {
        throw "SRUM database not found at $SourceDb. Verify Diagnostic Policy Service (DPS) is running."
    }
    # Native tool: in Windows PowerShell 5.1, stderr under "Stop" would throw before the exit code is checked
    $ErrorActionPreference = "Continue"
    $EsentOutput = & esentutl.exe /y "$SourceDb" /vss /d "$SnapshotDb" 2>&1 | Out-String
    $EsentExit   = $LASTEXITCODE
    $ErrorActionPreference = "Stop"
    if ($EsentExit -ne 0 -or -not (Test-Path $SnapshotDb) -or (Get-Item $SnapshotDb).Length -eq 0) {
        throw "Failed to snapshot SRUDB.dat via VSS (exit code $EsentExit). Details: $EsentOutput"
    }

    # ===============================================
    # [3/4] Export hourly SRUM records to CSV
    # ===============================================
    Write-Host "[3/4] Extracting hourly network records..." -ForegroundColor Cyan
    Start-Process -FilePath $ExePath -ArgumentList "/LoadFrom 2 /ExternalFilename `"$SnapshotDb`" /scomma `"$RawCsv`"" -Wait -NoNewWindow
    if (-not (Test-Path $RawCsv) -or (Get-Item $RawCsv).Length -eq 0) {
        throw "NetworkUsageView failed to export CSV records from $SnapshotDb."
    }
    $RawRows = @(Import-Csv -Path $RawCsv)
} finally {
    # The snapshot and the raw export hold hourly app and network history of every user on the device
    Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue
    if (Test-Path $TempDir) {
        Write-Warning "Could not delete '$TempDir' (SRUM copy and raw export). Delete it manually."
    }
}

# ===============================================
# [4/4] Validate, filter the last N days and aggregate
# ===============================================
Write-Host "[4/4] Aggregating Wi-Fi usage for the last $Days days..." -ForegroundColor Cyan
if ($RawRows.Count -eq 0) {
    throw "NetworkUsageView exported an empty table: nothing to aggregate."
}
$MissingColumns = @($ExpectedColumns | Where-Object { $RawRows[0].PSObject.Properties.Name -notcontains $_ })
if ($MissingColumns.Count -gt 0) {
    throw "NetworkUsageView export is missing columns: $($MissingColumns -join ', ')"
}

$CutoffDate    = (Get-Date).Date.AddDays(-($Days - 1))            # N calendar days, today included
$AdaptersFound = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
$UnparsedDates = 0

$FilteredRecords = foreach ($Row in $RawRows) {
    $Dt = ConvertTo-SafeDateTime -Text $Row.Timestamp
    if (-not $Dt) { $UnparsedDates++; continue }
    if ($Dt.Date -lt $CutoffDate) { continue }

    $Adapter = [string]$Row.'Network Adapter'
    if (-not [string]::IsNullOrWhiteSpace($Adapter)) { [void]$AdaptersFound.Add($Adapter) }

    # Wi-Fi by driver name; virtual adapters (VPN, TAP, Hyper-V) would count the same traffic twice
    $IsWifi = ($Adapter -match 'Wi-?Fi|Wireless|WLAN|802\.11') -and ($Adapter -notmatch 'Virtual|VPN|TAP|Hyper-V')
    if (-not $IncludeAllAdapters -and -not $IsWifi) { continue }

    $SentStr   = ($Row.'Bytes Sent' -replace '[^\d]', '')
    $RecvStr   = ($Row.'Bytes Received' -replace '[^\d]', '')
    $SentBytes = if ($SentStr) { [int64]$SentStr } else { 0L }
    $RecvBytes = if ($RecvStr) { [int64]$RecvStr } else { 0L }
    if (($SentBytes + $RecvBytes) -le 0) { continue }

    [PSCustomObject]@{
        DateStr    = $Dt.ToString("yyyy-MM-dd")
        DayOfWeek  = $Dt.ToString("dddd")
        HourBucket = $Dt.ToString("yyyy-MM-dd HH")
        AppName    = if ([string]::IsNullOrWhiteSpace($Row.'App Name')) { "System / Unknown" } else { Split-Path $Row.'App Name' -Leaf }
        SentBytes  = $SentBytes
        RecvBytes  = $RecvBytes
        TotalBytes = $SentBytes + $RecvBytes
    }
}

if ($UnparsedDates -gt 0) {
    Write-Warning "$UnparsedDates of $($RawRows.Count) rows had a timestamp that could not be parsed and were skipped."
}
if (-not $FilteredRecords) {
    Write-Warning "No Wi-Fi usage records found in the last $Days days."
    Write-Host "Adapters seen in SRUM: $($AdaptersFound -join ', ')" -ForegroundColor Yellow
    Write-Host "Tip: Re-run with -IncludeAllAdapters if your Wi-Fi card uses a custom driver name." -ForegroundColor Yellow
    exit 0
}

$BytesPerGB = 1e9
$SecondsIn8Hours = 8 * 3600

# Group by day
$DailySummary = $FilteredRecords | Group-Object -Property DateStr | Sort-Object Name | ForEach-Object {
    $DayRows     = $_.Group
    $SumSent     = ($DayRows | Measure-Object -Property SentBytes -Sum).Sum
    $SumRecv     = ($DayRows | Measure-Object -Property RecvBytes -Sum).Sum
    $SumTotal    = $SumSent + $SumRecv
    $ActiveHours = ($DayRows | Select-Object -ExpandProperty HourBucket -Unique).Count

    [PSCustomObject]@{
        Date                = $_.Name
        Day                 = $DayRows[0].DayOfWeek
        Download_GB         = [math]::Round($SumRecv / $BytesPerGB, 3)
        Upload_GB           = [math]::Round($SumSent / $BytesPerGB, 3)
        Total_GB            = [math]::Round($SumTotal / $BytesPerGB, 3)
        Total_Bytes         = $SumTotal
        Active_Hours        = $ActiveHours
        Avg_8Hr_Mbps        = [math]::Round(($SumTotal * 8 / 1e6) / $SecondsIn8Hours, 2)
        Avg_ActiveHour_Mbps = if ($ActiveHours -gt 0) { [math]::Round(($SumTotal * 8 / 1e6) / ($ActiveHours * 3600), 2) } else { 0 }
    }
}

# Group by application
$AppSummary = $FilteredRecords | Group-Object -Property AppName | ForEach-Object {
    $AppRows  = $_.Group
    $AppSent  = ($AppRows | Measure-Object -Property SentBytes -Sum).Sum
    $AppRecv  = ($AppRows | Measure-Object -Property RecvBytes -Sum).Sum

    [PSCustomObject]@{
        Application = $_.Name
        Download_GB = [math]::Round($AppRecv / $BytesPerGB, 3)
        Upload_GB   = [math]::Round($AppSent / $BytesPerGB, 3)
        Total_GB    = [math]::Round(($AppSent + $AppRecv) / $BytesPerGB, 3)
    }
} | Sort-Object Total_GB -Descending

$DailySummary | Export-Csv -Path $DailyCsv -NoTypeInformation -Encoding UTF8
$AppSummary   | Export-Csv -Path $AppsCsv -NoTypeInformation -Encoding UTF8

# ===============================================
# Results and capacity sizing (from bytes, not from rounded GB)
# ===============================================
Write-Host "`n================ DAILY WI-FI USAGE ($ComputerName - LAST $Days DAYS) ================" -ForegroundColor Green
$DailySummary | Format-Table -Property * -AutoSize

$TotalPeriodBytes = ($DailySummary | Measure-Object -Property Total_Bytes -Sum).Sum
$ActiveDaysCount  = @($DailySummary).Count
$TotalPeriodGB    = [math]::Round($TotalPeriodBytes / $BytesPerGB, 2)
$AvgCalendarDayGB = [math]::Round($TotalPeriodBytes / $BytesPerGB / $Days, 2)
$AvgActiveDayBytes = $TotalPeriodBytes / $ActiveDaysCount
$AvgActiveDayGB   = [math]::Round($AvgActiveDayBytes / $BytesPerGB, 2)
$PeakDay          = $DailySummary | Sort-Object Total_Bytes -Descending | Select-Object -First 1

# Sizing uses the active-day average so idle weekends don't underestimate workday needs
$ProjectedMonthlyGB  = [math]::Ceiling($AvgActiveDayBytes / $BytesPerGB * 30 * 1.15)
$AvgWorkdayMbps      = [math]::Round(($AvgActiveDayBytes * 8 / 1e6) / $SecondsIn8Hours, 2)
$RecommendedPlanMbps = [math]::Max(15, [math]::Ceiling($AvgWorkdayMbps * 8))

Write-Host "================ CAPACITY & BANDWIDTH SIZING SUMMARY ================" -ForegroundColor Cyan
Write-Host ("Total Wi-Fi Consumed ({0} days)      : {1} GB across {2} active days" -f $Days, $TotalPeriodGB, $ActiveDaysCount)
Write-Host ("Daily Average (Calendar {0}d / Active) : {1} GB/day  |  {2} GB/active day" -f $Days, $AvgCalendarDayGB, $AvgActiveDayGB)
Write-Host ("Peak Single-Day Consumption          : {0} GB ({1})" -f $PeakDay.Total_GB, $PeakDay.Date)
Write-Host ("Projected Monthly Quota (+15% buffer): {0} GB / month" -f $ProjectedMonthlyGB) -ForegroundColor Yellow
Write-Host ("8-Hr Workday Avg / Recommended Speed : {0} Mbps avg  |  {1}+ Mbps plan (8x avg, for bursts)" -f $AvgWorkdayMbps, $RecommendedPlanMbps) -ForegroundColor Yellow
Write-Host "`nTop 5 Data-Consuming Apps:" -ForegroundColor Cyan
$AppSummary | Select-Object -First 5 | Format-Table -AutoSize

Write-Host "Saved Daily Report : $DailyCsv" -ForegroundColor Green
Write-Host "Saved Apps Report  : $AppsCsv" -ForegroundColor Green
Write-Host "Completed: Wi-Fi usage report for $ComputerName." -ForegroundColor Green
