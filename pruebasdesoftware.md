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
| Versión | 0.2 |
| Estado | Borrador para aprobación |
| Fecha de emisión | 10/11/2026 |
| Última actualización | 12/11/2026 |
| Ubicación | Repositorio `jeyson4013/Analisis_ambiental` — archivo `pruebasdesoftware.md` |

### 1.2 Organización emisora y autores

- **Organización emisora:** Equipo de desarrollo del proyecto *Análisis Ambiental — Percepción Ambiental Ciudadana de Medellín*.
- **Autores:**
  - Keyner Gil
  - Jeyson González
  - Mateo Villada Villada

### 1.3 Autoridad de aprobación

| Rol | Nombre | Responsabilidad | Firma / Fecha |
|---|---|---|---|
| Docente | Roberto José Calderón Bermejo | Aprobación del plan, de los criterios de finalización y revisión del informe de cierre | |
| Líder de pruebas | Jeyson González | Elaboración y mantenimiento del plan | |

### 1.4 Historial de cambios y control de versiones

| Versión | Fecha | Autor | Descripción del cambio |
|---|---|---|---|
| 0.1 | 10/11/2026 | Equipo de desarrollo | Creación del borrador inicial con base en las directrices del docente. |
| 0.2 | 12/11/2026 | Equipo de desarrollo | Ajuste del volumen a 24 casos (18 manuales y 6 automatizados), y recálculo de la estimación de esfuerzo. |
| 1.0 | — | Equipo de desarrollo | Versión para aprobación (pendiente). |

El documento se versiona en Git junto al código fuente. Cada modificación se realiza mediante *commit* con mensaje descriptivo y, para cambios de alcance, mediante *Pull Request* revisado por al menos un integrante distinto del autor.

---

## 2. Introducción y Declaración de Adaptación (Tailoring)

### 2.1 Alcance del documento

Este plan define el enfoque, los recursos, el cronograma y las actividades de prueba del **Dashboard Ambiental Medellín**, una aplicación web desarrollada en Python/Streamlit que visualiza sobre un mapa interactivo la percepción ciudadana de cinco variables ambientales (Aire, Ríos, Ruido, Basuras y Contaminación Visual), a partir de la Encuesta de Calidad de Vida 2025 de *Medellín Cómo Vamos*.

El plan cubre el ciclo de pruebas de **3 semanas** sobre la versión del código en la rama `master` (commit `260f905a`), e incluye: gestión de riesgos, diseño de condiciones y casos de prueba, trazabilidad, entorno, criterios de suspensión/finalización, estimaciones, roles y cronograma.

El volumen de pruebas es de **24 casos**: **18 manuales** y **6 automatizados**.

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
2. **Restricciones del proyecto:** ciclo de pruebas de **3 semanas**, equipo de 3 personas con dedicación parcial, sin presupuesto para herramientas comerciales ni entornos dedicados.

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
| Automatización completa de pruebas de interfaz (Selenium/Playwright) | Costo de configuración elevado para el ciclo disponible. Solo se automatizan 6 casos de lógica pura con `pytest`. | Las pruebas de UI dependen de ejecución manual, con mayor posibilidad de error humano. |

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
- **6 pruebas automatizadas** con `pytest` de funciones puras (TI-03, TI-04, TI-05, TI-09).
- Pruebas **manuales de integración** de datos (Excel ↔ GeoJSON ↔ mapa).
- Pruebas **manuales de sistema** funcionales de la interfaz (mapa, filtros, modales, navegación).
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
- Pruebas dedicadas de cálculos geométricos (TI-06): riesgo R-09 aceptado.

### 3.3 Suposiciones y restricciones

**Suposiciones:**
- S-01: El archivo `ECV_2025_Limpio.xlsx` es la versión definitiva y ya está depurado.
- S-02: El GeoJSON contiene los polígonos válidos de los barrios y corregimientos de Medellín.
- S-03: Los evaluadores disponen de conexión a Internet (los mosaicos de CartoDB se cargan en línea).
- S-04: La versión bajo prueba se congela al inicio de la Semana 2; los cambios posteriores solo corrigen defectos.

