# CHECKLIST — Trabajo Integrador Unidad 11
**Proyecto:** DONAR-APP — Sistema de evaluación de donantes de sangre  
**Fecha de revisión:** 2026-05-25  
**Leyenda:** ✅ Cumplido · ⚠️ Parcial / mejorable · ❌ Falta

---

## 1. Reconocimiento de voz (ASR) — Bloque 4

| # | Requisito | Estado | Dónde está / Qué falta |
|---|-----------|--------|------------------------|
| 1.1 | Usuario puede interactuar por voz (micrófono del navegador) | ✅ | `useChatFlow.ts:iniciarVoz()` — botón 🎙️ en TabConsulta, panel "Asistente de voz" |
| 1.2 | SpeechRecognition (API de Google) como opción principal | ✅ | `window.SpeechRecognition / webkitSpeechRecognition`, `lang="es-AR"` |
| 1.3 | Whisper como alternativa offline | ✅ | Endpoint `/whisper` en `main.py:500-513` + `iniciarWhisper()` en hook |
| 1.4 | Transcripción visible en tiempo real en la interfaz | ✅ | Aparece como burbuja de usuario inmediatamente tras el reconocimiento |
| 1.5 | WER medido sobre 10+ frases de referencia | ✅ | 12 frases en `wer.py:FRASES_PRUEBA`, tab dedicado TabWER, endpoint `/wer/resumen` |
| 1.6 | WER media reportada | ✅ | `resumen_wer()` calcula promedio, visible en dashboard (StatCard "WER") |
| 1.7 | WER **desviación estándar** reportada | ❌ | `resumen_wer()` solo devuelve promedio; falta agregar `std` al cálculo |
| 1.8 | Documentar limitaciones del ASR (ruido, acentos, jerga) | ⚠️ | `evaluar_wer.py` tiene comentarios sobre tipos de errores (tildes, números); falta una sección formal de limitaciones en el informe |

**Estado del bloque: 6/8 ✅**

---

## 2. Síntesis de voz (TTS) — Bloque 4

| # | Requisito | Estado | Dónde está / Qué falta |
|---|-----------|--------|------------------------|
| 2.1 | Sistema responde al usuario con audio generado | ✅ | Endpoint `GET /tts` en `main.py:234-240` con gTTS |
| 2.2 | gTTS en español | ✅ | `lang="es", tld="com.ar"` — español rioplatense |
| 2.3 | Audio reproducible en la interfaz web | ✅ | `playTTS()` en `api.ts`, `<audio>` en `BotBurbuja.tsx` |
| 2.4 | Configurable: texto, voz o ambas | ✅ | Toggle "🔊 Voz activada / 🔇 Voz silenciada" en panel voz; panel texto sin TTS automático |

**Estado del bloque: 4/4 ✅**

---

## 3. Procesamiento del Lenguaje Natural — Bloque 1

| # | Requisito | Estado | Dónde está / Qué falta |
|---|-----------|--------|------------------------|
| 3.1 | Tokenización del texto de entrada | ✅ | `nlp.py:tokenizar()` — regex `[a-záéíóúüñ]+`, retorna lista de tokens |
| 3.2 | NER con al menos 3 tipos de entidades del dominio | ✅ | `extraer_entidades()` detecta: TIPO (50+ subcategorías de medicamentos, enfermedades, procedimientos), TIEMPO, PESO, EDAD |
| 3.3 | POS tagging | ✅ | `pos_tag()` en `nlp.py` — etiquetas VERB / NOUN / ADJ / STOP / NUM / OTHER (implementación propia con diccionarios) |
| 3.4 | Detección de intención o clasificación de consulta | ✅ | `detectar_intencion()` — 3 clases: `querer_donar`, `consulta_tiempo`, `consulta_general` |
| 3.5 | Uso de spaCy (`es_core_news_sm`) | ❌ | El PLN es completamente propio (regex + diccionarios). Funciona bien, pero la guía pide spaCy específicamente |
| 3.6 | Accuracy NER medida sobre 20+ ejemplos anotados | ❌ | No existe `eval_ner.py` ni conjunto de test anotado. Es uno de los ítems evaluados en la rúbrica (Accuracy NER ≥ 70%) |

**Estado del bloque: 4/6 ✅**

---

## 4. Modelo de N-gramas — Bloque 2

