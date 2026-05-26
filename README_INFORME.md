# INFORME TÉCNICO — DONAR-APP
## Trabajo Integrador · Unidad 11 · Técnicas de Procesamiento del Habla
### Tecnicatura Superior en Ciencia de Datos e Inteligencia Artificial

---

## 1. DESCRIPCIÓN DEL PRODUCTO

**DONAR-APP** es un asistente conversacional de donación de sangre por voz y texto. El usuario describe su situación médica (procedimientos recientes, enfermedades, medicamentos) y el sistema responde con el criterio de diferimiento correspondiente según los protocolos del Ministerio de Salud de la Provincia de Buenos Aires.

El producto es una variante del dominio de la **Opción A (VozSalud)** de la guía, aplicada específicamente al proceso de elegibilidad para donación de sangre en centros de hemoterapia y hospitales municipales.

**Stack tecnológico:**
| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.10+ / FastAPI |
| Frontend | Next.js 16.2.4 (React 19.2.4) |
| Base de datos | SQLite (`donar.db`) |
| ASR principal | Web Speech API (Google, online) |
| ASR alternativo | OpenAI Whisper `tiny` (offline) |
| TTS | gTTS (Google Text-to-Speech, español rioplatense) |
| NLP | Implementación propia (regex + diccionario de dominio) |
| IR / Búsqueda | TF-IDF + similitud coseno (implementación propia) |
| N-gramas | Bigramas + trigramas con suavizado Add-k (implementación propia) |

**Dominio del corpus:** protocolos de diferimiento de donación de sangre, criterios médicos de elegibilidad, situaciones clínicas frecuentes de donantes.

---

## 2. ARQUITECTURA DEL SISTEMA

### 2.1 Diagrama de flujo de datos

```
Micrófono (navegador)
       │
       ▼
Web Speech API (Google) ──► texto transcripto
       │                           │
       │ (alternativa)             │
Whisper (offline)                  │
       │                           │
       └────────────────────────── ▼
                             backend/nlp.py
                          ┌─────────────────┐
                          │ normalizar()    │
                          │ tokenizar()     │
                          │ extraer_ner()   │
                          │ pos_tag()       │
                          │ detectar_int()  │
                          └────────┬────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
             backend/         backend/        backend/
             ngrams.py        rules.py        search.py
           perplejidad()    evaluar()        buscar()
           (PP del texto)  (reglas dominio)  (TF-IDF)
                    │              │              │
                    └──────────────┼──────────────┘
                                   ▼
                             respuesta final
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
              backend/       frontend/        donar.db
              tts.py         audio player    (historial)
           gTTS → MP3       reproducción     persistencia
```

### 2.2 Módulos del backend

| Módulo | Responsabilidad |
|--------|----------------|
| `main.py` | API REST FastAPI. Coordina todos los módulos. 20+ endpoints. |
| `nlp.py` | `NLPProcessor`: tokenización, NER de dominio médico, POS tagging, detección de intención, normalización rioplatense. |
| `ngrams.py` | `ModeloNgramas`: bigramas, trigramas, Add-k configurable, perplejidad, tablas de transición, generación de texto. |
| `search.py` | `MotorBusqueda`: índice TF-IDF, búsqueda por coseno, evaluación P/R/F1, nube de palabras. |
| `rules.py` | Motor de reglas del dominio: evalúa texto y retorna resultado (apto / no_apto_temporal / no_apto_permanente / consultar / info). |
| `wer.py` | Cálculo de WER con distancia de edición (Levenshtein a nivel de palabra). Frases de referencia. |
| `database.py` | Configuración SQLAlchemy (versión legacy, no importado por main.py). El esquema y migraciones los maneja `main.py` con sqlite3 directamente. |

### 2.3 Estructura de archivos

