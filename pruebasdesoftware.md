# Plan de Pruebas — Dashboard Ambiental Medellín

> Documento elaborado según la estructura de **ISO/IEC/IEEE 29119-3:2021** (*Software and systems engineering — Software testing — Part 3: Test documentation*), con adaptación (*tailoring*) declarada en la sección 2.3.

---

## 1. Información Específica del Documento

### 1.1 Identificador único del documento

| Campo | Valor |
|---|---|
| Identificador | `PP-DAM-2026-001` |
| Título | Plan de Pruebas del Dashboard Ambiental Medellín |
| Tipo de documento | Plan de Pruebas de Proyecto (*Project Test Plan*) |
| Versión | 1.1 |
| Estado | Borrador para aprobación |
| Fecha de emisión | 10/11/2026 (v1.1: 13/11/2026) |
| Ubicación | Repositorio `jeyson4013/Analisis_ambiental` — archivo `pruebasdesoftware.md` |

### 1.2 Organización emisora y autores

- **Organización emisora:** Equipo de desarrollo del proyecto *Análisis Ambiental — Percepción Ambiental Ciudadana de Medellín*.
- **Autores del proyecto original** (desarrollo del dashboard en el PIA de Inteligencia de Negocios; se citan como referencia):
  - Camilo Carmona
  - Keyner Gil
  - Jeyson González
  - Marisol Roche
- **Autores del plan de pruebas** (curso Pruebas de Software; responsables de este documento y de su ejecución):
  - Jeyson González
  - Mateo
  - Keyner Gil

### 1.3 Autoridad de aprobación

| Rol | Nombre | Responsabilidad | Firma / Fecha |
|---|---|---|---|
| Asesor(a) académico(a) | Ingry Gómez | Aprobación del plan y de los criterios de finalización | |
| Asesor académico | Juan Zapata | Aprobación del plan y revisión del informe de cierre | |
| Líder de pruebas | Jeyson González | Elaboración y mantenimiento del plan | |

### 1.4 Historial de cambios y control de versiones

