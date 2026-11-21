# Plan de Pruebas — Dashboard Ambiental Medellín

> Documento elaborado según la estructura del plan de pruebas de **ISO/IEC/IEEE 29119-3:2013** (*Software and systems engineering — Software testing — Part 3: Test documentation*, cláusula 6.2 y Anexo A.2.4), con conformidad adaptada (*tailored conformance*, cláusula 2.2.2) declarada en la sección 2.3. Todas las cláusulas citadas en este plan son las de la edición 2013.
>
> **Cómo leer este documento respecto a la norma:** la sección 2.4 justifica por qué se eligió la serie ISO/IEC/IEEE 29119 y por qué se descartaron otras normas y marcos. Además, **cada sección termina con un apartado "Aplicación de la norma"** que indica, punto por punto: (1) qué exige la ISO 29119, (2) cómo se aplicó en este proyecto, (3) por qué se aplicó de esa forma, (4) por qué no se usó otra norma para ese punto y (5) qué parte de la norma no se aplicó y por qué. El Anexo B resume la conformidad con todos los procesos y documentos de la norma.

---

## 1. Información Específica del Documento

### 1.1 Identificador único del documento

| Campo | Valor |
|---|---|
| Identificador | `PP-DAM-2026-001` |
| Título | Plan de Pruebas del Dashboard Ambiental Medellín |
| Tipo de documento | Plan de Pruebas de Proyecto (*Project Test Plan*) |
| Versión | 1.2 |
| Estado | Borrador para aprobación |
| Fecha de emisión | 10/11/2026 (v1.1: 13/11/2026; v1.2: 17/11/2026) |
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
  - Mateo Villada
  - Keyner Gil

### 1.3 Autoridad de aprobación

| Rol | Nombre | Responsabilidad | Firma / Fecha |
|---|---|---|---|
| Docente | Roberto José Calderón Bermejo | Aprobación del plan, de los criterios de finalización y revisión del informe de cierre | |
| Líder de pruebas | Jeyson González | Elaboración y mantenimiento del plan | |

### 1.4 Historial de cambios y control de versiones