| # | Requisito | Estado | Dónde está / Qué falta |
|---|-----------|--------|------------------------|
| 4.1 | Modelo de bigramas entrenado en corpus del dominio | ✅ | `ngrams.py:ModeloNgramas.entrenar()` — corpus de `corpus.json` + frases de entrenamiento adicionales |
| 4.2 | Modelo de trigramas | ✅ | Mismo método `entrenar()` construye bigramas y trigramas simultáneamente |
| 4.3 | Suavizado Add-k con k configurable (no solo k=1) | ✅ | Parámetro `k` en constructor; slider en `TabNgramas.tsx`; acepta valores 0.01–10 |
| 4.4 | PP calculada y mostrada | ✅ | `perplejidad()` calculada por consulta, visible en tab N-gramas y en cada respuesta del backend |
| 4.5 | PP usada en al menos una funcionalidad | ✅ | Detección de fuera-de-dominio (PP > 60) en `main.py:181-197` — alerta al usuario si la consulta es incoherente |
| 4.6 | PP evaluada sobre **conjunto de test separado** del de entrenamiento | ❌ | No hay split train/test; PP se evalúa implícitamente sobre los mismos datos usados para entrenar |
| 4.7 | Comparación PP con MLE (k=0) vs Add-k | ❌ | No hay comparativa. La rúbrica dice "Comparar MLE vs Add-k" |
| 4.8 | Tablas de probabilidad de transición top-10 | ✅ | Endpoints `/ngramas/tabla_bigramas` y `/ngramas/tabla_trigramas` + `TabNgramas.tsx` con tablas interactivas |
| 4.9 | Autocompletado o sugerencia de continuación | ✅ | Endpoint `/ngramas/siguiente?palabra=...` — sección "Probabilidad condicional" en TabNgramas |
| 4.10 | Generación de texto (bonus) | ✅ | Endpoint `/ngramas/generar` — sección en TabNgramas |

**Estado del bloque: 7/10 ✅**

---

## 5. Recuperación de Información — Bloque 3

| # | Requisito | Estado | Dónde está / Qué falta |
|---|-----------|--------|------------------------|
| 5.1 | Índice invertido construido sobre el corpus | ✅ | `search.py:construir_indice()` |
| 5.2 | Pesos TF-IDF para cada término | ✅ | Calculado en `construir_indice()` — TF normalizado × IDF suavizado |
| 5.3 | Búsqueda por similitud coseno | ✅ | `buscar()` con `_coseno()` |
| 5.4 | Evaluación P/R/F1 sobre 10+ consultas etiquetadas | ✅ | 10 consultas en `main.py:CONSULTAS_EVALUACION`, `evaluar()` calcula P/R/F1 por consulta y promedio |
| 5.5 | Resultados rankeados con snippets | ✅ | Endpoint `/buscar` devuelve doc + score + snippet; visibles en `TabIR.tsx` |
| 5.6 | Índice persistido entre sesiones | ✅ | `indice_tfidf.json` — guardado al construir, cargado al iniciar el servidor |

**Estado del bloque: 6/6 ✅**

---

## 6. Persistencia en base de datos

| # | Requisito | Estado | Dónde está / Qué falta |
|---|-----------|--------|------------------------|
| 6.1 | SQLite como motor | ✅ | `donar.db` — creado automáticamente en `main.py:init_db()` |
| 6.2 | Mínimo 3 tablas | ✅ | `corpus`, `consultas`, `metricas` |
| 6.3 | Índice invertido persistido | ✅ | `indice_tfidf.json` (archivo JSON junto a la DB) |
| 6.4 | Historial con timestamp, texto original, texto transcripto, resultado, métricas | ✅ | Tabla `consultas` tiene: id, texto, texto_transcripto, resultado, motivo, intencion, entidades, fecha, perplejidad, score_ir, tiempo_respuesta_ms, origen |
| 6.5 | texto_transcripto separado del texto original en flujo de voz | ⚠️ | El campo existe pero en el flujo guiado la voz envía el texto transcripto directamente como "texto". En consultas libres sí se distinguen. |

**Estado del bloque: 4/5 ✅**

---

## 7. Interfaz web

### 7.1 Vista principal (usuario)

| # | Requisito | Estado | Dónde está / Qué falta |
|---|-----------|--------|------------------------|
| 7.1.1 | Botón de micrófono para captura de voz | ✅ | Panel "Asistente de voz" — botón 🎙️ grande, cambia a rojo mientras escucha |
| 7.1.2 | Campo de texto como alternativa | ✅ | Panel "Asistente de texto" con input + botón ➤ |
| 7.1.3 | Área de resultados con formato claro | ✅ | Interfaz de chat con burbujas `BotBurbuja` / `UsuarioBurbuja` |
| 7.1.4 | Reproducción de respuesta en audio (TTS) | ✅ | Auto-TTS en modo voz; toggle manual en ambos paneles |
| 7.1.5 | Historial de la sesión visible | ✅ | Mensajes acumulados en el chat durante la sesión |

### 7.2 Dashboard

