# Made by: Hazzard
# Instala las extensiones de extensions.txt. Con -Limpiar, antes desinstala las que no estén en la lista.
param(
    [string]$ExtensionsFile,
    [switch]$Limpiar
)

$ErrorActionPreference = "Stop"

if (-not $ExtensionsFile) {
    $baseDir = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }
    $ExtensionsFile = Join-Path $baseDir "extensions.txt"
}
if (-not (Get-Command code -ErrorAction SilentlyContinue)) {
    Write-Error "El CLI 'code' no está en el PATH. En VS Code: 'Shell Command: Install code command in PATH'."
    exit 1
}
if (-not (Test-Path -LiteralPath $ExtensionsFile)) {
    Write-Error "No encuentro la lista: $ExtensionsFile"
    exit 1
}

$target = Get-Content -LiteralPath $ExtensionsFile |
    ForEach-Object { $_.Trim() } |
    Where-Object { $_ -and -not $_.StartsWith("#") }

if ($Limpiar) {
    $sobran = @(code --list-extensions) | Where-Object { $target -notcontains $_ }
    foreach ($ext in $sobran) {
        Write-Host "Desinstalando $ext" -ForegroundColor DarkYellow
        code --uninstall-extension $ext | Out-Null
    }
}

$i = 0
foreach ($ext in $target) {
    $i++
    Write-Host "[$i/$($target.Count)] $ext" -ForegroundColor Gray
    code --install-extension $ext --force | Out-Null
}

$instaladas = @(code --list-extensions)
$faltan = @($target | Where-Object { $instaladas -notcontains $_ })
Write-Host "`nListo: $($target.Count - $faltan.Count) de $($target.Count) instaladas." -ForegroundColor Green
if ($faltan.Count -gt 0) { Write-Warning "No quedaron instaladas: $($faltan -join ', ')" }
