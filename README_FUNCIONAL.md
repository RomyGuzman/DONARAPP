# DONAR-APP — Guía Funcional Completa

> **Para quién es este documento:** estudiantes de primer año que necesitan entender qué hace cada parte de la aplicación, cómo se conectan entre sí, y poder explicarlo con sus propias palabras.

---

## ¿Qué hace esta aplicación en una sola oración?

El usuario describe su situación médica ("me hice un tatuaje hace 2 meses") y la aplicación le responde si puede donar sangre o no, explicando el motivo.

---

## Mapa general de la aplicación

```
┌─────────────────────────────────────────────┐
│              FRONTEND (Next.js)              │
│  Lo que ve el usuario en el navegador       │
│  Archivo principal: frontend/app/page.tsx   │
└───────────────────┬─────────────────────────┘
                    │ HTTP (peticiones y respuestas)
                    │ Ej: POST /consulta → respuesta JSON
                    ▼
┌─────────────────────────────────────────────┐
│              BACKEND (FastAPI)               │
│  El "cerebro" de la aplicación              │
│  Archivo principal: backend/main.py         │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  nlp.py  │  │ rules.py │  │ ngrams.py│  │
│  └──────────┘  └──────────┘  └──────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │search.py │  │  wer.py  │  │  db...   │  │
│  └──────────┘  └──────────┘  └──────────┘  │
└───────────────────┬─────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│           BASE DE DATOS (SQLite)             │
│  Archivo: backend/donar.db                  │
│  Guarda todas las consultas del usuario     │
└─────────────────────────────────────────────┘
```

---

## PARTE 1 — El Backend (la lógica)

El backend es la parte que el usuario **no ve**. Es el programa que recibe la pregunta del usuario, la analiza, y devuelve la respuesta. Está escrito en **Python**.

---

### `backend/main.py` — El director de orquesta

**¿Qué es?** Es el archivo principal del backend. Define todos los "endpoints" (las direcciones web a las que el frontend puede hacer preguntas).

**Analogía:** Es como el mostrador de un hospital. El paciente (frontend) llega con una consulta, el recepcionista (main.py) la recibe, la deriva al especialista correcto, y le devuelve la respuesta.

**¿Qué contiene?**

1. **El CORPUS** — una lista de 20 frases sobre donación de sangre. Es la "biblioteca" del sistema. Por ejemplo:
   ```
   "Si te hiciste un tatuaje reciente debes esperar 6 meses para donar sangre"
   "El dengue requiere esperar 28 días después de recuperarte para donar"
   ```

2. **CONSULTAS_EVALUACION** — 10 consultas de prueba con sus documentos relevantes. Se usan para medir qué tan bien funciona el buscador (Precisión, Recall, F1).

3. **CORPUS_ENTRENAMIENTO** — el corpus más frases adicionales simuladas. Se usa para entrenar el modelo de N-gramas.

4. **Los modelos en memoria:**
   - `modelo = ModeloNgramas()` — el modelo de lenguaje que se carga al iniciar
   - `nlp = NLPProcessor()` — el procesador de texto

5. **La base de datos** — funciones para crear y consultar las tablas SQLite.

6. **Los endpoints** — cada función con `@app.get(...)` o `@app.post(...)` es una "puerta" que escucha peticiones del frontend. Los principales son:

   | Endpoint | Qué hace |
   |----------|----------|
   | `POST /consulta` | Recibe la pregunta del usuario y devuelve el veredicto completo |
   | `GET /tts` | Convierte texto a audio MP3 (síntesis de voz) |
   | `POST /whisper` | Recibe un audio grabado y lo transcribe a texto |
   | `GET /historial` | Devuelve las últimas consultas guardadas |
   | `GET /stats/completo` | Devuelve todas las estadísticas para el Dashboard |
   | `GET /ngramas/tabla` | Devuelve la tabla de bigramas/trigramas |
   | `GET /ngramas/perplejidad` | Calcula qué tan "rara" es una frase |
   | `GET /ngramas/siguiente` | Predice la siguiente palabra |
   | `GET /ngramas/generar` | Genera texto automáticamente |
   | `GET /buscar` | Busca documentos relevantes con TF-IDF |
   | `GET /wer/frases` | Devuelve las 12 frases de prueba para evaluar el ASR |
   | `POST /wer/evaluar` | Calcula el WER entre una referencia y una transcripción |