**Restricciones:**
- RES-01: Ciclo total de **3 semanas** (10/11/2026 – 28/11/2026).
- RES-02: Equipo de 3 personas con dedicación parcial (≈ 8 h/semana por persona).
- RES-03: Sin herramientas comerciales; solo software libre (`pytest`, GitHub Issues).
- RES-04: La aplicación es un único script Streamlit, lo que dificulta pruebas unitarias aisladas (las funciones dependen de `st.session_state` y se ejecutan al importar el módulo).
- RES-05: La carpeta `env/` versionada en el repositorio contiene rutas absolutas de otra máquina y no es reutilizable; cada evaluador debe crear su propio entorno virtual.

### 3.4 Partes interesadas

| Parte interesada | Interés en las pruebas |
|---|---|
| Docente (Roberto José Calderón Bermejo) | Calidad del producto y cumplimiento del proceso ISO 29119 adaptado. |
| Equipo de desarrollo (Keyner Gil, Jeyson González, Mateo Villada Villada) | Detectar y corregir defectos antes de la entrega. |
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
| R-01 | Crítico | **Mitigar con pruebas (obligatorio)** | Pruebas automatizadas de `limpiar()` y del *matching*, y verificación manual de todos los barrios del GeoJSON contra el Excel (CDP-01, CDP-02). |
| R-02 | Alto | **Mitigar con pruebas (obligatorio)** | Pruebas automatizadas exhaustivas de `map_categoria()` (CDP-03). |
| R-03 | Alto | **Mitigar con pruebas (obligatorio)** | Prueba automatizada de límites del % negativo y comparación manual contra cálculo independiente (CDP-04, CDP-05). |
| R-04 | Alto | **Mitigar con pruebas (obligatorio)** | Pruebas de valores de estrato enteros, decimales y nulos (CDP-06). |
| R-05 | Alto | **Mitigar con pruebas (obligatorio)** | Pruebas de carga con archivos válidos y ausentes (CDP-07). |
| R-07 | Alto | **Mitigar con pruebas (obligatorio)** | Pruebas de transición de estados de navegación y modales (CDP-08). |
| RP-01 | Alto | Mitigar con gestión | Priorizar ejecución por exposición (Crítico → Alto → Medio); reserva de 2 días en Semana 3. |
| RP-02 | Alto | Mitigar con gestión y pruebas | Guía de instalación con entorno virtual nuevo; CP de instalación limpia (CDP-11). Recomendar retirar `env/` del repositorio. |
| R-06 | Medio | Mitigar con pruebas | AVL y tabla de decisión sobre el selector de variables (CDP-09). |
| R-08 | Medio | Mitigar con pruebas | Verificación visual de colores vs. categoría dominante (CDP-10). |
| R-13 | Medio | Mitigar con pruebas | Instalación limpia y fijación de versiones (CDP-11). |
| R-16 | Medio | Mitigar con pruebas | Prueba exploratoria en móvil vía QR y en tres navegadores (CDP-12). |
| RP-03 | Medio | Mitigar con gestión | Congelamiento de código al inicio de Semana 2; ejecución sobre *commit* identificado. |
| RP-04 | Medio | Mitigar con gestión | Asignación cruzada: cada CP con responsable y suplente. |
| R-09 | Bajo | Aceptar (sin caso dedicado) | Se observa de forma oportunista durante CP-15 y CP-16 (ubicación del marcador y zoom del barrio). |
| R-10 | Bajo | Aceptar | El archivo QR está versionado; se verifica de forma oportunista al abrir el modal QR durante CP-23. |
| R-11 | Bajo | Aceptar | Los nombres provienen de fuentes controladas y el código ya usa `html.escape()` en la mayoría de puntos. |
| R-12 | Bajo | Aceptar | Se registra el tiempo de carga como dato informativo en CP-12; sin criterio de aceptación. |
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
| CDP-07 | La aplicación carga los datos válidos y maneja de forma controlada la ausencia del Excel y del GeoJSON. | R-05 |
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
| **Análisis de Valores Límite (AVL)** | §5.2.3 | CDP-02, CDP-04, CDP-09: similitud del *matching* alrededor del `cutoff` 0.7, 0 %/100 % de percepción negativa, barrio sin respuestas, 1/2/3/4 variables seleccionadas. |
| **Transición de Estados (TE)** | §5.2.8 | CDP-08: máquina de estados de navegación y modales. |
| **Tablas de Decisión** | §5.2.6 | CDP-09: combinaciones de "Todas" / variable ya seleccionada / variable nueva / máximo alcanzado. |
| **Pruebas basadas en escenarios / casos de uso** | §5.2.9 | CDP-05, CDP-10, CDP-12: recorridos completos del usuario. |
| **Adivinación de errores (*Error Guessing*)** | §5.4.1 | CDP-02, CDP-11: barrios homónimos, corregimientos, versiones de librerías. |