| Versión | Fecha | Autor | Descripción del cambio |
|---|---|---|---|
| 0.1 | 10/11/2026 | Equipo de desarrollo | Creación del borrador inicial con base en las directrices del docente. |
| 1.0 | 10/11/2026 | Jeyson González | Plan completo publicado en `master` (PR #2). Pendiente de aprobación. |
| 1.1 | 13/11/2026 | Keyner Gil | Equipo de pruebas de 3 personas (§1.2, §2.3, §3.3, §3.4, §7.1); capacidad recalculada (§6.2); nuevos casos CP-35 y CP-36 (§5.3); preparación de pruebas unitarias implementada en `tests/conftest.py` (§5.4); Anexo A con la primera ejecución de las pruebas automatizadas y el defecto DEF-001. |
| 1.2 | 17/11/2026 | Jeyson González | Justificación del marco normativo (§2.4: por qué ISO 29119 y por qué no otras normas); apartado "Aplicación de la norma" al final de cada sección; comunicación de las pruebas (§7.2) y métricas (§5.5); Anexo B (matriz de conformidad). Alineación con la edición **29119-3:2013**: cada cláusula citada se verificó contra el texto de la norma; se retiran los códigos de proceso de 29119-2 (TP, TD, TE…) y se usan los nombres de proceso que da 29119-3; se agregan los elementos obligatorios del plan que faltaban (subprocesos, entregables, re-pruebas y regresión, desviaciones de la estrategia organizacional, §5.6) y los campos del informe de incidencias (Anexo A.3). Correcciones: conteo de casos (36 = 16 automatizados + 20 manuales), mapeo de actividades a procesos (§6.1), referencias a casos en §4.3, §5.2, §5.4 y §5.5, y eliminación de la estructura obsoleta con `utils.py`. |

El documento se versiona en Git junto al código fuente. Cada modificación se realiza mediante *commit* con mensaje descriptivo y, para cambios de alcance, mediante *Pull Request* revisado por al menos un integrante distinto del autor.

### 1.5 Aplicación de la norma en la sección 1

| Punto | Qué exige la ISO 29119 | Cómo se aplicó | Por qué se aplicó así |
|---|---|---|---|
| 1.1 Identificador | 29119-3 §6.2.2.2 (*Unique identification of document*): identificar de forma única cada versión del documento (título, fecha, versión, estado). | Código `PP-DAM-2026-001` (PP = Plan de Pruebas, DAM = Dashboard Ambiental Medellín, año, consecutivo), con versión, estado y fecha. | Permite citar el plan sin ambigüedad desde el código (`tests/conftest.py` lo cita), desde los *Issues* de defectos y desde el informe final. |
| 1.2 Organización y autores | 29119-3 §6.2.2.3 (*Issuing organization*): organización responsable de preparar el documento; puede incluir a los autores. | Se nombra la organización y se separan los autores del dashboard de los autores del plan. | Deja claro quién responde por el plan y quién por el código probado; la separación se usa en la §7.3 para analizar la independencia de las pruebas. |
| 1.3 Autoridad de aprobación | 29119-3 §6.2.2.4 (*Approval authority*): personas responsables de revisar y aprobar el documento. | El docente es la autoridad de aprobación; el líder de pruebas mantiene el plan. | Sin aprobación el plan no tiene una línea base contra la cual medir el avance ni el cierre. Además, §2.2.2 exige que las decisiones de adaptación sean acordadas por las partes interesadas; el aprobador es quien las acepta. |
| 1.4 Historial de cambios | 29119-3 §6.2.2.5 (*Change history*): registro de todos los cambios desde el origen, con su motivo y autor. | Tabla de versiones + control en Git con *commits* y *Pull Requests*. | La propia norma (§1, *Scope*) deja el manejo de versiones fuera de su alcance porque es un tema de gestión de configuración; por eso se resuelve con Git, que ya era la herramienta del proyecto (restricción R-03). |

**Por qué no se usó otra norma en esta sección:** IEEE 829-2008 también pedía un identificador de plan, pero 29119-3 la reemplaza y su Anexo T.1 muestra la equivalencia (*8.1.1 Document identifier* → *Unique identification of document*); usar ambas duplicaría información. La cláusula 7.5 de ISO 9001 (información documentada) exige control de documentos dentro de un sistema de gestión de la calidad de una organización, que este proyecto académico no tiene.

**Qué no se aplicó y por qué:** no se usa firma electrónica ni un sistema formal de gestión documental. §6.2.2.4 dice que la aprobación puede ser electrónica, no que deba serlo; la aprobación del docente queda en la tabla 1.3 y en el *Pull Request*.

---

## 2. Introducción y Declaración de Adaptación (Tailoring)

### 2.1 Alcance del documento

Este plan define el enfoque, los recursos, el cronograma y las actividades de prueba del **Dashboard Ambiental Medellín**, una aplicación web desarrollada en Python/Streamlit que visualiza sobre un mapa interactivo la percepción ciudadana de cinco variables ambientales (Aire, Ríos, Ruido, Basuras y Contaminación Visual), a partir de la Encuesta de Calidad de Vida 2025 de *Medellín Cómo Vamos*.

El plan cubre el ciclo de pruebas de **3 semanas** sobre la versión del código en la rama `master` (commit `260f905a`), e incluye: gestión de riesgos, diseño de condiciones y casos de prueba, trazabilidad, entorno, criterios de suspensión/finalización, estimaciones, roles y cronograma.

El volumen de pruebas es de **36 casos**: **18 automatizados** con `pytest` (CP-01 a CP-14, CP-17, CP-18, CP-35 y CP-36; CP-06 y CP-07 se automatizaron el 21/11/2026) y **18 manuales** de sistema e instalación (CP-15, CP-16, CP-19 a CP-34). El avance de cada caso está en la tabla de §5.3.

### 2.2 Referencias documentales

| ID | Documento |
|---|---|
| REF-01 | ISO/IEC/IEEE 29119-1:2013 — Conceptos y definiciones. Referencia normativa de 29119-3 (cláusula 3). |
| REF-02 | ISO/IEC/IEEE 29119-2:2013 — Procesos de prueba. Referencia normativa de 29119-3 (cláusula 3). |
| REF-03 | **ISO/IEC/IEEE 29119-3:2013 — Documentación de pruebas. Norma principal de este plan.** |
| REF-04 | ISO/IEC/IEEE 29119-4:2015 — Técnicas de prueba. Citada por 29119-3 (Introducción) como la fuente de las técnicas de diseño. |
| REF-05 | Directrices del docente: "Estructura Actualizada del Plan de Pruebas (Basada en ISO/IEC/IEEE 29119-3)". |
| REF-06 | Código fuente: `dashboard.py`, `requirements.txt`, `medellin_debug.geojson`, `ECV_2025_Limpio.xlsx`, `assets/qrPIA.jpeg`. |
| REF-07 | Medellín Cómo Vamos. *Medellín se mide: Calidad de Vida y Percepción Ciudadana 2025*. |
| REF-08 | Documentación oficial de Streamlit, Folium/streamlit-folium y Plotly Express. |
| REF-09 | Normas y marcos evaluados y **no adoptados** (ver §2.4.3): IEEE 829-2008, ISO/IEC 25010:2023, IEEE 1012-2016, ISTQB CTFL v4.0, TMMi, ISO 9001:2015, ISO 31000:2018. |

### 2.3 Conformidad y Adaptación (Tailoring)

**Declaración:** El proyecto **NO** aplica la norma ISO/IEC/IEEE 29119 de forma íntegra. Se declara **conformidad adaptada** (*tailored conformance*) con ISO/IEC/IEEE 29119-3:2013, una de las dos formas de conformidad que define la norma (§2.2: completa o adaptada; la seleccionada debe declararse). Según §2.2.2, la conformidad adaptada exige: (a) justificar cada elemento de información que no se elabore, (b) registrar cada decisión con su razón, considerando los riesgos, y (c) que las decisiones sean acordadas por las partes interesadas. Las tablas de esta sección y el Anexo B cumplen (a) y (b); la aprobación del docente (§1.3) cumple (c). Además, §2.1 permite **combinar varios documentos en uno solo** y cambiar sus títulos sin perder la conformidad; por eso la especificación de pruebas y los registros de ejecución están dentro de este plan. Se justifica por:

1. **Nivel de criticidad del software: BAJO.** El dashboard es una herramienta académica de visualización y consulta. No procesa transacciones, no gestiona datos personales identificables, no controla procesos físicos ni toma decisiones automatizadas que afecten a personas. Un fallo produce, en el peor caso, una visualización incorrecta o una interrupción del servicio.
2. **Restricciones del proyecto:** ciclo de pruebas de **3 semanas**, equipo de 3 personas con dedicación parcial, sin presupuesto para herramientas comerciales ni entornos dedicados.

**Procesos y documentos que se mantienen:**

| Documento de 29119-3:2013 | Aplicación |
|---|---|
| Plan de pruebas (§6.2), con su registro de riesgos (§6.2.6) | Íntegro (este documento; riesgos en la sección 4). |
| Especificación de diseño de pruebas (§7.2) | Integrada: elementos de prueba (§3.1) y condiciones (§5.1). |
| Especificación de casos de prueba (§7.3) | Integrada: elementos de cobertura (§5.2) y casos (§5.3). |
| Especificación de procedimientos (§7.4) | Integrada: los procedimientos automatizados son los *scripts* `pytest` (§4.27 de la norma: "una especificación de procedimiento para una ejecución automatizada suele llamarse *test script*"); los manuales son los pasos de la tabla §5.3. |
| Requisitos de datos (§7.5) y de entorno (§7.6) | Integrados en §5.4. |
| Resultados reales (§7.9), resultado de la prueba (§7.10) y registro de ejecución (§7.11) | Integrados en el Anexo A. |
| Informe de incidencias (§7.12) | Anexo A.3 y *Issues* de GitHub. |
| Informe de finalización (§6.4) | Simplificado: un único informe al cierre del ciclo. |

**Procesos excluidos o reducidos y riesgo asumido:**

| Proceso excluido / reducido | Justificación | Riesgo asumido |
|---|---|---|
| Política de pruebas (§5.2) y estrategia organizacional de pruebas (§5.3) | Son documentos de una organización, no de un proyecto (§5.1: "no dependen del proyecto"). No existe una organización permanente; es un proyecto académico único. | Falta de lineamientos corporativos; se mitiga adoptando este plan como única referencia. |
| Planes de prueba por subproceso separados (§6.2.1: unitario, integración, sistema) | §6.2.1 permite un único plan para proyectos pequeños. Se consolidan en un plan de proyecto por el tamaño del sistema (un solo módulo `dashboard.py`); los subprocesos se identifican en §5.6. | Menor detalle por nivel; posible omisión de casos de integración finos. |
| Especificaciones de diseño, casos y procedimientos como documentos separados (§7.2–7.4) | §7.1 (nota) permite que sean capítulos de un mismo documento. Se integran en las secciones 5.1 a 5.3. | Menor granularidad documental; mitigado con IDs únicos y trazabilidad completa. |
| Informe de estado (§6.3) | Sustituido por la reunión semanal con las métricas de §5.5. La nota de §6.3.1 admite que el informe de estado no sea escrito y se trate en reuniones. | Menor visibilidad formal del avance intermedio. |
| Informes de preparación de datos (§7.7) y de entorno (§7.8) | Sustituidos por el hito H2 y el caso CP-32 (instalación limpia); los datos reales están versionados y los sintéticos se crean dentro de las pruebas. | Un problema de datos o entorno se detecta al ejecutar y no antes. |
| Pruebas de rendimiento con carga concurrente, seguridad avanzada (pentesting) y accesibilidad formal (WCAG) | Fuera del alcance de 3 semanas y de la criticidad del producto. | Posibles degradaciones con muchos usuarios concurrentes o barreras de accesibilidad no detectadas. Riesgo **aceptado** (ver R-14, R-15). |
| Automatización completa de pruebas de interfaz (Selenium/Playwright) | Costo de configuración elevado para el ciclo disponible. Solo se automatizan los 16 casos de lógica pura y de datos con `pytest`. | Las pruebas de UI dependen de ejecución manual, con mayor posibilidad de error humano. |

### 2.4 Justificación del marco normativo

#### 2.4.1 Por qué se utiliza ISO/IEC/IEEE 29119

| # | Motivo | Consecuencia para este proyecto |
|---|---|---|
| M-1 | **Es requisito del curso.** Las directrices del docente (REF-05) piden un plan basado en ISO/IEC/IEEE 29119-3. | La estructura de las secciones 1 a 8 sigue el esquema del plan de pruebas de 29119-3 (§6.2 y Anexo A.2.4). |
| M-2 | **Es la norma específica de documentación de pruebas.** Es una norma conjunta de ISO, IEC e IEEE que reemplaza a IEEE 829-2008 y a BS 7925-2; su Anexo T muestra la equivalencia con ambas. Se usa la edición 2013, que es la entregada por el docente. | Cada sección del plan corresponde a un elemento de información de la norma, y las cláusulas citadas se pueden verificar en ella. |
| M-3 | **Sirve para cualquier proyecto y cualquier ciclo de vida.** §1 (*Scope*): "puede ser usada por cualquier organización, proyecto o actividad de prueba más pequeña" y "es aplicable en todos los modelos de ciclo de vida". | Se aplica a un proyecto académico pequeño con una aplicación Python/Streamlit y herramientas libres (`pytest`, GitHub). |
| M-4 | **Pone el riesgo en el centro del plan.** §6.2.6 exige un registro de riesgos de producto y de proyecto con su nivel de exposición (probabilidad × impacto) y su tratamiento. | Con solo 72 h-persona, el riesgo decide qué se prueba primero y qué se acepta sin probar (sección 4). |
| M-5 | **Permite conformidad adaptada (§2.2.2).** | Se puede omitir o combinar documentos justificando cada decisión, sin la carga documental de una organización grande (§2.3). |
| M-6 | **Admite pruebas manuales y automatizadas.** Su resumen indica que sirve para pruebas funcionales y no funcionales, manuales y automatizadas, con guion o sin él. | Cubre a la vez los 18 casos en `pytest` y los 18 manuales. |

#### 2.4.2 Por qué el plan cita también las partes 1, 2 y 4

**La norma que se aplica es 29119-3.** El plan no declara conformidad con las partes 1, 2 ni 4; las cita por tres motivos que impone la propia 29119-3:

| Parte | Qué dice 29119-3 sobre ella | Para qué se usa en el plan | ¿Se declara conformidad? |
|---|---|---|---|
| **29119-1** (conceptos y definiciones) | §3: referencia **normativa**, "indispensable para su aplicación". Su Introducción dice que los conceptos y el vocabulario de la documentación están definidos en 29119-1. | Vocabulario del glosario (§2.5). La cláusula 4 de 29119-3 repite las definiciones necesarias, por lo que el glosario cita esas cláusulas (p. ej., §4.15 *test coverage item*). | No |
| **29119-2** (procesos de prueba) | §3: referencia **normativa**. §1: los documentos de 29119-3 son "salidas de los procesos de 29119-2". | Nombrar el proceso en el que se produce cada documento (planificación, diseño e implementación, preparación del entorno, ejecución, reporte de incidencias, seguimiento y control, finalización; §6.1 del plan). | No. El Anexo B de 29119-3 dice que el mapeo a 29119-2 es opcional para quien no la usa; por eso no se citan sus actividades internas. |
| **29119-4** (técnicas de prueba) | Introducción: las técnicas de diseño que se usan en el diseño de pruebas están definidas en 29119-4. §6.2.7.3 exige declarar qué técnicas se aplican. | Nombre y definición de las técnicas de §5.2 (PCE, AVL, tablas de decisión, transición de estados, escenarios, adivinación de errores). | No |

En resumen: 29119-3 dice **qué documentar**, pero para escribir ese contenido remite a la parte 1 (vocabulario), a la 2 (de qué proceso sale cada documento) y a la 4 (catálogo de técnicas). Quitar esas citas no haría el plan más fiel a 29119-3; lo dejaría sin la fuente de los términos y técnicas que la propia norma exige declarar.

**Partes de la serie que no se usan:**

| Parte | Contenido | Por qué no se usa |
|---|---|---|
| 29119-5 | Pruebas dirigidas por palabras clave (*keyword-driven*) | Ver abajo. |
| ISO/IEC TR 29119-6 | Guía para usar 29119 en proyectos ágiles | Ver abajo. |
| ISO/IEC TR 29119-11 | Guía para probar sistemas basados en IA | Ver abajo. |

**Motivos:**
- **29119-5:** sirve para automatizar pruebas de interfaz o de sistema con palabras clave reutilizables. Aquí solo se automatizan funciones puras con `pytest` y la interfaz se prueba a mano (§2.3), así que no hay *scripts* de UI que estructurar con palabras clave.
- **TR 29119-6:** orienta cómo aplicar la norma en iteraciones ágiles (*sprints*, historias de usuario). Este proyecto tiene un único ciclo de 3 semanas, con un plan aprobado al inicio y una versión congelada (S-04).
- **TR 29119-11:** trata sistemas con aprendizaje automático. El dashboard no tiene componentes de IA; solo calcula porcentajes y empareja nombres con `difflib`.

#### 2.4.3 Normas y marcos evaluados y no adoptados

| Alternativa | Qué es | Por qué no se utiliza |
|---|---|---|
| **IEEE 829-2008** (documentación de pruebas) | Antecesora de 29119-3. | 29119-3 la reemplaza; su Anexo T.1 muestra a qué cláusula de 29119-3 corresponde cada apartado de IEEE 829. Usarla sería basarse en una norma reemplazada y no cumpliría la directriz del docente (REF-05). |
| **BS 7925-1 / BS 7925-2** e **IEEE 1008** | Vocabulario, técnicas de prueba de componentes y pruebas unitarias. | Retiradas; su contenido está incorporado en la serie 29119 (el Anexo T.3 de 29119-3 mapea BS 7925-2). |
| **ISTQB** (CTFL v4.0) | Programa de certificación y cuerpo de conocimiento. | No es una norma: no define requisitos ni permite declarar conformidad. Su terminología coincide con 29119, por lo que sirve de apoyo conceptual, pero no como marco del plan. |
| **ISO/IEC 25010:2023** (SQuaRE) | Modelo de calidad del producto (adecuación funcional, rendimiento, compatibilidad, usabilidad, seguridad, etc.). | Define **qué** características de calidad existen, no **cómo** planificar, diseñar ni ejecutar pruebas. Los tipos de riesgo de la §4.1 son coherentes con sus características, pero no se declara conformidad porque el proyecto no tiene requisitos de calidad cuantificados que medir. |
| **IEEE 1012-2016** (verificación y validación) | V&V de sistemas según niveles de integridad, con V&V independiente en todo el ciclo de vida. | Pensada para sistemas críticos. El dashboard tiene criticidad **baja** (§2.3) y el esfuerzo exigido supera las 72 h-persona disponibles. El Anexo T.1 de 29119-3 indica que los niveles de integridad no aplican en 29119-3. |
| **TMMi / TPI NEXT** | Modelos de madurez para mejorar el proceso de pruebas de una organización. | Evalúan y mejoran organizaciones permanentes a lo largo del tiempo. Este es un proyecto único, sin organización que madurar (mismo motivo por el que se excluyen la política y la estrategia organizacional). |
| **ISO 9001:2015 / ISO/IEC/IEEE 90003:2018** | Sistemas de gestión de la calidad (y su guía para software). | No son normas de pruebas y requieren un sistema de gestión de la calidad implantado, que no existe. |
| **ISO 31000:2018** (gestión del riesgo) | Marco general de gestión de riesgos. | Es genérico. 29119-3 §6.2.6 ya define el registro de riesgos que necesita un plan de pruebas (riesgos de producto y de proyecto, exposición y tratamiento). |
| **IEC 62304, ISO 26262, DO-178C, EN 50128** | Normas sectoriales de software crítico (médico, automotriz, aviónico, ferroviario). | El dashboard no pertenece a ninguno de esos sectores ni afecta la seguridad de personas. |
| **OWASP WSTG / ASVS** | Guías de pruebas de seguridad web. | Las pruebas de seguridad avanzada están excluidas (§2.3, R-11 con exposición baja). |
| **WCAG 2.2** | Pautas de accesibilidad web. | La certificación de accesibilidad está excluida (§2.3, R-15 aceptado). |
| **BDD / TDD** | Prácticas de desarrollo guiado por comportamiento o por pruebas. | No son normas. TDD requiere escribir las pruebas antes que el código, y el dashboard ya estaba construido; BDD requiere requisitos en forma de escenarios de usuario, que el proyecto no tiene. |

**Conclusión:** ISO/IEC/IEEE 29119-3 es la única opción que cumple a la vez cuatro condiciones: (a) es la norma pedida por el curso, (b) es específica de documentación de pruebas y reemplaza a IEEE 829, (c) define todos los documentos del ciclo de pruebas, y (d) permite adaptarse a un proyecto pequeño. Las demás o están retiradas, o no tratan de pruebas, o están pensadas para organizaciones o sistemas críticos.

### 2.5 Glosario

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
| **Conformidad adaptada (*tailored conformance*)** | Forma de cumplir ISO/IEC/IEEE 29119 en la que se omiten o reducen procesos y documentos, justificando cada decisión (§2.3, Anexo B). |
| **Elemento de cobertura (*test coverage item*)** | Atributo de un elemento de prueba que se mide para saber cuánto se ha probado: una clase de equivalencia, un valor límite, una transición o una regla de decisión (29119-3 §4.15). |

### 2.6 Aplicación de la norma en la sección 2

| Punto | Qué exige la ISO 29119 | Cómo se aplicó | Por qué se aplicó así |
|---|---|---|---|
| 2.1 Alcance del documento | 29119-3 §6.2.3.1 (*Scope*): extensión del documento, inclusiones, exclusiones, supuestos y limitaciones. | Se fija el sistema, la versión bajo prueba (*commit* `260f905a`), la duración y el volumen de casos. | Fijar la versión es necesario para que los resultados sean reproducibles; sin ello un cambio de código invalida lo ya probado (RP-03). |
| 2.2 Referencias | 29119-3 §6.2.3.2 (*References*): documentos referenciados y repositorios de información del sistema y de las pruebas, separables en externos e internos. | Tabla REF-01 a REF-09: externas (normas, encuesta, documentación de librerías) e internas (código y datos del repositorio). | Deja claro contra qué edición de la norma se declara la conformidad (29119-3:2013) y en qué papel se citan las demás partes. |
| 2.3 Adaptación | 29119-3 §2.2.2 (*Tailored Conformance*): justificar cada elemento no elaborado, registrar la razón y los riesgos, y acordarlo con las partes interesadas. §2.1 permite combinar documentos. | Tablas de documentos mantenidos y excluidos, cada exclusión con su justificación y su riesgo asumido. | Es el mecanismo que la propia norma ofrece para proyectos pequeños; aplicarla completa (política organizacional, informes de estado, especificaciones separadas) consumiría más horas de las disponibles sin reducir riesgos de producto. |
| 2.4 Marco normativo | La norma no lo exige; se agrega porque el curso pide justificar la elección. | Motivos, uso de cada parte de la serie y comparación con alternativas. | Una decisión metodológica sin justificación no se puede evaluar. |
| 2.5 Glosario | 29119-3 §6.2.3.3 (*Glossary*): términos, abreviaturas y acrónimos usados en el documento. | Términos de prueba tomados de la cláusula 4 de 29119-3 (que remite a 29119-1) y términos del dominio (comuna, estrato, ECV). | Evita que el equipo y el docente interpreten de forma distinta palabras como "condición" o "caso". |

**Por qué no se usó otra norma en esta sección:** ver §2.4.3. En particular, la conformidad adaptada con reglas explícitas (§2.2.2) es lo que permite omitir documentos de forma justificada; IEEE 829-2008 no ofrece ese mecanismo con las mismas reglas.

**Qué no se aplicó y por qué:** no se aplica la conformidad completa (§2.2.1 exige todos los elementos de las cláusulas 5, 6 y 7; motivos en §2.3), no se declara conformidad con las partes 1, 2 y 4 (solo se citan; §2.4.2) y no se usan 29119-5, TR 29119-6 ni TR 29119-11.

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
- **16 casos automatizados** con `pytest`: funciones puras (TI-03, TI-04, TI-05, TI-09) y verificación de los datos reales del Excel (TI-12, CP-35 y CP-36).
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
- R-01: Ciclo total de **3 semanas** (10/11/2026 – 28/11/2026).
- R-02: Equipo de pruebas de 3 personas (Jeyson González, Mateo Villada, Keyner Gil) con dedicación parcial (≈ 8 h/semana por persona).
- R-03: Sin herramientas comerciales; solo software libre (`pytest`, GitHub Issues).
- R-04: La aplicación es un único script Streamlit, lo que dificulta pruebas unitarias aisladas (las funciones dependen de `st.session_state` y se ejecutan al importar el módulo).
- R-05: La carpeta `env/` versionada en el repositorio contiene rutas absolutas de otra máquina y no es reutilizable; cada evaluador debe crear su propio entorno virtual.

### 3.4 Partes interesadas

| Parte interesada | Interés en las pruebas |
|---|---|
| Asesores académicos (Ingry Gómez, Juan Zapata) | Calidad del producto y cumplimiento del proceso ISO 29119 adaptado. |
| Equipo de desarrollo original (Camilo Carmona, Keyner Gil, Jeyson González, Marisol Roche) | Conocer los defectos detectados y corregirlos antes de la entrega. |
| Equipo de pruebas (Jeyson González, Mateo Villada, Keyner Gil) | Planificar, diseñar y ejecutar las pruebas; registrar defectos y su verificación. |
| Usuarios finales (ciudadanía, estudiantes, tomadores de decisiones) | Información correcta, navegación clara y disponibilidad en web/móvil. |
| Medellín Cómo Vamos (fuente de datos) | Representación fiel de los datos de la encuesta. |

### 3.5 Aplicación de la norma en la sección 3

| Punto | Qué exige la ISO 29119 | Cómo se aplicó | Por qué se aplicó así |
|---|---|---|---|
| 3.1 Elementos de prueba | 29119-3 §6.2.4.2 (*Test item(s)*): identificar los elementos de prueba con su versión, o dónde encontrarla. | 13 elementos (TI-01 a TI-13), uno por función o grupo de funciones de `dashboard.py`, más los datos y las dependencias; la versión es el *commit* `260f905a` (§2.1). | El sistema es un único archivo; dividirlo por funciones es la forma de enlazar cada riesgo con la parte exacta del código que lo origina (trazabilidad de la §5.3). |
| 3.2 Alcance y exclusiones | 29119-3 §6.2.4.3 (*Test scope*): resumir las características que se prueban e identificar las que se excluyen **con la razón de la exclusión**. | Listas explícitas "dentro" y "fuera" del alcance, cada exclusión con su razón y su riesgo aceptado. | Lo que no se prueba es un riesgo residual; la norma exige justificarlo para que el aprobador lo acepte de forma consciente. |
| 3.3 Suposiciones y restricciones | 29119-3 §6.2.4.4 (*Assumptions and constraints*): supuestos y restricciones, como tiempo, costo y disponibilidad de personal, herramientas y entornos. | S-01 a S-04 y R-01 a R-05 (3 semanas, 3 personas, solo software libre, entorno no reutilizable). | Explican por qué el plan toma ciertas decisiones (p. ej., no importar `dashboard.py` en las pruebas por R-04). |
| 3.4 Partes interesadas | 29119-3 §6.2.4.5 (*Stakeholders*): listar las partes interesadas, su relación con las pruebas y **cómo se comunicará con cada una**. | Tabla con el interés de cada parte; la forma de comunicación está en §7.2. | Define a quién se comunica cada resultado y quién debe aceptar los riesgos residuales. |

**Por qué no se usó otra norma en esta sección:** ISO/IEC 25010 permitiría definir el alcance por características de calidad, pero no pide identificar elementos de prueba ni exclusiones; IEEE 829-2008 tenía apartados equivalentes (*features to be tested / not to be tested*), que el Anexo T.1 de 29119-3 hace corresponder con *Test scope*.

**Qué no se aplicó y por qué:** §6.2.4.1 pide identificar el proyecto o los subprocesos para los que se escribe el plan. Este plan es único para todo el proyecto; los subprocesos (unitario, integración, sistema, instalación) se identifican en §5.6, pero no tienen planes separados (§2.3).

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
| R-06 | Medio | Mitigar con pruebas | AVL y tabla de decisión sobre el selector de variables (CDP-09). |
| R-08 | Medio | Mitigar con pruebas | Verificación visual de colores vs. categoría dominante (CDP-10). |
| R-13 | Medio | Mitigar con pruebas | Instalación limpia y fijación de versiones (CDP-11). |
| R-16 | Medio | Mitigar con pruebas | Prueba exploratoria en móvil vía QR y en tres navegadores (CDP-12). |
| RP-03 | Medio | Mitigar con gestión | Congelamiento de código al inicio de Semana 2; ejecución sobre *commit* identificado. |
| RP-04 | Medio | Mitigar con gestión | Asignación cruzada: cada CP con responsable y suplente. |
| R-09 | Bajo | Aceptar (sin caso dedicado) | Se observa de forma oportunista durante CP-23, CP-24 y CP-27 (ubicación del marcador y zoom del barrio). Además, las pruebas opcionales `test_ti06_…` del Anexo A cubren `centroide_feature()` y `bounds_from_features()`. |
| R-10 | Bajo | Aceptar | El archivo QR está versionado; se verifica de forma oportunista al abrir el modal QR durante CP-33. |
| R-11 | Bajo | Aceptar | Los nombres provienen de fuentes controladas y el código ya usa `html.escape()` en la mayoría de puntos. |
| R-12 | Bajo | Aceptar | Se registra el tiempo de carga como dato informativo en CP-20; sin criterio de aceptación. |
| R-14 | Bajo | Aceptar | Excluido por *tailoring* (sección 2.3). |
| R-15 | Bajo | Aceptar | Excluido por *tailoring* (sección 2.3). |
| R-17 | Bajo | Aceptar | Se reporta como observación documental. |
| RP-05 | Bajo | Aceptar | Sesión de capacitación de 1 h en `pytest` en Semana 1. |

### 4.4 Aplicación de la norma en la sección 4

| Punto | Qué exige la ISO 29119 | Cómo se aplicó | Por qué se aplicó así |
|---|---|---|---|
| 4.1 Identificación | 29119-3 §6.2.6 (*Risk register*): identificar los riesgos considerados por las pruebas, separados en riesgos de **producto** (§6.2.6.1) y de **proyecto** (§6.2.6.2). | 17 riesgos de producto (R-01 a R-17) y 5 de proyecto (RP-01 a RP-05), cada uno ligado a un elemento de prueba. | Los riesgos se obtuvieron leyendo el código (p. ej., `cutoff=0.5` en el *matching*, `str(x).isdigit()` en el estrato), no de una lista genérica; por eso apuntan a defectos concretos, como DEF-001. |
| 4.2 Análisis | 29119-3 §6.2.6: dar a cada riesgo un **nivel de exposición basado en su impacto y su probabilidad**. La norma no impone la escala. | Matriz Probabilidad × Impacto de 3 × 3; Exposición = P × I. | Es exactamente el cálculo que pide la norma (el ejemplo del Anexo F.2.1 usa también E = P × I). Con 22 riesgos y un equipo de 3, una escala de 1 a 3 basta para ordenarlos. |
| 4.3 Tratamiento | 29119-3 §6.2.6: dar recomendaciones para tratar cada riesgo (el ejemplo de la norma: eliminar, reducir o ignorar). | Mitigar con pruebas (obligatorio para Críticos y Altos), mitigar con gestión o aceptar. | El esfuerzo se dirige a donde un fallo hace más daño y lo demás se acepta de forma explícita; los riesgos aceptados quedan como riesgos residuales para el informe de finalización (§6.4.4.6 de la norma). |

**Por qué no se usó otra norma en esta sección:** ISO 31000 es un marco genérico de gestión de riesgos que añadiría actividades (contexto organizacional, comunicación y monitoreo continuo) innecesarias aquí; 29119-3 ya define el registro de riesgos que necesita el plan. El AMFE/FMEA (IEC 60812) puntúa severidad, ocurrencia y detección para obtener un número de prioridad: es más preciso, pero desproporcionado para un sistema de criticidad baja.

**Qué no se aplicó y por qué:** el informe de estado de 29119-3 (§6.3.4.5) incluye los riesgos nuevos y modificados en cada periodo. Como ese informe se sustituye por la reunión semanal (§7.2), los riesgos se revisan ahí sin una nueva versión formal de la matriz, salvo que aparezca un riesgo nuevo o un defecto que cambie su exposición.

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

29119-3 §6.2.7.3 exige declarar las técnicas de diseño que se aplican; su definición se toma de ISO/IEC/IEEE 29119-4, que 29119-3 señala como fuente de las técnicas (ver §2.4.2). Las referencias de la columna central son cláusulas de 29119-4:

| Técnica | Referencia 29119-4 | Aplicación |
|---|---|---|
| **Partición de Clases de Equivalencia (PCE)** | §5.2.1 | CDP-01, CDP-03, CDP-06, CDP-07: clases de entradas de texto, categorías Likert, tipos de estrato y estados de archivos. |
| **Análisis de Valores Límite (AVL)** | §5.2.3 | CDP-02, CDP-04, CDP-09: similitud del *matching* alrededor del `cutoff` 0.7, 0 %/100 % de percepción negativa, barrio sin respuestas, 1/2/3/4 variables seleccionadas. |
| **Transición de Estados (TE)** | §5.2.8 | CDP-08: máquina de estados de navegación y modales. |
| **Tablas de Decisión** | §5.2.6 | CDP-09: combinaciones de "Todas" / variable ya seleccionada / variable nueva / máximo alcanzado. |
| **Pruebas basadas en escenarios / casos de uso** | §5.2.9 | CDP-05, CDP-10, CDP-12: recorridos completos del usuario. |
| **Adivinación de errores (*Error Guessing*)** | §5.4.1 | CDP-02, CDP-11: barrios homónimos, corregimientos, versiones de librerías. |

#### Datos de entrada generados por cada técnica

**AVL — `cutoff` del *matching* (CP-05).** `difflib.SequenceMatcher` calcula `ratio = 2·M / T`, donde M es el número de caracteres coincidentes y T el total de caracteres de ambas cadenas. Con el `cutoff = 0.7` se eligieron dos pares reales de nombres, uno justo por debajo y otro justo por encima del límite:

| Par (A, B) | M | T | Ratio | Resultado esperado con `cutoff = 0.7` |
|---|---|---|---|---|
| `LA AMERICA` / `LA CANDELARIA` | 8 | 23 | 0.6957 | Sin coincidencia (`None`) |
| `POBLADO` / `ROBLEDO` | 5 | 14 | 0.7143 | Coincidencia |

El segundo par es además un ejemplo de falso positivo: son barrios distintos que el *matching* aceptaría si no se restringe la búsqueda a la comuna.

**AVL — percepción negativa (CP-11 a CP-14).** Para `% negativo = (Mala + Muy mala) / total × 100`, con total = n:

| Caso límite | n | Negativas | % esperado |
|---|---|---|---|
| Barrio sin respuestas | 0 | 0 | `(None, None, None)` sin excepción |
| Mínimo | 10 | 0 | 0.0 |
| Máximo | 10 | 10 | 100.0 |
| Mixto (1 Mala, 1 Buena, 1 No sabe) | 3 | 1 | 33.3 |

**AVL — número de variables seleccionadas (CP-30).** Valores 1, 2, 3 (máximo permitido) y 4 (primer valor inválido).

**PCE — `map_categoria()` (CP-08 a CP-10).**

| Clase | Ejemplos de entrada | Salida esperada |
|---|---|---|
| V1 "muy buena" | "Muy buena", "MUY BUENA" | Muy buena |
| V2 "buena" (sin "muy") | "Buena", "buena " | Buena |
| V3 "aceptable"/"regular" | "Aceptable", "Regular" | Aceptable |
| V4 "muy mala" | "Muy mala", "MUY MALA", "Muy Mala " | Muy mala |
| V5 "mala" (sin "muy") | "Mala" | Mala |
| I1 nulo | `NaN`, `None` | No sabe |
| I2 otro texto | "No sabe", "NS/NR", "" | No sabe |

**PCE — estrato (CP-17, CP-18).** Clases: enteros (`1, 2, 3`), decimales (`1.0, 2.0`) y nulos (`NaN`). Un representante por clase.

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

**Casos de prueba:**

| ID CP | Técnica | Precondición | Entrada / Pasos | Resultado esperado | Nivel | Avance | Estado |
|---|---|---|---|---|---|---|---|
| CP-01 | PCE | — | `limpiar("Laureles Estadío")` | `"LAURELES ESTADIO"` | Unitario | 100 % | Aprobado (pytest, Anexo A) |
| CP-02 | PCE | — | `limpiar("  La  Candelaria!! ")` | `"LA CANDELARIA"` | Unitario | 100 % | Aprobado (pytest, Anexo A) |
| CP-03 | PCE / AVL | — | `limpiar("")`, `limpiar(None)` | `""` | Unitario | 100 % | Aprobado (pytest, Anexo A) |
| CP-04 | PCE | — | `limpiar("Castilla-Ñ")` | `"CASTILLA N"` | Unitario | 100 % | Aprobado (pytest, Anexo A) |
| CP-05 | AVL | Lista de barrios | `encontrar_mejor_match` con similitud justo por encima y por debajo de 0.7 | Devuelve coincidencia / `None` respectivamente | Unitario | 100 % | Aprobado (pytest, Anexo A) |
| CP-06 | Adivinación de errores | Datos cargados | Recorrer todos los *features* del GeoJSON y comparar `comuna_df` con la comuna oficial del polígono | 0 barrios asignados a comuna errónea; lista de no emparejados documentada | Integración | 100 % | Aprobado (pytest, `test_integracion_geojson.py`; Anexo A.6) |
| CP-07 | Adivinación de errores | Datos cargados | Verificar barrios homónimos en comunas distintas | Cada uno conserva su propia comuna | Integración | 100 % | Aprobado (pytest, `test_integracion_geojson.py`; Anexo A.6) |
| CP-08 | PCE | — | `map_categoria` con clases V1–V5 (5 valores) | Categoría correspondiente según tabla 5.2 | Unitario | 100 % | Aprobado (pytest, Anexo A) |
| CP-09 | PCE | — | `map_categoria` con I1–I2 (`NaN`, `""`, "NS/NR") | `"No sabe"` | Unitario | 100 % | Aprobado (pytest, Anexo A) |
| CP-10 | PCE | — | `map_categoria("MUY MALA")` y `"Muy Mala "` | `"Muy mala"` (no `"Mala"`) | Unitario | 100 % | Aprobado (pytest, Anexo A) |
| CP-11 | AVL | DataFrame sintético | 10 respuestas, 0 negativas | % negativo = 0.0 | Unitario | 100 % | Aprobado (pytest, Anexo A) |
| CP-12 | AVL | DataFrame sintético | 10 respuestas, 10 negativas | % negativo = 100.0 | Unitario | 100 % | Aprobado (pytest, Anexo A) |
| CP-13 | AVL | DataFrame sintético | 3 respuestas: 1 Mala, 1 Buena, 1 No sabe | % negativo = 33.3 | Unitario | 100 % | Aprobado (pytest, Anexo A) |
| CP-14 | AVL | — | DataFrame vacío | `(None, None, None)` sin excepción | Unitario | 100 % | Aprobado (pytest, Anexo A) |
| CP-15 | Escenario | Barrio real seleccionado | Comparar % del gráfico "Resumen por variable" con cálculo manual en hoja de cálculo | Diferencia ≤ 0.1 puntos | Sistema | 0 % | Pendiente — ver tabla de casos no completados |
| CP-16 | Escenario | Barrio con ≥ 2 estratos | Gráfico "Por estrato": sumar porcentajes de cada barra | Suma = 100 % ± 1 por estrato | Sistema | 0 % | Pendiente — ver tabla de casos no completados |
| CP-17 | PCE | DataFrame sintético | Columna estrato con enteros (`1, 2, 3`) | Etiquetas "Estrato 1..3"; filtro con 3 opciones | Unitario | 100 % | Aprobado (pytest, Anexo A) |
| CP-18 | PCE | DataFrame sintético | Columna estrato con decimales (`1.0, 2.0`, `NaN`) | Etiquetas "Estrato 1", "Estrato 2"; filtro no vacío | Unitario | 100 % | Aprobado tras corregir DEF-001 (Anexo A.6) |
| CP-19 | PCE | Barrio real | Aplicar filtro "Estrato 3" en el modal | Los tres gráficos y el conteo reflejan solo estrato 3 | Sistema | 0 % | Pendiente — ver tabla de casos no completados |
| CP-20 | PCE | Archivos válidos | Iniciar aplicación | Mapa con todas las comunas coloreadas, sin errores | Sistema | 100 % | Aprobado en Edge (21/11): mapa con todas las comunas, sin errores |
| CP-21 | PCE | Renombrar `medellin_debug.geojson` | Iniciar aplicación | Mensaje "Error cargando GeoJSON local", la app no se detiene | Sistema | 100 % | Aprobado (21/11): mensaje "Error cargando GeoJSON local", la app no se detiene |
| CP-22 | PCE | Renombrar `ECV_2025_Limpio.xlsx` | Iniciar aplicación | Mensaje de error controlado y la app se detiene sin excepción no controlada | Sistema | 100 % | Aprobado tras corregir DEF-002 (Anexo A.6) |
| CP-23 | TE | E0 | Clic en una comuna | Transición a E1: solo barrios de esa comuna, sidebar con "Comuna activa" | Sistema | 0 % | Pendiente — ver tabla de casos no completados |
| CP-24 | TE | E1 | Clic en un barrio | Transición a E2: modal de estadísticas con nombre de barrio y comuna correctos | Sistema | 0 % | Pendiente — ver tabla de casos no completados |
| CP-25 | TE | E2 | Clic en barra "Aire" o botón "💨 Aire" | Transición a E3: modal de detalle con la variable Aire | Sistema | 0 % | Pendiente — ver tabla de casos no completados |
| CP-26 | TE | E3 | "← Volver" | Retorna a E2 del mismo barrio | Sistema | 0 % | Pendiente — ver tabla de casos no completados |
| CP-27 | TE | E1b | "❌ Quitar" y luego "⬅️ Volver a todas las comunas" | E1 sin barrio y luego E0 con zoom/centro inicial | Sistema | 0 % | Pendiente — ver tabla de casos no completados |
| CP-28 | TE (transición inválida) | E2 abierto | Cerrar modal y pulsar F5 / recargar | No se reabre un modal sin barrio seleccionado; sin excepciones | Sistema | 0 % | Pendiente — ver tabla de casos no completados |
| CP-29 | Tabla de decisión | Vista general | Reglas D1–D6 de la tabla 5.2 | Estado del selector según tabla | Sistema | 0 % | Pendiente — ver tabla de casos no completados |
| CP-30 | AVL | 3 variables activas | Seleccionar una 4.ª variable | Quedan 3; se descarta la primera elegida; texto de ayuda "3 variables activas (máximo)" | Sistema | 0 % | Pendiente — ver tabla de casos no completados |
| CP-31 | Escenario | Comuna activa con 1 variable | Comparar color de 5 barrios con su categoría predominante calculada | Color = color de la leyenda para esa categoría | Sistema | 0 % | Pendiente — ver tabla de casos no completados |
| CP-32 | Adivinación de errores | Equipo limpio con Python 3.11+ | Crear `venv`, `pip install -r requirements.txt`, `streamlit run dashboard.py` | Aplicación inicia sin errores; se registran versiones instaladas | Instalación | 100 % | Aprobado (21/11): Python 3.12.6, streamlit 1.67.0, pandas 3.1.1, plotly 7.1.0, folium 1.0.0, streamlit-folium 0.27.4, openpyxl 3.1.5 |
| CP-33 | Escenario | Despliegue accesible por URL | Escanear QR desde móvil y navegar E0 → E2 | Mapa y modal legibles y operables | Sistema | 0 % | Pendiente — ver tabla de casos no completados |
| CP-34 | Escenario | — | Ejecutar CP-20, CP-23 y CP-24 en Chrome, Firefox y Edge | Resultado idéntico en los tres navegadores | Sistema | 11 % | En curso: 1 de 9 ejecuciones (CP-20 en Edge) |
| CP-35 | PCE / Adivinación de errores | `ECV_2025_Limpio.xlsx` (DP-01) | Para las 5 variables, comparar los valores únicos con el catálogo de 6 categorías y aplicar `map_categoria()` a cada valor | Ningún valor fuera del catálogo ni nulo; `map_categoria(v) == v` para todos | Integración | 100 % | Aprobado (pytest, Anexo A) |
| CP-36 | PCE | `ECV_2025_Limpio.xlsx` (DP-01) | Revisar tipo, rango y nulos de la columna `11. Estrato` | Tipo entero, valores entre 1 y 6, 0 nulos | Integración | 100 % | Aprobado (pytest, Anexo A) |

**Cómo se calcula el avance:** porcentaje de ejecuciones previstas del caso que ya se hicieron con evidencia (resultado de `pytest`, captura o registro en el Anexo A). Un caso con una sola ejecución está en 0 % o en 100 %; CP-34 tiene 9 ejecuciones (3 casos × 3 navegadores). Corte: **21/11/2026**.

**Resumen de avance:**

| Grupo | Casos | Completados | Avance |
|---|---|---|---|
| Riesgos Críticos y Altos (CP-01 a CP-28, CP-32, CP-35, CP-36) | 31 | 22 | **71 %** |
| Riesgos Medios (CP-29 a CP-31, CP-33, CP-34) | 5 | 0 | **2 %** (solo CP-34 iniciado) |
| **Total del plan** | **36** | **22** | **61 %** |
| Por forma de ejecución: automatizados | 18 | 18 | 100 % |
| Por forma de ejecución: manuales | 18 | 4 (CP-20, CP-21, CP-22, CP-32) | 22 % |

**Casos no completados: causa y plan de mejora:**

| Casos | Avance | Por qué no se ha completado | Plan de mejora | Responsable | Fecha |
|---|---|---|---|---|---|
| CP-15, CP-16, CP-19 (exactitud de porcentajes y filtro por estrato) | 0 % | Requieren la hoja de referencia DP-05 con el cálculo manual de 3 barrios, que aún no se ha elaborado. | (1) Elaborar DP-05 con 3 barrios de comunas distintas. (2) Automatizar el cálculo independiente con `pandas` y compararlo con `figuras_estadisticas_barrio()` como prueba de integración, para que se pueda repetir en cada regresión. (3) Verificar visualmente en la app un barrio. | Jeyson González (suplente: Mateo Villada) | 24–25/11 |
| CP-23 a CP-28 (navegación y modales) | 0 % | Pruebas manuales de interfaz; a la fecha no hay registro de ejecución en el repositorio. La dedicación parcial del equipo (RP-04) retrasó la ejecución. El mapa Folium se dibuja dentro de un `iframe`, lo que impide automatizar los clics sobre los polígonos. | (1) Ejecución manual con capturas en `docs/resultados-pruebas-sistema.md`. (2) Automatizar con `streamlit.testing` (AppTest) las transiciones que no dependen del clic en el mapa (CP-26, CP-27, CP-28) modificando `session_state`. | Mateo Villada (suplente: Keyner Gil) | 24–25/11 |
| CP-29, CP-30 (selector de variables) | 0 % | Igual que el grupo anterior: manuales y sin ejecutar. | Automatizar las reglas D1–D6 con AppTest pulsando los botones del selector (no dependen del mapa) y dejarlas en la suite de regresión. | Keyner Gil (suplente: Mateo Villada) | 25/11 |
| CP-31 (colores del mapa) | 0 % | Necesita comparar el color de cada barrio con su categoría predominante; no se ha ejecutado. | Calcular la categoría predominante de 5 barrios con `pandas` y compararla con el color en la app. | Mateo Villada | 25/11 |
| CP-33 (móvil vía QR) | 0 % | La app no está desplegada en una URL pública, así que el QR no se puede probar. | Desplegar en Streamlit Community Cloud; antes, fijar las versiones de `requirements.txt` con las verificadas en CP-32 (riesgo R-13). | Jeyson González | 26/11 |
| CP-34 (Chrome, Firefox y Edge) | 11 % | Solo se ejecutó CP-20 en Edge. | Repetir CP-20, CP-23 y CP-24 en Chrome y Firefox junto con la ejecución de CP-23/CP-24. | Mateo Villada | 25/11 |

Con estos pendientes **no se cumple todavía** el criterio de finalización de §5.5 ("100 % de los casos de riesgos Críticos y Altos"): faltan 9 de 31. El plan de mejora los cubre dentro de la reserva de la Semana 3 (RP-01).

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
| Dependencias | `requirements.txt` + `pytest` para pruebas automatizadas. |
| Ejecución | `streamlit run dashboard.py` (local) o despliegue en Streamlit Community Cloud para la prueba móvil. |
| Navegadores | Google Chrome, Mozilla Firefox, Microsoft Edge (últimas versiones); navegador móvil Android o iOS. |
| Control de versiones | Git / GitHub; ejecución sobre *commit* identificado y registrado en cada resultado. |
| Registro de defectos | GitHub Issues con etiqueta `bug` y prioridad (`P1`–`P3`). |

**Preparación para pruebas unitarias:** dado que `dashboard.py` ejecuta la interfaz al importarse, no se importa. `tests/conftest.py` lee `dashboard.py` con el módulo `ast`, extrae solo las funciones puras (`limpiar`, `encontrar_mejor_match`, `map_categoria`, `centroide_feature`, `bounds_from_features`, `figuras_estadisticas_barrio`) y las constantes que usan (`variables`, `COLOR_MAP_CATEG`, `CAT_ORDER`), y las ejecuta aisladas. Así `dashboard.py` no se modifica y las pruebas siempre ejercitan el código vigente, no una copia; si una función se renombra, la carga falla con un mensaje explícito. Las dependencias de prueba están en `requirements-test.txt` y se ejecutan con `python -m pytest -v` desde la raíz. (La v1.0 preveía extraer las funciones a un módulo `utils.py`; se descartó porque obligaba a mantener una copia del código que podía quedar desactualizada.)

**Estructura del repositorio para las pruebas:**

```
/pruebasdesoftware.md              ← este plan (casos manuales y enlaces a los automatizados)
/requirements-test.txt             ← dependencias de prueba (pytest)
/tests
   ├── conftest.py                 ← carga con `ast` las funciones puras de dashboard.py
   ├── test_funciones_dashboard.py ← CP-01 a CP-05, CP-08 a CP-14, CP-17, CP-18, TI-06 (opcional)
   └── test_datos_ecv.py           ← CP-35, CP-36 (datos reales del Excel)
```

**Datos de prueba:**

| ID | Conjunto | Uso |
|---|---|---|
| DP-01 | `ECV_2025_Limpio.xlsx` (datos reales) | Pruebas de sistema e integración (incluye CP-35 y CP-36). |
| DP-02 | `medellin_debug.geojson` (datos reales) | Pruebas de mapa e integración. |
| DP-03 | DataFrames sintéticos construidos en `pytest` (respuestas controladas, estratos enteros/decimales/nulos) | CP-11 a CP-14, CP-17, CP-18. |
| DP-04 | Listas de cadenas con tildes, eñes, símbolos, vacías y nulas; pares de barrios del *matching*; valores Likert | CP-01 a CP-05, CP-08 a CP-10. |
| DP-05 | Hoja de cálculo de referencia con cálculos manuales para 3 barrios seleccionados | CP-15, CP-16, CP-19. |
| DP-06 | Copias renombradas de los archivos de datos | CP-21, CP-22. |

### 5.5 Criterios de suspensión y finalización

**Criterios de suspensión:**
- La aplicación no inicia en el entorno de pruebas (bloquea todos los casos de sistema).
- Falla la carga de datos reales (Excel o GeoJSON) en el entorno de referencia.
- Más del 30 % de los casos ejecutados en un día fallan por una misma causa raíz.
- Cambio de código no planificado sobre la versión congelada.

**Criterios de reanudación:**
- Corrección del defecto bloqueante verificada en un nuevo *commit* identificado.
- Re-ejecución de los casos afectados, de la suite automatizada completa (`python -m pytest -v`) y de una prueba de humo (CP-20, CP-23, CP-24).

**Criterios de finalización (salida):**
- 100 % de los casos asociados a riesgos **Críticos y Altos** ejecutados (CP-01 a CP-28, CP-32, CP-35 y CP-36; ver matriz de trazabilidad §5.3).
- ≥ 90 % de los casos asociados solo a riesgos **Medios** ejecutados (CP-29, CP-30, CP-31, CP-33, CP-34).
- 0 defectos abiertos de prioridad **P1** (datos erróneos o sistema inutilizable).
- Defectos **P2** abiertos documentados con decisión aprobada por el docente.
- ≥ 95 % de los casos ejecutados en estado "Aprobado" (al menos 35 de 36). CP-18 cuenta como fallido mientras DEF-001 siga abierto.
- Informe de finalización de pruebas redactado y entregado.

**Métricas que se recolectan** (29119-3 §6.2.7.5, *Metrics to be collected*):

| Métrica | Cálculo | Uso |
|---|---|---|
| Avance de ejecución | Casos ejecutados / 36 | Seguimiento semanal (§7.2) y criterio de finalización. |
| Tasa de aprobación | Casos aprobados / casos ejecutados | Criterio de finalización (≥ 95 %). |
| Cobertura de riesgos | Riesgos Críticos y Altos con todos sus casos ejecutados / riesgos Críticos y Altos | Criterio de finalización (100 %). |
| Defectos por prioridad | Conteo de *Issues* abiertos y cerrados por P1, P2 y P3 | Criterio de finalización (0 P1) y decisión de suspensión. |
| Capacidad de detección | Defectos introducidos a propósito que las pruebas detectan / defectos introducidos | Confianza en la suite automatizada (Anexo A.4). |

### 5.6 Subprocesos, entregables, re-pruebas y desviaciones

29119-3 §6.2.7 incluye en la estrategia de pruebas cuatro elementos que el plan no tenía de forma explícita. El Anexo B.1.3 de la norma los marca como obligatorios (*shall*), excepto las desviaciones (*should*).

**Subprocesos de prueba (§6.2.7.1).** Este plan de proyecto cubre cuatro subprocesos, sin planes separados (§2.3):

| Subproceso | Casos | Forma de ejecución |
|---|---|---|
| Pruebas unitarias (componente) | CP-01 a CP-05, CP-08 a CP-14, CP-17, CP-18 | Automatizada (`pytest`) |
| Pruebas de integración de datos | CP-06, CP-07, CP-35, CP-36 | Automatizada (`pytest`) |
| Pruebas de sistema (funcionales y de compatibilidad) | CP-15, CP-16, CP-19 a CP-31, CP-33, CP-34 | Manual |
| Pruebas de instalación | CP-32 | Manual |

**Entregables de prueba (§6.2.7.2).**

| Entregable | Dónde queda | Responsable | Cuándo |
|---|---|---|---|
| Plan de pruebas (este documento, con la especificación de pruebas integrada) | `pruebasdesoftware.md` | Líder de pruebas | H1 (14/11) y cada nueva versión |
| *Scripts* de prueba automatizados y datos sintéticos | `tests/`, `requirements-test.txt` | Ingeniero de pruebas automatizadas | 18–19/11 |
| Registro de ejecución y resultados (automatizados y manuales) | Anexo A; `docs/resultados-pruebas-sistema.md` | Ingeniero de pruebas automatizadas; ejecutor de pruebas de sistema | Al ejecutar cada caso |
| Informes de incidencias | Anexo A.3 y GitHub *Issues* | Gestor de configuración y defectos | Al detectar cada defecto |
| Hoja de referencia DP-05 | Repositorio | Gestor de configuración y defectos | Antes de CP-15 |
| Informe de finalización | Repositorio | Líder de pruebas | H5 (28/11) |

**Re-pruebas y pruebas de regresión (§6.2.7.8).**
- **Re-prueba:** todo caso fallido se vuelve a ejecutar cuando su defecto se marca como corregido, sobre el nuevo *commit*.
- **Regresión:** después de cada corrección se ejecuta la suite automatizada completa (`python -m pytest -v`, menos de 2 s) y la prueba de humo (CP-20, CP-23, CP-24). En la Semana 3 (A-12) se repiten todos los casos de riesgo Crítico y Alto.
- **Ciclos estimados:** dos ciclos de ejecución (Semana 2 y Semana 3), el segundo con regresión completa.

**Desviaciones de la estrategia organizacional (§6.2.7.10).** No aplica: no existe una estrategia organizacional de pruebas (§2.3), por lo que no hay desviaciones que registrar. Este plan es la única referencia de estrategia.

### 5.7 Aplicación de la norma en la sección 5

| Punto | Qué exige la ISO 29119 | Cómo se aplicó | Por qué se aplicó así |
|---|---|---|---|
| 5.1 Condiciones de prueba | 29119-3 §7.2.5 (*Test conditions*, dentro de la especificación de diseño): cada condición con identificador único, descripción, prioridad y trazabilidad a la base de prueba. | 12 condiciones (CDP-01 a CDP-12), cada una ligada a uno o más riesgos; la prioridad es la exposición del riesgo. | El proyecto no tiene requisitos escritos; los riesgos de la §4 son la base de prueba disponible. La nota de §7.2.5.1 admite que una condición sea un modelo creado para probar (tabla de decisión, modelo de estados), como los de §5.2. |
| 5.2 Técnicas | 29119-3 §6.2.7.3 exige declarar las técnicas; §7.3.4 (*Test coverage items*) dice que los elementos de cobertura se obtienen aplicando una técnica a cada condición (p. ej., la PCE produce particiones válidas e inválidas). | Seis técnicas de 29119-4, elegidas según el tipo de entrada de cada condición; los elementos de cobertura son las clases, límites, transiciones y reglas de las tablas de la §5.2. | Cada técnica se aplica donde rinde más: PCE para entradas con categorías (texto, Likert, estrato), AVL para umbrales numéricos (`cutoff`, 0 %/100 %, máximo de 3 variables), transición de estados para la navegación con `session_state`, tablas de decisión para el selector con varias condiciones combinadas. |
| 5.3 Casos y trazabilidad | 29119-3 §7.3.5 (*Test cases*): identificador único, objetivo, prioridad, trazabilidad, precondiciones, entradas y resultados esperados. La matriz de trazabilidad está definida en §4.33. | 36 casos con esas columnas y una matriz Riesgo → Condición → Caso. | La trazabilidad demuestra la cobertura del 100 % de los riesgos Críticos y Altos y permite saber qué casos repetir si cambia una función. |
| 5.4 Entorno y datos | 29119-3 §6.2.7.6 y §6.2.7.7 (requisitos de datos y de entorno en el plan), detallables en §7.5 y §7.6. | Tabla de entorno, datos DP-01 a DP-06, entorno virtual nuevo y carga de funciones con `tests/conftest.py`. | El entorno versionado (`env/`) no era reutilizable (RP-02); sin un entorno reproducible los resultados de dos evaluadores no serían comparables. |
| 5.5 Criterios y métricas | 29119-3 §6.2.7.4 (criterios de finalización), §6.2.7.5 (métricas) y §6.2.7.9 (suspensión y reanudación: criterios, responsable y actividades a repetir). | Criterios medibles ligados a la exposición del riesgo y a la prioridad de los defectos; tabla de métricas; el líder de pruebas decide la suspensión (§7.1). | El ejemplo de la norma (§6.2.7.4) es "alcanzar una cobertura y tener menos de cierto número de defectos abiertos"; los criterios del plan siguen esa forma ("100 % de casos Críticos y Altos", "0 defectos P1"), lo que evita cerrar las pruebas por fecha en lugar de por calidad. |
| 5.6 Subprocesos, entregables, re-pruebas y desviaciones | 29119-3 §6.2.7.1, §6.2.7.2, §6.2.7.8 y §6.2.7.10. | Tablas de subprocesos y entregables, reglas de re-prueba y regresión, y declaración de que no hay estrategia organizacional. | Son elementos obligatorios del plan según el Anexo B.1.3; sin ellos el plan no cumpliría la cláusula 6.2. |

**Por qué no se usaron otras técnicas del catálogo de 29119-4:**
- **Árbol de clasificación y diseño combinatorio (*pairwise*):** sirven cuando hay muchos parámetros que se combinan. Aquí las entradas tienen uno o dos parámetros; la PCE y la tabla de decisión ya cubren las combinaciones relevantes.
- **Grafo causa-efecto:** produce lo mismo que la tabla de decisión del selector (D1–D6) con más trabajo.
- **Pruebas de sintaxis:** el sistema no recibe entradas con gramática formal (comandos, archivos con formato propio).
- **Pruebas aleatorias y metamórficas:** requieren un generador de datos o relaciones entre salidas; no compensan para funciones con resultados esperados fáciles de calcular a mano.
- **Técnicas estructurales (cobertura de sentencias y ramas, 29119-4 §5.3):** no se usan como técnica de diseño porque los riesgos son de exactitud de datos y de comportamiento, no de lógica interna compleja. Además, `tests/conftest.py` ejecuta las funciones fuera de `dashboard.py`, por lo que una medición de cobertura sobre ese archivo no sería fiable.

**Por qué no se usó otra norma en esta sección:** ISTQB describe las mismas técnicas, pero 29119-4 es la fuente que señala 29119-3. BDD (escenarios Gherkin) se descartó porque no hay requisitos en forma de escenarios de usuario (§2.4.3).

**Qué no se aplicó y por qué:** no se elaboran documentos separados de especificación de diseño, casos y procedimientos (29119-3 §7.2–7.4) ni los informes de preparación de datos y de entorno (§7.7–7.8). La nota de §7.1 permite que la especificación sea un capítulo de otro documento; los informes de preparación se sustituyen por el hito H2 y CP-32 (§2.3). Tampoco se agrupan los casos en conjuntos de prueba con identificador propio (§7.4.4): los conjuntos son los subprocesos de §5.6 y los archivos de `tests/`.

---

## 6. Actividades de Prueba y Estimaciones

### 6.1 Desglose de tareas

La columna "Proceso" usa los nombres de proceso con los que 29119-3 organiza sus documentos (cláusulas 6 y 7; §5.3.5.1 lista los cuatro procesos dinámicos).

| ID | Actividad | Proceso | Documento de 29119-3 que produce | Entregable |
|---|---|---|---|---|
| A-01 | Análisis del contexto e identificación de elementos de prueba | Planificación | Plan, §6.2.4 | Sección 3 |
| A-02 | Identificación y análisis de riesgos | Planificación | Plan, §6.2.6 | Sección 4 |
| A-03 | Redacción, aprobación y comunicación del plan | Planificación | Plan, §6.2 | Este documento |
| A-04 | Capacitación en `pytest` y preparación del entorno limpio | Preparación y mantenimiento del entorno | Requisitos de entorno, §7.6 | Entorno operativo |
| A-05 | Carga aislada de funciones puras para las pruebas | Preparación y mantenimiento del entorno | Requisitos de entorno, §7.6 | `tests/conftest.py` |
| A-06 | Diseño de condiciones y casos de prueba | Diseño e implementación | Especificación de diseño y de casos, §7.2–7.3 | Sección 5 |
| A-07 | Preparación de datos de prueba (DP-01 a DP-06) | Diseño e implementación | Requisitos de datos, §7.5 | Datos de prueba |
| A-08 | Implementación de los 16 casos automatizados | Diseño e implementación | Especificación de procedimientos (*test scripts*), §7.4 | `tests/test_*.py` |
| A-09 | Ejecución de pruebas automatizadas | Ejecución | Resultados y registro de ejecución, §7.9–7.11 | Reporte `pytest` (Anexo A) |
| A-10 | Ejecución de los 20 casos manuales (integración, sistema e instalación) | Ejecución | Resultados y registro de ejecución, §7.9–7.11 | Registro de resultados |
| A-11 | Registro y seguimiento de defectos | Reporte de incidencias | Informe de incidencias, §7.12 | GitHub Issues |
| A-12 | Re-pruebas y pruebas de regresión | Ejecución | Resultados, §7.9–7.10 | Registro actualizado |
| A-13 | Informe de finalización de pruebas | Finalización | Informe de finalización, §6.4 | Informe final |
| — | Seguimiento semanal del avance (incluido en las horas de A-11 y A-13) | Seguimiento y control | Sustituye al informe de estado, §6.3 | Acta breve de reunión (§7.2) |

### 6.2 Estimación de esfuerzo por actividad

Técnica de estimación: **juicio de expertos del equipo + descomposición por actividades (WBS)**.

| ID | Actividad | v1.0 (h) | v1.1 (h) | Jeyson | Mateo | Keyner | Motivo del ajuste |
|---|---|---|---|---|---|---|---|
| A-01 | Análisis del contexto | 3 | 3 | 3 | | | Ejecutada. |
| A-02 | Análisis de riesgos | 4 | 4 | 4 | | | Ejecutada. |
| A-03 | Plan de pruebas | 6 | 6 | 5 | | 1 | v1.0 (Jeyson) y v1.1 (Keyner). |
| A-04 | Capacitación y entorno | 6 | 3 | | | 3 | Entorno `.venv` documentado; capacitación de 1 h en `pytest` para el equipo. |
| A-05 | Extracción de funciones | 3 | 2 | | | 2 | Resuelta con `tests/conftest.py`, sin crear `utils.py`. |
| A-06 | Diseño de casos | 6 | 4 | 2 | 2 | | Casos ya diseñados en v1.0; resta detallar los manuales. |
| A-07 | Datos de prueba | 5 | 4 | 2 | | 2 | DP-03/DP-04 en las pruebas; DP-05/DP-06 pendientes. |
| A-08 | Implementación de pruebas unitarias | 12 | 8 | | | 8 | Implementadas (Anexo A). |
| A-09 | Ejecución unitaria | 2 | 1 | | | 1 | Automática (< 2 s por corrida). |
| A-10 | Ejecución integración y sistema | 20 | 16 | 4 | 11 | 1 | 20 casos manuales o de integración, ≈ 48 min por caso. |
| A-11 | Gestión de defectos | 5 | 4 | 2 | 2 | | |
| A-12 | Re-pruebas y regresión | 8 | 6 | | 3 | 3 | La regresión unitaria es automática. |
| A-13 | Informe final | 4 | 4 | 2 | 1 | 1 | |
| | **Subtotal** | **84** | **65** | **24** | **19** | **22** | |
| | Contingencia | 12 | 7 (≈ 10 %) | 0 | 5 | 2 | Reserva administrada por el líder de pruebas. |
| | **Total** | **96** | **72** | **24** | **24** | **24** | |

Capacidad disponible (v1.1): 3 personas × 8 h/semana × 3 semanas = **72 h-persona**. La reestimación v1.1 ajusta el esfuerzo al equipo de 3 personas sin recortar casos de prueba: se reduce en las actividades ya ejecutadas o automatizadas (A-04, A-05, A-08, A-09, A-12) y en el diseño ya realizado en la v1.0 (A-06, A-07). Cada integrante queda con 24 h (8 h/semana). La contingencia (7 h) se toma de la holgura de Mateo Villada (5 h) y Keyner Gil (2 h) y la asigna el líder de pruebas si alguna actividad se retrasa.

### 6.3 Aplicación de la norma en la sección 6

| Punto | Qué exige la ISO 29119 | Cómo se aplicó | Por qué se aplicó así |
|---|---|---|---|
| 6.1 Desglose de tareas | 29119-3 §6.2.8 (*Testing activities and estimates*): identificar todas las actividades según el proceso de prueba usado, incluidas re-pruebas y regresión. | 13 actividades + seguimiento, cada una con su proceso y el documento de 29119-3 que produce. | La asociación demuestra que se cubre el ciclo completo de la norma (planificar → diseñar → preparar entorno → ejecutar → reportar → cerrar) y permite revisar la conformidad del Anexo B. |
| 6.2 Estimación | 29119-3 §6.2.8: estimar cada actividad; la nota de la norma admite describir las actividades como una estructura de desglose de trabajo (WBS). No impone técnica de estimación. | Juicio de expertos + WBS, reestimada en la v1.1. | Es la forma que sugiere la propia norma y basta para 13 actividades. La reestimación v1.1 aplica §6.2.1: el plan "evoluciona con la re-planificación que se hace como parte del control". |

**Por qué no se usó otra técnica o norma en esta sección:** el Análisis de Puntos de Prueba (*Test Point Analysis*) requiere conocer los puntos de función del sistema, que no se midieron; COCOMO estima el esfuerzo de desarrollo, no el de pruebas. La guía PMBOK es de gestión general de proyectos y no aporta nada específico de pruebas que 29119-3 no cubra.

**Qué no se aplicó y por qué:** no hay un informe de estado formal en cada semana (29119-3 §6.3); el seguimiento se hace en la reunión semanal (§7.2).

---

## 7. Personal

### 7.1 Roles y responsabilidades de prueba

| Rol | Responsable | Suplente | Responsabilidades |
|---|---|---|---|
| Líder de pruebas | Jeyson González | Keyner Gil | Plan de pruebas, seguimiento del cronograma, criterios de suspensión/finalización, informe final, contacto con asesores. |
| Analista de riesgos y diseño | Jeyson González | Mateo Villada | Matriz de riesgos, condiciones de prueba, casos y trazabilidad. |
| Ingeniero de pruebas automatizadas | Keyner Gil | Jeyson González | Carga de funciones puras (`tests/conftest.py`), pruebas `pytest` (CP-01 a CP-05, CP-08 a CP-14, CP-17, CP-18, CP-35, CP-36) e instalación limpia (CP-32). |
| Ejecutor de pruebas de sistema | Mateo Villada | Keyner Gil | Pruebas manuales de navegación, selector de variables, colores, compatibilidad y móvil (CP-23 a CP-31, CP-33, CP-34). |
| Gestor de configuración y defectos | Jeyson González | Mateo Villada | Congelamiento de versión, GitHub Issues, verificación de correcciones; pruebas de integración y exactitud de datos (CP-06, CP-07, CP-15, CP-16, CP-19 a CP-22). |
| Desarrolladores (corrección) | Todo el equipo | — | Corrección de defectos asignados. |
| Aprobador (docente) | Roberto José Calderón Bermejo | — | Aprobación del plan, aceptación del informe y de riesgos residuales. |

**Necesidades de capacitación (29119-3 §6.2.9.3):** sesión de 1 h en `pytest` (Semana 1, RP-05). **Necesidades de contratación (§6.2.9.2):** ninguna; el equipo de 3 personas cubre todos los roles.

### 7.2 Comunicación de las pruebas

| Qué se comunica | A quién | Medio | Frecuencia |
|---|---|---|---|
| Avance (métricas de §5.5), bloqueos y riesgos nuevos | Equipo de pruebas | Reunión semanal y acta breve en el repositorio | Semanal |
| Defectos detectados | Equipo de desarrollo | GitHub *Issues* con etiqueta `bug` y prioridad P1–P3 | Al detectarlos |
| Cambios del plan | Equipo y docente | *Pull Request* con la nueva versión de este documento | En cada cambio de alcance |
| Resultado final y riesgos residuales | Docente y asesores | Informe de finalización | Al cierre (27–28/11) |

### 7.3 Aplicación de la norma en la sección 7

| Punto | Qué exige la ISO 29119 | Cómo se aplicó | Por qué se aplicó así |
|---|---|---|---|
| 7.1 Roles | 29119-3 §6.2.9.1 (*Roles, activities, and responsibilities*): responsables principales (líderes de la actividad) y secundarios (apoyo), y quién entrega los elementos de prueba. §6.2.9.2 y §6.2.9.3: necesidades de contratación y de capacitación. | Seis roles con responsable y suplente, casos asignados por rol, y necesidades de contratación y capacitación declaradas. | La pareja responsable/suplente es la que pide la norma (principal y secundario). Con dedicación parcial (RP-04), el suplente evita que un caso quede sin ejecutar, y la asignación cruzada da algo de independencia: quien escribió una parte del código no es el único que la prueba. |
| 7.2 Comunicación | 29119-3 §6.2.5 (*Testing communication*): líneas de comunicación entre las pruebas y las demás actividades, incluida la autoridad que resuelve problemas y aprueba. | Tabla de qué se comunica, a quién, por qué medio y con qué frecuencia. | Sustituye el informe de estado formal (§2.3) sin perder visibilidad del avance, como admite la nota de §6.3.1. |

**Por qué no se usó otra norma en esta sección:** los niveles de independencia de IEEE 1012 (V&V independiente con un equipo externo) son propios de sistemas críticos y no son viables con un equipo de 3 personas. En 29119-3 el grado de independencia se declara en la estrategia organizacional (§5.3.5.4), que este proyecto no tiene; por eso se resuelve con la asignación cruzada.

**Qué no se aplicó y por qué:** no hay un equipo de pruebas independiente del de desarrollo; el riesgo se reduce con la asignación cruzada de responsables y suplentes.

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

### 8.2 Aplicación de la norma en la sección 8

| Punto | Qué exige la ISO 29119 | Cómo se aplicó | Por qué se aplicó así |
|---|---|---|---|
| 8.1 Hitos y fechas | 29119-3 §6.2.10 (*Schedule*): hitos de prueba y calendario de cada actividad según las estimaciones, los recursos y las restricciones, indicando dónde los resultados vuelven al desarrollo. | Cronograma por semana con cinco hitos (H1 a H5) y un diagrama de barras. | Los hitos coinciden con los documentos de la norma: plan aprobado (§6.2), entorno y versión listos (§7.6), ejecución por prioridad de riesgo (§7.9–7.11), defectos devueltos al desarrollo y re-probados (§7.12) y cierre (§6.4). La ejecución empieza por los riesgos Críticos y Altos (H3) para que, si falta tiempo, lo que quede sin probar sea de exposición baja. |

**Por qué no se usó otra herramienta o norma en esta sección:** 29119-3 no exige una herramienta de cronograma (el ejemplo de su Anexo F.2.2 es un diagrama de barras simple); un diagrama en texto dentro del mismo archivo se versiona con Git y no requiere licencias (R-03), a diferencia de MS Project.

**Qué no se aplicó y por qué:** no se incluyen dependencias detalladas entre tareas ni ruta crítica; con 13 actividades en 3 semanas, el orden por semana es suficiente.

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

Campos según 29119-3 §7.12.5 (*Incident details*):

| Campo (§7.12.5) | DEF-001 |
|---|---|
| Fecha (§7.12.5.1) | 13/11/2026 |
| Originador (§7.12.5.2) | Keyner Gil, ingeniero de pruebas automatizadas |
| Contexto (§7.12.5.3) | Elemento TI-09 (`figuras_estadisticas_barrio()`) de `dashboard.py` en la versión `260f905a`; caso CP-18; subproceso de pruebas unitarias; entorno del Anexo A.1. |
| Descripción (§7.12.5.4) | Con estrato decimal (`1.0`), `str(x).isdigit()` es falso: la etiqueta queda `"1.0"` en lugar de `"Estrato 1"` (verificado por CP-18) y, por inspección de código, la lista del filtro de estratos de los modales queda vacía. Reproducible: `python -m pytest tests/test_funciones_dashboard.py -k cp18 -rx`. |
| Severidad (§7.12.5.5) | Baja: hoy no se manifiesta, porque CP-36 confirma que el Excel guarda el estrato como entero. Contorno conocido: mantener la columna como entero. |
| Prioridad (§7.12.5.6) | P3 propuesta; confirmar con el gestor de defectos. |
| Riesgo (§7.12.5.7) | Confirma el riesgo R-04; su exposición no cambia porque el defecto es latente. |
| Estado (§7.12.5.8) | **Cerrado** (21/11/2026): corregido con la función `estrato_entero()` en `dashboard.py` y verificado por CP-18 y CP-18b (ver A.6). |

| Campo (§7.12.5) | DEF-002 |
|---|---|
| Fecha (§7.12.5.1) | 21/11/2026 |
| Originador (§7.12.5.2) | Jeyson González, gestor de configuración y defectos |
| Contexto (§7.12.5.3) | Elemento TI-01 (`cargar_datos()`) de `dashboard.py`; caso CP-22; subproceso de pruebas de sistema; aplicación ejecutada sin el archivo `ECV_2025_Limpio.xlsx`. |
| Descripción (§7.12.5.4) | Si falta el Excel, `pd.read_excel()` lanza `FileNotFoundError` sin capturar y la aplicación muestra una traza técnica en lugar de un mensaje. La carga del GeoJSON sí estaba protegida (`try/except` + `st.error`). Reproducible: renombrar el Excel y ejecutar `streamlit run dashboard.py`. |
| Severidad (§7.12.5.5) | Media: la aplicación queda inutilizable, pero solo si falta el archivo de datos. |
| Prioridad (§7.12.5.6) | P2. |
| Riesgo (§7.12.5.7) | Confirma el riesgo R-05. |
| Estado (§7.12.5.8) | **Cerrado** (21/11/2026): `cargar_datos()` captura el error, muestra un mensaje con `st.error` y detiene la app con `st.stop()` (ver A.6). |

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

### A.6 Segunda ejecución: corrección de defectos y regresión (21/11/2026)

| Campo | Valor |
|---|---|
| Ejecutor | Jeyson González |
| Rama | `jeysongonzalez` |
| Entorno | Windows; Python 3.12 en `.venv` nuevo; dependencias de `requirements.txt` y `requirements-test.txt`. |
| Cambios en `dashboard.py` | (1) Nueva función `estrato_entero()`, usada en la etiqueta de estrato de `figuras_estadisticas_barrio()` y en los dos filtros de estrato de los modales (DEF-001). (2) `cargar_datos()` con `try/except`, `st.error` y `st.stop()` (DEF-002). |
| Cambios en `tests/` | Se retira el `xfail` de CP-18; se agregan CP-18b (`estrato_entero`) y `test_integracion_geojson.py` (CP-06, CP-07). |
| Resultado global | **49 pruebas aprobadas, 0 fallidas** (`python -m pytest -v`). |

| Caso | Antes | Después |
|---|---|---|
| CP-18 / CP-18b (DEF-001) | Fallido: etiquetas `{'1.0', '2.0'}` en lugar de `{'Estrato 1', 'Estrato 2'}`. | Aprobado. Al corregir, la marca `xfail(strict=True)` reportó `XPASS(strict)`, como estaba previsto, y se retiró. |
| CP-22 (DEF-002) | Fallido: excepción no controlada `FileNotFoundError: ... 'ECV_2025_Limpio.xlsx'`. | Aprobado: mensaje "No se pudo cargar el archivo de datos ECV_2025_Limpio.xlsx…" y la app se detiene de forma controlada. Con el Excel presente, la app carga sin errores. |
| CP-06 (R-01, Crítico) | — (no ejecutado en la primera corrida) | Aprobado: 332 polígonos, 0 asignados a una comuna ajena (299 por coincidencia exacta, 5 por barrio aproximado, 26 por comuna y 2 sin comuna en el GeoJSON). |
| CP-07 (R-01, Crítico) | — | Aprobado: 10 nombres de barrio repetidos en comunas distintas (p. ej. "San Pablo" en Popular y Altavista); todos conservan su comuna. |
| Regresión (suite completa) | 39 aprobadas + 1 `xfail` | 49 aprobadas |

### A.7 Aplicación de la norma en el Anexo A

| Punto | Qué exige la ISO 29119 | Cómo se aplicó | Por qué se aplicó así |
|---|---|---|---|
| A.1 Datos de la ejecución | 29119-3 §7.11 (*Test Execution Log*): eventos de la ejecución con identificador, hora, descripción e impacto; §7.11.2.3 permite indicar el probador si no es el autor. | Tabla con fecha, ejecutor, rama y *commit*, versiones de Python y librerías, comando y resultado global. | Sin la versión y el entorno exactos no se puede reproducir un resultado ni saber si un fallo nuevo es una regresión. |
| A.2 Resultado por caso | 29119-3 §7.9 (*Actual Results*) y §7.10 (*Test Result*: aprobado, fallido o bloqueado). | Tabla caso → prueba `pytest` → número de entradas → Aprobado / Fallido. | §7.9 admite que una herramienta automatizada registre los resultados reales y §7.10 que la comparación con el esperado sea "totalmente automatizada"; eso hace `pytest`. La tabla traduce su salida a los IDs del plan, y el caso fallido se marca con el número de su incidencia (DEF-001), como sugiere el ejemplo de §7.10. |
| A.3 Defectos | 29119-3 §7.12.5 (*Incident details*): fecha, originador, contexto, descripción reproducible, severidad, prioridad, riesgo y estado. | DEF-001 con los ocho campos; marca `xfail(strict=True)` en la prueba. | La marca `xfail` mantiene el defecto visible en cada ejecución sin bloquear la suite y avisa cuando se corrija. |
| A.4 Capacidad de detección | La norma no lo exige; es una verificación adicional (idea de las pruebas de mutación). | Defectos introducidos a propósito en una copia de `dashboard.py`. | Demuestra que las pruebas que pasan no pasan "por defecto": si el código falla, la prueba lo detecta. |

**Qué no se aplicó y por qué:** el registro de ejecución y los incidentes se anexan a este plan en lugar de ser documentos separados (§2.1 de la norma lo permite; ver §2.3). El registro de A.1 resume la sesión en una fila en lugar de listar cada evento con su hora (§7.11.4), porque la ejecución automatizada dura menos de 2 s y no tuvo eventos anómalos; la ejecución de los casos manuales sí registrará eventos con hora e impacto.

---

## Anexo B. Matriz de conformidad con ISO/IEC/IEEE 29119

> Es la declaración de conformidad adaptada de la §2.3 en forma de lista de verificación, contra ISO/IEC/IEEE 29119-3:2013. La nota 2 de §2.2.2 de la norma recomienda un mapeo así cuando los nombres o la organización de los documentos difieren de los de la norma.

### B.1 Contenido del plan de pruebas (29119-3 §6.2 y Anexo B.1.3)

La columna "Exigencia" es el nivel que la norma asigna a cada elemento en su Anexo B.1.3 (*shall* = obligatorio, *should* = recomendado).

| Elemento del plan (§) | Exigencia | Dónde está en este plan |
|---|---|---|
| Información del documento: identificador, organización, aprobación, historial (§6.2.2) | — | §1.1 a §1.4 |
| Introducción: alcance, referencias, glosario (§6.2.3) | — | §2.1, §2.2, §2.5 |
| Proyecto / subprocesos (§6.2.4.1) | *Shall* | §2.1 y §5.6 |
| Elementos de prueba (§6.2.4.2) | *Shall* | §3.1 |
| Alcance de las pruebas (§6.2.4.3) | *Shall* | §3.2 |
| Supuestos y restricciones (§6.2.4.4) | *Should* | §3.3 |
| Partes interesadas (§6.2.4.5) | *Should* | §3.4 |
| Comunicación de las pruebas (§6.2.5) | *Should* | §7.2 |
| Registro de riesgos: producto y proyecto (§6.2.6) | *Shall* | §4 |
| Subprocesos de prueba (§6.2.7.1) | *Shall* | §5.6 |
| Entregables (§6.2.7.2) | *Shall* | §5.6 |
| Técnicas de diseño (§6.2.7.3) | *Shall* | §5.2 |
| Criterios de finalización (§6.2.7.4) | *Shall* | §5.5 |
| Métricas (§6.2.7.5) | *Shall* | §5.5 |
| Requisitos de datos (§6.2.7.6) | *Shall* | §5.4 |
| Requisitos de entorno (§6.2.7.7) | *Shall* | §5.4 |
| Re-pruebas y regresión (§6.2.7.8) | *Shall* | §5.6 |
| Suspensión y reanudación (§6.2.7.9) | *Shall* | §5.5 |
| Desviaciones de la estrategia organizacional (§6.2.7.10) | *Should* | §5.6 (no aplica: no hay estrategia organizacional) |
| Actividades y estimaciones (§6.2.8) | *Shall* | §6.1, §6.2 |
| Roles, contratación y capacitación (§6.2.9) | *Should* | §7.1 |
| Cronograma (§6.2.10) | *Shall* | §8 |

Resultado: el plan contiene todos los elementos obligatorios y recomendados del plan de pruebas de 29119-3.

### B.2 Documentos (29119-3)

| Cláusula | Documento | Estado | Dónde | Justificación |
|---|---|---|---|---|
| §5.2 | Política de pruebas | **No aplicado** | — | Documento organizacional; no hay organización. |
| §5.3 | Estrategia organizacional de pruebas | **No aplicado** | — | Igual que el anterior; la estrategia del proyecto está en la §5. |
| §6.2 | Plan de pruebas | Aplicado | Este documento | — |
| §6.3 | Informe de estado | **Sustituido** | §7.2 | Reunión semanal con las métricas de la §5.5. |
| §6.4 | Informe de finalización | Pendiente (27/11) | A-13 | Se elabora al cierre. |
| §7.2 | Especificación del modelo de prueba | Integrado | §5.1, §5.2 | Evita duplicar información en un sistema de un solo módulo. |
| §7.3 | Especificación de casos | Integrado | §5.3 | Ídem. |
| §7.4 | Especificación de procedimientos | Integrado | §5.3, `tests/` | Ídem. |
| §7.5 | Requisitos de datos de prueba | Integrado | §5.4 (DP-01 a DP-06) | Ídem. |
| §7.6 | Requisitos de entorno | Integrado | §5.4 | Ídem. |
| §7.7 | Informe de preparación de datos | **Sustituido** | — | Los datos sintéticos se crean dentro de las pruebas y los reales están versionados; CP-35 y CP-36 verifican los reales. |
| §7.8 | Informe de preparación del entorno | **Sustituido** | Hito H2, CP-32 | La instalación limpia de CP-32 demuestra que el entorno está listo. |
| §7.9–7.10 | Resultados reales y resultado de la prueba | Aplicado | Anexo A.2 | — |
| §7.11 | Registro de ejecución | Aplicado | Anexo A.1 | — |
| §7.12 | Informe de incidencias | Aplicado | Anexo A.3, GitHub Issues | — |

### B.3 Técnicas declaradas (29119-3 §6.2.7.3; definiciones de 29119-4)

| Técnica | Estado | Dónde / por qué no |
|---|---|---|
| Partición de clases de equivalencia | Aplicada | §5.2, CP-01 a CP-04, CP-08 a CP-10, CP-17 a CP-22, CP-35, CP-36 |
| Análisis de valores límite | Aplicada | §5.2, CP-05, CP-11 a CP-14, CP-30 |
| Tablas de decisión | Aplicada | §5.2, CP-29 |
| Transición de estados | Aplicada | §5.2, CP-23 a CP-28 |
| Pruebas de escenarios | Aplicada | CP-15, CP-16, CP-31, CP-33, CP-34 |
| Adivinación de errores | Aplicada | CP-06, CP-07, CP-32, CP-35 |
| Árbol de clasificación, combinatoria, causa-efecto, sintaxis, aleatoria, metamórfica | No aplicadas | Motivos en §5.7 |
| Técnicas estructurales (sentencias, ramas, decisiones) | No aplicadas | Motivos en §5.7 |