**¿Cómo se inicia?**
```powershell
venv\Scripts\activate
python -m uvicorn main:app --reload
```
Esto levanta un servidor web en `http://localhost:8000`.

---

### `backend/nlp.py` — El que entiende el lenguaje

**¿Qué es?** NLP significa *Natural Language Processing* (Procesamiento del Lenguaje Natural). Este archivo contiene la clase `NLPProcessor`, que es el módulo encargado de "entender" lo que escribió el usuario.

**Analogía:** Es como un médico que lee la historia clínica del paciente y subraya las palabras importantes: "tatuaje", "2 meses", "cirugía".

**¿Qué hace exactamente?**

#### 1. Tokenización (`tokenizar`)
Convierte una oración en una lista de palabras individuales (tokens).
```
"Me hice un tatuaje hace 2 meses"
→ ["me", "hice", "un", "tatuaje", "hace", "meses"]
```
Los números y signos de puntuación se manejan por separado.

#### 2. POS Tagging (`pos_tag`)
POS = *Part of Speech* = categoría gramatical. A cada token le asigna una etiqueta:
- `VERB` — verbos: "hice", "tuve", "donar"
- `NOUN` — sustantivos: "tatuaje", "meses", "sangre"
- `ADJ` — adjetivos: "apto", "sano"
- `STOP` — palabras vacías que no aportan significado: "me", "un", "la"
- `NUM` — números: "2", "6"
- `OTHER` — todo lo demás

```
"me hice un tatuaje hace 2 meses"
→ me(STOP) hice(VERB) un(STOP) tatuaje(NOUN) hace(STOP) 2(NUM) meses(NOUN)
```

#### 3. Extracción de entidades NER (`extraer_entidades`)
NER = *Named Entity Recognition* = reconocimiento de entidades. Detecta los conceptos importantes:

**Tipos de entidades:**
- `TIPO` — qué situación tiene el usuario: tatuaje, piercing, medicamento, enfermedad, embarazo, viaje, cirugía
- `TIEMPO` — cuánto tiempo hace: "2 meses", "la semana pasada", "ayer", "hace mucho"
- `PESO` — cuánto pesa: "45 kg"
- `EDAD` — cuántos años tiene: "tengo 16 años"

**Ejemplos de detección de tiempo:**

| El usuario escribe | La app detecta |
|--------------------|---------------|
| "hace 2 meses" | TIEMPO = 2 meses |
| "hace tres semanas" | TIEMPO = 0.75 meses |
| "ayer" | TIEMPO = 0.03 meses (~1 día) |
| "la semana pasada" | TIEMPO = 0.25 meses |
| "el mes pasado" | TIEMPO = 1 mes |
| "hace mucho" | TIEMPO = 13 meses |
| "recién" | TIEMPO = 0.03 meses |

#### 4. Detección de intención (`detectar_intencion`)
Clasifica qué quiere saber el usuario:
- `querer_donar` — "quiero donar", "puedo donar"
- `consulta_tiempo` — "cuánto tiempo debo esperar"
- `informacion` — "qué requisitos necesito"
- `consulta_general` — cualquier otra cosa

#### 5. `interpretar`
Resume las entidades en: tipo, tiempo, peso, edad.

---

### `backend/rules.py` — El que toma la decisión

**¿Qué es?** El motor de reglas. Recibe las entidades detectadas por `nlp.py` y aplica las reglas médicas para decidir si el usuario puede donar o no.

**Analogía:** Es el médico que, después de que la enfermera (nlp.py) le resumió la situación del paciente, toma la decisión clínica.

