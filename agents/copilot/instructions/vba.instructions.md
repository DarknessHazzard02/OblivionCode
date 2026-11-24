---
applyTo: "**/*.{bas,cls,frm,vba}"
description: "Estándar de VBA"
---

# VBA

Detalle: skill `estandares-codigo §2`.

- `Option Explicit` en la primera línea.
- `On Error GoTo ErrorHandler`; el handler restaura `Application` y dice qué falló.
- Banners: Variable Declaration → Application Settings → Logic → Restore Application Settings.
- `ScreenUpdating`, `Calculation` y `EnableEvents` se restauran siempre, también en el handler.
- PascalCase descriptivo; `ListObject` en vez de rangos fijos.
- Firma `'Made by: Hazzard` en la última línea, después de `End Sub`.
