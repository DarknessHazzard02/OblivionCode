$ParentFolder = "C:\Users\NMC08UG\OneDrive - Nidec\MASTER - MASTER\Reports"

# Get ALL subfolders recursively that match dd-MMM-yy
$DateFolders = Get-ChildItem -Path $ParentFolder -Directory -Recurse | Where-Object {
    $_.Name -match '^\d{2}-[A-Za-z]{3}-\d{2}$'
}

foreach ($Folder in $DateFolders) {

    # Parse folder name safely
    try {
        $ParsedDate = [datetime]::ParseExact($Folder.Name, "dd-MMM-yy", [System.Globalization.CultureInfo]::InvariantCulture)
        $DateStamp = $ParsedDate.ToString("yyyyMMdd")
    }
    catch {
        Write-Warning " Skipping invalid folder: $($Folder.FullName)"
        continue
    }

    # Rename files inside each detected folder
    Get-ChildItem -Path $Folder.FullName -Filter *.xlsx | Where-Object {
        $_.BaseName -notmatch '\d{8}$'
    } | ForEach-Object {

        $NewName = "$($_.BaseName)_$DateStamp$($_.Extension)"
        Rename-Item $_.FullName -NewName $NewName
    }

    Write-Output " Processed: $($Folder.FullName) → $DateStamp"
}