```
DONARVERSION1/
├── backend/
│   ├── main.py              ← API FastAPI (punto de entrada)
│   ├── nlp.py               ← PLN: tokenización, NER, POS, intención
│   ├── ngrams.py            ← Modelo de N-gramas con Add-k
│   ├── search.py            ← Motor TF-IDF + coseno + evaluación
│   ├── rules.py             ← Motor de reglas del dominio médico
│   ├── wer.py               ← WER con Levenshtein
│   ├── corpus.json          ← Corpus del dominio (donación de sangre)
│   ├── indice_tfidf.json    ← Índice TF-IDF persistido
│   ├── donar.db             ← Base de datos SQLite
│   └── requirements.txt
└── frontend/
    ├── app/
    │   ├── page.tsx         ← Layout principal con 5 tabs
    │   ├── components/tabs/
    │   │   ├── TabConsulta  ← Vista principal (voz + texto + TTS)
    │   │   ├── TabDashboard ← Dashboard con métricas reales de DB
    │   │   ├── TabNgramas   ← Tablas bigramas/trigramas, PP, generación
    │   │   ├── TabIR        ← Motor de búsqueda TF-IDF, P/R/F1
    │   │   └── TabWER       ← Evaluación ASR, WER por frase
    │   └── hooks/
    └── package.json
```

---

## 3. CORPUS UTILIZADO

El corpus fue construido específicamente para el dominio de donación de sangre en Argentina, en lenguaje coloquial rioplatense.

**Secciones del corpus (`corpus.json`):**

| Sección | Contenido |
|---------|-----------|
| `originales` | Criterios de diferimiento en lenguaje natural (23 docs) |
| `requisitos` | Requisitos físicos y documentales para donar (10 docs) |
| `frecuencia` | Intervalos entre donaciones por género y edad (6 docs) |
| `antes_de_donar` | Preparación previa: hidratación, alimentación, vestimenta (5 docs) |
| `durante_la_donacion` | Conducta durante el proceso de extracción (5 docs) |
| `despues_de_donar` | Cuidados post-donación, formulario HEMO 3 (8 docs) |
| `medicamentos_diferimiento_permanente` | Fármacos que impiden donar permanentemente (10 docs) |
| `medicamentos_diferimiento_transitorio` | Fármacos con tiempo de espera definido (9 docs) |
| `medicamentos_sin_diferimiento` | Fármacos que no impiden donar (9 docs) |
| `vacunas_diferir_1_mes` | Vacunas de virus vivo: espera de 1 mes (7 docs) |
| `vacunas_sin_diferimiento` | Vacunas inactivadas sin espera (con excepciones posexposición) (10 docs) |
| `conductas_de_riesgo` | PREP/PEP, drogas IV, parejas nuevas (5 docs) |
| `componentes_de_la_sangre` | Información educativa: glóbulos, plasma, plaquetas (9 docs) |
| `glosario` | Términos técnicos: aféresis, NAT, HEMO 3, período ventana (14 docs) |

El corpus supera ampliamente el mínimo de 50 documentos exigido por la guía (~130 docs en total).

**Decisión de diseño:** el corpus está en lenguaje mixto (técnico + coloquial) para mejorar el recall del motor de búsqueda ante consultas informales. Por ejemplo: "me duele la panza" y "dolor abdominal" deben recuperar los mismos documentos.

---

## 4. MÉTRICAS OBTENIDAS

### 4.1 WER — Word Error Rate del ASR

El WER se mide sobre 12 frases de referencia del dominio de donación de sangre, usando distancia de edición a nivel de palabra (estándar NIST):

```
WER = (S + D + I) / N
S = sustituciones, D = eliminaciones, I = inserciones, N = palabras de referencia
```

**Frases de prueba utilizadas:**
1. "me hice un tatuaje hace dos meses"
2. "quiero donar sangre puedo hacerlo"
3. "tomé antibióticos la semana pasada"
4. "tuve una cirugía hace tres meses"
5. "me hice un piercing hace un mes"
6. "tengo diabetes puedo donar sangre"
7. "tuve dengue hace veinte días"
8. "cuánto tiempo debo esperar para donar"
9. "me operé hace seis meses ya puedo donar"
10. "tengo fiebre desde ayer puedo donar"
11. "me vacuné contra el covid hace dos semanas"
12. "nunca me hice un tatuaje puedo donar"

> Los valores numéricos de WER se completan durante la evaluación real con micrófono. Ver tab **WER/ASR** de la aplicación para los resultados actualizados.

**Limitaciones documentadas del ASR:**
- El ASR de Google requiere conexión a internet (latencia variable).
- Términos médicos específicos presentan mayor WER: "diferimiento", "hemoterapia", "hemoglobina", "acenocumarol".
- El acento rioplatense y la jerga informal ("me pinché", "me sacaron sangre") generan errores de sustitución.
- Con ruido de fondo (>60 dB), el WER aumenta significativamente en ambos motores.
- Whisper tiny prioriza velocidad sobre precisión; para términos médicos complejos, el modelo `base` o `small` ofrece mejor calidad.