#### Datos de entrada generados por cada técnica

**AVL — `cutoff` del *matching* (CP-02).** `difflib.SequenceMatcher` calcula `ratio = 2·M / T`, donde M es el número de caracteres coincidentes y T el total de caracteres de ambas cadenas. Con el `cutoff = 0.7` se eligieron dos pares reales de nombres, uno justo por debajo y otro justo por encima del límite:

| Par (A, B) | M | T | Ratio | Resultado esperado con `cutoff = 0.7` |
|---|---|---|---|---|
| `LA AMERICA` / `LA CANDELARIA` | 8 | 23 | 0.6957 | Sin coincidencia (`None`) |
| `POBLADO` / `ROBLEDO` | 5 | 14 | 0.7143 | Coincidencia |

El segundo par es además un ejemplo de falso positivo: son barrios distintos que el *matching* aceptaría si no se restringe la búsqueda a la comuna.

**AVL — percepción negativa (CP-05).** Para `% negativo = (Mala + Muy mala) / total × 100`, con total = n:

| Caso límite | n | Negativas | % esperado |
|---|---|---|---|
| Barrio sin respuestas | 0 | 0 | `(None, None, None)` sin excepción |
| Mínimo | 10 | 0 | 0.0 |
| Máximo | 10 | 10 | 100.0 |
| Mixto (1 Mala, 1 Buena, 1 No sabe) | 3 | 1 | 33.3 |

**AVL — número de variables seleccionadas (CP-20).** Valores 1, 2, 3 (máximo permitido) y 4 (primer valor inválido).

**PCE — `map_categoria()` (CP-03, CP-04).**

| Clase | Ejemplos de entrada | Salida esperada |
|---|---|---|
| V1 "muy buena" | "Muy buena", "MUY BUENA" | Muy buena |
| V2 "buena" (sin "muy") | "Buena", "buena " | Buena |
| V3 "aceptable"/"regular" | "Aceptable", "Regular" | Aceptable |
| V4 "muy mala" | "Muy mala", "MUY MALA", "Muy Mala " | Muy mala |
| V5 "mala" (sin "muy") | "Mala" | Mala |
| I1 nulo | `NaN`, `None` | No sabe |
| I2 otro texto | "No sabe", "NS/NR", "" | No sabe |

**PCE — estrato (CP-06).** Clases: enteros (`1, 2, 3`), decimales (`1.0, 2.0`) y nulos (`NaN`). Un representante por clase.

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

**Volumen:** 24 casos de prueba, **18 manuales** (CP-07 a CP-24) y **6 automatizados** (CP-01 a CP-06).

#### 5.3.1 Casos automatizados (6)

Los casos automatizados no describen pasos: el procedimiento está en el script enlazado, alojado en el repositorio (carpeta `tests/`).