**¿Qué devuelve?** Siempre devuelve un diccionario con dos campos:
- `resultado` — uno de estos valores:
  - `apto` — puede donar
  - `no_apto_temporal` — no puede donar ahora, pero en el futuro sí
  - `no_apto_permanente` — nunca podrá donar
  - `consultar` — necesita hablar con un médico
  - `info` — respuesta informativa (no es un veredicto)
- `mensaje` — el texto que se le muestra al usuario

**Las reglas que aplica (en orden):**

| Condición detectada | Resultado |
|--------------------|-----------|
| Peso < 50 kg | no_apto_permanente |
| Edad < 18 o > 65 | no_apto_permanente |
| Pregunta sobre ayunas | info (4 horas mínimo) |
| Hepatitis, HIV, SIDA, Diabetes, Cáncer | no_apto_permanente |
| Dengue (sin tiempo) | no_apto_temporal (esperar 1 mes) |
| Dengue (con tiempo >= 1 mes) | apto |
| COVID (sin tiempo) | no_apto_temporal (esperar 14 días) |
| Gripe / fiebre | no_apto_temporal (esperar 7 días) |
| Anemia, hipertensión | consultar |
| Medicamento / antibiótico | no_apto_temporal (7 días) |
| Tatuaje / piercing (sin tiempo) | no_apto_temporal (esperar 6 meses) |
| Tatuaje / piercing (con tiempo >= 6 meses) | apto |
| Cirugía | consultar |
| Vacuna virus vivo (fiebre amarilla, varicela...) | no_apto_temporal (4 semanas) |
| Vacuna común (COVID, gripe...) | no_apto_temporal (14 días) |
| Embarazo / lactancia | no_apto_temporal (6 meses post-parto) |
| Viaje a zona de malaria | no_apto_temporal (12 meses) |
| Viaje genérico | consultar |
| Pregunta sobre requisitos | info |
| Pregunta sobre frecuencia | info |
| Nada de lo anterior | info (fallback) |

---

### `backend/ngrams.py` — El modelo de lenguaje

**¿Qué es?** Implementa el modelo de N-gramas. Un N-grama es una secuencia de N palabras consecutivas. Este archivo contiene la clase `ModeloNgramas`.

**Analogía:** Es como aprender a adivinar la siguiente palabra de una oración contando cuántas veces aparecen pares y tríos de palabras juntas en los textos de entrenamiento. Si siempre que aparece "donar" viene después "sangre", el modelo aprende esa relación.

**¿Qué tipo de N-gramas usa?**

- **Unigramas** — palabras sueltas: "donar", "tatuaje", "meses"
- **Bigramas** — pares de palabras: "donar sangre", "tatuaje reciente"
- **Trigramas** — tríos de palabras: "donar sangre necesitás", "tatuaje hace meses"

**¿Para qué sirve cada función?**

#### `entrenar(corpus)`
Lee todos los textos del corpus y cuenta cuántas veces aparece cada par/trío de palabras. Guarda esos conteos en diccionarios.

#### `prob_bigrama(palabra, anterior)`
Calcula la probabilidad de que una palabra siga a otra.
- Ejemplo: ¿Cuál es la probabilidad de que "sangre" siga a "donar"?
- Fórmula con **suavizado Add-k**: `(conteo("donar sangre") + k) / (conteo("donar") + k × |vocabulario|)`
- El suavizado Add-k evita que la probabilidad sea 0 para palabras que nunca aparecieron juntas.

#### `perplejidad(texto)`
Mide qué tan "rara" o "inesperada" es una frase para el modelo.
- Una frase sobre donación de sangre → perplejidad baja (el modelo la espera)
- Una frase sobre otro tema → perplejidad alta (el modelo no la espera)
- **Se usa como detector de "fuera de dominio"**: si la perplejidad supera 60 (umbral), la consulta probablemente no es sobre donación.

