# DONAR-APP — Documentación Técnica Completa

Sistema inteligente de consultas para donación de sangre. El usuario describe su situación médica por texto o voz y el sistema determina si puede donar, mostrando el análisis completo del procesamiento lingüístico.

---

## Índice

1. [Corpus](#1-corpus)
2. [Vista Consulta — resultado completo](#2-vista-consulta--resultado-completo)
   - 2.1 El veredicto
   - 2.2 Síntesis de voz (TTS)
   - 2.3 Intención detectada
   - 2.4 Perplejidad
   - 2.5 Score IR (TF-IDF)
   - 2.6 Tiempo de respuesta
   - 2.7 Entidades detectadas (NER)
   - 2.8 POS Tagging
   - 2.9 Documentos relevantes (TF-IDF)
3. [Vista Dashboard](#3-vista-dashboard)
4. [Vista N-gramas](#4-vista-n-gramas)
5. [Vista IR — Motor de búsqueda](#5-vista-ir--motor-de-búsqueda)
6. [Vista WER](#6-vista-wer)
7. [Reconocimiento de voz (ASR)](#7-reconocimiento-de-voz-asr)
8. [Base de datos](#8-base-de-datos)
9. [Endpoints del backend](#9-endpoints-del-backend)
10. [Cómo correr la aplicación](#10-cómo-correr-la-aplicación)

---

## 1. Corpus

### ¿Qué es un corpus?

Un corpus es una colección de textos del dominio específico que alimenta todos los módulos del sistema. En lenguaje natural, el "dominio" es el tema sobre el que trabaja el sistema — en este caso, los criterios médicos para donar sangre.

El corpus cumple dos roles:

**Corpus de documentos** (para el motor de búsqueda TF-IDF): todos los textos del archivo `corpus.json`. Cuando el usuario hace una consulta, el sistema busca los documentos más similares y los usa como referencia.

**Corpus de entrenamiento** (para el modelo de N-gramas): los mismos documentos más 11 frases coloquiales que simulan cómo escribiría un usuario real. Permite que el modelo aprenda las probabilidades de transición entre palabras en el contexto de donación de sangre.

### Estructura del corpus — `backend/corpus.json`

El corpus se carga desde `corpus.json` al iniciar el servidor. Está organizado en 14 secciones temáticas que se aplanan en una lista única para TF-IDF y N-gramas:

| Sección | Docs | Contenido |
|---------|------|-----------|
| `originales` | 23 | Documentos base: tatuajes, enfermedades, medicamentos, requisitos generales |
| `requisitos` | 10 | Requisitos físicos para donar: peso, temperatura, hemoglobina, tensión, pulso |
| `frecuencia` | 6 | Intervalos entre donaciones: hombres, mujeres, jóvenes, aféresis |
| `antes_de_donar` | 5 | Instrucciones previas: no ayunas, hidratarse, vestimenta cómoda |
| `durante_la_donacion` | 5 | Instrucciones durante: posición, no mover el brazo, avisar molestias |
| `despues_de_donar` | 8 | Cuidados post-donación: refrigerio, apósito, evitar ejercicio |
| `medicamentos_diferimiento_permanente` | 10 | Medicamentos que inhabilitan de forma permanente |
| `medicamentos_diferimiento_transitorio` | 9 | Medicamentos con período de espera (1 mes a 3 años) |
| `medicamentos_sin_diferimiento` | 9 | Medicamentos que no requieren espera |
| `vacunas_diferir_1_mes` | 7 | Vacunas de virus vivo que requieren 1 mes de espera |
| `vacunas_sin_diferimiento` | 10 | Vacunas sin diferimiento (con excepciones por exposición) |
| `conductas_de_riesgo` | 5 | Conductas sexuales y uso de drogas que generan diferimiento |
| `componentes_de_la_sangre` | 9 | Glóbulos, plasma, plaquetas — qué son y para qué se usan |
| `glosario` | 14 | Términos técnicos: donante habitual, período ventana, NAT, HEMO 3 |
| **Total** | **~130** | |

El corpus se puede ampliar editando `corpus.json` sin modificar ningún archivo Python. Al reiniciar el servidor se recarga automáticamente y se reconstruye el índice TF-IDF.

---

## 2. Vista Consulta — resultado completo

Esta es la vista principal. Ejemplo de consulta: *"tuve dengue hace dos meses, ¿puedo donar sangre?"*

```
✅ PODÉS DONAR
Con 2 meses desde el episodio de dengue, ya podrías donar.
Te recomendamos confirmarlo en el centro de donación.

🔊
▼ Ver análisis técnico
  Intención          Perplejidad     Score IR        Tiempo
  querer_donar          32.72          0.3465        0.58 ms

  Entidades NER detectadas:
    TIPO: enfermedad    TIEMPO: 2 meses

  POS tagging:
    tuve(VERB)  dengue(OTHER)  hace(STOP)  dos(OTHER)  meses(NOUN)
    puedo(VERB)  donar(VERB)  sangre(NOUN)

  Documentos relevantes (TF-IDF):
    [0.347] ...El dengue requiere esperar 28 días después de recuperarte para donar...
    [0.218] ...Las mujeres pueden donar sangre cada 4 meses como mínimo...
    [0.202] ...Se puede donar sangre cada 3 meses en el caso de los hombres...
```

---

### 2.1 El veredicto

El primer bloque visible es el resultado para el usuario, sin tecnicismos. El módulo `rules.py` determina el tipo de respuesta a partir de las entidades detectadas por el NLP:

| Ícono | Etiqueta | Significado | Color |
|-------|----------|-------------|-------|
| ✅ | PODÉS DONAR | La persona cumple los requisitos para donar | Verde |
| ⏳ | AÚN NO PODÉS DONAR | Restricción temporal (tatuaje, dengue, antibióticos, etc.) | Rojo |
| 🚫 | NO PODÉS DONAR (PERMANENTE) | Condición que inhabilita de forma definitiva | Violeta |
| 🏥 | CONSULTÁ CON UN MÉDICO | El sistema no puede determinar, requiere evaluación | Azul |
| ⚠️ | FUERA DEL DOMINIO | La consulta no es sobre donación de sangre | Amarillo |
| ℹ️ | INFORMACIÓN | El sistema ofrece información general sin veredicto | Gris |

**Lógica completa de `rules.py`:**

El módulo recibe el texto de la consulta, llama al NLPProcessor para extraer entidades, y aplica las siguientes reglas en orden:

| Condición detectada | Tiempo transcurrido | Resultado |
|--------------------|---------------------|-----------|
| Enfermedad: dengue | ≥ 28 días (1 mes) | `apto` |
| Enfermedad: dengue | < 28 días | `no_apto_temporal` |
| Enfermedad: COVID | ≥ 14 días (0.5 meses) | `apto` |
| Enfermedad: COVID | < 14 días | `no_apto_temporal` |
| Enfermedad: gripe / fiebre / infección | ≥ 7 días (0.25 meses) | `apto` |
| Enfermedad: gripe / fiebre / infección | < 7 días | `no_apto_temporal` |
| Enfermedad: hepatitis | — | `no_apto_permanente` |
| Enfermedad: VIH / SIDA | — | `no_apto_permanente` |
| Enfermedad: diabetes | — | `no_apto_permanente` |
| Enfermedad: cáncer | — | `no_apto_permanente` |
| Enfermedad: hipertensión / anemia | — | `consultar` |
| Medicamento (antibióticos, etc.) | — | `no_apto_temporal` (7 días) |
| Tatuaje o piercing | ≥ 6 meses | `apto` |
| Tatuaje o piercing | < 6 meses | `no_apto_temporal` |
| Cirugía / operación | — | `no_apto_temporal` (variable) |
| Vacuna de virus vivo (fiebre amarilla, varicela, etc.) | — | `no_apto_temporal` (4 semanas) |
| Vacuna común (gripe, COVID, etc.) | ≥ 14 días | `apto` |
| Vacuna común | < 14 días | `no_apto_temporal` |
| Embarazo | — | `no_apto_temporal` |
| Lactancia | — | `no_apto_temporal` (6 meses post-parto) |
| Viaje a zona de malaria | — | `no_apto_temporal` (12 meses) |
| Consulta sobre requisitos | Sin entidad específica | `info` con lista de requisitos |
| Consulta sobre frecuencia | — | `info` (hombres c/3 meses, mujeres c/4 meses) |
| Sin entidad reconocida | — | `info` con temas disponibles |

Adicionalmente, si la **perplejidad supera el umbral de 60**, el sistema marca la consulta como `fuera_de_dominio` y sobreescribe el mensaje de `info` con una advertencia.

---

### 2.2 Síntesis de voz — botón 🔊

Al hacer clic en 🔊, el frontend llama al endpoint:

```
GET /tts?texto=Con 2 meses desde el episodio de dengue, ya podrías donar.
```

El backend usa **gTTS** (Google Text-to-Speech) para convertir el texto a audio MP3 en español argentino (`lang="es"`, `tld="com.ar"`). El audio se devuelve como stream de bytes y el navegador lo reproduce automáticamente.

El checkbox "🔊 Voz" activa o desactiva la reproducción automática después de cada consulta.

---

### 2.3 Intención detectada

**¿Qué es la detección de intención?**

La intención es el propósito detrás del texto del usuario. En vez de analizar palabra por palabra, se clasifica la consulta en una categoría de alto nivel.

**¿Cómo se detecta?**

El módulo `nlp.py` busca frases clave en el texto:

| Intención | Frases que la activan |
|-----------|----------------------|
| `querer_donar` | "puedo donar", "quiero donar", "soy apto", "puedo ser donante" |
| `consulta_tiempo` | "cuánto tiempo", "cuándo puedo", "cuánto falta" |
| `informacion` | "qué necesito", "requisitos", "condiciones", "qué piden" |
| `consulta_general` | Cualquier otra consulta |

---

### 2.4 Perplejidad

**¿Qué es la perplejidad?**

La perplejidad es una métrica del modelo de N-gramas que mide qué tan "esperada" o "coherente" es una frase dentro del dominio del corpus.

- **Perplejidad baja** (≤ 60): la frase es reconocida como consulta típica del dominio de donación de sangre.
- **Perplejidad alta** (> 60): la frase contiene palabras o combinaciones inesperadas. El sistema la marca como `fuera_de_dominio`.

**Fórmula:**

```
PP = exp( -1/N × Σ log P(wᵢ | wᵢ₋₁) )

Donde:
  N  = cantidad de palabras en el texto
  wᵢ = palabra en posición i
  P(wᵢ | wᵢ₋₁) = probabilidad del bigrama (calculada con Add-k)
```

**Umbral de detección de anomalías: PP_UMBRAL = 60**

Ejemplos observados:
- "tuve dengue hace dos meses" → PP ≈ 32 (dentro del dominio)
- "hola cómo estás" → PP ≈ 71 (fuera del dominio)

**Suavizado Add-k:**

```
P(palabra | anterior) = (conteo(anterior, palabra) + k) / (conteo(anterior) + k × |vocabulario|)
```

Con `k=1` (Laplace), todas las combinaciones no vistas reciben probabilidad pequeña pero no nula.

---

### 2.5 Score IR (TF-IDF)

**¿Qué es el Score IR?**

Es la similitud coseno entre la consulta del usuario y el documento más relevante del corpus. Va de 0 a 1.

**¿Cómo se calcula?**

**TF (Term Frequency):**
```
TF(término, doc) = veces que aparece el término / total de palabras del doc
```

**IDF (Inverse Document Frequency):**
```
IDF(término) = log( (N + 1) / (df(término) + 1) ) + 1

Donde N = total documentos, df = en cuántos documentos aparece el término
```

**Similitud del Coseno:**
```
similitud(consulta, doc) = (consulta · doc) / (|consulta| × |doc|)
```

El índice TF-IDF se construye una sola vez al iniciar el servidor y se persiste en `indice_tfidf.json` para no recalcularlo en cada arranque.

---

### 2.6 Tiempo de respuesta

Milisegundos que tardó el servidor en procesar la consulta completa: recibir texto → NLP → N-gramas → TF-IDF → reglas → guardar en DB → armar respuesta.

Tiempos típicos observados: **0.5 ms – 20 ms**, lo que confirma que todos los módulos son eficientes para este tamaño de corpus.

---

### 2.7 Entidades detectadas (NER)

**¿Qué es el NER?**

Named Entity Recognition — identifica y clasifica fragmentos de texto que representan conceptos con significado específico.

**¿Cómo funciona en la aplicación?**

El módulo `nlp.py` usa diccionarios de palabras clave por categoría y expresiones regulares para detectar tiempos.

**Entidades de TIPO** (qué condición menciona el usuario):

| Tipo | Palabras clave que lo activan |
|------|-------------------------------|
| `tatuaje` | tatuaje, tattoo, tatuarme |
| `medicamento` | antibiótico, penicilina, amoxicilina, ibuprofeno, pastilla, medicamento |
| `cirugia` | cirugía, operación, operar, operé, intervención |
| `enfermedad` | gripe, fiebre, dengue, covid, hepatitis, VIH, SIDA, diabetes, anemia, hipertensión, cáncer, infección |
| `piercing` | piercing, arito, pendiente |
| `embarazo` | embarazo, embarazada, lactancia, amamantando, parto, cesárea |
| `viaje` | viaje, viajé, malaria, paludismo, africa, tropical |

**Entidades de TIEMPO** (cuánto tiempo pasó):

Se detectan en múltiples formatos y se convierten a meses:

| Formato | Ejemplo | Resultado |
|---------|---------|-----------|
| Número + meses | "2 meses" | 2 meses |
| Texto + meses | "dos meses" | 2 meses |
| Número + años | "1 año" | 12 meses |
| Texto + años | "un año" | 12 meses |
| Semanas | "3 semanas" | 0.75 meses |
| Días | "28 días" | 0.93 meses |

---

### 2.8 POS Tagging

**¿Qué es el POS Tagging?**

Part-of-Speech Tagging — asigna a cada palabra su categoría gramatical. Es implementado con reglas y diccionarios en `nlp.py` (sin librerías externas como spaCy).

| Categoría | Código | Ejemplos en el dominio |
|-----------|--------|------------------------|
| Sustantivo | `NOUN` | tatuaje, sangre, mes, año, donante, cirugía |
| Verbo | `VERB` | hice, tuve, tomé, operé, puedo, quiero, donar |
| Adjetivo | `ADJ` | apto, sano, enfermo, reciente |
| Número | `NUM` | 1, 2, 15, 28 |
| Stopword | `STOP` | me, un, el, la, de, hace, desde |
| Otro | `OTHER` | palabras no clasificadas |

---

### 2.9 Documentos relevantes (TF-IDF)

Los 3 documentos del corpus más similares a la consulta, ordenados por similitud coseno, con un snippet contextual centrado en las palabras de la consulta.

---

## 3. Vista Dashboard

El Dashboard muestra métricas globales acumuladas de todas las consultas registradas en la base de datos. Se actualiza haciendo clic en **🔄 Actualizar**. Los datos también se pueden exportar con **⬇️ Exportar CSV**.

### Tarjetas de métricas globales

| Tarjeta | Descripción | Fuente (SQL) |
|---------|-------------|--------------|
| Total consultas | Cantidad total de consultas procesadas | `COUNT(*) FROM consultas` |
| Aptos | Consultas con resultado `apto` | `WHERE resultado='apto'` |
| No aptos | Consultas con resultado `no_apto_temporal` | `WHERE resultado='no_apto_temporal'` |
| PP promedio | Promedio de perplejidad de todas las consultas | `AVG(perplejidad)` |
| Score IR promedio | Promedio de similitud coseno del mejor doc encontrado | `AVG(score_ir)` |
| Tiempo promedio | Latencia promedio del endpoint /consulta en ms | `AVG(tiempo_respuesta_ms)` |
| WER promedio | WER promedio de las frases evaluadas (si se hizo evaluación) | Tabla `metricas` |

### Métricas del motor IR

Muestra Precisión, Recall y F1 promedio calculados sobre las 10 consultas de evaluación preconfiguradas. Ver sección 5 para la explicación completa.

### Gráfico de líneas — Consultas por día

Evolución temporal de las consultas agrupadas por día. Construido con SVG puro sin librerías externas.

```sql
SELECT substr(fecha, 1, 10) as dia, COUNT(*) as total
FROM consultas GROUP BY dia ORDER BY dia
```

### Gráfico de torta — Distribución por resultado

Muestra la proporción de cada tipo de veredicto (`apto`, `no_apto_temporal`, `no_apto_permanente`, `consultar`, `fuera_de_dominio`, `info`). Construido con SVG calculando ángulos proporcionales al valor de cada segmento.

```sql
SELECT resultado, COUNT(*) as total
FROM consultas GROUP BY resultado
```

**¿Para qué sirve?** Si la mayoría son `info`, indica que las consultas son vagas y el sistema no puede clasificarlas bien. Si la mayoría son `no_apto_temporal`, el sistema está detectando muchas restricciones temporales.

### Top 10 consultas frecuentes

```sql
SELECT texto, COUNT(*) as total
FROM consultas GROUP BY texto ORDER BY total DESC LIMIT 10
```

### Nube de palabras del corpus

Términos más frecuentes del corpus de documentos, con tamaño proporcional a la frecuencia. Las stopwords están filtradas. Construida con CSS puro (font-size proporcional, colores rotativos).

### Exportar CSV

Descarga el historial completo en formato CSV con columnas: id, texto, resultado, intención, perplejidad, score_ir, tiempo_respuesta_ms, origen, fecha. Incluye BOM UTF-8 para compatibilidad con Excel.

### Tabla de últimas 10 consultas

| Columna | Descripción |
|---------|-------------|
| # | ID único en la DB |
| Texto | Primeros 35 caracteres de la consulta |
| Resultado | Veredicto con color (verde/rojo/gris) |
| PP | Perplejidad calculada |
| IR | Score de similitud coseno |
| ms | Tiempo de respuesta |
| Origen | "texto", "voz" o "whisper" |

---

## 4. Vista N-gramas

### ¿Qué son los N-gramas?

Un modelo de N-gramas es un modelo de lenguaje estadístico que estima la probabilidad de que aparezca una palabra dado el contexto de las N-1 palabras anteriores.

- **Bigrama (N=2):** P(palabra | palabra anterior). Dado "tatuaje", ¿cuál es la palabra más probable?
- **Trigrama (N=3):** P(palabra | dos palabras anteriores). Dado "hice un", ¿qué palabra sigue?

### Parámetro k — Suavizado Add-k (Laplace generalizado)

**¿Por qué hace falta suavizado?**

Si una combinación de palabras no aparece en el corpus, su probabilidad es 0. Esto rompe el cálculo de perplejidad (`log(0) = -∞`).

**Fórmula Add-k:**

```
P(palabra | anterior) = (conteo(anterior, palabra) + k) / (conteo(anterior) + k × |vocabulario|)
```

| Valor de k | Efecto |
|------------|--------|
| k = 0.01 | Suavizado muy leve. Fiel al corpus, pero frágil con palabras no vistas. |
| k = 1 | Suavizado de Laplace. Estándar académico. |
| k = 10 | Suavizado agresivo. Todas las palabras con probabilidades más similares. |

El usuario puede cambiar k con el selector y recalcular en tiempo real.

### Calculadora de Perplejidad

Permite ingresar cualquier frase y ver su perplejidad respecto al modelo entrenado. El resultado muestra si la frase está dentro o fuera del dominio (umbral: 60).

**Ejemplos típicos:**
- "tuve dengue hace un mes" → PP ≈ 20-35 (dentro del dominio)
- "hola cómo estás" → PP ≈ 60-80 (fuera del dominio)

### Probabilidad condicional P(w | contexto)

Dado una palabra de contexto, muestra las palabras más probables que la siguen según el modelo de bigramas. Los resultados incluyen la probabilidad porcentual y el conteo de co-ocurrencias en el corpus.

**Ejemplo:** dado "tatuaje" → las palabras más probables pueden ser: "reciente", "debes", "requieren", etc.

### Generación de texto con N-gramas

A partir de una frase inicial, el modelo completa la frase seleccionando en cada paso la siguiente palabra mediante muestreo ponderado por las probabilidades de bigramas. Es una demostración del modelo de lenguaje estadístico: genera texto coherente con el dominio de donación de sangre.

**Ejemplo:** inicio "me hice un" → genera "tatuaje reciente debes esperar seis meses para donar"

### Tabla de Top-10 Bigramas

| Columna | Significado |
|---------|-------------|
| Contexto | Primera palabra del bigrama |
| Siguiente | Segunda palabra (la predicha) |
| P(w\|ctx) | Probabilidad condicional con Add-k |
| n | Conteo de co-ocurrencias en el corpus |

**Ejemplo de lectura:** Contexto="tatuaje" → Siguiente="reciente" con prob=0.214 significa que en el corpus, después de "tatuaje" aparece "reciente" el 21.4% de las veces.

### Tabla de Top-10 Trigramas

Igual que bigramas pero con contexto de dos palabras. Los trigramas capturan dependencias de mayor alcance y suelen ser más precisos, pero necesitan más datos de entrenamiento para ser confiables.

---

## 5. Vista IR — Motor de búsqueda

### ¿Qué es la Recuperación de Información?

La RI (IR en inglés) es el proceso de encontrar los documentos más relevantes en una colección dado una consulta en lenguaje natural. El modelo implementado es el **modelo vectorial** con pesos TF-IDF y similitud del coseno.

El índice TF-IDF se construye al iniciar el servidor y se persiste en `indice_tfidf.json`. Si el archivo existe, se carga directamente sin recalcular.

### Búsqueda en el corpus

Permite buscar libremente entre los 20 documentos. Los resultados se muestran ordenados de mayor a menor similitud coseno, con el score y un snippet del documento centrado en los términos de la consulta.

### Evaluación — Precisión, Recall y F1

Métricas estándar para evaluar motores de búsqueda, calculadas sobre 10 consultas etiquetadas manualmente.

**Precisión (P):** de los documentos recuperados, ¿cuántos son realmente relevantes?

```
P = Documentos relevantes recuperados / Total documentos recuperados
```

**Recall (R):** de todos los documentos relevantes, ¿cuántos encontró el sistema?

```
R = Documentos relevantes recuperados / Total documentos relevantes existentes
```

**F1:** media armónica entre P y R. Penaliza si alguna de las dos es muy baja.

```
F1 = 2 × (P × R) / (P + R)
```

### Las 10 consultas de evaluación

| Consulta | Documentos relevantes (índices) |
|----------|---------------------------------|
| tatuaje donar sangre meses esperar | 0, 1 |
| antibiótico penicilina esperar donación | 3, 4 |
| cirugía operación esperar donar | 5, 6 |
| hepatitis HIV SIDA donación permanente | 7, 17 |
| dengue covid fiebre esperar donar | 8, 9, 16 |
| piercing esperar donación | 10 |
| diabetes hipertensión donación | 11, 12 |
| edad peso requisitos donar | 13, 14 |
| frecuencia donar hombres mujeres | 18, 19 |
| ayunas fiebre condiciones donar | 14, 16 |

El umbral de score para considerar un documento como "recuperado" es 0.05 (similitud coseno mínima).

---

## 6. Vista WER

### ¿Qué es el WER?

El WER (Word Error Rate) es la métrica estándar para evaluar la calidad de un sistema de reconocimiento de voz. Mide el porcentaje de palabras que el ASR transcribió incorrectamente.

**Fórmula:**

```
WER = (S + D + I) / N

Donde:
  S = Sustituciones: palabras incorrectas (ej: "hice" → "ice")
  D = Eliminaciones: palabras que el ASR omitió
  I = Inserciones: palabras de más que el ASR agregó
  N = Total de palabras en la referencia (texto correcto)
```

**Ejemplo concreto:**

```
Referencia: "me hice un tatuaje hace dos meses"   (N = 7)
Hipótesis:  "me ice un tatuaje hace do meses"

  me    → me    ✓
  hice  → ice   ✗ Sustitución (S=1)
  un    → un    ✓
  tatuaje → tatuaje ✓
  hace  → hace  ✓
  dos   → do    ✗ Sustitución (S=2)
  meses → meses ✓

WER = (2 + 0 + 0) / 7 = 0.286 = 28.6%
```

**¿Cómo se calcula internamente?**

Con el algoritmo de **distancia de edición de Levenshtein** aplicado a nivel de palabras (no de caracteres). Se construye una matriz de programación dinámica donde cada celda representa el mínimo de operaciones para transformar la secuencia de referencia en la hipótesis.

**¿Qué es un WER aceptable?**

| WER | Interpretación |
|-----|----------------|
| 0 – 10% | Excelente |
| 10 – 20% | Bueno |
| 20 – 30% | Aceptable |
| 30 – 50% | Deficiente |
| 50%+ | Muy deficiente |

Los sistemas comerciales (Google, Azure) tienen WER 5-10% en condiciones normales. Con ruido o vocabulario médico, puede subir al 20-30%.

### Las 12 frases de prueba — resultados experimentales

Evaluación realizada con hipótesis simuladas que reproducen los errores típicos documentados de cada sistema en español rioplatense (pérdida de tildes, números transcritos como dígitos, confusión en palabras largas).

| # | Frase de referencia | N | Google ASR | Whisper tiny | Error principal |
|---|---------------------|---|-----------|--------------|-----------------|
| 1 | me hice un tatuaje hace dos meses | 7 | 0.0% | 14.3% | W: "dos"→"2" (D=1) |
| 2 | quiero donar sangre puedo hacerlo | 5 | 0.0% | 0.0% | — |
| 3 | tomé antibióticos la semana pasada | 5 | 20.0% | 40.0% | G: tilde "tomé" (S=1); W: +tilde "antibióticos" (S=2) |
| 4 | tuve una cirugía hace tres meses | 6 | 0.0% | 16.7% | W: tilde "cirugía" (S=1) |
| 5 | me hice un piercing hace un mes | 7 | 0.0% | 0.0% | — |
| 6 | tengo diabetes puedo donar sangre | 5 | 0.0% | 0.0% | — |
| 7 | tuve dengue hace veinte días | 5 | 0.0% | 20.0% | W: "veinte"→"20" (D=1) |
| 8 | cuánto tiempo debo esperar para donar | 6 | 16.7% | 16.7% | G/W: tilde "cuánto" (S=1) |
| 9 | me operé hace seis meses ya puedo donar | 8 | 12.5% | 25.0% | G: tilde "operé" (S=1); W: +seis→"6" (S+D=2) |
| 10 | tengo fiebre desde ayer puedo donar | 6 | 0.0% | 0.0% | — |
| 11 | me vacuné contra el covid hace dos semanas | 8 | 12.5% | 25.0% | G: tilde "vacuné" (S=1); W: +dos→"2" (S+D=2) |
| 12 | nunca me hice un tatuaje puedo donar | 7 | 0.0% | 0.0% | — |
| **Promedio** | | | **5.1%** | **13.1%** | |

**Observaciones:**
- Google ASR comete errores casi exclusivamente por pérdida de tildes en verbos conjugados ("tomé", "cuánto", "operé", "vacuné") — 4 de las 12 frases.
- Whisper tiny acumula esos mismos errores más la transcripción de números escritos ("dos"→"2", "veinte"→"20", "seis"→"6") — 7 de las 12 frases.
- Las 5 frases con vocabulario no acentuado ni numérico obtienen WER=0% en ambos sistemas.
- El WER de 5.1% (Google) es consistente con resultados reportados en literatura para ASR comercial en español en condiciones controladas (sin ruido, hablante nativo, vocabulario familiar).
- El WER de 13.1% (Whisper tiny) es esperable dado que el modelo `tiny` (39M parámetros) prioriza velocidad sobre precisión y no aplica post-procesamiento de tildes.

**Impacto en el sistema:** los errores de tilde no afectan la detección de entidades porque `nlp.py` busca tanto la forma acentuada como la no acentuada de cada keyword (ej. "cirugía" y "cirugia"). Los errores de número (2 vs "dos") tampoco afectan porque `extraer_entidades` captura ambos formatos con regex separados.

### Cómo usar la evaluación WER

**Modo normal (con micrófono):**
1. Clic en **Comenzar evaluación**
2. Leer la frase en voz alta
3. Clic en **🎤 Hablar ahora** — Google ASR transcribe
4. Clic en **Evaluar → siguiente frase**
5. Los círculos de navegación cambian de color: 🟢 WER < 10%, 🟡 10-30%, 🔴 > 30%
6. Al finalizar, clic en **Ver resumen global** para ver el WER promedio

**Modo demo (sin micrófono):**
1. Activar el checkbox **📝 Modo demo (escribir)**
2. Escribir manualmente la transcripción en el campo de texto
3. Evaluar normalmente — útil para presentaciones sin micrófono o para simular distintos escenarios de error

### Limitaciones del ASR

| Factor | Impacto en WER | Ejemplo en este dominio |
|--------|----------------|-------------------------|
| Ruido de fondo | Alto — +15-30% | Voces u otros sonidos al consultar |
| Acento regional | Medio — +5-15% | Pronunciación argentina de "cirugía", "antibiótico" |
| Vocabulario médico | Alto | "Amoxicilina", "hepatitis", "dengue" suelen transcribirse mal |
| Tildes y acentos | Bajo-Medio | "Tomé" → "tome", "cirugía" → "cirugia" |
| Velocidad de habla | Medio | Frases largas (#9 y #11) más propensas a errores |
| Calidad del micrófono | Alto | Micrófonos integrados vs externos |
| Whisper tiny vs Google | Whisper tiny tiene mayor WER | Modelo pequeño con menor vocabulario médico especializado |

---

## 7. Reconocimiento de voz (ASR)

La aplicación implementa dos motores de ASR accesibles desde la vista Consulta:

### 🎤 Consulta por voz — Google ASR

Usa la **Web Speech API**, una API nativa del navegador que envía el audio a los servidores de Google para transcribirlo en tiempo real.

- Requiere conexión a internet
- Compatible con Chrome y Edge (no Firefox)
- Configurado para español argentino (`lang="es-AR"`)
- El resultado llega como texto y se envía directamente a `/consulta` con `origen="voz"`

**Flujo:**
1. Usuario hace clic → navegador activa el micrófono
2. Google ASR transcribe en tiempo real (streaming)
3. Al silencio, devuelve el texto → se envía al backend automáticamente

### 🟣 Voz sin internet — Whisper offline

Whisper es un modelo de reconocimiento de voz open-source de OpenAI que corre **localmente** en el servidor, sin enviar datos a internet.

**Flujo:**
1. Usuario hace clic → navegador graba con `MediaRecorder` en formato WebM
2. Al clic en "Detener", el audio se sube al endpoint `/whisper`
3. El servidor guarda el audio en un archivo temporal
4. El modelo Whisper transcribe el audio
5. El archivo temporal se elimina
6. El texto transcripto se devuelve al frontend y se envía a `/consulta` con `origen="whisper"`

**Modelos disponibles:**

| Modelo | Tamaño | Velocidad | Precisión |
|--------|--------|-----------|-----------|
| tiny | 72 MB | Muy rápido | Básica |
| base | 142 MB | Rápido | Buena |
| small | 461 MB | Moderado | Muy buena |
| medium | 1.5 GB | Lento | Excelente |

La aplicación usa `tiny` para priorizar la velocidad. Se puede cambiar modificando el modelo en el endpoint `/whisper` de `main.py`.

---

## 8. Base de datos

La aplicación usa **SQLite** — motor de base de datos relacional que guarda todo en un único archivo (`donar.db`). No requiere servidor separado.

### Tabla `corpus`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER | Clave primaria autoincremental |
| texto | TEXT UNIQUE | Contenido del documento |
| fecha_carga | TEXT | Timestamp de inserción |

### Tabla `consultas`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER | Clave primaria |
| texto | TEXT | Consulta original del usuario |
| texto_transcripto | TEXT | Transcripción ASR (si fue por voz) |
| resultado | TEXT | apto / no_apto_temporal / no_apto_permanente / consultar / fuera_de_dominio / info |
| motivo | TEXT | Mensaje de respuesta al usuario |
| intencion | TEXT | Intención detectada por NLP |
| entidades | TEXT | Lista de entidades extraídas (serializada como texto) |
| fecha | TEXT | Timestamp ISO 8601 |
| perplejidad | REAL | Perplejidad calculada con N-gramas |
| score_ir | REAL | Similitud coseno con el documento más relevante |
| tiempo_respuesta_ms | REAL | Latencia del endpoint en milisegundos |
| origen | TEXT | "texto", "voz" o "whisper" |

> La tabla `consultas` soporta migración no destructiva: si la DB fue creada con una versión anterior del sistema (sin columnas nuevas), el servidor las agrega automáticamente con `ALTER TABLE` al iniciar.

### Tabla `metricas`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER | Clave primaria |
| fecha | TEXT | Timestamp del registro |
| tipo | TEXT | Tipo de métrica (ej: "wer") |
| clave | TEXT | Identificador (ej: "frase_0") |
| valor | REAL | Valor numérico |

---

## 9. Endpoints del backend

| Método | Endpoint | Parámetros | Descripción |
|--------|----------|------------|-------------|
| POST | `/consulta` | body: `{texto, origen}` | Procesa una consulta: NLP + N-gramas + TF-IDF + reglas + DB |
| GET | `/tts` | `texto=...` | Genera audio MP3 con gTTS |
| POST | `/whisper` | form: `audio` (archivo) | Transcribe audio con Whisper offline |
| GET | `/wer/frases` | — | Devuelve las 12 frases de prueba |
| POST | `/wer/evaluar` | body: `{referencia, hipotesis, frase_id}` | Calcula WER entre referencia e hipótesis |
| GET | `/wer/resumen` | — | WER promedio de frases evaluadas |
| GET | `/ngramas/tabla_bigramas` | `top_n=10`, `k=1.0` | Top N bigramas por probabilidad |
| GET | `/ngramas/tabla_trigramas` | `top_n=10`, `k=1.0` | Top N trigramas por probabilidad |
| GET | `/ngramas/perplejidad` | `texto=...`, `k=1.0` | Perplejidad de una frase y si supera el umbral |
| GET | `/ngramas/siguiente` | `palabra=...`, `top_n=6`, `k=1.0` | Palabras más probables que siguen a una palabra dada |
| GET | `/ngramas/generar` | `inicio=...`, `max_palabras=12`, `k=1.0` | Genera texto a partir de una frase inicial |
| GET | `/buscar` | `q=...`, `top_k=5` | Búsqueda TF-IDF en el corpus |
| GET | `/ir/metricas` | — | P/R/F1 sobre 10 consultas de evaluación |
| GET | `/stats` | — | Métricas básicas: total, aptos, no_aptos, PP, IR, tiempo promedio |
| GET | `/stats/completo` | — | Métricas globales + IR + WER combinadas (para el Dashboard) |
| GET | `/stats_diario` | — | Consultas agrupadas por día |
| GET | `/stats_tipos` | — | Distribución por tipo de resultado |
| GET | `/stats_top_consultas` | — | Top 10 consultas más frecuentes |
| GET | `/historial` | `limit=10` | Últimas N consultas con todos sus campos |
| GET | `/corpus` | — | Lista de documentos del corpus |
| GET | `/palabras_frecuentes` | `top_n=30` | Términos más frecuentes del corpus (para nube de palabras) |

---

## 10. Cómo correr la aplicación

### Instalación (primera vez)

```bash
# Backend
cd C:\DONARVERSION1\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd C:\DONARVERSION1\frontend
npm install
```

### Ejecución (cada vez)

Ver [activar_aplicacion.md](activar_aplicacion.md) para las instrucciones paso a paso.

Resumen rápido — abrir **dos terminales de PowerShell**:

```powershell
# Terminal 1 — Backend
cd C:\DONARVERSION1\backend
venv\Scripts\activate
python -m uvicorn main:app --reload
# Esperar: "Application startup complete."
```

```powershell
# Terminal 2 — Frontend
cd C:\DONARVERSION1\frontend
npm run dev
# Esperar: "Ready on http://localhost:3000"
```

Abrir en el navegador (Chrome o Edge recomendado): **http://localhost:3000**

### Dependencias del backend (`requirements.txt`)

| Librería | Versión | Uso |
|----------|---------|-----|
| fastapi | 0.136.0 | Framework web para la API REST |
| uvicorn | 0.44.0 | Servidor ASGI para correr FastAPI |
| gTTS | 2.5.4 | Text-to-Speech (síntesis de voz) |
| openai-whisper | latest | Reconocimiento de voz offline |
| python-multipart | latest | Recepción de archivos de audio |
| pydantic | 2.13.2 | Validación de datos en FastAPI |
| requests | 2.33.1 | Cliente HTTP |

### Arquitectura del proyecto

```
DONARVERSION1/
├── backend/
│   ├── main.py               ← API FastAPI, carga corpus, endpoints, DB
│   ├── nlp.py                ← NER, POS tagging, tokenización, intenciones
│   ├── ngrams.py             ← Modelo bigrama/trigrama, Add-k, perplejidad
│   ├── search.py             ← Motor TF-IDF, similitud coseno, P/R/F1
│   ├── rules.py              ← Reglas de elegibilidad (basadas en entidades NLP)
│   ├── wer.py                ← Cálculo WER con Levenshtein, 12 frases de prueba
│   ├── evaluar_wer.py        ← Script auxiliar para evaluar WER con hipótesis simuladas
│   ├── corpus.json           ← Corpus (~130 docs, 14 secciones temáticas)
│   ├── indice_tfidf.json     ← Índice TF-IDF persistido (generado automáticamente)
│   ├── donar.db              ← Base de datos SQLite
│   ├── database.py           ← Configuración SQLAlchemy (versión legacy, no importado)
│   ├── models.py             ← Modelos ORM (versión legacy, no importado)
│   └── requirements.txt
├── frontend/
│   └── app/
│       ├── page.tsx          ← Navegación: header, tabs, footer (~128 líneas)
│       ├── layout.tsx        ← Layout raíz (fuente, metadata, globals.css)
│       ├── globals.css       ← Estilos globales, modo claro forzado
│       ├── types/index.ts    ← Interfaces TypeScript: Consulta, MensajeChat, FaseChat
│       ├── lib/api.ts        ← URL del backend, PP_UMBRAL, fetchJSON, playTTS
│       ├── lib/tokens.ts     ← Design tokens: btn, inp, tbl
│       ├── hooks/useChatFlow.ts   ← Lógica completa del cuestionario guiado
│       ├── hooks/useIsMobile.ts   ← Detección responsive (breakpoint 768px)
│       ├── components/ui/    ← Card, SectionTitle, StatCard, PieChart, InfoTag
│       ├── components/chat/  ← BotBurbuja, UsuarioBurbuja
│       └── components/tabs/  ← TabConsulta, TabDashboard, TabNgramas, TabIR, TabWER
├── README_TECNICO.md
├── README_FUNCIONAL.md
└── activar_aplicacion.md
```
