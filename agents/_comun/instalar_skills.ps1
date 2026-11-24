# Made by: Hazzard
# Copia las skills de un agente a una carpeta que comparten varios agentes (.agents\skills) sin pisar ni
# borrar las de otro. Cada agente lleva su lista en .instalado-<agente>.txt: al reinstalar o quitar,
# solo toca las carpetas de su lista que ningún otro agente reclama.
# Uso (desde el instalar.ps1 de cada agente):
#   . (Join-Path $PSScriptRoot "..\_comun\instalar_skills.ps1")
#   Install-SharedSkills -Origen <carpeta skills> -Destino <repo>\.agents\skills -Agente codex [-Quitar]

function Test-SkillName([string]$Nombre) {
    return ($Nombre -match '^[\w][\w.-]*$') -and ($Nombre -notmatch '\.\.')
}

function Get-SkillHash([string]$Carpeta) {
    $archivo = Join-Path $Carpeta "SKILL.md"
    if (Test-Path -LiteralPath $archivo) { return (Get-FileHash -LiteralPath $archivo -Algorithm SHA256).Hash }
    return ""
}

function Install-SharedSkills {
    param(
        [Parameter(Mandatory)][string]$Origen,
        [Parameter(Mandatory)][string]$Destino,
        [Parameter(Mandatory)][string]$Agente,
        [switch]$Quitar
    )
    # ===============================================
    # Lo que es de este agente y lo que es de otros
    # ===============================================
    $manifiesto = Join-Path $Destino ".instalado-$Agente.txt"
    $propias = @()
    if (Test-Path -LiteralPath $manifiesto) {
        $propias = @(Get-Content -LiteralPath $manifiesto | Where-Object { $_ -and (Test-SkillName $_) })
    }
    $ajenas = @()
    $hayManifiestos = $false
    if (Test-Path -LiteralPath $Destino) {
        $manifiestos = @(Get-ChildItem -LiteralPath $Destino -Filter ".instalado-*.txt" -File)
        $hayManifiestos = $manifiestos.Count -gt 0
        $ajenas = @($manifiestos | Where-Object { $_.FullName -ne $manifiesto } |
            ForEach-Object { Get-Content -LiteralPath $_.FullName } |
            Where-Object { $_ -and (Test-SkillName $_) })
    }
    # Instalación vieja, sin manifiestos: no se sabe de quién es cada carpeta. Al quitar no se borra nada
    # (pueden ser del otro agente); al instalar se adoptan las que este agente trae, que se vuelven a copiar.
    if (-not $hayManifiestos -and (Test-Path -LiteralPath $Destino) -and $Quitar) {
        Write-Warning "$Destino viene de una instalacion vieja sin manifiestos: no se borra nada. Reinstala los agentes que la usan y luego quita este."
        return
    }
    if (-not $hayManifiestos -and (Test-Path -LiteralPath $Destino)) {
        $deOrigen = @(Get-ChildItem -LiteralPath $Origen -Directory | ForEach-Object { $_.Name })
        $propias = @(Get-ChildItem -LiteralPath $Destino -Directory | Where-Object { $deOrigen -contains $_.Name } |
            ForEach-Object { $_.Name })
    }

    # ===============================================
    # Quitar lo propio que nadie más usa
    # ===============================================
    foreach ($nombre in $propias) {
        if ($ajenas -contains $nombre) { continue }
        $ruta = Join-Path $Destino $nombre
        if (Test-Path -LiteralPath $ruta) { Remove-Item -LiteralPath $ruta -Recurse -Force }
    }
    if ($Quitar) {
        if (Test-Path -LiteralPath $manifiesto) { Remove-Item -LiteralPath $manifiesto -Force }
        Write-OrphanSkills -Destino $Destino
        if ((Test-Path -LiteralPath $Destino) -and -not (Get-ChildItem -LiteralPath $Destino -Force)) {
            Remove-Item -LiteralPath $Destino -Force
        }
        $compartidas = @($propias | Where-Object { $ajenas -contains $_ })
        Write-Host "Quitado: skills de $Agente en $Destino ($($compartidas.Count) se quedan porque otro agente las usa)"
        return
    }

    # ===============================================
    # Copiar carpeta por carpeta
    # ===============================================
    New-Item -ItemType Directory -Force -Path $Destino | Out-Null
    $instaladas = @()
    foreach ($carpeta in Get-ChildItem -LiteralPath $Origen -Directory) {
        $dest = Join-Path $Destino $carpeta.Name
        if (Test-Path -LiteralPath $dest) {
            if (($ajenas -contains $carpeta.Name) -and ((Get-SkillHash $dest) -ne (Get-SkillHash $carpeta.FullName))) {
                Write-Warning "$($carpeta.Name): otro agente la instalo con otro SKILL.md; queda la version de $Agente"
            }
            Remove-Item -LiteralPath $dest -Recurse -Force
        }
        Copy-Item -LiteralPath $carpeta.FullName -Destination $dest -Recurse -Force
        $instaladas += $carpeta.Name
    }
    Set-Content -LiteralPath $manifiesto -Value $instaladas -Encoding utf8
    Write-Host "Instalado: $($instaladas.Count) skills de $Agente en $Destino"
    Write-OrphanSkills -Destino $Destino
}

function Write-OrphanSkills([string]$Destino) {
    # Carpetas que ningún manifiesto reclama: restos de una instalación vieja o de una skill que se borró
    if (-not (Test-Path -LiteralPath $Destino)) { return }
    $reclamadas = @(Get-ChildItem -LiteralPath $Destino -Filter ".instalado-*.txt" -File |
        ForEach-Object { Get-Content -LiteralPath $_.FullName } | Where-Object { $_ })
    $huerfanas = @(Get-ChildItem -LiteralPath $Destino -Directory | Where-Object { $reclamadas -notcontains $_.Name } |
        ForEach-Object { $_.Name })
    if ($huerfanas.Count -gt 0) {
        Write-Warning "Skills sin duenio en ${Destino}: $($huerfanas -join ', '). Borralas a mano si ya no se usan."
    }
}
