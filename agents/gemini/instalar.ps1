# Made by: Hazzard
# Instala la configuración de Gemini CLI / Antigravity en la raíz del repo, copiando desde agents/gemini/.
# Lo instalado está en .gitignore: se edita en agents/gemini/, nunca en la copia.
param(
    [string]$Repo = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [switch]$Quitar
)
$ErrorActionPreference = "Stop"
$Origen = $PSScriptRoot

. (Join-Path $PSScriptRoot "..\_comun\instalar_skills.ps1")

$Pares = @(
    @{ Origen = "GEMINI.md"; Destino = "GEMINI.md" },
    @{ Origen = "rules"; Destino = ".agents\rules" },
    @{ Origen = "workflows"; Destino = ".agents\workflows" },
    @{ Origen = "commands"; Destino = ".gemini\commands" }
)

# .agents\skills lo comparte con Codex: se copia carpeta por carpeta, sin borrar las del otro
Install-SharedSkills -Origen (Join-Path $Origen "skills") -Destino (Join-Path $Repo ".agents\skills") -Agente "gemini" -Quitar:$Quitar

foreach ($p in $Pares) {
    $destino = Join-Path $Repo $p.Destino
    if (Test-Path -LiteralPath $destino) { Remove-Item -LiteralPath $destino -Recurse -Force }
    if ($Quitar) { Write-Host "Quitado: $($p.Destino)"; continue }
    $padre = Split-Path -Parent $destino
    if ($padre -and -not (Test-Path -LiteralPath $padre)) { New-Item -ItemType Directory -Force -Path $padre | Out-Null }
    Copy-Item -LiteralPath (Join-Path $Origen $p.Origen) -Destination $destino -Recurse -Force
    Write-Host "Instalado: $($p.Destino)"
}

# Gemini CLI lee .gemini/settings.json. Si ya existe uno que NO es de aquí, se respalda una sola vez:
# reinstalar no pisa el respaldo con la copia propia. -Quitar borra la copia propia y devuelve el respaldo.
$gs = Join-Path $Repo ".gemini\settings.json"
$respaldo = "$gs.respaldo"
$marca = "agents/_comun/flujo/guardias.py"
$esPropio = (Test-Path -LiteralPath $gs) -and (Select-String -LiteralPath $gs -Pattern $marca -SimpleMatch -Quiet)
# El instalador anterior respaldaba en cada corrida: un respaldo con la marca es una copia propia, no el original
if ((Test-Path -LiteralPath $respaldo) -and (Select-String -LiteralPath $respaldo -Pattern $marca -SimpleMatch -Quiet)) {
    Remove-Item -LiteralPath $respaldo -Force
    Write-Host "Borrado: .gemini\settings.json.respaldo era una copia propia, no el original"
}
if ($Quitar) {
    if ($esPropio) { Remove-Item -LiteralPath $gs -Force; Write-Host "Quitado: .gemini\settings.json" }
    if ((Test-Path -LiteralPath $respaldo) -and (Test-Path -LiteralPath $gs)) {
        Write-Warning ".gemini\settings.json ya no es la copia de este repo y hay un respaldo: no se toca ninguno. Revisalos a mano."
    } elseif (Test-Path -LiteralPath $respaldo) {
        Move-Item -LiteralPath $respaldo -Destination $gs -Force
        Write-Host "Devuelto: .gemini\settings.json desde el respaldo"
    }
    $carpeta = Join-Path $Repo ".gemini"
    if ((Test-Path -LiteralPath $carpeta) -and -not (Get-ChildItem -LiteralPath $carpeta -Force)) { Remove-Item -LiteralPath $carpeta -Force }
} else {
    if ((Test-Path -LiteralPath $gs) -and -not $esPropio) {
        if (Test-Path -LiteralPath $respaldo) {
            Write-Warning ".gemini\settings.json no es de este repo y ya hay un respaldo: no se pisa ninguno. Revisalos a mano."
            return
        }
        Copy-Item -LiteralPath $gs -Destination $respaldo
        Write-Host "Respaldo: .gemini\settings.json.respaldo"
    }
    New-Item -ItemType Directory -Force -Path (Join-Path $Repo ".gemini") | Out-Null
    Copy-Item -LiteralPath (Join-Path $Origen "settings.json") -Destination $gs -Force
    Write-Host "Instalado: .gemini\settings.json"
}

if (-not $Quitar) {
    $hook = Join-Path $Repo ".git\hooks\pre-commit"
    if (-not ((Test-Path $hook) -and (Select-String -Path $hook -Pattern "candado-personal" -Quiet))) {
        Write-Warning "El candado de git no está instalado: python agents/_comun/candado/instalar.py"
    }
}