#### `tabla_bigramas` y `tabla_trigramas`
Devuelven los pares/tríos más frecuentes del corpus para mostrarlos en la pestaña N-gramas de la app.

---

### `backend/search.py` — El buscador TF-IDF

**¿Qué es?** Implementa el motor de búsqueda por relevancia. Cuando el usuario hace una consulta, este módulo encuentra cuáles de los 20 documentos del corpus son los más relacionados.

**Analogía:** Es como Google, pero para los 20 documentos del corpus. Busca cuál habla más del tema que preguntó el usuario.

**¿Cómo funciona TF-IDF?**

- **TF (Term Frequency)** = cuántas veces aparece una palabra en un documento, dividido por el total de palabras de ese documento.
  - "dengue" aparece 3 veces en un documento de 10 palabras → TF = 0.3

- **IDF (Inverse Document Frequency)** = qué tan rara es esa palabra en todo el corpus.
  - Si "dengue" aparece en 2 de los 20 documentos → es específica → IDF alto
  - Si "sangre" aparece en los 20 documentos → es común → IDF bajo

- **TF-IDF = TF × IDF** = una palabra vale mucho si aparece mucho en ese documento pero poco en los demás.

**Similitud coseno:** Para comparar la consulta del usuario con cada documento, el sistema convierte ambos en vectores numéricos (uno por cada palabra del vocabulario) y mide el ángulo entre ellos. Cuanto más pequeño el ángulo, más parecidos son. El resultado es un número entre 0 y 1 — ese es el **Score IR**.

**Precisión, Recall, F1:**
- **Precisión** = de los documentos que el sistema recuperó, ¿cuántos eran realmente relevantes?
- **Recall** = de todos los documentos relevantes que existen, ¿cuántos recuperó el sistema?
- **F1** = promedio armónico de precisión y recall (balance entre ambos)

**`indice_tfidf.json`** — El índice se guarda en este archivo para no recalcularlo cada vez que se inicia el servidor.

---

### `backend/wer.py` — El evaluador de reconocimiento de voz

**¿Qué es?** WER = *Word Error Rate* = Tasa de Error por Palabras. Mide qué tan bien el sistema de reconocimiento de voz (ASR) transcribió lo que dijo el usuario.

**Analogía:** El usuario dice "me hice un tatuaje hace dos meses". El ASR escribe "me hice un tatuaje hace 2 meses". ¿Cuántas palabras se equivocó? Ese porcentaje es el WER.

**La fórmula:**
```
WER = (S + D + I) / N

S = Sustituciones (una palabra por otra: "dos" → "2")
D = Eliminaciones (una palabra que faltó)
I = Inserciones (una palabra que sobró)
N = Total de palabras en la referencia (lo que se dijo)
```

**Ejemplo:**
```
Referencia: "me hice un tatuaje hace dos meses"   (7 palabras)
Hipótesis:  "me hice un tatuaje hace 2 meses"
                                        ↑ sustitución

S=1, D=0, I=0, N=7 → WER = 1/7 = 14.3%
```

**Las 12 frases de prueba** son oraciones representativas del dominio de donación de sangre. Se usan para medir el WER del sistema ASR de forma consistente y reproducible.

**Resultados obtenidos:**
| Sistema | WER promedio |
|---------|-------------|
| Google ASR | 5.1% |
| Whisper tiny | 13.1% |

---

### `backend/nlp.py` + `backend/rules.py` juntos — El flujo completo de una consulta

Cuando el usuario escribe "tuve dengue hace dos meses", pasan estas cosas en orden:

