# Made by: Hazzard
# Instala la configuración de Gemini CLI / Antigravity en la raíz del repo, copiando desde agents/gemini/.
# Lo instalado está en .gitignore: se edita en agents/gemini/, nunca en la copia.
param(
    [string]$Repo = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [switch]$Quitar
)
$ErrorActionPreference = "Stop"
$Origen = $PSScriptRoot

$Pares = @(
    @{ Origen = "GEMINI.md"; Destino = "GEMINI.md" },
    @{ Origen = "rules"; Destino = ".agents\rules" },
    @{ Origen = "workflows"; Destino = ".agents\workflows" },
    @{ Origen = "skills"; Destino = ".agents\skills" },
    @{ Origen = "commands"; Destino = ".gemini\commands" }
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

# Gemini CLI lee .gemini/settings.json: si ya existe uno que no es de aquí, se respalda.
if (-not $Quitar) {
    $gs = Join-Path $Repo ".gemini\settings.json"
    if (Test-Path $gs) { Copy-Item $gs "$gs.respaldo" -Force; Write-Host "Respaldo: .gemini\settings.json.respaldo" }
    New-Item -ItemType Directory -Force -Path (Join-Path $Repo ".gemini") | Out-Null
    Copy-Item (Join-Path $Origen "settings.json") $gs -Force
    Write-Host "Instalado: .gemini\settings.json"
}

if (-not $Quitar) {
    $hook = Join-Path $Repo ".git\hooks\pre-commit"
    if (-not ((Test-Path $hook) -and (Select-String -Path $hook -Pattern "candado-personal" -Quiet))) {
        Write-Warning "El candado de git no está instalado: python agents/_comun/candado/instalar.py"
    }
}