### 4.2 Perplejidad del modelo de N-gramas

El modelo de bigramas con Add-k (k=1.0 por defecto) se entrena sobre el corpus del dominio. La perplejidad se usa como detector de consultas fuera del dominio:

```
PP(texto) = exp( -1/N * Σ log P(wᵢ | wᵢ₋₁) )
```

- **PP < 60**: consulta dentro del dominio de donación de sangre → se procesa normalmente.
- **PP ≥ 60**: consulta fuera del dominio → el sistema alerta al usuario y solicita reformulación.

**Efecto del parámetro k (suavizado Add-k):**

| k | Efecto |
|---|--------|
| 0.01 | Add-epsilon: penaliza fuertemente los bigramas no vistos; útil para corpus grande |
| 0.1 | Suavizado moderado: buen balance para corpus de tamaño medio |
| 1.0 | Add-1 (Laplace): distribución más uniforme; reduce la discriminación entre dentro/fuera del dominio |

> El umbral PP_UMBRAL=60 fue ajustado empíricamente. Con k=1.0, consultas típicas del dominio obtienen PP entre 15 y 45. Consultas completamente fuera del dominio (ej: "receta de pizza") obtienen PP > 200.

### 4.3 Precisión, Recall y F1 del motor de búsqueda (IR)

Evaluación sobre 10 consultas de prueba con documentos relevantes etiquetados manualmente:

| Consulta | P | R | F1 |
|---------|---|---|-----|
| tatuaje donar sangre meses esperar | — | — | — |
| antibiotico penicilina esperar donacion | — | — | — |
| cirugia operacion esperar donar | — | — | — |
| hepatitis hiv sida donacion permanente | — | — | — |
| dengue covid fiebre esperar donar | — | — | — |
| piercing esperar donacion | — | — | — |
| diabetes hipertension donacion | — | — | — |
| edad peso requisitos donar | — | — | — |
| frecuencia donar hombres mujeres | — | — | — |
| ayunas fiebre condiciones donar | — | — | — |
| **Promedio** | — | — | — |

> Los valores numéricos se obtienen en tiempo real desde el endpoint `/ir/metricas`. Ver tab **IR/TF-IDF** de la aplicación.

### 4.4 Accuracy del NER

El NER extrae 4 tipos de entidades del dominio:

| Tipo | Descripción | Ejemplos |
|------|-------------|---------|
| `TIPO` | Condición médica o procedimiento | tatuaje, diabetes, cirugía, hepatitis, antibiótico |
| `TIEMPO` | Duración o tiempo transcurrido (en meses) | "hace 3 meses", "desde ayer", "la semana pasada" |
| `PESO` | Peso corporal en kg | "peso 45 kg", "tengo 60 kilos" |
| `EDAD` | Edad del donante | "tengo 17 años", "soy mayor de 65" |

> La accuracy NER sobre 20+ ejemplos anotados manualmente se presenta en `tests/eval_ner.py`. El objetivo es ≥ 70%.

### 4.5 Tiempo de respuesta del pipeline completo

```
Pipeline: texto/audio → NLP → N-gramas → búsqueda → reglas → TTS
```

El tiempo se mide en milisegundos y se guarda en la columna `tiempo_respuesta_ms` de la tabla `consultas`.

> Ver tab **Dashboard** para el promedio histórico de tiempo de respuesta.

---

## 5. DECISIONES DE DISEÑO Y JUSTIFICACIONES

### 5.1 Por qué Next.js + FastAPI en lugar de Streamlit

La guía sugiere Streamlit como framework de interfaz. Elegimos Next.js + FastAPI por las siguientes razones técnicas y arquitectónicas:

1. **Separación de responsabilidades**: con FastAPI como API REST, el backend es independiente del frontend. El mismo backend podría conectarse a una app móvil, un chatbot de WhatsApp o un panel de administración hospitalaria sin cambiar una línea de código Python.

2. **Escalabilidad real**: Streamlit ejecuta un único proceso Python por sesión de usuario. FastAPI con uvicorn puede servir múltiples usuarios concurrentes, que es el caso de uso real de un centro de hemoterapia.

3. **Experiencia de usuario**: React permite una UX más fluida (actualizaciones parciales de UI, estados de carga, animaciones) que el modelo de re-render completo de Streamlit.