| ID CP | Condición | Riesgo | Técnica | Datos de entrada (ver 5.2) | Resultado esperado | Script |
|---|---|---|---|---|---|---|
| CP-01 | CDP-01 | R-01 | PCE | `"Laureles Estadío"`, `"  La  Candelaria!! "`, `"Castilla-Ñ"`, `""`, `None` | `"LAURELES ESTADIO"`, `"LA CANDELARIA"`, `"CASTILLA N"`, `""`, `""` | [test_limpiar.py](tests/test_limpiar.py) |
| CP-02 | CDP-02 | R-01 | AVL | Pares `LA AMERICA`/`LA CANDELARIA` (0.6957) y `POBLADO`/`ROBLEDO` (0.7143), `cutoff = 0.7` | `None` y coincidencia, respectivamente | [test_matching.py](tests/test_matching.py) |
| CP-03 | CDP-03 | R-02 | PCE | Clases V1–V5 (incluye `"MUY MALA"` y `"Muy Mala "`) | Categoría de la tabla de 5.2; `"Muy mala"` nunca devuelve `"Mala"` | [test_categoria.py](tests/test_categoria.py) |
| CP-04 | CDP-03 | R-02 | PCE | Clases I1–I2: `NaN`, `None`, `""`, `"NS/NR"`, `"No sabe"` | `"No sabe"` | [test_categoria.py](tests/test_categoria.py) |
| CP-05 | CDP-04 | R-03 | AVL | DataFrames sintéticos de la tabla "percepción negativa" (n = 0, 10/0, 10/10, 1/3) | 0.0; 100.0; 33.3; `(None, None, None)` | [test_estadisticas.py](tests/test_estadisticas.py) |
| CP-06 | CDP-06 | R-04 | PCE | Columna estrato con enteros (`1, 2, 3`), decimales (`1.0, 2.0`) y `NaN` | Etiquetas "Estrato 1", "Estrato 2", "Estrato 3"; filtro no vacío | [test_estrato.py](tests/test_estrato.py) |

#### 5.3.2 Casos manuales (18)

| ID CP | Condición | Riesgo | Técnica | Precondición | Pasos | Resultado esperado | Nivel |
|---|---|---|---|---|---|---|---|
| CP-07 | CDP-02 | R-01 | Adivinación de errores | Datos cargados | Recorrer todos los *features* del GeoJSON y comparar `comuna_df` con la comuna oficial del polígono | 0 barrios asignados a comuna errónea; lista de no emparejados documentada | Integración |
| CP-08 | CDP-02 | R-01 | Adivinación de errores | Datos cargados | Verificar barrios homónimos en comunas distintas | Cada uno conserva su propia comuna | Integración |
| CP-09 | CDP-04 | R-03 | Escenario | Barrio real seleccionado | Comparar el % del gráfico "Resumen por variable" con el cálculo manual en hoja de cálculo (DP-05) | Diferencia ≤ 0.1 puntos | Sistema |
| CP-10 | CDP-05 | R-03 | Escenario | Barrio con ≥ 2 estratos | En el gráfico "Por estrato", sumar los porcentajes de cada barra | Suma = 100 % ± 1 por estrato | Sistema |
| CP-11 | CDP-06 | R-04 | PCE | Barrio real | Aplicar el filtro "Estrato 3" en el modal | Los tres gráficos y el conteo reflejan solo el estrato 3 | Sistema |
| CP-12 | CDP-07 | R-05 | PCE | Archivos válidos | Iniciar la aplicación y registrar el tiempo de carga | Mapa con todas las comunas coloreadas, sin errores | Sistema |
| CP-13 | CDP-07 | R-05 | PCE | Renombrar `medellin_debug.geojson` | Iniciar la aplicación | Mensaje "Error cargando GeoJSON local"; la app no se detiene | Sistema |
| CP-14 | CDP-07 | R-05 | PCE | Renombrar `ECV_2025_Limpio.xlsx` | Iniciar la aplicación | Comportamiento documentado (actualmente excepción no controlada → se registra defecto si aplica) | Sistema |
| CP-15 | CDP-08 | R-07 | TE | E0 | Clic en una comuna | Transición a E1: solo barrios de esa comuna, sidebar con "Comuna activa" | Sistema |
| CP-16 | CDP-08 | R-07 | TE | E1 | Clic en un barrio | Transición a E2: modal de estadísticas con nombre de barrio y comuna correctos | Sistema |
| CP-17 | CDP-08 | R-07 | TE | E2 | Clic en la barra "Aire" o en el botón "💨 Aire"; luego "← Volver" | Transición a E3 (modal de detalle de Aire) y retorno a E2 del mismo barrio | Sistema |
| CP-18 | CDP-08 | R-07 | TE | E1b | "❌ Quitar" y luego "⬅️ Volver a todas las comunas" | E1 sin barrio y luego E0 con zoom/centro inicial | Sistema |
| CP-19 | CDP-08 | R-07 | TE (transición inválida) | E2 abierto | Cerrar el modal y pulsar F5 / recargar | No se reabre un modal sin barrio seleccionado; sin excepciones | Sistema |
| CP-20 | CDP-09 | R-06 | Tabla de decisión + AVL | Vista general | Ejecutar las reglas D1–D6 de la tabla de 5.2; con 3 variables activas, seleccionar una 4.ª | Estado según la tabla; quedan 3, se descarta la primera elegida y se muestra "3 variables activas (máximo)" | Sistema |
| CP-21 | CDP-10 | R-08 | Escenario | Comuna activa con 1 variable | Comparar el color de 5 barrios con su categoría predominante calculada (DP-05) | Color = color de la leyenda para esa categoría | Sistema |
| CP-22 | CDP-11 | R-13, RP-02 | Adivinación de errores | Equipo limpio con Python 3.11+ | Crear `venv`, `pip install -r requirements.txt`, `streamlit run dashboard.py` | La aplicación inicia sin errores; se registran las versiones instaladas | Instalación |
| CP-23 | CDP-12 | R-16 | Escenario | Despliegue accesible por URL | Escanear el QR desde un móvil y navegar E0 → E2 | Mapa y modal legibles y operables | Sistema |
| CP-24 | CDP-12 | R-16 | Escenario | — | Ejecutar CP-12, CP-15 y CP-16 en Chrome, Firefox y Edge | Resultado idéntico en los tres navegadores | Sistema |