```
1. main.py recibe el texto vía POST /consulta

2. nlp.py lo procesa:
   tokenizar → ["tuve", "dengue", "hace", "dos", "meses"]
   extraer_entidades → [
     {tipo: "TIPO", valor: "enfermedad"},   ← detectó "dengue"
     {tipo: "TIEMPO", unidad: "meses", valor: 2}  ← detectó "dos meses"
   ]
   interpretar → tipo="enfermedad", tiempo=2

3. rules.py evalúa:
   ¿"dengue" está en _ENFERMEDAD_ESPERA? Sí → espera = 1 mes
   ¿tiempo >= 1? Sí (tiempo=2) → resultado = "apto"
   mensaje = "Con 2 meses desde el episodio de dengue, ya podrías donar."

4. main.py también calcula:
   - perplejidad de la frase (ngrams.py)
   - documentos relevantes (search.py)
   - POS tags (nlp.py)

5. main.py guarda todo en la base de datos

6. main.py devuelve el JSON completo al frontend
```

---

### `backend/database.py` — La conexión a la base de datos

**¿Qué es?** Configura la conexión con SQLite usando SQLAlchemy (una biblioteca de Python para bases de datos).

**¿Qué contiene?**
- `DATABASE_URL` — la dirección del archivo de base de datos: `sqlite:///./donar.db`
- `engine` — el motor de conexión
- `SessionLocal` — una "fábrica" de sesiones de base de datos

**Nota:** Este archivo fue generado al inicio del proyecto pero en la versión actual el backend usa `sqlite3` directamente (sin SQLAlchemy) para mayor simplicidad. Este archivo queda como remanente de la primera versión.

---

### `backend/models.py` — El modelo de la base de datos (SQLAlchemy)

**¿Qué es?** Define la estructura de las tablas usando clases de Python (ORM = Object-Relational Mapping). Cada clase Python representa una tabla de la base de datos.

**Nota:** Al igual que `database.py`, este archivo es de la primera versión del proyecto. La versión actual maneja las tablas directamente con SQL en `main.py`. Queda como documentación de la estructura original.

---

### `backend/donar.db` — La base de datos

**¿Qué es?** El archivo físico donde se guardan todos los datos. Es una base de datos SQLite — un solo archivo que contiene todas las tablas.

**¿Por qué SQLite y no MySQL o PostgreSQL?** SQLite es perfecta para proyectos pequeños y de desarrollo: no necesita un servidor separado, el archivo es portable, y funciona sin configuración extra.

**Las 3 tablas:**

#### Tabla `corpus`
Guarda los documentos del corpus.
| Columna | Tipo | Para qué sirve |
|---------|------|----------------|
| id | INTEGER | Identificador único |
| texto | TEXT | El texto del documento |
| fecha_carga | TEXT | Cuándo se cargó |

#### Tabla `consultas`
Guarda cada consulta que hace un usuario.
| Columna | Tipo | Para qué sirve |
|---------|------|----------------|
| id | INTEGER | Identificador único |
| texto | TEXT | Lo que escribió el usuario |
| resultado | TEXT | apto / no_apto_temporal / etc. |
| respuesta | TEXT | El mensaje que recibió |
| intencion | TEXT | querer_donar / informacion / etc. |
| entidades | TEXT | JSON con las entidades detectadas |
| perplejidad | REAL | Qué tan rara fue la frase |
| fuera_de_dominio | INTEGER | 1 si perplejidad > 60 |
| score_ir | REAL | Similitud con el documento más relevante |
| tiempo_respuesta_ms | INTEGER | Cuántos milisegundos tardó |
| origen | TEXT | "texto", "voz" o "whisper" |
| fecha | TEXT | Cuándo se hizo la consulta |

#### Tabla `metricas`
Guarda evaluaciones de WER y otras métricas.
| Columna | Tipo | Para qué sirve |
|---------|------|----------------|
| id | INTEGER | Identificador único |
| fecha | TEXT | Cuándo se midió |
| tipo | TEXT | Tipo de métrica (ej: "wer") |
| clave | TEXT | Identificador específico (ej: "frase_1") |
| valor | REAL | El valor numérico medido |

---

### `backend/requirements.txt` — Las dependencias

**¿Qué es?** La lista de bibliotecas externas que necesita el proyecto para funcionar. Es como la lista de ingredientes de una receta.

