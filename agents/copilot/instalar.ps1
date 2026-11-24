# Made by: Hazzard
# Instala la configuración de GitHub Copilot en la raíz del repo, copiando desde agents/copilot/.
# Lo instalado está en .gitignore: se edita en agents/copilot/, nunca en la copia.
param(
    [string]$Repo = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [switch]$Quitar
)
$ErrorActionPreference = "Stop"
$Origen = $PSScriptRoot

$Pares = @(
    @{ Origen = "copilot-instructions.md"; Destino = ".github\copilot-instructions.md" },
    @{ Origen = "instructions"; Destino = ".github\instructions" },
    @{ Origen = "prompts"; Destino = ".github\prompts" },
    @{ Origen = "agents"; Destino = ".github\agents" },
    @{ Origen = "skills"; Destino = ".github\skills" },
    @{ Origen = "hooks"; Destino = ".github\hooks" }
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