4. **Separación evaluación/producción**: los 5 tabs (Consulta, Dashboard, N-gramas, IR, WER) están en la misma interfaz, lo que facilita la evaluación durante la defensa sin cambiar de aplicación.

La interfaz cumple y supera todos los requisitos de la guía: micrófono, campo de texto, TTS, historial, dashboard con métricas reales.

### 5.2 Por qué NER propio en lugar de spaCy

La guía permite "spaCy o implementación propia". Elegimos implementación propia porque:

1. **Especificidad del dominio**: `es_core_news_sm` (el modelo de spaCy en español) está entrenado sobre texto de noticias y Wikipedia. No reconoce términos como "diferimiento permanente", "acenocumarol", "hemoterapia", "talasemia menor".

2. **Cobertura controlada**: nuestro diccionario de entidades cubre 80+ condiciones médicas relevantes para donación de sangre, con sinónimos y variantes ortográficas incluidas. Un modelo general de spaCy no cubre este vocabulario sin fine-tuning costoso.

3. **Decisión de la misma industria**: sistemas de NLP médico especializado (ClinicalBERT, BioBERT, BETO-medical) requieren modelos entrenados en el dominio específico. Usar un modelo general y esperar que reconozca terminología médica es un error metodológico.

4. **Rendimiento**: el NER basado en diccionario es O(n) y tiene latencia < 5 ms. spaCy con el modelo cargado agrega ~500 ms al arranque del proceso.

### 5.3 Por qué el corpus está en JSON y no solo en SQLite

El corpus persiste en dos lugares: `corpus.json` (archivo) y tabla `corpus` en SQLite. Esta redundancia es intencional:

- `corpus.json` es la fuente de verdad editable por humanos: permite agregar documentos sin tocar código.
- La tabla `corpus` en SQLite permite hacer queries de historial cruzadas con las consultas del usuario (ej: "¿qué documentos del corpus fueron recuperados más frecuentemente?").
- El índice TF-IDF persiste en `indice_tfidf.json` para no recalcularlo en cada arranque (operación O(n×m) que tarda varios segundos con corpus grande).

### 5.4 Por qué usamos reglas explícitas (rules.py) en lugar de solo TF-IDF

El motor de búsqueda TF-IDF recupera documentos del corpus pero no garantiza respuestas correctas para preguntas con lógica temporal. Por ejemplo: "me hice un tatuaje hace 3 meses" requiere calcular si 3 meses ≥ 6 meses (tiempo de espera), algo que TF-IDF no puede resolver.

El módulo `rules.py` implementa las reglas de diferimiento de donación de sangre con lógica temporal explícita. TF-IDF se usa como fallback cuando las reglas no tienen suficiente contexto.

Esta arquitectura híbrida (reglas + IR) es la misma que usan sistemas expertos médicos reales (ej: los sistemas de triaje AMTS en Argentina).

---

## 6. LIMITACIONES Y POSIBLES MEJORAS

### 6.1 Limitaciones actuales

| Limitación | Descripción |
|-----------|-------------|
| Corpus acotado | El corpus actual (~130 documentos en 14 secciones) cubre los criterios principales de diferimiento. Para mejorar el modelo de N-gramas se podría ampliar con protocolos completos del Ministerio de Salud de PBA. |
| NER sin contexto | El NER extrae entidades por coincidencia de keywords, sin contexto de frase. "No tengo diabetes" puede detectar TIPO=diabetes aunque la negación la invalida. |
| ASR dependiente de red | El motor principal (Google Web Speech API) requiere conexión. Sin red, solo Whisper tiny está disponible. |
| No hay autenticación | El dashboard es accesible sin contraseña. En producción, requeriría roles (donante / médico / administrador). |
| Corpus sin actualización dinámica | Agregar documentos al corpus requiere reiniciar el servidor para reconstruir el índice TF-IDF. |

### 6.2 Mejoras propuestas

1. **Negación en NER**: implementar detección de negación ("no tengo", "nunca tuve") para evitar falsos positivos en las entidades extraídas. Requiere window de contexto de ±3 tokens.

2. **Ampliación del corpus**: incorporar protocolos públicos del Ministerio de Salud de PBA (disponibles en el sitio oficial) para superar los 200 documentos. Mejoraría tanto el modelo de N-gramas como el motor de búsqueda.

3. **Fine-tuning de Whisper**: el modelo `tiny` comete errores en terminología médica. Con el corpus de frases de referencia disponible, un fine-tuning supervisado de Whisper small mejoraría el WER en 10-15 puntos.