| Biblioteca | Para qué se usa |
|------------|-----------------|
| `fastapi` | El framework web — define los endpoints y maneja las peticiones HTTP |
| `uvicorn` | El servidor web que ejecuta FastAPI |
| `gTTS` | Google Text-to-Speech — convierte texto a audio MP3 |
| `openai-whisper` | El modelo de reconocimiento de voz offline de OpenAI |
| `python-multipart` | Necesario para recibir archivos de audio en FastAPI |
| `SQLAlchemy` | ORM para bases de datos (usado en la primera versión) |
| `pydantic` | Validación de datos — FastAPI lo usa internamente |
| `requests` | Para hacer peticiones HTTP desde Python |

Para instalarlas todas: `pip install -r requirements.txt`

---

### `backend/evaluar_wer.py` — Script de evaluación WER

**¿Qué es?** Un script auxiliar (no forma parte de la app en producción) que sirve para correr la evaluación WER con hipótesis simuladas y ver los resultados en la consola. Se creó para obtener los números reales del README.

---

### `backend/indice_tfidf.json` — El índice persistido

**¿Qué es?** El índice TF-IDF guardado en disco. Cuando el servidor arranca, primero intenta cargar este archivo en vez de recalcular el índice desde cero. Si no existe, lo calcula y lo guarda.

**¿Por qué guardarlo?** Construir el índice es computacionalmente costoso. Guardarlo evita recalcularlo cada vez que se reinicia el servidor.

---

## PARTE 2 — El Frontend (lo que ve el usuario)

El frontend es la interfaz visual. Está hecho con **Next.js** (un framework de React) y **TypeScript**. El único archivo que importa entender es `page.tsx`.

---

### `frontend/app/page.tsx` — La interfaz completa

**¿Qué es?** Es el único archivo de interfaz. Contiene absolutamente todo lo que ve el usuario: las 5 pestañas, todos los componentes visuales, y la lógica de interacción.

**¿Por qué un solo archivo?** Para proyectos educativos es más fácil tener todo junto y poder leerlo de corrido.

#### Las 5 pestañas de la aplicación

---

**Pestaña 🩸 Consulta** — La función principal

Es donde el usuario hace su consulta. Contiene:

- **Campo de texto** — donde se escribe la situación médica. Tiene un botón ✕ para limpiar y se vacía automáticamente al enviar. Si se intenta enviar vacío, aparece un borde rojo y un mensaje de error.

- **Botón "Consultar"** — envía el texto al backend (POST /consulta) y muestra el resultado.

- **Botón "Consulta por voz" (Google ASR)** — usa la Web Speech API del navegador (disponible en Chrome/Edge). Graba la voz del usuario y la transcribe a texto en tiempo real usando los servidores de Google. Requiere internet.

- **Botón "Voz sin internet (Whisper)"** — graba el audio con el micrófono del dispositivo, lo envía al backend, y el backend usa el modelo Whisper tiny (instalado localmente, sin internet) para transcribirlo.

- **Toggle TTS** — activa o desactiva la síntesis de voz. Si está activo, cuando llega la respuesta se reproduce en audio (usando gTTS en el backend).

- **ResultadoCard** — muestra el veredicto con color e ícono:
  - ✅ Verde → apto
  - ⏳ Rojo → no apto temporal
  - 🚫 Violeta → no apto permanente
  - 🏥 Azul → consultar médico
  - ⚠️ Amarillo → fuera de dominio
  - ℹ️ Gris → información

- **Panel de detalles técnicos** — muestra todo el análisis:
  - Entidades detectadas (NER)
  - POS tagging de cada token
  - Perplejidad de la frase
  - Score IR
  - Documentos más relevantes del corpus
  - Tiempo de procesamiento

- **Historial** — tabla con las últimas 20 consultas de la sesión actual.

- **Acerca de** — panel desplegable con explicaciones simples de cada tecnología (Google ASR, Whisper, TTS, Perplejidad, TF-IDF, WER).

---

**Pestaña 📊 Dashboard** — Las estadísticas

