# Reparto del trabajo de pruebas — equipo Jeyson, Mateo y Keyner

> Plan de referencia: `pruebasdesoftware.md` (PP-DAM-2026-001). Cada integrante trabaja en **su propia rama**
> y aporta pruebas + cambios al repositorio; la integración a `master` se hace después por Pull Request.

**Dos grupos distintos de personas**
- *Creadores originales del dashboard* (solo referencia): Camilo Carmona, Keyner Gil, Jeyson González, Marisol Roche.
- *Equipo de pruebas* (quien ejecuta este plan): Jeyson González, Mateo y Keyner Gil.

## Estado de partida (revisado el 13/11/2026)
| Elemento | Estado |
|---|---|
| Plan de pruebas (secciones 1–8 de la guía del profesor) | Completo en `master`: 17 riesgos de producto, 5 de proyecto, 12 condiciones, 34 casos, trazabilidad. |
| Código de pruebas (`tests/`) | **No existía** en ninguna rama. |
| Resultados de ejecución / defectos | **No existen** todavía. |
| Versión bajo prueba (`260f905a`) | Vigente: no hay cambios en `dashboard.py`, Excel, GeoJSON ni `requirements.txt` hasta `master` actual. |

## Reparto de casos de prueba (36 = 34 del plan + CP-35 y CP-36 nuevos)
| Integrante | Rol (plan §7.1) | Casos | Aporte al repositorio |
|---|---|---|---|
| **Keyner** | Ingeniero de pruebas automatizadas | CP-01–05, 08–14, 17, 18 (automatizados), CP-35, 36 (nuevos), CP-32 (instalación limpia) | `tests/` con pytest (ya redactado en este paquete) |
| **Jeyson** | Líder de pruebas + gestión de defectos | CP-06, 07 (matching GeoJSON↔Excel, riesgo **Crítico**), CP-15, 16, 19 (exactitud vs. hoja de referencia), CP-20–22 (carga de archivos) | `tests/test_integracion_geojson.py` + hoja de referencia DP-05 + Issues de defectos + informe final |
| **Mateo** | Ejecutor de pruebas de sistema | CP-23–28 (navegación/estados), CP-29–31 (selector y colores), CP-33, 34 (móvil y navegadores) | `docs/resultados-pruebas-sistema.md` (evidencia con capturas) y retirar `env/` y `node_modules/` del control de versiones (RP-02) |

## Por actualizar en `pruebasdesoftware.md` (versión 1.1)
1. §1.2: separar *Autores del proyecto original* de *Autores del plan de pruebas*.
2. §2.3, §3.3 (R-02), §3.4, §7.1: hoy dicen "equipo de 4 personas" y asignan roles a Camilo y Marisol → reasignar a Jeyson, Mateo y Keyner.
3. §5.3: agregar CP-35 y CP-36 a la matriz (R-02 → CDP-03 → CP-35; R-04 → CDP-06 → CP-36).
4. §6.2: **la capacidad ya no alcanza** → ver decisión pendiente.

## Decisiones pendientes del equipo
- **Capacidad:** el plan estima 84 h-persona (96 con contingencia) y asume 4 personas × 8 h × 3 semanas = 96 h.
  Con 3 personas a 8 h/semana hay 72 h. Opciones: subir a ≈ 11 h/semana por persona, o recortar el alcance de
  los riesgos Medios (CP-29–34) y documentarlo en el *tailoring* (§2.3).
- **Defecto DEF-001 (R-04):** con estrato decimal (`1.0`) la etiqueta sale `1.0` y el filtro queda vacío
  (`str(x).isdigit()`). Hoy es **latente**: el Excel guarda enteros. Decidir si se corrige o se acepta el riesgo.
- **`env/` y `node_modules/` versionados:** 8 192 archivos en `master` pese al `.gitignore`.