| Versión | Fecha | Autor | Descripción del cambio |
|---|---|---|---|
| 0.1 | 10/11/2026 | Equipo de desarrollo | Creación del borrador inicial con base en las directrices del docente. |
| 1.0 | 10/11/2026 | Jeyson González | Plan completo publicado en `master` (PR #2). Pendiente de aprobación. |
| 1.1 | 13/11/2026 | Keyner Gil | Equipo de pruebas de 3 personas (§1.2, §2.3, §3.3, §3.4, §7.1); capacidad recalculada (§6.2); nuevos casos CP-35 y CP-36 (§5.3); preparación de pruebas unitarias implementada en `tests/conftest.py` (§5.4); Anexo A con la primera ejecución de las pruebas automatizadas y el defecto DEF-001. |

El documento se versiona en Git junto al código fuente. Cada modificación se realiza mediante *commit* con mensaje descriptivo y, para cambios de alcance, mediante *Pull Request* revisado por al menos un integrante distinto del autor.

---

## 2. Introducción y Declaración de Adaptación (Tailoring)

### 2.1 Alcance del documento

Este plan define el enfoque, los recursos, el cronograma y las actividades de prueba del **Dashboard Ambiental Medellín**, una aplicación web desarrollada en Python/Streamlit que visualiza sobre un mapa interactivo la percepción ciudadana de cinco variables ambientales (Aire, Ríos, Ruido, Basuras y Contaminación Visual), a partir de la Encuesta de Calidad de Vida 2025 de *Medellín Cómo Vamos*.

El plan cubre el ciclo de pruebas de **3 semanas** sobre la versión del código en la rama `master` (commit `260f905a`), e incluye: gestión de riesgos, diseño de condiciones y casos de prueba, trazabilidad, entorno, criterios de suspensión/finalización, estimaciones, roles y cronograma.

### 2.2 Referencias documentales

| ID | Documento |
|---|---|
| REF-01 | ISO/IEC/IEEE 29119-1:2022 — Conceptos y definiciones. |
| REF-02 | ISO/IEC/IEEE 29119-2:2021 — Procesos de prueba. |
| REF-03 | ISO/IEC/IEEE 29119-3:2021 — Documentación de pruebas. |
| REF-04 | ISO/IEC/IEEE 29119-4:2021 — Técnicas de prueba. |
| REF-05 | Directrices del docente: "Estructura Actualizada del Plan de Pruebas (Basada en ISO/IEC/IEEE 29119-3)". |
| REF-06 | Código fuente: `dashboard.py`, `requirements.txt`, `medellin_debug.geojson`, `ECV_2025_Limpio.xlsx`, `assets/qrPIA.jpeg`. |
| REF-07 | Medellín Cómo Vamos. *Medellín se mide: Calidad de Vida y Percepción Ciudadana 2025*. |
| REF-08 | Documentación oficial de Streamlit, Folium/streamlit-folium y Plotly Express. |

### 2.3 Conformidad y Adaptación (Tailoring)

**Declaración:** El proyecto **NO** aplica la norma ISO/IEC/IEEE 29119 de forma íntegra. Se declara **conformidad adaptada** (*tailored conformance*) conforme a lo permitido por la propia norma, justificada por:

1. **Nivel de criticidad del software: BAJO.** El dashboard es una herramienta académica de visualización y consulta. No procesa transacciones, no gestiona datos personales identificables, no controla procesos físicos ni toma decisiones automatizadas que afecten a personas. Un fallo produce, en el peor caso, una visualización incorrecta o una interrupción del servicio.
2. **Restricciones del proyecto:** ciclo de pruebas de **3 semanas**, equipo de pruebas de 3 personas con dedicación parcial, sin presupuesto para herramientas comerciales ni entornos dedicados.

**Procesos y documentos que se mantienen:**

| Proceso / Documento 29119 | Aplicación |
|---|---|
| Plan de Pruebas (29119-3 §7.2) | Íntegro (este documento). |
| Evaluación de riesgos (29119-2 TP3/TP4) | Íntegro (sección 4). |
| Diseño e implementación de pruebas (29119-2 TD1–TD4) | Íntegro: condiciones, técnicas, casos y trazabilidad (sección 5). |
| Ejecución y registro de incidencias (29119-2 TE1–TE3) | Simplificado: registro en *Issues* de GitHub. |
| Informe de finalización de pruebas | Simplificado: un único informe al cierre del ciclo. |

**Procesos excluidos o reducidos y riesgo asumido:**

| Proceso excluido / reducido | Justificación | Riesgo asumido |
|---|---|---|
| Política de Pruebas Organizacional y Estrategia Organizacional (29119-2, nivel organizacional) | No existe una organización permanente; es un proyecto académico único. | Falta de lineamientos corporativos; se mitiga adoptando este plan como única referencia. |
| Planes de prueba por nivel separados (unitario, integración, sistema) | Se consolidan en un único plan de proyecto por el tamaño del sistema (un solo módulo `dashboard.py`). | Menor detalle por nivel; posible omisión de casos de integración finos. |
| Especificaciones separadas de diseño, casos y procedimientos (29119-3 §8.2–8.4) | Se integran en la matriz de trazabilidad de la sección 5.3. | Menor granularidad documental; mitigado con IDs únicos y trazabilidad completa. |
| Informes de estado periódicos (*Test Status Report*) | Sustituidos por seguimiento semanal en reunión de equipo. | Menor visibilidad formal del avance intermedio. |
| Pruebas de rendimiento con carga concurrente, seguridad avanzada (pentesting) y accesibilidad formal (WCAG) | Fuera del alcance de 3 semanas y de la criticidad del producto. | Posibles degradaciones con muchos usuarios concurrentes o barreras de accesibilidad no detectadas. Riesgo **aceptado** (ver R-14, R-15). |
| Automatización completa de pruebas de interfaz (Selenium/Playwright) | Costo de configuración elevado para el ciclo disponible. | Las pruebas de UI dependen de ejecución manual, con mayor posibilidad de error humano. |

### 2.4 Glosario

| Término | Definición |
|---|---|
| **Caso de prueba (CP)** | Conjunto de precondiciones, entradas y resultados esperados diseñado para verificar una condición de prueba. |
| **Condición de prueba (CDP)** | Aspecto evaluable de un elemento de prueba derivado de un riesgo. |
| **Comuna / Corregimiento** | División administrativa urbana / rural de Medellín. |
| **ECV 2025** | Encuesta de Calidad de Vida 2025 (fuente de datos `ECV_2025_Limpio.xlsx`). |
| **Estrato** | Clasificación socioeconómica de la vivienda (1 a 6). |
| **Exposición al riesgo** | Resultado de combinar Probabilidad × Impacto de un riesgo. |
| **Fuzzy matching** | Coincidencia aproximada de cadenas (`difflib.get_close_matches`) usada para emparejar nombres de barrios/comunas entre GeoJSON y Excel. |
| **GeoJSON** | Formato de datos geoespaciales (`medellin_debug.geojson`) con los polígonos de barrios. |
| **Modal** | Ventana emergente (`st.dialog`) con estadísticas, detalle de variable, QR o "Acerca de". |
| **Percepción negativa** | Porcentaje de respuestas clasificadas como "Mala" o "Muy mala". |
| **RBT** | *Risk-Based Testing*, pruebas basadas en riesgo. |
| **Session state** | Estado de sesión de Streamlit (`st.session_state`) que conserva la navegación del usuario entre re-ejecuciones. |
| **AVL / PCE / TE** | Análisis de Valores Límite / Partición de Clases de Equivalencia / Transición de Estados. |

---

## 3. Contexto de las Pruebas

### 3.1 Elementos de prueba (Test items)

| ID | Elemento | Descripción | Ubicación |
|---|---|---|---|
| TI-01 | Carga de datos | `cargar_datos()`: lectura del Excel, filtro por municipio "Medellín", normalización de "LAURELES" → "LAURELES ESTADIO", relleno de nulos. | `dashboard.py` |
| TI-02 | Carga de GeoJSON | `cargar_geojson()`: lectura del GeoJSON, cálculo de `barrio_limpio` y `comuna_limpia`, manejo de error. | `dashboard.py` |
| TI-03 | Normalización de texto | `limpiar()`: mayúsculas, eliminación de tildes y caracteres especiales. | `dashboard.py` |
| TI-04 | Emparejamiento difuso | `encontrar_mejor_match()` y mapeo jerárquico comuna/barrio GeoJSON ↔ Excel. | `dashboard.py` |
| TI-05 | Categorización | `map_categoria()`: recodificación de respuestas Likert a 6 categorías. | `dashboard.py` |
| TI-06 | Cálculos geométricos | `centroide_feature()` y `bounds_from_features()`. | `dashboard.py` |
| TI-07 | Selector de variables | `render_variable_btns()`: selección múltiple hasta 3 variables con opción "Todas". | `dashboard.py` |
| TI-08 | Mapa interactivo | Mapa Folium por comunas y por barrios, colores, tooltip, leyenda, marcador y límites de zoom. | `dashboard.py` |
| TI-09 | Estadísticas | `figuras_estadisticas_barrio()`: gráficos de % negativo, por estrato y distribución. | `dashboard.py` |
| TI-10 | Modales | Estadísticas del barrio, detalle por variable, QR y "Acerca de". | `dashboard.py` |
| TI-11 | Navegación | Flujo comunas → barrio → estadísticas → detalle → volver. | `dashboard.py` |
| TI-12 | Datos fuente | `ECV_2025_Limpio.xlsx`, `medellin_debug.geojson`, `assets/qrPIA.jpeg`. | Raíz del repositorio |
| TI-13 | Dependencias | `requirements.txt` (streamlit, pandas, plotly, requests, folium, streamlit-folium, openpyxl). | Raíz del repositorio |

### 3.2 Alcance y exclusiones de las pruebas

**Dentro del alcance:**
- Pruebas **unitarias** de funciones puras (TI-03, TI-04, TI-05, TI-06, TI-09) con `pytest`.
- Pruebas de **integración** de datos (Excel ↔ GeoJSON ↔ mapa).
- Pruebas de **sistema** funcionales de la interfaz (mapa, filtros, modales, navegación) ejecutadas manualmente.
- Pruebas de **compatibilidad** básica en Chrome, Firefox y Edge (escritorio) y un navegador móvil (acceso vía QR).
- Pruebas de **instalación/despliegue** desde un entorno limpio con `requirements.txt`.
- Verificación de **exactitud de datos** (porcentajes y conteos) contra cálculos independientes.

**Fuera del alcance (exclusiones):**
- Pruebas de carga y estrés con usuarios concurrentes.
- Pruebas de penetración y auditoría de seguridad formal.
- Certificación de accesibilidad WCAG.
- Validación estadística/metodológica de la encuesta ECV 2025 (responsabilidad de la fuente).
- Contenido textual de los análisis en `DETALLES_ANALISIS` y "Acerca de" (solo se verifica que se muestre).
- Librerías de terceros (Streamlit, Folium, Plotly) y servicios de mosaicos de mapa (CartoDB).
- Carpetas `scratch/`, `node_modules/` y `env/`.

### 3.3 Suposiciones y restricciones

**Suposiciones:**
- S-01: El archivo `ECV_2025_Limpio.xlsx` es la versión definitiva y ya está depurado.
- S-02: El GeoJSON contiene los polígonos válidos de los barrios y corregimientos de Medellín.
- S-03: Los evaluadores disponen de conexión a Internet (los mosaicos de CartoDB se cargan en línea).
- S-04: La versión bajo prueba se congela al inicio de la Semana 2; los cambios posteriores solo corrigen defectos.

**Restricciones:**
- R-01: Ciclo total de **3 semanas** (10/11/2026 – 28/11/2026).
- R-02: Equipo de pruebas de 3 personas (Jeyson González, Mateo, Keyner Gil) con dedicación parcial (≈ 8 h/semana por persona).
- R-03: Sin herramientas comerciales; solo software libre (`pytest`, GitHub Issues).
- R-04: La aplicación es un único script Streamlit, lo que dificulta pruebas unitarias aisladas (las funciones dependen de `st.session_state` y se ejecutan al importar el módulo).
- R-05: La carpeta `env/` versionada en el repositorio contiene rutas absolutas de otra máquina y no es reutilizable; cada evaluador debe crear su propio entorno virtual.

### 3.4 Partes interesadas

| Parte interesada | Interés en las pruebas |
|---|---|
| Asesores académicos (Ingry Gómez, Juan Zapata) | Calidad del producto y cumplimiento del proceso ISO 29119 adaptado. |
| Equipo de desarrollo original (Camilo Carmona, Keyner Gil, Jeyson González, Marisol Roche) | Conocer los defectos detectados y corregirlos antes de la entrega. |
| Equipo de pruebas (Jeyson González, Mateo, Keyner Gil) | Planificar, diseñar y ejecutar las pruebas; registrar defectos y su verificación. |
| Usuarios finales (ciudadanía, estudiantes, tomadores de decisiones) | Información correcta, navegación clara y disponibilidad en web/móvil. |
| Medellín Cómo Vamos (fuente de datos) | Representación fiel de los datos de la encuesta. |

---

## 4. Gestión de Riesgos y Matriz de Exposición (RBT)

### 4.1 Identificación de Riesgos

**Riesgos de producto**

| ID | Riesgo | Tipo | Elemento |
|---|---|---|---|
| R-01 | El emparejamiento difuso asigna un barrio del GeoJSON a una comuna o barrio incorrecto del Excel (p. ej., `cutoff=0.5` en comunas), mostrando datos de otra zona. | Funcional / exactitud | TI-04 |
| R-02 | `map_categoria()` clasifica mal respuestas (orden de evaluación "muy mala"/"mala", valores nulos, mayúsculas, "Regular"). | Funcional / exactitud | TI-05 |
| R-03 | El % de percepción negativa o los porcentajes por estrato se calculan de forma incorrecta (denominador incluye "No sabe", filtros de estrato mal aplicados). | Funcional / exactitud | TI-09 |
| R-04 | El estrato se almacena como número decimal (p. ej. `3.0`) y `str(x).isdigit()` falla: el filtro de estratos queda vacío y las etiquetas aparecen como "3.0". | Funcional | TI-09, TI-10 |
| R-05 | Fallo al cargar el Excel o el GeoJSON (archivo ausente, ruta relativa, columna renombrada) deja la aplicación sin mapa o sin datos. | Disponibilidad | TI-01, TI-02 |
| R-06 | El selector de variables no respeta el máximo de 3, o el comportamiento de "Todas" / deselección es inconsistente. | Funcional | TI-07 |
| R-07 | Transiciones de navegación inconsistentes en `session_state` (modal que no abre, abre dos veces, "Volver" pierde contexto, barrio de otra comuna queda seleccionado). | Funcional / usabilidad | TI-10, TI-11 |
| R-08 | Colores del mapa no corresponden a la categoría predominante del barrio o a la leyenda. | Funcional / visual | TI-08 |
| R-09 | Cálculo de centroides o límites erróneo (MultiPolygon, polígonos con huecos), ubicando el marcador fuera del barrio o restringiendo el zoom. | Funcional | TI-06, TI-08 |
| R-10 | El modal QR no muestra la imagen si falta `assets/qrPIA.jpeg` (el *fallback* base64 está vacío). | Funcional | TI-10 |
| R-11 | Inyección de HTML a través de nombres de barrio/comuna en bloques `unsafe_allow_html`. | Seguridad | TI-08, TI-10 |
| R-12 | Tiempos de carga inicial elevados (iteración fila a fila con `iterrows` sobre todo el dataset, GeoJSON grande). | Rendimiento | TI-01, TI-04 |
| R-13 | Incompatibilidad de versiones: `requirements.txt` sin versiones fijas; parámetros como `width="stretch"` o `st.dialog` requieren Streamlit reciente. | Instalación | TI-13 |
| R-14 | Degradación con múltiples usuarios concurrentes. | Rendimiento | Sistema |
| R-15 | Barreras de accesibilidad (contraste, navegación por teclado, lectores de pantalla). | Usabilidad | Sistema |
| R-16 | Visualización deficiente en dispositivos móviles (acceso por QR). | Compatibilidad | TI-08, TI-10 |
| R-17 | Textos estáticos de "Acerca de" inconsistentes con la lógica (3 categorías declaradas vs. 6 implementadas). | Documentación | TI-10 |

**Riesgos de proyecto**

| ID | Riesgo | Tipo |
|---|---|---|
| RP-01 | Tiempo insuficiente (3 semanas) para ejecutar todos los casos planificados. | Tiempo |
| RP-02 | Entorno no reproducible: `env/` versionado con rutas de otra máquina; diferencias entre equipos. | Entorno |
| RP-03 | Cambios de código durante la ejecución que invalidan resultados ya obtenidos. | Gestión de configuración |
| RP-04 | Disponibilidad parcial de los integrantes (otras asignaturas). | Personal |
| RP-05 | Baja experiencia del equipo en `pytest` y en pruebas de aplicaciones Streamlit. | Conocimiento |

### 4.2 Matriz de Análisis de Riesgos

**Escalas:**
- **Probabilidad (P):** 1 = Baja, 2 = Media, 3 = Alta.
- **Impacto (I):** 1 = Bajo (cosmético), 2 = Medio (funcionalidad degradada), 3 = Alto (datos erróneos o sistema inutilizable).
- **Exposición (E = P × I):** 9 = **Crítico**, 6 = **Alto**, 3–4 = **Medio**, 1–2 = **Bajo**.

**Matriz Probabilidad × Impacto:**

| P \ I | Impacto 1 (Bajo) | Impacto 2 (Medio) | Impacto 3 (Alto) |
|---|---|---|---|
| **Prob. 3 (Alta)** | Medio (3) | Alto (6) | Crítico (9) |
| **Prob. 2 (Media)** | Bajo (2) | Medio (4) | Alto (6) |
| **Prob. 1 (Baja)** | Bajo (1) | Bajo (2) | Medio (3) |

**Calificación de cada riesgo:**

| ID | P | I | E | Exposición |
|---|---|---|---|---|
| R-01 | 3 | 3 | 9 | **Crítico** |
| R-03 | 2 | 3 | 6 | **Alto** |
| R-02 | 2 | 3 | 6 | **Alto** |
| R-04 | 3 | 2 | 6 | **Alto** |
| R-05 | 2 | 3 | 6 | **Alto** |
| R-07 | 3 | 2 | 6 | **Alto** |
| RP-02 | 3 | 2 | 6 | **Alto** |
| RP-01 | 2 | 3 | 6 | **Alto** |
| R-06 | 2 | 2 | 4 | Medio |
| R-08 | 2 | 2 | 4 | Medio |
| R-13 | 2 | 2 | 4 | Medio |
| R-16 | 2 | 2 | 4 | Medio |
| RP-03 | 2 | 2 | 4 | Medio |
| RP-04 | 2 | 2 | 4 | Medio |
| R-09 | 1 | 2 | 2 | Bajo |
| R-10 | 1 | 2 | 2 | Bajo |
| R-11 | 1 | 2 | 2 | Bajo |
| R-12 | 2 | 1 | 2 | Bajo |
| R-14 | 1 | 2 | 2 | Bajo |
| R-15 | 2 | 1 | 2 | Bajo |
| R-17 | 2 | 1 | 2 | Bajo |
| RP-05 | 2 | 1 | 2 | Bajo |

### 4.3 Tratamiento y Mitigación

| ID | Exposición | Tratamiento | Acción |
|---|---|---|---|
| R-01 | Crítico | **Mitigar con pruebas (obligatorio)** | Pruebas unitarias del *matching* y verificación integral de todos los barrios del GeoJSON contra el Excel (CDP-01, CDP-02). |
| R-02 | Alto | **Mitigar con pruebas (obligatorio)** | Pruebas unitarias exhaustivas de `map_categoria()` (CDP-03). |
| R-03 | Alto | **Mitigar con pruebas (obligatorio)** | Comparación de porcentajes contra cálculo independiente (CDP-04, CDP-05). |
| R-04 | Alto | **Mitigar con pruebas (obligatorio)** | Pruebas de valores de estrato enteros, decimales y nulos (CDP-06). Resultado v1.1: CP-18 confirma el defecto DEF-001; CP-36 muestra que hoy es latente (Anexo A). |
| R-05 | Alto | **Mitigar con pruebas (obligatorio)** | Pruebas de carga con archivos válidos, ausentes y corruptos (CDP-07). |
| R-07 | Alto | **Mitigar con pruebas (obligatorio)** | Pruebas de transición de estados de navegación y modales (CDP-08). |
| RP-01 | Alto | Mitigar con gestión | Priorizar ejecución por exposición (Crítico → Alto → Medio); reserva de 2 días en Semana 3. |
| RP-02 | Alto | Mitigar con gestión y pruebas | Guía de instalación con entorno virtual nuevo; CP de instalación limpia (CDP-11). Recomendar retirar `env/` del repositorio. |
| R-06 | Medio | Mitigar con pruebas | AVL sobre número de variables seleccionadas (CDP-09). |
| R-08 | Medio | Mitigar con pruebas | Verificación visual de colores vs. categoría dominante (CDP-10). |
| R-13 | Medio | Mitigar con pruebas | Instalación limpia y fijación de versiones (CDP-11). |
| R-16 | Medio | Mitigar con pruebas | Prueba exploratoria en móvil vía QR (CDP-12). |
| RP-03 | Medio | Mitigar con gestión | Congelamiento de código al inicio de Semana 2; ejecución sobre *commit* identificado. |
| RP-04 | Medio | Mitigar con gestión | Asignación cruzada: cada CP con responsable y suplente. |
| R-09 | Bajo | Aceptar (prueba opcional) | Se cubre indirectamente en CP-25 si hay tiempo. |
| R-10 | Bajo | Aceptar | El archivo QR está versionado; se verifica en CP-27 de forma oportunista. |
| R-11 | Bajo | Aceptar | Los nombres provienen de fuentes controladas y el código ya usa `html.escape()` en la mayoría de puntos. |
| R-12 | Bajo | Aceptar | Se registra el tiempo de carga como dato informativo en CP-31; sin criterio de aceptación. |
| R-14 | Bajo | Aceptar | Excluido por *tailoring* (sección 2.3). |
| R-15 | Bajo | Aceptar | Excluido por *tailoring* (sección 2.3). |
| R-17 | Bajo | Aceptar | Se reporta como observación documental. |
| RP-05 | Bajo | Aceptar | Sesión de capacitación de 1 h en `pytest` en Semana 1. |

---

## 5. Estrategia de Pruebas y Derivación de Casos (Test Design Process)

### 5.1 Derivación de Condiciones de Prueba

| ID CDP | Condición de prueba | Riesgo(s) |
|---|---|---|
| CDP-01 | `limpiar()` normaliza correctamente mayúsculas, tildes, eñes, caracteres especiales, espacios múltiples y valores vacíos/nulos. | R-01 |
| CDP-02 | Cada barrio del GeoJSON se asigna a la comuna correcta del Excel; ningún barrio queda asignado a una comuna ajena. | R-01 |
| CDP-03 | `map_categoria()` devuelve la categoría correcta para cada valor posible de la escala Likert, incluyendo nulos y valores inesperados. | R-02 |
| CDP-04 | El % de percepción negativa por variable es igual a (Mala + Muy mala) / total de respuestas del barrio filtrado. | R-03 |
| CDP-05 | Los porcentajes por estrato suman 100 % por estrato y la distribución (torta) coincide con los conteos reales. | R-03 |
| CDP-06 | El filtro y las etiquetas de estrato funcionan con valores enteros, decimales (`3.0`) y nulos. | R-04 |
| CDP-07 | La aplicación carga los datos válidos y maneja de forma controlada la ausencia o corrupción del Excel y del GeoJSON. | R-05 |
| CDP-08 | Las transiciones entre estados de navegación (vista general, comuna, barrio, modal estadísticas, modal detalle) son correctas y conservan el contexto. | R-07 |
| CDP-09 | El selector de variables permite entre 1 y 3 variables, gestiona "Todas" y descarta la más antigua al superar el máximo. | R-06 |
| CDP-10 | El color de cada barrio corresponde a su categoría predominante y coincide con la leyenda. | R-08 |
| CDP-11 | La aplicación se instala y ejecuta en un entorno limpio con `requirements.txt`. | R-13, RP-02 |
| CDP-12 | El dashboard es usable en navegadores de escritorio y en un dispositivo móvil. | R-16 |

### 5.2 Técnicas de Diseño de Pruebas

Técnicas seleccionadas de ISO/IEC/IEEE 29119-4:

| Técnica | Referencia 29119-4 | Aplicación |
|---|---|---|
| **Partición de Clases de Equivalencia (PCE)** | §5.2.1 | CDP-01, CDP-03, CDP-06, CDP-07: clases de entradas de texto, categorías Likert, tipos de estrato y estados de archivos. |
| **Análisis de Valores Límite (AVL)** | §5.2.3 | CDP-04, CDP-09: 0 %, 100 %, barrio sin respuestas, 0/1/3/4 variables seleccionadas, `cutoff` del *matching* (0.7 y 0.5). |
| **Transición de Estados (TE)** | §5.2.8 | CDP-08: máquina de estados de navegación y modales. |
| **Tablas de Decisión** | §5.2.6 | CDP-09: combinaciones de "Todas" / variable ya seleccionada / variable nueva / máximo alcanzado. |
| **Pruebas basadas en escenarios / casos de uso** | §5.2.9 | CDP-10, CDP-12: recorridos completos del usuario. |
| **Adivinación de errores (*Error Guessing*)** | §5.4.1 | CDP-02, CDP-11: barrios homónimos, corregimientos, versiones de librerías. |

**Modelo de transición de estados (CDP-08):**

```
                 clic comuna                   clic barrio
 [E0 Vista general] ───────────► [E1 Comuna] ─────────────► [E2 Modal Estadísticas]
        ▲                          │   ▲  ▲                         │        │
        │ "Volver a todas"         │   │  │ "Cerrar"                │        │ clic barra / botón variable
        └──────────────────────────┘   │  └─────────────────────────┘        ▼
                                       │                          [E3 Modal Detalle variable]
                                       │ "Quitar"                            │
                                       └──── [E1b Comuna + barrio] ◄─────────┘ "Volver" → E2
                                                    │
                                                    └── "📊 Estadísticas" → E2
 Estados transversales: [Modal QR] y [Modal Acerca de] accesibles desde cualquier estado del sidebar.
```

**Clases de equivalencia de `map_categoria()` (CDP-03):**

| Clase | Ejemplos de entrada | Salida esperada |
|---|---|---|
| V1 "muy buena" | "Muy buena", "MUY BUENA" | Muy buena |
| V2 "buena" (sin "muy") | "Buena", "buena " | Buena |
| V3 "aceptable"/"regular" | "Aceptable", "Regular" | Aceptable |
| V4 "muy mala" | "Muy mala" | Muy mala |
| V5 "mala" (sin "muy") | "Mala" | Mala |
| I1 nulo | `NaN`, `None` | No sabe |
| I2 otro texto | "No sabe", "NS/NR", "" | No sabe |

**Tabla de decisión del selector de variables (CDP-09):**

| Regla | Botón pulsado | Estado actual | Resultado esperado |
|---|---|---|---|
| D1 | "Todas" | Cualquiera | `["Todas"]` |
| D2 | Variable X | `["Todas"]` | `[X]` |
| D3 | Variable X | Contiene X (única) | `["Todas"]` |
| D4 | Variable X | Contiene X y otras | Se elimina X |
| D5 | Variable X | 1–2 variables sin X | Se añade X |
| D6 | Variable X | 3 variables sin X | Se elimina la más antigua y se añade X (quedan 3) |

### 5.3 Generación de Casos de Prueba y Trazabilidad

**Casos de prueba:**

| ID CP | Técnica | Precondición | Entrada / Pasos | Resultado esperado | Nivel |
|---|---|---|---|---|---|
| CP-01 | PCE | — | `limpiar("Laureles Estadío")` | `"LAURELES ESTADIO"` | Unitario |
| CP-02 | PCE | — | `limpiar("  La  Candelaria!! ")` | `"LA CANDELARIA"` | Unitario |
| CP-03 | PCE / AVL | — | `limpiar("")`, `limpiar(None)` | `""` | Unitario |
| CP-04 | PCE | — | `limpiar("Castilla-Ñ")` | `"CASTILLA N"` | Unitario |
| CP-05 | AVL | Lista de barrios | `encontrar_mejor_match` con similitud justo por encima y por debajo de 0.7 | Devuelve coincidencia / `None` respectivamente | Unitario |
| CP-06 | Adivinación de errores | Datos cargados | Recorrer todos los *features* del GeoJSON y comparar `comuna_df` con la comuna oficial del polígono | 0 barrios asignados a comuna errónea; lista de no emparejados documentada | Integración |
| CP-07 | Adivinación de errores | Datos cargados | Verificar barrios homónimos en comunas distintas | Cada uno conserva su propia comuna | Integración |
| CP-08 | PCE | — | `map_categoria` con clases V1–V5 (5 valores) | Categoría correspondiente según tabla 5.2 | Unitario |
| CP-09 | PCE | — | `map_categoria` con I1–I2 (`NaN`, `""`, "NS/NR") | `"No sabe"` | Unitario |
| CP-10 | PCE | — | `map_categoria("MUY MALA")` y `"Muy Mala "` | `"Muy mala"` (no `"Mala"`) | Unitario |
| CP-11 | AVL | DataFrame sintético | 10 respuestas, 0 negativas | % negativo = 0.0 | Unitario |
| CP-12 | AVL | DataFrame sintético | 10 respuestas, 10 negativas | % negativo = 100.0 | Unitario |
| CP-13 | AVL | DataFrame sintético | 3 respuestas: 1 Mala, 1 Buena, 1 No sabe | % negativo = 33.3 | Unitario |
| CP-14 | AVL | — | DataFrame vacío | `(None, None, None)` sin excepción | Unitario |
| CP-15 | Escenario | Barrio real seleccionado | Comparar % del gráfico "Resumen por variable" con cálculo manual en hoja de cálculo | Diferencia ≤ 0.1 puntos | Sistema |
| CP-16 | Escenario | Barrio con ≥ 2 estratos | Gráfico "Por estrato": sumar porcentajes de cada barra | Suma = 100 % ± 1 por estrato | Sistema |
| CP-17 | PCE | DataFrame sintético | Columna estrato con enteros (`1, 2, 3`) | Etiquetas "Estrato 1..3"; filtro con 3 opciones | Unitario |
| CP-18 | PCE | DataFrame sintético | Columna estrato con decimales (`1.0, 2.0`, `NaN`) | Etiquetas "Estrato 1", "Estrato 2"; filtro no vacío | Unitario |
| CP-19 | PCE | Barrio real | Aplicar filtro "Estrato 3" en el modal | Los tres gráficos y el conteo reflejan solo estrato 3 | Sistema |
| CP-20 | PCE | Archivos válidos | Iniciar aplicación | Mapa con todas las comunas coloreadas, sin errores | Sistema |
| CP-21 | PCE | Renombrar `medellin_debug.geojson` | Iniciar aplicación | Mensaje "Error cargando GeoJSON local", la app no se detiene | Sistema |
| CP-22 | PCE | Renombrar `ECV_2025_Limpio.xlsx` | Iniciar aplicación | Comportamiento documentado (actualmente excepción no controlada → se registra defecto si aplica) | Sistema |
| CP-23 | TE | E0 | Clic en una comuna | Transición a E1: solo barrios de esa comuna, sidebar con "Comuna activa" | Sistema |
| CP-24 | TE | E1 | Clic en un barrio | Transición a E2: modal de estadísticas con nombre de barrio y comuna correctos | Sistema |
| CP-25 | TE | E2 | Clic en barra "Aire" o botón "💨 Aire" | Transición a E3: modal de detalle con la variable Aire | Sistema |
| CP-26 | TE | E3 | "← Volver" | Retorna a E2 del mismo barrio | Sistema |
| CP-27 | TE | E1b | "❌ Quitar" y luego "⬅️ Volver a todas las comunas" | E1 sin barrio y luego E0 con zoom/centro inicial | Sistema |
| CP-28 | TE (transición inválida) | E2 abierto | Cerrar modal y pulsar F5 / recargar | No se reabre un modal sin barrio seleccionado; sin excepciones | Sistema |
| CP-29 | Tabla de decisión | Vista general | Reglas D1–D6 de la tabla 5.2 | Estado del selector según tabla | Sistema |
| CP-30 | AVL | 3 variables activas | Seleccionar una 4.ª variable | Quedan 3; se descarta la primera elegida; texto de ayuda "3 variables activas (máximo)" | Sistema |
| CP-31 | Escenario | Comuna activa con 1 variable | Comparar color de 5 barrios con su categoría predominante calculada | Color = color de la leyenda para esa categoría | Sistema |
| CP-32 | Adivinación de errores | Equipo limpio con Python 3.11+ | Crear `venv`, `pip install -r requirements.txt`, `streamlit run dashboard.py` | Aplicación inicia sin errores; se registran versiones instaladas | Instalación |
| CP-33 | Escenario | Despliegue accesible por URL | Escanear QR desde móvil y navegar E0 → E2 | Mapa y modal legibles y operables | Sistema |
| CP-34 | Escenario | — | Ejecutar CP-20, CP-23 y CP-24 en Chrome, Firefox y Edge | Resultado idéntico en los tres navegadores | Sistema |
| CP-35 | PCE / Adivinación de errores | `ECV_2025_Limpio.xlsx` (DP-01) | Para las 5 variables, comparar los valores únicos con el catálogo de 6 categorías y aplicar `map_categoria()` a cada valor | Ningún valor fuera del catálogo ni nulo; `map_categoria(v) == v` para todos | Integración |
| CP-36 | PCE | `ECV_2025_Limpio.xlsx` (DP-01) | Revisar tipo, rango y nulos de la columna `11. Estrato` | Tipo entero, valores entre 1 y 6, 0 nulos | Integración |

**Matriz de trazabilidad (Riesgo → Condición → Caso):**

| Riesgo | Exposición | Condición(es) | Casos de prueba |
|---|---|---|---|
| R-01 | Crítico | CDP-01, CDP-02 | CP-01, CP-02, CP-03, CP-04, CP-05, CP-06, CP-07 |
| R-02 | Alto | CDP-03 | CP-08, CP-09, CP-10, CP-35 |
| R-03 | Alto | CDP-04, CDP-05 | CP-11, CP-12, CP-13, CP-14, CP-15, CP-16 |
| R-04 | Alto | CDP-06 | CP-17, CP-18, CP-19, CP-36 |
| R-05 | Alto | CDP-07 | CP-20, CP-21, CP-22 |
| R-07 | Alto | CDP-08 | CP-23, CP-24, CP-25, CP-26, CP-27, CP-28 |
| RP-02 | Alto | CDP-11 | CP-32 |
| R-06 | Medio | CDP-09 | CP-29, CP-30 |
| R-08 | Medio | CDP-10 | CP-31 |
| R-13 | Medio | CDP-11 | CP-32 |
| R-16 | Medio | CDP-12 | CP-33, CP-34 |
| R-09, R-10, R-11, R-12, R-14, R-15, R-17 | Bajo | — | Aceptados sin pruebas dedicadas (sección 4.3) |

**Cobertura:** 100 % de los riesgos Críticos y Altos de producto tienen al menos una condición y un caso de prueba asociado. Desde la v1.1 el plan suma **36 casos**: CP-35 y CP-36 verifican que los datos reales del Excel cumplen lo que el código supone.

### 5.4 Requisitos de entorno y datos de prueba

**Entorno:**

| Componente | Especificación |
|---|---|
| Sistema operativo | Windows 10/11 (principal); opcional Linux/macOS. |
| Python | 3.11 o superior, en entorno virtual nuevo (no usar la carpeta `env/` del repositorio). |
| Dependencias | `requirements.txt` + `pytest` para pruebas unitarias. |
| Ejecución | `streamlit run dashboard.py` (local) o despliegue en Streamlit Community Cloud para la prueba móvil. |
| Navegadores | Google Chrome, Mozilla Firefox, Microsoft Edge (últimas versiones); navegador móvil Android o iOS. |
| Control de versiones | Git / GitHub; ejecución sobre *commit* identificado y registrado en cada resultado. |
| Registro de defectos | GitHub Issues con etiqueta `bug` y prioridad (`P1`–`P3`). |

**Preparación para pruebas unitarias:** dado que `dashboard.py` ejecuta la interfaz al importarse, no se importa. `tests/conftest.py` lee `dashboard.py` con el módulo `ast`, extrae solo las funciones puras (`limpiar`, `encontrar_mejor_match`, `map_categoria`, `centroide_feature`, `bounds_from_features`, `figuras_estadisticas_barrio`) y las constantes que usan (`variables`, `COLOR_MAP_CATEG`, `CAT_ORDER`), y las ejecuta aisladas. Así `dashboard.py` no se modifica y las pruebas siempre ejercitan el código vigente, no una copia; si una función se renombra, la carga falla con un mensaje explícito. Las dependencias de prueba están en `requirements-test.txt` y se ejecutan con `python -m pytest -v` desde la raíz.

**Datos de prueba:**

| ID | Conjunto | Uso |
|---|---|---|
| DP-01 | `ECV_2025_Limpio.xlsx` (datos reales) | Pruebas de sistema e integración (incluye CP-35 y CP-36). |
| DP-02 | `medellin_debug.geojson` (datos reales) | Pruebas de mapa e integración. |
| DP-03 | DataFrames sintéticos construidos en `pytest` (respuestas controladas, estratos enteros/decimales/nulos) | CP-11 a CP-14, CP-17, CP-18. |
| DP-04 | Listas de cadenas con tildes, eñes, símbolos, vacías y nulas | CP-01 a CP-05, CP-08 a CP-10. |
| DP-05 | Hoja de cálculo de referencia con cálculos manuales para 3 barrios seleccionados | CP-15, CP-16, CP-31. |
| DP-06 | Copias renombradas/corruptas de los archivos de datos | CP-21, CP-22. |

### 5.5 Criterios de suspensión y finalización

**Criterios de suspensión:**
- La aplicación no inicia en el entorno de pruebas (bloquea todos los casos de sistema).
- Falla la carga de datos reales (Excel o GeoJSON) en el entorno de referencia.
- Más del 30 % de los casos ejecutados en un día fallan por una misma causa raíz.
- Cambio de código no planificado sobre la versión congelada.

**Criterios de reanudación:**
- Corrección del defecto bloqueante verificada en un nuevo *commit* identificado.
- Re-ejecución de los casos afectados y de una prueba de humo (CP-20, CP-23, CP-24).

**Criterios de finalización (salida):**
- 100 % de los casos asociados a riesgos **Críticos y Altos** ejecutados.
- ≥ 90 % de los casos asociados a riesgos **Medios** ejecutados.
- 0 defectos abiertos de prioridad **P1** (datos erróneos o sistema inutilizable).
- Defectos **P2** abiertos documentados con decisión aprobada por los asesores.
- ≥ 95 % de los casos ejecutados en estado "Aprobado".
- Informe de finalización de pruebas redactado y entregado.

---

## 6. Actividades de Prueba y Estimaciones

### 6.1 Desglose de tareas

| ID | Actividad | Proceso 29119-2 | Entregable |
|---|---|---|---|
| A-01 | Análisis del contexto e identificación de elementos de prueba | TP1, TP2 | Sección 3 |
| A-02 | Identificación y análisis de riesgos | TP3, TP4 | Sección 4 |
| A-03 | Redacción y aprobación del Plan de Pruebas | TP5–TP8 | Este documento |
| A-04 | Capacitación en `pytest` y preparación del entorno limpio | TE1 | Entorno operativo |
| A-05 | Extracción de funciones puras a módulo auxiliar | TD4 | `utils.py` / `tests/` |
| A-06 | Diseño de condiciones y casos de prueba | TD1–TD3 | Sección 5 |
| A-07 | Preparación de datos de prueba (DP-01 a DP-06) | TD4 | Datos de prueba |
| A-08 | Implementación de pruebas unitarias automatizadas | TD4 | `tests/test_*.py` |
| A-09 | Ejecución de pruebas unitarias | TE2 | Reporte `pytest` |
| A-10 | Ejecución de pruebas de integración y sistema | TE2 | Registro de resultados |
| A-11 | Registro y seguimiento de defectos | TE3 | GitHub Issues |
| A-12 | Re-pruebas y pruebas de regresión | TE2 | Registro actualizado |
| A-13 | Informe de finalización de pruebas | TC1–TC4 | Informe final |

### 6.2 Estimación de esfuerzo por actividad

Técnica de estimación: **juicio de expertos del equipo + descomposición por actividades (WBS)**.

| ID | Actividad | Esfuerzo (h-persona) |
|---|---|---|
| A-01 | Análisis del contexto | 3 |
| A-02 | Análisis de riesgos | 4 |
| A-03 | Plan de pruebas | 6 |
| A-04 | Capacitación y entorno | 6 |
| A-05 | Extracción de funciones | 3 |
| A-06 | Diseño de casos | 6 |
| A-07 | Datos de prueba | 5 |
| A-08 | Implementación de pruebas unitarias | 12 |
| A-09 | Ejecución unitaria | 2 |
| A-10 | Ejecución integración y sistema | 20 |
| A-11 | Gestión de defectos | 5 |
| A-12 | Re-pruebas y regresión | 8 |
| A-13 | Informe final | 4 |
| | **Subtotal** | **84** |
| | Contingencia (≈ 15 %) | 12 |
| | **Total estimado** | **96 h-persona** |

Capacidad disponible (v1.1): 3 personas × 8 h/semana × 3 semanas = **72 h-persona**, frente a 84 h estimadas (96 h con contingencia): **déficit de 12 h sin contingencia y de 24 h con ella**. Decisión pendiente del líder de pruebas: (a) aumentar la dedicación a ≈ 11 h/semana por persona, o (b) recortar casos de riesgo Medio y declararlo en §2.3. Parte de A-05, A-08 y A-09 ya se ejecutó el 13/11/2026 (Anexo A).

---

## 7. Personal

### 7.1 Roles y responsabilidades de prueba

| Rol | Responsable | Suplente | Responsabilidades |
|---|---|---|---|
| Líder de pruebas | Jeyson González | Keyner Gil | Plan de pruebas, seguimiento del cronograma, criterios de suspensión/finalización, informe final, contacto con asesores. |
| Analista de riesgos y diseño | Jeyson González | Mateo | Matriz de riesgos, condiciones de prueba, casos y trazabilidad. |
| Ingeniero de pruebas automatizadas | Keyner Gil | Jeyson González | Carga de funciones puras (`tests/conftest.py`), pruebas `pytest` (CP-01 a CP-05, CP-08 a CP-14, CP-17, CP-18, CP-35, CP-36) e instalación limpia (CP-32). |
| Ejecutor de pruebas de sistema | Mateo | Keyner Gil | Pruebas manuales de navegación, selector de variables, colores, compatibilidad y móvil (CP-23 a CP-31, CP-33, CP-34). |
| Gestor de configuración y defectos | Jeyson González | Mateo | Congelamiento de versión, GitHub Issues, verificación de correcciones; pruebas de integración y exactitud de datos (CP-06, CP-07, CP-15, CP-16, CP-19 a CP-22). |
| Desarrolladores (corrección) | Todo el equipo | — | Corrección de defectos asignados. |
| Aprobadores | Ingry Gómez, Juan Zapata | — | Aprobación del plan, aceptación del informe y de riesgos residuales. |

---

## 8. Cronograma

### 8.1 Hitos y fechas de ejecución (Alineado al ciclo de 3 semanas)

**Semana 1 — Planificación y diseño (10/11/2026 – 14/11/2026)**

| Fecha | Actividad | Hito |
|---|---|---|
| 10/11 | A-01, A-02 | Riesgos identificados |
| 11/11 – 12/11 | A-03, A-06 | — |
| 13/11 | A-04 (capacitación y entorno) | Entorno limpio operativo |
| 14/11 | Revisión con asesores | **H1: Plan de pruebas aprobado** |

**Semana 2 — Preparación y ejecución (17/11/2026 – 21/11/2026)**

| Fecha | Actividad | Hito |
|---|---|---|
| 17/11 | Congelamiento de código; A-05, A-07 | **H2: Versión bajo prueba congelada** |
| 18/11 – 19/11 | A-08, A-09 | Pruebas unitarias ejecutadas |
| 19/11 – 21/11 | A-10 (riesgos Crítico y Alto primero), A-11 | **H3: 100 % de casos Críticos/Altos ejecutados** |

**Semana 3 — Corrección, regresión y cierre (24/11/2026 – 28/11/2026)**

| Fecha | Actividad | Hito |
|---|---|---|
| 24/11 – 25/11 | A-10 (riesgos Medios), corrección de defectos | — |
| 26/11 | A-12 (re-pruebas y regresión) | **H4: 0 defectos P1 abiertos** |
| 27/11 | A-13 | Informe de finalización redactado |
| 28/11 | Entrega y sustentación | **H5: Cierre del ciclo de pruebas** |

```
Semana            S1 (10–14 nov)   S2 (17–21 nov)   S3 (24–28 nov)
Planificación     ██████████
Diseño de casos       ██████
Entorno / datos         ████     ████
Pruebas unitarias                ██████
Pruebas sistema                    ██████████   ████
Defectos / regresión                   ████     ██████
Informe final                                       ████
Hitos             H1 (14/11)  H2 (17/11)  H3 (21/11)  H4 (26/11)  H5 (28/11)
```

---

## Anexo A. Registro de ejecución — pruebas automatizadas (A-08, A-09)

> Por la adaptación declarada en §2.3, el registro de ejecución se anexa a este plan en lugar de un documento separado.

### A.1 Datos de la ejecución

| Campo | Valor |
|---|---|
| Fecha | 13/11/2026 |
| Ejecutor | Keyner Gil (ingeniero de pruebas automatizadas) |
| Rama y versión | `keynergil`, sincronizada con `master` (`16fd4079`). `dashboard.py`, `ECV_2025_Limpio.xlsx`, `medellin_debug.geojson` y `requirements.txt` son idénticos a la versión bajo prueba `260f905a` (§2.1). |
| Entorno | Windows; Python 3.14.4 en entorno virtual nuevo `.venv` (excluido por `.gitignore`); pytest 9.2.0, pandas 3.1.1, plotly 7.1.0. |
| Comando | `python -m pytest -v`, desde la raíz del repositorio. |
| Archivos de prueba | `tests/conftest.py`, `tests/test_funciones_dashboard.py`, `tests/test_datos_ecv.py`, `requirements-test.txt`. |
| Resultado global | **40 pruebas: 39 aprobadas y 1 fallo esperado (`xfail`, DEF-001)**, en 1,85 s. |

Esta ejecución es previa al congelamiento de código (H2, 17/11/2026). Se repetirá sobre el *commit* congelado y el resultado se agregará a este anexo.

### A.2 Resultado por caso de prueba

| Caso | Prueba(s) `pytest` | Entradas | Resultado |
|---|---|---|---|
| CP-01 | `test_cp01_limpiar_tildes_y_mayusculas` | 1 | Aprobado |
| CP-02 | `test_cp02_limpiar_simbolos_y_espacios` | 1 | Aprobado |
| CP-03 | `test_cp03_limpiar_vacio_y_nulo` | 2 (`""`, `None`) | Aprobado |
| CP-04 | `test_cp04_limpiar_enie_y_guion` | 1 | Aprobado |
| CP-05 | `test_cp05_match_valor_limite_del_cutoff`, `test_cp05b_…`, `test_cp05c_…` | 3 (similitud 0,7 exacta acepta; 0,6 rechaza; vacío; texto con tilde) | Aprobado |
| CP-08 | `test_cp08_map_categoria_clases_validas` | 8 (clases V1–V5) | Aprobado |
| CP-09 | `test_cp09_map_categoria_invalidos_son_no_sabe` | 6 (`NaN`, `None`, `pd.NA`, `""`, "NS/NR", "No sabe") | Aprobado |
| CP-10 | `test_cp10_muy_mala_no_se_confunde_con_mala` | 2 | Aprobado |
| CP-11 | `test_cp11_cero_negativas_da_cero_por_ciento` | 1 | Aprobado |
| CP-12 | `test_cp12_todas_negativas_da_cien_por_ciento` | 1 | Aprobado |
| CP-13 | `test_cp13_un_tercio_negativo` | 1 | Aprobado |
| CP-14 | `test_cp14_dataframe_vacio_devuelve_tres_none` | 1 | Aprobado |
| CP-17 | `test_cp17_estratos_enteros` | 1 | Aprobado |
| CP-18 | `test_cp18_estratos_decimales` | 1 | **Fallido: DEF-001** (marcado `xfail`) |
| CP-35 | `test_cp35_…catalogo_de_6_categorias`, `test_cp35b_…identidad_sobre_datos_reales` | 2 (10 316 registros, 5 variables) | Aprobado |
| CP-36 | `test_cp36_estrato_real_es_entero_entre_1_y_6_sin_nulos` | 1 | Aprobado |
| TI-06 (opcional, R-09) | `test_ti06_…` (centroide y límites) | 7 | Aprobado |

### A.3 Defectos registrados

| ID | Riesgo / caso | Descripción | Severidad | Estado |
|---|---|---|---|---|
| DEF-001 | R-04 / CP-18 | Con estrato decimal (`1.0`), `str(x).isdigit()` es falso: en `figuras_estadisticas_barrio()` la etiqueta queda `"1.0"` en lugar de `"Estrato 1"` (verificado por CP-18) y, por inspección de código, la lista del filtro de estratos de los modales queda vacía. | P3 propuesta (latente); confirmar con el gestor de defectos. | Abierto. CP-36 confirma que el Excel actual guarda el estrato como entero, por lo que hoy no se manifiesta. |

La prueba de CP-18 usa `xfail(strict=True)`: cuando se corrija DEF-001 pasará a "XPASS" y `pytest` lo reportará como fallo, para recordar quitar la marca y cerrar el defecto.

### A.4 Verificación de la capacidad de detección

Para comprobar que las pruebas detectan errores reales se introdujeron defectos a propósito en una copia de `dashboard.py` (no en el repositorio):

| Defecto introducido | Pruebas que lo detectaron |
|---|---|
| `map_categoria()` evalúa "mala" antes que "muy mala" | CP-08, CP-10 y CP-35 (4 pruebas fallidas) |
| `encontrar_mejor_match()` con `cutoff=0.8` en lugar de 0.7 | CP-05 |
| % negativo redondeado a 0 decimales en lugar de 1 | CP-13 |

Los tres defectos fueron detectados.

### A.5 Observaciones

- A-05 (extracción de funciones) se resolvió sin crear `utils.py` ni modificar `dashboard.py`; ver §5.4.
- RP-02 confirmado: `env/` y `node_modules/` siguen versionados en `master` (8 192 archivos) aunque estén en `.gitignore`, y la carpeta `env/` no es reutilizable. La ejecución usó un entorno `.venv` nuevo. Se recomienda retirarlos del control de versiones con `git rm -r --cached env node_modules`.