#### 5.3.3 Matriz de trazabilidad (Riesgo ⇄ Condición ⇄ Caso)

| Riesgo | Exposición | Condición(es) | Casos de prueba |
|---|---|---|---|
| R-01 | Crítico | CDP-01, CDP-02 | CP-01, CP-02, CP-07, CP-08 |
| R-02 | Alto | CDP-03 | CP-03, CP-04 |
| R-03 | Alto | CDP-04, CDP-05 | CP-05, CP-09, CP-10 |
| R-04 | Alto | CDP-06 | CP-06, CP-11 |
| R-05 | Alto | CDP-07 | CP-12, CP-13, CP-14 |
| R-07 | Alto | CDP-08 | CP-15, CP-16, CP-17, CP-18, CP-19 |
| RP-02 | Alto | CDP-11 | CP-22 |
| R-06 | Medio | CDP-09 | CP-20 |
| R-08 | Medio | CDP-10 | CP-21 |
| R-13 | Medio | CDP-11 | CP-22 |
| R-16 | Medio | CDP-12 | CP-23, CP-24 |
| R-09, R-10, R-11, R-12, R-14, R-15, R-17 | Bajo | — | Aceptados sin casos dedicados (sección 4.3) |

**Cobertura:**
- 100 % de los riesgos Críticos y Altos de producto tienen al menos una condición y un caso de prueba asociado.
- Ningún caso queda huérfano: cada uno de los 24 casos responde a una condición que mitiga un riesgo evaluado (la columna "Condición" y "Riesgo" de 5.3.1 y 5.3.2 permite recorrer la trazabilidad en ambos sentidos).
- Distribución: 4 casos de riesgo Crítico (CP-01, CP-02, CP-07, CP-08), 15 de riesgos Altos de producto (CP-03 a CP-06, CP-09 a CP-19), 1 caso (CP-22) que cubre un riesgo Alto de proyecto (RP-02) y uno Medio (R-13), y 4 casos de riesgos Medios (CP-20, CP-21, CP-23, CP-24).

### 5.4 Requisitos de entorno y datos de prueba

**Entorno:**

| Componente | Especificación |
|---|---|
| Sistema operativo | Windows 10/11 (principal); opcional Linux/macOS. |
| Python | 3.11 o superior, en entorno virtual nuevo (no usar la carpeta `env/` del repositorio). |
| Dependencias | `requirements.txt` + `pytest` para pruebas automatizadas. |
| Ejecución | `streamlit run dashboard.py` (local) o despliegue en Streamlit Community Cloud para la prueba móvil. |
| Navegadores | Google Chrome, Mozilla Firefox, Microsoft Edge (últimas versiones); navegador móvil Android o iOS. |
| Control de versiones | Git / GitHub; ejecución sobre *commit* identificado y registrado en cada resultado. |
| Registro de defectos | GitHub Issues con etiqueta `bug` y prioridad (`P1`–`P3`). |

**Estructura del repositorio para las pruebas:**