Muestra métricas del sistema. Se carga haciendo clic en "Actualizar". Mientras carga, muestra un skeleton animado (tarjetas grises parpadeantes).

Contiene:
- **Tarjetas de resumen** — total de consultas, aptos, no aptos, WER promedio, perplejidad promedio, Score IR promedio, tiempo de respuesta promedio.
- **Gráfico de torta** — distribución de resultados (apto, no_apto_temporal, etc.) construido con SVG puro (sin librería externa).
- **Gráfico de línea** — consultas por día, también con SVG puro.
- **Métricas IR** — Precisión, Recall, F1 del motor de búsqueda.
- **Top 10 consultas frecuentes** — las frases más repetidas.
- **Nube de palabras** — los términos más frecuentes del corpus visualizados por tamaño según su frecuencia.
- **Últimas 10 consultas** — tabla con las consultas más recientes guardadas en la base de datos.
- **Exportar CSV** — descarga el historial como archivo Excel-compatible.

---

**Pestaña 🔢 N-gramas** — El modelo de lenguaje

Permite explorar el modelo de N-gramas interactivamente.

Contiene:
- **Calculadora de perplejidad** — escribís una frase y el sistema dice qué tan "esperable" es para el modelo. Muestra el número y si supera el umbral de 60 (fuera de dominio).
- **Probabilidad condicional** — escribís una palabra y el sistema muestra las palabras más probables que la siguen, con sus probabilidades.
- **Generador de texto** — escribís una palabra de inicio y el sistema genera una frase automáticamente usando el modelo de bigramas (muestreo ponderado por probabilidad).
- **Tabla de bigramas** — los 10 pares de palabras más frecuentes del corpus.
- **Tabla de trigramas** — los 10 tríos de palabras más frecuentes del corpus.
- **Control de k (suavizado)** — permite cambiar el parámetro k del suavizado Add-k y ver cómo afecta las probabilidades.

---

**Pestaña 🔍 IR** — Recuperación de información (TF-IDF)

Permite buscar en el corpus usando TF-IDF.

Contiene:
- **Buscador** — escribís una consulta y el sistema devuelve los documentos del corpus más relevantes, con su score de similitud y un snippet del texto.
- **Métricas P/R/F1** — muestra la evaluación del buscador sobre las 10 consultas etiquetadas. Tabla con precisión, recall y F1 por consulta, y el promedio global.

---

**Pestaña 🎙️ WER** — Evaluación del reconocimiento de voz

Permite evaluar qué tan bien el sistema de voz transcribe las frases de prueba.

Contiene:
- **Modo normal** — el usuario lee cada frase en voz alta, el ASR la transcribe, y se calcula el WER automáticamente.
- **Modo demo (checkbox)** — el usuario escribe manualmente la transcripción (útil para presentaciones sin micrófono o para simular errores).
- **Indicadores de color** por frase según el WER: 🟢 < 10%, 🟡 10-30%, 🔴 > 30%.
- **Resumen global** al finalizar: WER promedio, total de S/D/I.

---

#### Componentes reutilizables dentro de `page.tsx`

| Componente | Para qué sirve |
|------------|----------------|
| `useIsMobile()` | Hook que detecta si el ancho de pantalla es menor a 768px para adaptar el diseño |
| `InfoTag` | El botón `?` con tooltip flotante que explica términos técnicos |
| `PieChart` | Gráfico de torta dibujado con SVG sin librerías externas |
| `Card` | Contenedor blanco con sombra y bordes redondeados |
| `SectionTitle` | Título de sección con línea separadora |
| `StatCard` | Tarjeta de estadística con número grande y color |
| `ResultadoCard` | Muestra el veredicto con el color e ícono correspondiente |

---

### `frontend/app/layout.tsx` — El marco de la aplicación

**¿Qué es?** Define la estructura HTML base que envuelve a todas las páginas. Establece el título del browser, el favicon (🩸), el idioma y las fuentes.

---

### `frontend/app/globals.css` — Los estilos globales