| # | Requisito | Estado | Dónde está / Qué falta |
|---|-----------|--------|------------------------|
| 7.2.1 | Métricas globales (total consultas, WER, PP, tiempo de respuesta) | ✅ | 7 StatCards: total, aptos, no aptos, PP promedio, Score IR, tiempo ms, WER% |
| 7.2.2 | Top 10 consultas más frecuentes | ✅ | Barras horizontales con frecuencia relativa |
| 7.2.3 | Distribución por tipo/categoría (gráfico de torta) | ✅ | `PieChart` con colores por resultado (apto, no_apto_temporal, etc.) |
| 7.2.4 | Evolución temporal (gráfico de líneas por día) | ✅ | `LineChart` SVG con consultas por día |
| 7.2.5 | Métricas P/R/F1 del motor de búsqueda | ✅ | StatCards de Precisión, Recall, F1 con datos reales de `ir/metricas` |
| 7.2.6 | Nube de palabras o histograma de términos | ✅ | Nube de palabras CSS con tamaño proporcional a frecuencia |
| 7.2.7 | Datos REALES de la base de datos (no inventados) | ✅ | Todo viene de endpoints que leen SQLite en tiempo real |
| 7.2.8 | Exportar historial (bonus) | ✅ | Botón "⬇️ Exportar CSV" del historial |

**Estado del bloque: 13/13 ✅**

---

## 8. Evaluación y métricas

| # | Métrica | Estado | Detalle |
|---|---------|--------|---------|
| 8.1 | WER media sobre 10+ frases | ✅ | 12 frases, media calculada y guardada en DB |
| 8.2 | WER desviación estándar | ❌ | Falta agregar `std` a `resumen_wer()` en `wer.py` |
| 8.3 | PP sobre conjunto de test separado del de entrenamiento | ❌ | Todo el corpus es de entrenamiento; no hay set de test |
| 8.4 | Comparación PP MLE vs Add-k documentada | ❌ | No implementada; la guía la pide explícitamente |
| 8.5 | P/R/F1 sobre 10+ consultas etiquetadas | ✅ | 10 consultas en `CONSULTAS_EVALUACION`, evaluación automática al iniciar |
| 8.6 | Accuracy NER sobre 20+ ejemplos anotados | ❌ | No existe script de evaluación NER ni conjunto anotado |
| 8.7 | Tiempo de respuesta del pipeline medido | ✅ | `tiempo_respuesta_ms` medido y guardado en cada consulta, visible en dashboard |
| 8.8 | Valores documentados con números en informe | ❌ | No existe informe formal todavía |

**Estado del bloque: 4/8 ✅**

---

## 9. Documentación y entrega

| # | Requisito | Estado | Detalle |
|---|-----------|--------|---------|
| 9.1 | README.md con instrucciones de instalación y ejecución | ✅ | Completo: prerrequisitos, instalación, ejecución, estructura, endpoints, base de datos |
| 9.2 | requirements.txt con dependencias y versiones | ✅ | `backend/requirements.txt` con versiones fijadas |
| 9.3 | Informe técnico 3-5 páginas | ❌ | No existe. Debe incluir: descripción, arquitectura, corpus, métricas, limitaciones, mejoras |
| 9.4 | Video demo 3-5 minutos con voz real | ❌ | No existe |
| 9.5 | Código organizado en módulos | ✅ | `nlp.py`, `ngrams.py`, `search.py`, `wer.py`, `rules.py`, `main.py` — frontend en tabs y hooks |
| 9.6 | Docstrings en el código | ⚠️ | Solo `evaluar_wer.py` tiene docstring. El resto de los módulos no tiene docstrings en las clases/métodos |
| 9.7 | Presentación para defensa oral (15 min) | ❌ | No preparada todavía |

**Estado del bloque: 3/7 ✅**

---

## Estructura de archivos (recomendada vs actual)

| Recomendado por la guía | Estado | Archivo actual |
|------------------------|--------|----------------|
| `app.py` (Streamlit) | ➡️ Diferente (mejor) | `backend/main.py` (FastAPI) + `frontend/` (Next.js) — stack más profesional |
| `modules/asr.py` | ⚠️ | **No existe** — el ASR está en `useChatFlow.ts` (frontend). Falta un módulo Python para cálculo de WER documentado como ASR |
| `modules/nlp.py` | ✅ | `backend/nlp.py` |
| `modules/ngrams.py` | ✅ | `backend/ngrams.py` |
| `modules/search.py` | ✅ | `backend/search.py` |
| `modules/tts.py` | ⚠️ | TTS inline en `main.py:234-240` — no es módulo separado |
| `modules/db.py` | ⚠️ | DB inline en `main.py:72-134` — no es módulo separado |
| `data/corpus/` | ⚠️ | `backend/corpus.json` — un JSON, no carpeta con `.txt` individuales |
| `tests/eval_wer.py` | ✅ | `backend/evaluar_wer.py` |
| `tests/eval_search.py` | ⚠️ | Integrado en endpoint `/ir/metricas`, no script independiente |
| `tests/eval_ner.py` | ❌ | **No existe** |
| `docs/informe.pdf` | ❌ | **No existe** |

