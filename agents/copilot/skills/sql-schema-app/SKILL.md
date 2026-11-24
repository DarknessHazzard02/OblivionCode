---
name: sql-schema-app
description: Convenciones para las bases de datos de las apps de Haz - cómo se nombran las tablas (HZ_<APP>_<TABLA>, por ejemplo HZ_SOLICITUDES_REGISTRO), catálogos, bitácoras, y cómo se conecta una app a SQL Server sin guardar credenciales. Úsala SIEMPRE que se cree, nombre, renombre o documente una tabla, vista o esquema de una app propio, o se escriba un CREATE TABLE, una migración, un modelo de datos o un diccionario de datos. También cuando se mencione SQL Server, base de datos, BD, tabla, esquema, cadena de conexión, connection string, ODBC, pyodbc, SQLAlchemy, migración, catálogo, bitácora, la app de Solicitudes, o cuando haya que llevar las tablas de una app a Fabric.
---

# Bases de datos de las apps — Hazzard

> Adaptado de experiencia laboral, ofuscado: rutas, GUIDs, nombres y sistemas son marcadores (`<GUID>`, `<lakehouse>`, `\\Servidor\Recurso`).

> Reglas base (cierre `Lo que tienes que hacer`, credenciales, sin firma de IA, avisar y parar): skill `estandar-hazzard`.

Aplica a todos los proyectos de Haz. Cubre las apps que **escriben**
datos (captura, flujos, bitácoras) en una base de SQL Server de seguridad. Los tableros del
portal solo leen JSON y no llevan base: eso está en `seguridad-web`.

---

## 1. Nombre de las tablas: `HZ_<APP>_<TABLA>`

| Parte | Qué es | Ejemplo |
|---|---|---|
| `LOG` | fijo: **Logística**. Distingue nuestras tablas de las de otras áreas en la misma instancia de seguridad | `LOG` |
| `<APP>` | el nombre corto de la app, **el mismo en todas sus tablas** | `ANOMALIAS` |
| `<TABLA>` | qué guarda la tabla | `REGISTRO` |

Reglas:

- **MAYÚSCULAS, ASCII, separadas por `_`.** Sin acentos, sin `Ñ`, sin espacios ni
  guiones: `HZ_SOLICITUDES_MODO_FALLA`, no `Log_Solicitudes_Modo Falla`. Un acento en un
  nombre de tabla se rompe en el primer driver o en la primera copia a Fabric.
- **Singular**, como entidad: `HZ_SOLICITUDES_PROVEEDOR`, no `..._PROVEEDORES`.
- **Catálogos con `CAT_`** al inicio de la tabla: `HZ_SOLICITUDES_CAT_MODO_FALLA`. Así
  se separan de las tablas transaccionales a simple vista, y se sabe cuáles administra
  el admin de la app.
- **Bitácora de cambios con `BITACORA`**: `HZ_SOLICITUDES_BITACORA`. Toda app que
  escribe tiene una: quién, cuándo, qué registro, qué cambió.
- **Vistas con `VW_`** después de la app: `HZ_SOLICITUDES_VW_KPI_PROVEEDOR`.
- **El nombre de la app no cambia después del primer despliegue.** Renombrar tablas
  rompe las copias a Fabric, los reportes y los permisos que dio seguridad.

### Ejemplo: Solicitudes

```
HZ_SOLICITUDES_REGISTRO            la anomalía, una por folio
HZ_SOLICITUDES_ADJUNTO             fotos y documentos (la ruta del archivo, no el archivo)
HZ_SOLICITUDES_ESTATUS_HISTORIAL   cada cambio de estatus, para medir antigüedad por etapa
HZ_SOLICITUDES_BITACORA            quién cambió qué
HZ_SOLICITUDES_CAT_MODO_FALLA      catálogo ES/EN con su categoría y área responsable
HZ_SOLICITUDES_CAT_PROVEEDOR
HZ_SOLICITUDES_CAT_AREA
HZ_SOLICITUDES_CAT_LUGAR_ARRIBO
```

### Columnas

- **MAYÚSCULAS y `_`**, igual que las tablas: `FECHA_APERTURA`, `USUARIO_CAPTURA`.
- **Llave primaria `ID`**; llaves foráneas `ID_<TABLA>`: `ID_MODO_FALLA`.
- **Fechas en `DATETIME2`**, y el nombre dice si es UTC: `FECHA_CREACION_UTC`. Sin eso,
  una fecha guardada en UTC sale un día corrida en el tablero.
- **Textos que el usuario ve en dos idiomas, en dos columnas**: `NOMBRE_ES`,
  `NOMBRE_EN`. Nunca una traducción calculada aparte (el `#N/A` de la bitácora de Excel
  salió de ahí).

---

## 2. En Fabric se llaman igual

Cuando una tabla de la app se copie al lakehouse, **conserva su nombre**:
`HZ_SOLICITUDES_REGISTRO` en SQL Server es `HZ_SOLICITUDES_REGISTRO` en `<lakehouse>`.
El prefijo dice de dónde salió igual que `SAP_` en las tablas de SAP. Si hace falta una
versión limpia, lleva `_CLEAN` al final, como las de SAP.

---

## 3. ⛔ Conexión sin credenciales

- **La app entra a SQL Server con Windows Authentication**, con la cuenta de servicio
  del pool de IIS (`Trusted_Connection=yes`). En la configuración solo van servidor y
  base; **ningún usuario ni contraseña de SQL**.
- Si seguridad solo ofrece usuario y contraseña de SQL, **se detiene y se habla con Haz**
  (credenciales): esa credencial terminaría en un archivo del servidor.
- **La cuenta de la app tiene solo lo que necesita**: leer y escribir sus tablas
  `HZ_<APP>_*`. Nada de `db_owner` ni `sysadmin` para correr.
- **Los usuarios no se guardan con contraseña.** El usuario sale de Windows (IIS) y el
  rol sale de su grupo de AD.
- **Nada de datos reales en el repo**: ni un `.bak`, ni un export, ni un script de carga
  con proveedores reales. Los datos de prueba son inventados y su carpeta lleva
  `CONTRATO.md` (datos).
- **Consultas siempre con parámetros**, nunca armadas concatenando texto. Un nombre de
  proveedor con un apóstrofo es suficiente para romper una consulta concatenada, y
  cualquiera que capture puede inyectar SQL.

---

## Checklist antes del PR

- [ ] Toda tabla nueva cumple `HZ_<APP>_<TABLA>`, en mayúsculas y sin acentos
- [ ] Catálogos con `CAT_`, vistas con `VW_`, y la app tiene su `BITACORA`
- [ ] Ninguna cadena de conexión con usuario o contraseña; `Trusted_Connection=yes`
- [ ] Todas las consultas van parametrizadas
- [ ] Los datos de prueba son inventados y su carpeta tiene `CONTRATO.md`
