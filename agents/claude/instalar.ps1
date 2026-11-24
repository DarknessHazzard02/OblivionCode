# Made by: Hazzard
# Instala la configuración de Claude Code en la raíz del repo, copiando desde agents/claude/.
# Lo instalado está en .gitignore: se edita en agents/claude/, nunca en la copia.
param(
    [string]$Repo = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [switch]$Quitar
)
$ErrorActionPreference = "Stop"
$Origen = $PSScriptRoot

$Pares = @(
    @{ Origen = "CLAUDE.md"; Destino = "CLAUDE.md" },
    @{ Origen = "skills"; Destino = ".claude\skills" },
    @{ Origen = "agents"; Destino = ".claude\agents" },
    @{ Origen = "settings.json"; Destino = ".claude\settings.json" }
)

foreach ($p in $Pares) {
    $destino = Join-Path $Repo $p.Destino
    if (Test-Path -LiteralPath $destino) { Remove-Item -LiteralPath $destino -Recurse -Force }
    if ($Quitar) { Write-Host "Quitado: $($p.Destino)"; continue }
    $padre = Split-Path -Parent $destino
    if ($padre -and -not (Test-Path -LiteralPath $padre)) { New-Item -ItemType Directory -Force -Path $padre | Out-Null }
    Copy-Item -LiteralPath (Join-Path $Origen $p.Origen) -Destination $destino -Recurse -Force
    Write-Host "Instalado: $($p.Destino)"
}

if (-not $Quitar) {
    $hook = Join-Path $Repo ".git\hooks\pre-commit"
    if (-not ((Test-Path $hook) -and (Select-String -Path $hook -Pattern "candado-personal" -Quiet))) {
        Write-Warning "El candado de git no está instalado: python agents/_comun/candado/instalar.py"
    }
}