---

## Resumen ejecutivo

| Bloque | Cumplido | Total | % |
|--------|----------|-------|---|
| 1. ASR | 6 | 8 | 75% |
| 2. TTS | 4 | 4 | 100% |
| 3. PLN | 4 | 6 | 67% |
| 4. N-gramas | 7 | 10 | 70% |
| 5. IR | 6 | 6 | 100% |
| 6. Base de datos | 4 | 5 | 80% |
| 7. Interfaz | 13 | 13 | 100% |
| 8. Evaluación | 4 | 8 | 50% |
| 9. Documentación | 3 | 7 | 43% |
| **TOTAL** | **51** | **67** | **76%** |

---

## Lo que hay que hacer ahora (prioridades)

### 🔴 CRÍTICO — afecta directamente la nota

1. **Informe técnico** (`docs/informe.md` o `.pdf`, 3-5 páginas)  
   Debe incluir: descripción del problema, arquitectura, corpus, métricas obtenidas (WER, PP, P/R/F1), limitaciones y mejoras posibles.

2. **Video demo** (3-5 minutos)  
   Mostrar flujo completo con voz real: micrófono → transcripción → NLP → búsqueda → respuesta TTS → dashboard.

3. **Accuracy NER** (`tests/eval_ner.py`)  
   Crear 20+ oraciones anotadas manualmente con las entidades esperadas y medir cuántas detecta correctamente el sistema. Reportar porcentaje.

4. **WER desviación estándar**  
   Agregar `std` al retorno de `resumen_wer()` en `wer.py`. Una línea de código.

5. **Separación train/test para PP**  
   Reservar el 20% del corpus como set de test (no usarlo en `entrenar()`). Calcular PP sobre ese subset y reportar el valor.

### 🟡 IMPORTANTE — mejora significativa la nota

6. **Comparación MLE vs Add-k**  
   Ejecutar `perplejidad()` con `k=0.0001` (≈MLE) y con `k=1.0` sobre el mismo test set. Mostrar la tabla comparativa en el informe y en `TabNgramas`.

7. **Módulo `asr.py` en Python**  
   Crear `backend/asr.py` que encapsule `calcular_wer` y `FRASES_PRUEBA`. Importarlo en `main.py`. La guía pide que el backend tenga este módulo.

8. **Docstrings en módulos principales**  
   Agregar un docstring de una línea a cada clase y método público en `nlp.py`, `ngrams.py`, `search.py`, `wer.py`.

9. **Documentar limitaciones del ASR**  
   Agregar una sección en el informe o en el README con los tipos de errores observados (pérdida de tildes, números escritos como dígitos, vocabulario técnico médico no reconocido).

10. **Preparar presentación de defensa** (15 minutos)  
    Slides o esquema con: propósito del sistema, arquitectura, demo en vivo, métricas, análisis de errores, conclusiones.

### 🟢 OPCIONAL — puede sumar puntos

11. Separar `tts.py` y `db.py` como módulos independientes para alinearse a la estructura sugerida.
12. Agregar spaCy opcionalmente para NER (actualmente el PLN propio es funcional y más específico al dominio).
13. Crear `tests/eval_search.py` como script independiente (actualmente la evaluación IR está embebida en el servidor).
14. Limpiar archivos legacy (`backend/models.py`, `backend/database.py`) que el README mismo indica que no se usan.

---

## Lo que está muy bien (puntos fuertes a destacar en la defensa)

- **Stack profesional**: FastAPI + Next.js en vez de Streamlit — mucho más realista como prototipo funcional para un cliente real.
- **NLP propio con coverage amplio**: `rules.py` cubre 30+ condiciones médicas reales con tiempos de diferimiento correctos, incluyendo medicamentos específicos, vacunas, conductas de riesgo y enfermedades crónicas.
- **Dos motores de ASR integrados**: Web Speech API (online) y Whisper tiny (offline), con endpoint `/whisper` funcional.
- **Interfaz de chat dual**: panel de texto y panel de voz side-by-side, con flujo guiado de 20+ preguntas clínicas.
- **Dashboard 100% con datos reales**: todos los gráficos leen SQLite. Nunca hay datos ficticios.
- **N-gramas con 4 funcionalidades**: cálculo de PP, detección de fuera-de-dominio, autocompletado por probabilidad condicional, y generación de texto estadístico.
- **IR con persistencia**: el índice TF-IDF se guarda en `indice_tfidf.json` y no se recalcula en cada arranque.
- **Flujo de voz completo**: el asistente de voz guía al usuario por toda la entrevista clínica con TTS automático en cada pregunta y respuesta.

---

> Este checklist fue generado automáticamente revisando el código fuente contra los requisitos de la guía del trabajo integrador (Unidad 11 — Técnicas de Procesamiento del Habla).
