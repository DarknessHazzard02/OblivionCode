"""Sube items de Fabric por el protocolo git, sin working tree.

    python push_git.py <rama> <titulo> <archivo-con-el-mensaje> <ruta> [<ruta> ...]

Reemplaza a `push.py`, que usaba la Git Data API de GitHub. esa API contesta **404 en todo lo que sea datos de git** (`git/ref`, `git/blobs`,
`commits`, `branches`, `tarball`) con el mismo token que sí lee la metadata del
repo y los pull requests. El protocolo git funciona sin problema, así que se
trabaja por ahí.

Tampoco se puede clonar normal: el repo tiene nombres de item que Windows no
puede crear (espacios al final, `&#32;`), el checkout queda incompleto y un
`git add -A` en ese estado borraría cientos de archivos. La solución es
`--no-checkout` + plumbing: el índice se arma a mano y el working tree nunca se
materializa, así que esos nombres nunca tocan el disco.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO_URL = "https://github.com/<org>/<repo-fabric>.git"  # migrado desde repo-fabric-anterior (ya no existe)
BASE_BRANCH = "fabric"
ORIGEN = Path(__file__).parent / "fabric"
# Fuera de cualquier repo con junction: si viviera dentro del clon de skills,
# el `git pull` del hook de auto-actualizacion chocaria con el clon interno.
CLON = Path.home() / ".claude" / "fabrepo-git"
# ⛔ SIN FIRMA. Ni trailer de co-autoria en el commit, ni pie en el cuerpo
# del PR. Decision del equipo (Haz): el trabajo sale a nombre
# de quien lo empuja y de nadie mas, y aplica igual para los demás.
# Si vuelves a ver un "Co-Authored-By" o un "Generated with" aqui,
# quitalo: no es un descuido de formato.

def git(*args, entrada=None):
    r = subprocess.run(["git", "-C", str(CLON), *args], capture_output=True,
                       text=True, encoding="utf-8", input=entrada)
    if r.returncode:
        sys.exit(f"ERROR git {' '.join(args[:3])}\n{r.stderr[:600]}")
    return r.stdout.strip()

def _bytes_en_la_rama(base, ruta):
    """El contenido que la rama YA tiene en esa ruta, en crudo. None si es nuevo."""
    r = subprocess.run(["git", "-C", str(CLON), "cat-file", "-p", f"{base}:{ruta}"],
                       capture_output=True)
    return r.stdout if r.returncode == 0 else None

def git_bytes_hash(datos):
    """`hash-object` con la entrada en BYTES.

    En texto, Windows traduce los saltos de linea al escribir en la tuberia y el
    archivo llega al repo con otros terminadores que los que tiene en disco.

    Y en BYTES quiere decir TAL CUAL. Los notebooks de Fabric traen los saltos
    MEZCLADOS a proposito: el andamiaje `# META` / `# CELL` va con LF y el
    codigo con CRLF. Uniformarlos —aunque sea "al estilo de la rama"— reescribe
    setenta lineas de andamiaje en cada empuje, y el cambio de verdad se pierde
    entre ellas: el PR #71 salio con 211 lineas para un cambio de seis. La
    herramienta no opina sobre el formato; el espejo local guarda la verdad.
    """
    r = subprocess.run(["git", "-C", str(CLON), "hash-object", "-w", "--stdin"],
                       input=datos, capture_output=True)
    if r.returncode:
        sys.exit(f"ERROR git hash-object\n{r.stderr[:400]}")
    return r.stdout.decode().strip()

def main():
    if len(sys.argv) < 5:
        sys.exit(__doc__)
    rama, titulo, msg_file, *rutas = sys.argv[1:]
    cuerpo = Path(msg_file).read_text(encoding="utf-8").strip()

    if not CLON.exists():
        subprocess.run(["git", "clone", "--no-checkout", "--depth", "1",
                        "--branch", BASE_BRANCH, REPO_URL, str(CLON)], check=True)
    else:
        git("fetch", "--depth", "1", "origin", BASE_BRANCH)
        git("update-ref", f"refs/heads/{BASE_BRANCH}", "FETCH_HEAD")

    base = git("rev-parse", BASE_BRANCH)
    print(f"{BASE_BRANCH} esta en {base[:7]}")

    # El indice se arma desde el arbol base, NO desde el disco: `git add` querria
    # leer el working tree que a proposito no existe.
    git("read-tree", base)

    archivos = []
    for rel in rutas:
        p = ORIGEN / rel
        if p.is_dir():
            archivos += sorted(q for q in p.rglob("*") if q.is_file())
        elif p.is_file():
            archivos.append(p)
        else:
            sys.exit(f"No existe {p}")

    for p in archivos:
        ruta = p.relative_to(ORIGEN).as_posix()
        # `read_text` normaliza cualquier salto de linea a "\n".
        sha = git_bytes_hash(p.read_bytes())
        git("update-index", "--add", "--cacheinfo", f"100644,{sha},{ruta}")
        print(f"  {sha[:7]}  {ruta}")

    tree = git("write-tree")
    commit = git("commit-tree", tree, "-p", base, "-m", cuerpo + "\n")
    print(f"arbol {tree[:7]}, commit {commit[:7]}")

    git("push", "origin", f"{commit}:refs/heads/{rama}")
    print(f"rama {rama} empujada")

    # Por REST, no con `gh pr create`: ese usa GraphQL, y GraphQL se cayo con
    # 503 en la misma tanda en que la Git Data API empezo a dar 404. La API
    # REST de pulls no se movio.
    r = subprocess.run(["gh", "api",
                        "-X", "POST", "repos/<org>/<repo-fabric>/pulls",
                        "--input", "-"],
                       input=json.dumps({
                           "title": titulo, "head": rama, "base": BASE_BRANCH,
                           "body": cuerpo}),
                       capture_output=True, text=True, encoding="utf-8", shell=True)
    if r.returncode:
        print("no pude abrir el PR:", r.stderr[:300])
        print(f"la rama {rama} ya quedo empujada; el PR se puede abrir a mano")
    else:
        d = json.loads(r.stdout)
        print(f"PR #{d['number']}: {d['html_url']}")

if __name__ == "__main__":
    main()