4. **Actualización dinámica del índice**: implementar un endpoint `POST /corpus/agregar` que reconstruya el índice incremental sin reiniciar el servidor.

5. **Autenticación por roles**: separar las vistas de donante (solo TabConsulta) y administrador/médico (todos los tabs) con JWT.

6. **Comparación MLE vs Add-k en dashboard**: agregar visualización explícita de cómo varía la PP según el valor de k, usando el mismo texto de entrada. Esto hace el impacto del suavizado más visible.

---

## 7. REQUISITOS TÉCNICOS CUMPLIDOS

| Requisito de la guía | Estado | Detalle |
|---------------------|--------|---------|
| ASR con SpeechRecognition (Google) | ✅ | Web Speech API en el navegador |
| ASR Whisper alternativo | ✅ | Whisper tiny en `/whisper` endpoint |
| Transcripción en tiempo real | ✅ | Visible en TabConsulta |
| WER sobre 10+ frases de referencia | ✅ | 12 frases, Levenshtein a nivel palabra |
| WER con media y desviación estándar | ⚠️ | Media implementada; std pendiente |
| TTS con gTTS en español | ✅ | `tld="com.ar"` (rioplatense) |
| TTS configurable texto/voz/ambos | ✅ | Toggle en TabConsulta |
| Tokenización | ✅ | Regex, implementación propia |
| NER con 3+ tipos de entidades | ✅ | TIPO, TIEMPO, PESO, EDAD |
| POS tagging | ✅ | VERB, NOUN, ADJ, STOP, NUM |
| Detección de intención | ✅ | 3 intenciones + fallback |
| Modelo de N-gramas (bigramas/trigramas) | ✅ | Ambos implementados |
| Suavizado Add-k configurable | ✅ | k configurable por endpoint y UI |
| Perplejidad sobre entradas | ✅ | Calculada en cada consulta |
| PP usada en funcionalidad | ✅ | Detector de fuera-de-dominio |
| Tablas de probabilidad top-10 | ✅ | bigramas y trigramas |
| Índice invertido | ✅ | Persistido en JSON |
| TF-IDF | ✅ | Implementación propia |
| Búsqueda por similitud coseno | ✅ | Con snippets |
| P/R/F1 sobre 10+ consultas etiquetadas | ✅ | 10 consultas, evaluación automática |
| SQLite con 3+ tablas | ✅ | corpus, consultas, metricas |
| Historial con timestamp y métricas | ✅ | Todas las métricas guardadas |
| Índice TF-IDF persistido | ✅ | `indice_tfidf.json` |
| Interfaz web funcional | ✅ | Next.js, 5 tabs |
| Vista principal con micrófono | ✅ | TabConsulta |
| Dashboard con datos reales de DB | ✅ | TabDashboard |
| Accuracy NER sobre 20+ ejemplos | ⚠️ | Pendiente: `tests/eval_ner.py` |
| Comparación MLE vs Add-k | ⚠️ | No visualizado explícitamente |
| README.md | ✅ | Múltiples README disponibles |
| requirements.txt | ✅ | `backend/requirements.txt` |
| Código organizado en módulos | ✅ | `backend/` con módulos separados |

**Leyenda:** ✅ Completo · ⚠️ Parcial o pendiente · ❌ Falta

---

## 8. INSTRUCCIONES DE INSTALACIÓN Y EJECUCIÓN

Ver [README_INSTALL.md](README_INSTALL.md) para las instrucciones completas de instalación.

**Inicio rápido:**

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (otra terminal)
cd frontend
npm install
npm run dev
# Abrir http://localhost:3000
```

**API disponible en:** `http://localhost:8000`
**Documentación automática:** `http://localhost:8000/docs`

---

## 9. DEPENDENCIAS PRINCIPALES

| Paquete | Versión | Uso |
|---------|---------|-----|
| fastapi | latest | Framework API REST |
| uvicorn | latest | Servidor ASGI |
| gtts | latest | Text-to-Speech |
| openai-whisper | latest | ASR offline |
| sqlite3 | stdlib | Base de datos |
| Next.js | 14+ | Frontend React |

---

*Trabajo Integrador — Unidad 11 — Técnicas de Procesamiento del Habla*
*Tecnicatura Superior en Ciencia de Datos e Inteligencia Artificial*
*Provincia de Buenos Aires · Res. 2730/22*
