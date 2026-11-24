---
name: ofuscar-de-trabajo
description: Cómo pasar a este repo algo que nació de experiencia laboral (una consulta, una macro, un patrón, una skill o un aprendizaje) sin que lleve nada de la organización - qué se quita (empresa, plantas, códigos de planta, servidores, rutas, GUIDs, cifras internas, personas, transacciones propias), qué se conserva (tipos, restricciones, relaciones, la lección técnica) y cómo se verifica antes del commit. Úsala SIEMPRE que se vaya a copiar, adaptar, homologar o respaldar algo de trabajo en un repo de Haz, o cuando se diga "ofusca", "limpia esto para mi portafolio" o "quítale lo de la empresa".
---

# Ofuscar lo que viene de trabajo

**Nunca se copia tal cual.** Se reescribe: la lección técnica se queda y la identidad se va. Un respaldo literal de algo de la organización no entra a este repo.

## 1. Qué se quita y cómo se reemplaza

| Se quita | Se reemplaza por |
|---|---|
| Nombre de la empresa, marcas, dominios | `ERP_CORP`, `example.com` |
| Plantas y códigos de planta | `Plant_A`, `Plant_B` |
| Servidores, rutas UNC, unidades mapeadas, rutas de usuario | `\\Servidor\Recurso`, `C:\ruta\a\la\carpeta` |
| GUIDs de workspaces, lakehouses, conexiones | `<GUID>`, `<lakehouse>` |
| Transacciones y tablas propias (las `Z*`) | `ZXX_<tema>`; las estándar (MB52, COOIS, MD04) se quedan |
| Personas: nombres, correos, usuarios, IDs | Se eliminan; si hace falta un rol, `<responsable>` |
| Cifras internas (volúmenes, costos, clientes) | Valores inventados del mismo orden |
| Nombres de tableros, apps, repos y organizaciones | Nombres genéricos (`Inventory_Coverage`, `<repo-portal>`) |

```sql
-- Original:  SELECT OrderQty FROM <EMPRESA>.dbo.SAP_MB52 WHERE Plant = '<PLANTA_REAL>'
-- Ofuscado:  SELECT OrderQty FROM ERP_CORP.dbo.Inventory_MB52 WHERE Plant = 'Plant_A'
```

## 2. Qué se conserva

Tipos, restricciones, relaciones, el orden de los pasos, los errores conocidos y por qué pasaron. Eso es lo que vale para el portafolio.

## 3. Nivel

| Nivel | Cuándo | Resultado |
|---|---|---|
| **Homologado** | Vale la pena la profundidad (una ingesta, un estándar de tableros) | Misma estructura y lecciones, reescrito y ofuscado; nota al inicio: *"Adaptado de experiencia laboral, ofuscado."* |
| **Patrón** | Solo importa la idea | Pocas líneas genéricas |

## 4. Verificar antes del commit

1. Buscar en el diff: nombre de la empresa, plantas, `\\`, unidades `X:\`, `@` con dominio, GUIDs (`[0-9a-f]{8}-[0-9a-f]{4}-`), `Z[A-Z]{2,}` propias, nombres de personas.
2. Que no quede ningún marcador roto **dentro de código** (`<carpeta>` donde iba `n:` o `Scripts\pip`): compilar o correr lo que se tocó.
3. El candado aplica sus reglas privadas (fuera del repo) sobre las líneas agregadas.
4. Lo ya publicado **no se arregla** con un commit nuevo: sigue en el historial. Eso lo decide Haz.