```
/pruebasdesoftware.md            ← este plan (casos manuales y enlaces a los automatizados)
/utils.py                        ← funciones puras extraídas de dashboard.py
/tests
   ├── test_limpiar.py           ← CP-01
   ├── test_matching.py          ← CP-02
   ├── test_categoria.py         ← CP-03, CP-04
   ├── test_estadisticas.py      ← CP-05
   └── test_estrato.py           ← CP-06
```

**Preparación para pruebas automatizadas:** dado que `dashboard.py` ejecuta la interfaz al importarse, las funciones puras (`limpiar`, `encontrar_mejor_match`, `map_categoria`, `figuras_estadisticas_barrio`) se probarán extrayéndolas a un módulo auxiliar (`utils.py`), sin alterar su lógica. Se ejecutan con `pytest tests/`.

**Datos de prueba:**

| ID | Conjunto | Uso |
|---|---|---|
| DP-01 | `ECV_2025_Limpio.xlsx` (datos reales) | Pruebas de sistema e integración. |
| DP-02 | `medellin_debug.geojson` (datos reales) | Pruebas de mapa e integración. |
| DP-03 | DataFrames sintéticos construidos en `pytest` (respuestas controladas, estratos enteros/decimales/nulos) | CP-05, CP-06. |
| DP-04 | Listas de cadenas con tildes, eñes, símbolos, vacías y nulas; pares de barrios del *matching* | CP-01 a CP-04. |
| DP-05 | Hoja de cálculo de referencia con cálculos manuales para 3 barrios seleccionados | CP-09, CP-10, CP-21. |
| DP-06 | Copias renombradas de los archivos de datos | CP-13, CP-14. |

### 5.5 Criterios de suspensión y finalización

**Criterios de suspensión:**
- La aplicación no inicia en el entorno de pruebas (bloquea todos los casos de sistema).
- Falla la carga de datos reales (Excel o GeoJSON) en el entorno de referencia.
- Más del 30 % de los casos ejecutados en un día fallan por una misma causa raíz.
- Cambio de código no planificado sobre la versión congelada.

**Criterios de reanudación:**
- Corrección del defecto bloqueante verificada en un nuevo *commit* identificado.
- Re-ejecución de los casos afectados y de una prueba de humo (CP-12, CP-15, CP-16).

**Criterios de finalización (salida):**
- 100 % de los casos asociados a riesgos **Críticos y Altos** ejecutados (CP-01 a CP-19 y CP-22).
- ≥ 90 % de los casos asociados a riesgos **Medios** ejecutados (CP-20, CP-21, CP-23, CP-24).
- 0 defectos abiertos de prioridad **P1** (datos erróneos o sistema inutilizable).
- Defectos **P2** abiertos documentados con decisión aprobada por el docente.
- ≥ 95 % de los casos ejecutados en estado "Aprobado" (al menos 23 de 24).
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
| A-05 | Extracción de funciones puras a módulo auxiliar | TD4 | `utils.py` |
| A-06 | Diseño de condiciones y casos de prueba | TD1–TD3 | Sección 5 |
| A-07 | Preparación de datos de prueba (DP-01 a DP-06) | TD4 | Datos de prueba |
| A-08 | Implementación de las 6 pruebas automatizadas | TD4 | `tests/test_*.py` |
| A-09 | Ejecución de pruebas automatizadas | TE2 | Reporte `pytest` |
| A-10 | Ejecución de las 18 pruebas manuales (integración y sistema) | TE2 | Registro de resultados |
| A-11 | Registro y seguimiento de defectos | TE3 | GitHub Issues |
| A-12 | Re-pruebas y pruebas de regresión | TE2 | Registro actualizado |
| A-13 | Informe de finalización de pruebas | TC1–TC4 | Informe final |

### 6.2 Estimación de esfuerzo por actividad

Técnica de estimación: **juicio de expertos del equipo + descomposición por actividades (WBS)**.

Bases de cálculo: A-08 = 6 casos × 1 h + 1 h de configuración de `pytest`; A-10 = 18 casos × 0,5 h de ejecución + 5 h de preparación de evidencias y hojas de cálculo.