**¿Qué es?** La hoja de estilos CSS que aplica a toda la aplicación. Contiene:
- Reset de márgenes y paddings
- Forzar modo claro (evita que el modo oscuro del sistema operativo afecte la app)
- Colores base del texto y fondo
- Animación `pulse` para el skeleton loader del Dashboard

---

## PARTE 3 — Archivos de documentación y configuración

---

### `README.md` — El README principal

Descripción breve del proyecto para quien llega al repositorio por primera vez.

---

### `README_TECNICO.md` — La documentación técnica completa

Documento extenso con todas las decisiones técnicas, fórmulas, tablas de resultados, ejemplos de uso de cada endpoint, y el diagrama de arquitectura. Orientado a quienes quieren entender el **cómo** de cada componente.

---

### `README_FUNCIONAL.md` — Este archivo

Explicación didáctica de **qué hace** cada archivo y componente, pensada para estudiantes. Si tenés que explicar el proyecto frente a un tribunal, este es el documento de referencia.

---

### `activar_aplicacion.md` — Cómo correr el proyecto

Instrucciones paso a paso para levantar el backend y el frontend.

---

## PARTE 4 — Conceptos clave para poder explicar el proyecto

### ¿Qué es un API REST?
Es una forma de comunicación entre programas. El frontend le "pregunta" al backend enviando una petición HTTP a una URL específica, y el backend responde con datos en formato JSON.

Ejemplo:
```
Frontend envía:  POST http://localhost:8000/consulta
                 {"texto": "tuve dengue hace dos meses"}

Backend responde: {"resultado": "apto", "respuesta": "Con 2 meses desde el dengue..."}
```

### ¿Qué es JSON?
Un formato de texto para representar datos estructurados. Es lo que viaja entre el frontend y el backend.
```json
{
  "resultado": "no_apto_temporal",
  "mensaje": "Después de dengue debés esperar 1 mes."
}
```

### ¿Qué es un framework?
Una colección de herramientas y convenciones que facilitan construir un tipo específico de software.
- **FastAPI** = framework para construir APIs en Python
- **Next.js** = framework para construir interfaces web en JavaScript/TypeScript

### ¿Qué es TypeScript?
JavaScript con tipos. Permite detectar errores antes de ejecutar el código. `page.tsx` está escrito en TypeScript.

### ¿Qué es React?
Una biblioteca de JavaScript para construir interfaces. Next.js está construido sobre React. Cada componente (`Card`, `PieChart`, `InfoTag`) es una función de React.

### ¿Qué es un hook en React?
Una función especial que empieza con `use` y agrega comportamiento a un componente.
- `useState` — guarda un valor y re-renderiza cuando cambia
- `useEffect` — ejecuta código cuando el componente monta/desmonta
- `useIsMobile` — hook propio que detecta el tamaño de la pantalla

---

## Diagrama de flujo de una consulta completa

```
Usuario escribe "tuve dengue hace 2 meses"
         │
         ▼
   [page.tsx] consultar()
   POST /consulta {"texto": "tuve dengue hace 2 meses"}
         │
         ▼
   [main.py] endpoint POST /consulta
         │
         ├──► [nlp.py] extraer_entidades()
         │    → TIPO: enfermedad (dengue)
         │    → TIEMPO: 2 meses
         │
         ├──► [rules.py] evaluar()
         │    → espera dengue = 1 mes
         │    → tiempo >= espera → resultado: "apto"
         │
         ├──► [ngrams.py] perplejidad()
         │    → 23.4 (dentro del dominio)
         │
         ├──► [search.py] buscar()
         │    → doc 8 ("El dengue requiere esperar 28 días...") score: 0.72
         │
         ├──► Guardar en donar.db (tabla consultas)
         │
         └──► Respuesta JSON completa al frontend
                   │
                   ▼
         [page.tsx] muestra ResultadoCard
         ✅ PODÉS DONAR
         "Con 2 meses desde el episodio de dengue,
          ya podrías donar."
```