| ID | Actividad | Esfuerzo (h-persona) | Dependencia | Responsables (h) |
|---|---|---|---|---|
| A-01 | Análisis del contexto | 2 | — | Jeyson (2) |
| A-02 | Análisis de riesgos | 3 | A-01 | Mateo (3) |
| A-03 | Plan de pruebas | 5 | A-02 | Jeyson (5) |
| A-04 | Capacitación y entorno | 5 | — | Keyner (2), Mateo (2), Jeyson (1) |
| A-05 | Extracción de funciones | 3 | A-04 | Keyner (3) |
| A-06 | Diseño de casos | 5 | A-02 | Mateo (5) |
| A-07 | Datos de prueba | 3 | A-06 | Mateo (2), Keyner (1) |
| A-08 | Implementación de pruebas automatizadas | 7 | A-05, A-07 | Keyner (7) |
| A-09 | Ejecución automatizada | 1 | A-08 | Keyner (1) |
| A-10 | Ejecución manual (integración y sistema) | 14 | A-06, A-07 | Mateo (5), Jeyson (4), Keyner (5) |
| A-11 | Gestión de defectos | 4 | A-10 | Jeyson (4) |
| A-12 | Re-pruebas y regresión | 6 | A-11 | Jeyson (2), Keyner (2), Mateo (2) |
| A-13 | Informe final | 4 | A-12 | Jeyson (2), Mateo (2) |
| | **Subtotal** | **62** | | Jeyson 20 · Keyner 21 · Mateo 21 |
| | Contingencia (≈ 15 %) | 9 | | |
| | **Total estimado** | **71 h-persona** | | |

**Verificación de viabilidad:** capacidad disponible = 3 personas × 8 h/semana × 3 semanas = **72 h-persona**. Total estimado 71 h ≤ 72 h, con 1 h de holgura adicional. La contingencia se libera para riesgos de exposición Media si no se consume.

---

## 7. Personal

### 7.1 Roles y responsabilidades de prueba

| Rol | Responsable | Suplente | Responsabilidades |
|---|---|---|---|
| Líder de pruebas y gestor de configuración | Jeyson González | Mateo Villada Villada | Plan de pruebas, seguimiento del cronograma, criterios de suspensión/finalización, informe final, contacto con el docente, congelamiento de versión, GitHub Issues y verificación de correcciones. |
| Analista de riesgos y diseño | Mateo Villada Villada | Keyner Gil | Matriz de riesgos, condiciones de prueba, casos y trazabilidad. Ejecuta CP-07 a CP-14 (datos, integración y carga de archivos). |
| Ingeniero de pruebas automatizadas | Keyner Gil | Jeyson González | Extracción de funciones, pruebas `pytest` (CP-01 a CP-06). Ejecuta CP-20 a CP-24 (selector, colores, instalación, móvil y navegadores). |
| Ejecutor de pruebas de navegación | Jeyson González | Mateo Villada Villada | Ejecuta CP-15 a CP-19 (transiciones de estado y modales). |
| Desarrolladores (corrección) | Todo el equipo | — | Corrección de defectos asignados. |
| Aprobador (docente) | Roberto José Calderón Bermejo | — | Aprobación del plan, aceptación del informe y de riesgos residuales. |

---

## 8. Cronograma

### 8.1 Hitos y fechas de ejecución (Alineado al ciclo de 3 semanas)

**Semana 1 — Planificación y diseño (10/11/2026 – 14/11/2026)**

| Fecha | Actividad | Hito |
|---|---|---|
| 10/11 | A-01, A-02 | Riesgos identificados |
| 11/11 – 12/11 | A-03, A-06 | — |
| 13/11 | A-04 (capacitación y entorno) | Entorno limpio operativo |
| 14/11 | Revisión con el docente | **H1: Plan de pruebas aprobado** |

**Semana 2 — Preparación y ejecución (17/11/2026 – 21/11/2026)**

| Fecha | Actividad | Hito |
|---|---|---|
| 17/11 | Congelamiento de código; A-05, A-07 | **H2: Versión bajo prueba congelada** |
| 18/11 – 19/11 | A-08, A-09 | Pruebas automatizadas ejecutadas |
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
Pruebas automat.                 ██████
Pruebas manuales                   ██████████   ████
Defectos / regresión                   ████     ██████
Informe final                                       ████
Hitos             H1 (14/11)  H2 (17/11)  H3 (21/11)  H4 (26/11)  H5 (28/11)
```