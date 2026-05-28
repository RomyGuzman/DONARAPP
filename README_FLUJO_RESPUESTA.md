# README — Flujo completo de una respuesta del usuario

> Este documento explica, paso a paso y sin asumir conocimiento previo, qué pasa desde que el usuario escribe o habla una respuesta hasta que el sistema le muestra un mensaje de vuelta.
>
> Archivo fuente principal: `frontend/app/hooks/useChatFlow.ts`

---

## Índice

1. [Qué es este sistema](#1-qué-es-este-sistema)
2. [Componentes involucrados](#2-componentes-involucrados)
3. [El concepto de "fase"](#3-el-concepto-de-fase)
4. [Orden completo de las fases](#4-orden-completo-de-las-fases)
5. [Punto de entrada — `manejarEnvio`](#5-punto-de-entrada--manejarenvio)
6. [Fases iniciales (antes de las preguntas médicas)](#6-fases-iniciales-antes-de-las-preguntas-médicas)
7. [El motor de evaluación — `procesarRespuestaPregunta`](#7-el-motor-de-evaluación--procesarrespuestapregunta)
8. [Cómo se consulta el corpus](#8-cómo-se-consulta-el-corpus)
9. [El resolvedor de flujo — `resolverFlujoMedico`](#9-el-resolvedor-de-flujo--resolverflujomédico)
10. [Cómo se determina la respuesta final](#10-cómo-se-determina-la-respuesta-final)
11. [Casos especiales](#11-casos-especiales)
12. [Modo voz](#12-modo-voz)
13. [Sistema de restricciones acumuladas](#13-sistema-de-restricciones-acumuladas)
14. [Diagrama completo del flujo](#14-diagrama-completo-del-flujo)
15. [Glosario](#15-glosario)

---

## 1. Qué es este sistema

El sistema es un **asistente conversacional guiado** que evalúa si una persona puede donar sangre según las normas del Instituto de Hemoterapia de la Provincia de Buenos Aires.

Funciona como un formulario inteligente: hace preguntas en orden, interpreta las respuestas del usuario en lenguaje natural (no solo "sí/no"), consulta una base de conocimiento (llamada *corpus*) para generar respuestas informativas, y al final emite un veredicto.

El asistente **no improvisa**. Cada respuesta que da sigue una lógica programada que se describe en este documento.

---

## 2. Componentes involucrados

| Componente | Qué hace |
|---|---|
| **`useChatFlow.ts`** | Hook de React. Contiene toda la lógica del flujo, el estado de la conversación y las llamadas al backend. |
| **`TabConsulta.tsx`** | Componente visual que muestra los mensajes y el input. Llama a `manejarEnvio` cuando el usuario envía una respuesta. |
| **Backend `/consulta`** | API HTTP que recibe un texto, lo busca en el corpus y devuelve una respuesta estructurada. |
| **Backend `/whisper`** | API HTTP que recibe audio grabado y lo convierte a texto (solo modo voz con Whisper). |

---

## 3. El concepto de "fase"

La conversación está dividida en **fases**. En todo momento, el sistema sabe exactamente en qué fase está (`fase` en el estado de React). Cada mensaje del usuario es procesado según la fase activa.

Tipos de fase:

- **Fases de datos básicos**: `confirmar_inicio`, `pedir_peso`, `pedir_edad`, `pedir_sexo`
- **Fases de preguntas médicas**: `q_sintomas_hoy`, `q_fiebre_72h`, `q_medicacion`, etc.
- **Sub-fases de detalle**: `q_sintomas_describe`, `q_medicacion_detalle`, `q_diabetes_tipo`, `q_sintomas_continuar`
- **Fase final**: `resultado`

Una vez que el sistema entra en `resultado`, **no procesa más respuestas**.

---

## 4. Orden completo de las fases

```
confirmar_inicio
    ↓ (usuario dice "sí")
pedir_peso
    ↓
pedir_edad
    ↓
pedir_sexo
    ↓
q_sintomas_hoy
    ↓
q_fiebre_72h
    ↓
q_medicacion
    ↓ (si dice sí → sub-fase q_medicacion_detalle)
q_corazon
    ↓
q_diabetes
    ↓ (si dice sí → sub-fase q_diabetes_tipo)
q_riñones_pulmones
    ↓
q_neuro_cancer
    ↓
q_hepatitis
    ↓
q_ets_vih
    ↓
q_chagas
    ↓
q_procedimientos
    ↓
q_tatuaje
    ↓
q_transfusion
    ↓
q_riesgo_sexual
    ↓
q_drogas
    ↓
q_vacunas
    ↓
q_embarazo  ← solo si sexo = Mujer
    ↓
resultado
```

> Si en cualquier punto se detecta una restricción permanente (❌), el flujo puede saltar directamente a `resultado` sin hacer el resto de preguntas.

---

## 5. Punto de entrada — `manejarEnvio`

**Cada vez que el usuario envía un mensaje** (toca el botón, presiona Enter, o termina de hablar), se llama a `manejarEnvio(texto)`.

```
texto vacío  →  error: "Escribí tu respuesta."

fase = confirmar_inicio      →  procesarConfirmacion()
fase = pedir_peso            →  procesarPeso()
fase = pedir_edad            →  procesarEdad()
fase = pedir_sexo            →  procesarSexoPorVoz()
fase = q_sintomas_describe   →  procesarSintomasDescribe()
fase = q_sintomas_continuar  →  procesarSintomaContinuar()
fase = q_medicacion_detalle  →  procesarMedicacionDetalle()
fase = q_diabetes_tipo       →  procesarRespuestaPregunta()
fase = resultado             →  (ignora el mensaje, no hace nada)
fase = cualquier pregunta médica → procesarRespuestaPregunta()
cualquier otro texto libre   →  consultarAPI()  (modo libre)
```

---

## 6. Fases iniciales (antes de las preguntas médicas)

### 6.1 `confirmar_inicio` — ¿Querés comenzar?

El sistema busca en el texto si hay una afirmación o negación simple.

- **Afirmación** (sí, dale, ok, claro, s): arranca el flujo, pregunta el peso.
- **Negación** (no, nop, nel, negativo): muestra despedida y pasa a `resultado`.
- **Otra cosa**: error "Respondé Sí o No." — el usuario debe reintentar.

### 6.2 `pedir_peso` — ¿Cuánto pesás?

- Extrae el número del texto (acepta coma decimal, "kg", etc.).
- **Menos de 50 kg**: fin del flujo, no puede donar (requisito de peso).
- **50 kg o más**: guarda el peso y pregunta la edad.
- **Número inválido**: error "Ingresá un peso válido en kg."

### 6.3 `pedir_edad` — ¿Cuántos años tenés?

- Extrae el número entero.
- **Menos de 16**: fin del flujo.
- **16 o 17**: puede donar con restricciones (máximo 2 veces por año, requiere autorización). Sigue al paso de sexo.
- **18 a 65**: rango normal. Sigue al paso de sexo.
- **Más de 65**: puede donar con certificado médico. Sigue al paso de sexo.
- **Número inválido**: error.

### 6.4 `pedir_sexo` — ¿Cuál es tu sexo biológico?

En modo texto: el usuario elige un botón (Masculino / Femenino / Otro).
En modo voz: el sistema detecta palabras clave en el audio.

- Guarda el sexo en el perfil del usuario.
- Lanza la primera pregunta médica: `q_sintomas_hoy`.
- **El sexo importa** al final: la pregunta `q_embarazo` solo se hace si el sexo es "Mujer".

---

## 7. El motor de evaluación — `procesarRespuestaPregunta`

Esta función es el **núcleo del sistema**. Se ejecuta para todas las preguntas médicas (desde `q_sintomas_hoy` hasta `q_embarazo`).

Recibe: la fase actual (`f`) y el texto del usuario (`raw`).

Primero normaliza el texto a minúsculas (`txt = raw.toLowerCase().trim()`), luego aplica una **cadena de filtros en orden**. Apenas un filtro produce resultado, la función termina sin ejecutar los siguientes.

### Cadena de filtros (en orden de prioridad)

---

#### FILTRO 0 — Caso especial `q_sintomas_hoy` (se ejecuta antes que todo lo demás)

Solo aplica cuando la fase es `q_sintomas_hoy` ("¿Te sentís bien hoy?").

Se evalúan tres condiciones **en este orden**:

**A) ¿Expresa bienestar?**
Busca palabras positivas: "bien", "muy bien", "excelente", "genial", "sano", "todo ok", etc.
Pero si el texto contiene la palabra "no", automáticamente descarta el bienestar
(para que "no me siento bien" no active esta rama).

→ Si da positivo: el usuario se siente bien → llama a `resolverFlujoMedico(esSi=true)`

**B) ¿Describe un síntoma específico?**
Busca palabras como: "dolor", "fiebre", "tos", "mareo", "cansancio", "congestion", etc.

→ Si da positivo: el usuario tiene síntomas → llama a `procesarSintomasDescribe()`

**C) ¿Es una negación simple?**
Detecta "no", "nop", "nel", "negativo", "para nada", "tampoco", "me siento mal", "no estoy bien", etc.

→ Si da positivo: el usuario no se siente bien → llama a `resolverFlujoMedico(esSi=false)`

**D) Ninguno de los tres:**
→ Error: "No entendí tu respuesta. Decí si te sentís bien o describí un síntoma (ej: dolor de cabeza, fiebre, tos)."

---

#### FILTRO 1 — Negación directa

Detecta si el texto **empieza** con: "no", "nop", "nel", "nunca", "jamás", "negativo", "para nada", "tampoco".
O si contiene esas palabras como palabras completas.

→ Llama a `resolverFlujoMedico(esSi=false)`

---

#### FILTRO 2 — Medicación inline (solo para fase `q_medicacion`)

Aplica **solo** cuando la fase es `q_medicacion` ("¿Estás tomando algún medicamento?").

- Si el texto contiene "nada", "ninguno", "ningún" → trata como negación.
- Si el texto empieza con una afirmación seguida de un nombre de medicamento
  (ej: "sí, metformina") → extrae el nombre y lo pasa directo a `procesarMedicacionDetalle`.
- Si el texto tiene 6 palabras o menos y no es solo una afirmación simple → asume que ES el nombre del medicamento y lo pasa a `procesarMedicacionDetalle`.

Este filtro evita que el usuario tenga que responder en dos pasos ("¿Tomás medicación?" + "¿Cuál?") cuando puede decirlo todo junto.

---

#### FILTRO 3 — Afirmación directa

Detecta: "sí", "si", "s", "yes", "dale", "ok", "claro", "correcto", "afirmativo", "efectivamente", "cierto", "verdad", "exacto", "obvio", "por supuesto".

→ Llama a `resolverFlujoMedico(esSi=true)`

---

#### FILTRO 4 — Tipo de diabetes (solo para fase `q_diabetes_tipo`)

Aplica **solo** cuando la fase es `q_diabetes_tipo` ("¿Qué tipo de diabetes tenés?").

- Detecta **Tipo 1** o **presión alta grave**: "tipo 1", "insulina", "inyección", "me inyecto", "hipertensión", "presión", etc.
  → `resolverFlujoMedico(esSi=true)` (implica restricción)

- Detecta **Tipo 2**: "tipo 2", "pastillas", "metformina", "dieta", "sin insulina", etc.
  → `resolverFlujoMedico(esSi=false)` (no implica restricción)

- Si no detecta ninguno: error "Por favor indicá: tipo 1 (con insulina), tipo 2 (pastillas o dieta) o presión alta."

---

#### FILTRO 5 — Verbo con o sin negación

Analiza si el texto usa verbos en primera persona que indican presencia o ausencia de condición.

**Patrón de negación + verbo** (ej: "no tengo", "no tuve", "no soy", "nunca usé"):
Detecta expresiones como "no tengo", "no tuve", "no soy", "no fui", "no tomo", "no recibí", "no me hice".
→ `resolverFlujoMedico(esSi=false)`

**Solo verbo afirmativo** (ej: "tuve", "tengo", "me vacuné", "me operé"):
Detecta: "tengo", "tuve", "padezco", "tomo", "recibí", "me hice", "me diagnosticaron", "me operé", "me tatué", "me inyecté", etc.
→ `resolverFlujoMedico(esSi=true)`

---

#### FILTRO 6 — Palabras clave específicas por fase (`KEYWORDS_SI`)

Para cada fase médica existe una lista de palabras clave que indican directamente que el usuario **tiene** esa condición.

Ejemplos:

| Fase | Palabras clave detectadas |
|---|---|
| `q_fiebre_72h` | fiebre, diarrea, vómito, tos, gripe, catarro, malestar, cefalea, etc. |
| `q_corazon` | infarto, angina, válvula, arritmia, marcapasos, stent, bypass, etc. |
| `q_hepatitis` | hepatitis, ictericia |
| `q_ets_vih` | VIH, HIV, sífilis, gonorrea, ETS, clamidia, herpes genital |
| `q_drogas` | jeringa, droga, cocaína, heroína, drogadicto |
| `q_embarazo` | embarazada, embarazo, parto, cesárea, aborto, gestación |

Si alguna de estas palabras aparece en el texto → `resolverFlujoMedico(esSi=true)`

---

#### FILTRO 7 — Última instancia: consulta directa al corpus (API)

Si ningún filtro anterior produjo resultado, el sistema llama directamente al endpoint `/consulta` con el **texto original del usuario** como consulta libre.

El backend evalúa el texto y devuelve un objeto con:
- `tipo`: puede ser `apto`, `no_apto_temporal`, `no_apto_permanente`, o `fuera_de_dominio`
- `respuesta`: el texto que el bot debe mostrar

Lógica de interpretación:
- `tipo = no_apto_permanente` o `no_apto_temporal` → el usuario tiene la condición → `resolverFlujoMedico(esSi=true)`
- `tipo = apto` → el usuario no tiene la condición → `resolverFlujoMedico(esSi=false)`
- `tipo = fuera_de_dominio` → el texto no está relacionado con donación → error "Tu respuesta no está relacionada con la pregunta."
- Error de red → error "No entendí. Escribí 'sí' o 'no', o describí tu situación."

En este caso, el bot **también muestra** la respuesta del corpus antes de continuar el flujo (a diferencia de los filtros anteriores que solo determinan sí/no).

---

## 8. Cómo se consulta el corpus

### La función `fromCorpus`

Todos los accesos al corpus pasan por esta función. Recibe una **query** (texto de búsqueda) y devuelve la respuesta del corpus o `null` si no encontró nada relevante.

```
fromCorpus(query)
    → POST /consulta  { texto: query, origen: "texto" }
    → Si tipo ≠ "fuera_de_dominio"  →  devuelve respuesta (string)
    → Si tipo = "fuera_de_dominio"  →  devuelve null
    → Si hay error de red           →  devuelve null
```

### Las dos tablas de queries

El sistema tiene **dos diccionarios** de queries predefinidas:

**`QUERIES_CORPUS`** — queries para cuando el usuario responde "SÍ":

| Fase | Query que se envía al corpus |
|---|---|
| `q_sintomas_hoy` | "me siento bien hoy sin síntomas evaluación donante sangre" |
| `q_fiebre_72h` | "fiebre diarrea síntomas recientes esperar donar sangre" |
| `q_corazon` | "enfermedad del corazón infarto angina válvulas arritmia diferimiento" |
| `q_riñones_pulmones` | "insuficiencia renal crónica EPOC asma broncodilatadores diferimiento" |
| `q_neuro_cancer` | "epilepsia en tratamiento ACV cáncer quimioterapia radioterapia diferimiento permanente" |
| `q_diabetes_tipo_si` | "diabetes tipo 1 insulina diferimiento permanente" |
| `q_diabetes_tipo_no` | "diabetes tipo 2 controlada donar sangre" |
| `q_hepatitis` | "hepatitis B C análisis positivo diferimiento permanente" |
| `q_ets_vih` | "VIH sífilis gonorrea ETS diferimiento permanente" |
| `q_chagas` | "chagas malaria brucelosis diferimiento permanente" |
| `q_procedimientos` | "cirugía operación endoscopía implante esperar meses donar" |
| `q_tatuaje` | "tatuaje piercing acupuntura esperar meses donar sangre" |
| `q_transfusion` | "transfusión trasplante órgano esperar donar sangre" |
| `q_riesgo_sexual` | "relaciones sexuales sin preservativo pareja nueva esperar meses" |
| `q_drogas` | "drogas inyectables jeringa diferimiento permanente" |
| `q_vacunas` | "vacuna fiebre amarilla triple viral varicela BCG polio oral dengue esperar mes" |
| `q_embarazo` | "embarazada parto cesárea aborto diferimiento donar" |

**`QUERIES_CORPUS_NO`** — queries para cuando el usuario responde "NO":

| Fase | Query que se envía al corpus |
|---|---|
| `q_fiebre_72h` | "sin fiebre sin síntomas recientes puede donar sangre" |
| `q_medicacion` | "sin medicación puede donar sangre" |
| `q_corazon` | "sin enfermedad del corazón puede donar sangre" |
| `q_riñones_pulmones` | "sin enfermedad renal ni pulmonar puede donar sangre" |
| `q_neuro_cancer` | "sin epilepsia sin cáncer sin ACV puede donar sangre" |
| `q_diabetes` | "sin diabetes sin presión alta puede donar sangre" |
| `q_hepatitis` | "sin hepatitis puede donar sangre" |
| `q_ets_vih` | "sin VIH sin ETS puede donar sangre" |
| `q_chagas` | "sin chagas sin malaria puede donar sangre" |
| `q_procedimientos` | "sin cirugía sin procedimientos recientes puede donar sangre" |
| `q_tatuaje` | "sin tatuajes sin piercings recientes puede donar sangre" |
| `q_transfusion` | "sin transfusiones sin trasplantes puede donar sangre" |
| `q_riesgo_sexual` | "sin relaciones sexuales de riesgo puede donar sangre" |
| `q_drogas` | "sin drogas inyectables sin alcoholismo puede donar sangre" |
| `q_vacunas` | "sin vacunas recientes puede donar sangre" |
| `q_embarazo` | "sin embarazo sin parto reciente puede donar sangre" |

### Comportamiento cuando el corpus no responde (`null`)

- **Respuesta "Sí" + corpus null**: se muestra el **mensaje de fallback** hardcodeado
  (por ejemplo: "Las enfermedades graves del corazón como infarto... generalmente impiden donar de forma permanente.").
- **Respuesta "No" + corpus null**: no se muestra ningún mensaje extra, se pasa directamente a la siguiente pregunta sin prefijo.

---

## 9. El resolvedor de flujo — `resolverFlujoMedico`

Una vez que los filtros en `procesarRespuestaPregunta` determinaron si la respuesta es **"sí" o "no"**, se llama a `resolverFlujoMedico(fase, esSi)`.

Esta función decide:
1. Qué mensaje mostrar al usuario.
2. Si registrar una restricción de donación.
3. Cuál es la siguiente fase.

### La función interna `responder`

Para la mayoría de las preguntas médicas (`q_corazon`, `q_hepatitis`, `q_ets_vih`, etc.) se usa la función `responder` que aplica la misma lógica para todos:

**Cuando `esSi = true` (usuario TIENE la condición):**
```
1. Registra la restricción (ej: "❌ Enfermedad cardíaca grave")
2. Consulta corpus con QUERIES_CORPUS[fase]
3. Si corpus responde → muestra esa respuesta
4. Si corpus no responde → muestra el fallback hardcodeado
5. Si hay restricción permanente → pasa a "resultado"
6. Si no → muestra la respuesta + siguiente pregunta
```

**Cuando `esSi = false` (usuario NO TIENE la condición):**
```
1. Consulta corpus con QUERIES_CORPUS_NO[fase]
2. Si corpus responde → muestra esa respuesta como prefijo
3. Si corpus no responde → no muestra nada extra
4. Pasa a la siguiente pregunta (o a "resultado" si era la última)
```

### Manejo especial de cada fase

Algunas fases tienen lógica propia que no usa `responder`:

| Fase | Lógica especial |
|---|---|
| `q_sintomas_hoy` sí | Consulta corpus y muestra prefijo antes de preguntar por fiebre |
| `q_sintomas_hoy` no | Pregunta "¿Qué te pasa?" y pasa a `q_sintomas_describe` |
| `q_fiebre_72h` sí | Corpus + fallback hardcoded + restricción temporal → resultado |
| `q_fiebre_72h` no | Corpus + pasa a `q_medicacion` |
| `q_medicacion` sí | Pregunta "¿Cuál?" y pasa a `q_medicacion_detalle` |
| `q_medicacion` no | Corpus + pasa a siguiente pregunta |
| `q_diabetes` sí | Pregunta sub-fase `q_diabetes_tipo` |
| `q_diabetes` no | Corpus + pasa a siguiente pregunta |
| `q_diabetes_tipo` sí (tipo 1) | Corpus + fallback + restricción permanente → resultado |
| `q_diabetes_tipo` no (tipo 2) | Corpus + continúa flujo |

---

## 10. Cómo se determina la respuesta final

Cuando todas las preguntas terminan (o cuando se detecta una restricción que cierra el flujo), se llama a `irAResultado()`.

Esta función mira el **listado de restricciones acumuladas** durante la conversación:

```
Sin restricciones
    → "Podés donar sangre. Acercate al banco de sangre más cercano."
    → tipo: "apto"

Hay restricciones, pero todas son temporales (⏳)
    → "Por el momento no podés donar sangre. Cuando estés recuperado/a..."
    → tipo: "no_apto_temporal"

Hay al menos una restricción permanente (❌)
    → "No podés donar sangre. Te recomendamos hablar con el médico..."
    → tipo: "no_apto_permanente"
```

Los símbolos ❌ y ⏳ al inicio de cada restricción son los que determinan el tipo:
- `❌` = permanente (VIH, cáncer, drogas inyectables, etc.)
- `⏳` = temporal (síntomas recientes, vacuna, procedimiento reciente, etc.)

---

## 11. Casos especiales

### 11.1 Descripción de síntomas — `procesarSintomasDescribe`

Se activa cuando el usuario no se siente bien en `q_sintomas_hoy` y en la sub-fase `q_sintomas_describe`.

```
1. Envía al corpus: "síntomas: [texto del usuario]"
2. Si corpus dice no_apto → muestra respuesta + restricción + resultado
3. Si SINTOMAS_IMPEDITIVOS coincide → restricción + resultado (sin corpus)
4. Si hay malestar leve (duele, cansancio, molestia) → "no es impedimento" + sigue a q_fiebre_72h
5. Si no reconoce nada → pide más detalle
```

### 11.2 Detalle de medicación — `procesarMedicacionDetalle`

Se activa cuando el usuario dice qué medicamento toma.

```
1. Envía al corpus: "medicamento: [nombre]"
2. Si corpus reconoce el medicamento:
   - no_apto_permanente → restricción + resultado
   - no_apto_temporal → advertencia + resultado
   - apto → continúa flujo normal
3. Si corpus dice fuera_de_dominio:
   a. Si el texto empieza con "para/sirve para/lo tomo para": reintenta con "indicación médica: [propósito]"
   b. Si primer intento fallido: pregunta de nuevo ("¿podés escribirlo correctamente?")
   c. Si segundo intento también falla: avisa que el centro lo evaluará → continúa flujo
```

### 11.3 La pregunta de embarazo es condicional

La fase `q_embarazo` **solo se hace si el sexo del usuario es "Mujer"**. La función `siguientePregunta()` verifica esto y si el sexo es "Hombre" u "Otro", salta directamente a `resultado` cuando llega a esa posición en el flujo.

---

## 12. Modo voz

El asistente tiene **dos modos de voz**:

**Web Speech API (`iniciarVoz`)**
- Usa el reconocedor de voz nativo del navegador (Chrome/Edge).
- El usuario toca el micrófono, habla, y el texto transcripto se pasa automáticamente a `manejarEnvio`.
- El idioma configurado es español argentino (`es-AR`).

**Whisper (`iniciarWhisper`)**
- Graba audio con `MediaRecorder`.
- Al terminar la grabación, envía el audio al endpoint `/whisper` del backend.
- El backend (OpenAI Whisper) convierte el audio a texto.
- El texto se pasa a `manejarEnvio`.

En modo voz, si TTS está activado (`ttsOn = true`), cada respuesta del bot también se reproduce en audio mediante el endpoint `/tts`.

---

## 13. Sistema de restricciones acumuladas

Durante toda la conversación, se va llenando un array `restricciones[]`. Cada vez que el sistema detecta un impedimento se llama a `addRestriccion(texto)`.

Ejemplos de restricciones que se van acumulando:
```
⏳ Síntomas recientes (fiebre, diarrea u otros) — esperá hasta recuperarte completamente.
❌ Enfermedad cardíaca grave — probable restricción permanente.
⏳ Tatuaje, piercing o acupuntura reciente — espera de 6 a 12 meses.
⚠️ Tomás medicación — el centro verificará si es compatible con la donación.
```

El símbolo al inicio determina la gravedad:
- `❌` Restricción permanente
- `⏳` Restricción temporal
- `⚠️` Advertencia (requiere verificación en el centro)

---

## 14. Diagrama completo del flujo

```
USUARIO ENVÍA TEXTO
        │
        ▼
  manejarEnvio(texto)
        │
  ¿Fase actual?
  ├─ confirmar_inicio    → procesarConfirmacion()
  ├─ pedir_peso          → procesarPeso()
  ├─ pedir_edad          → procesarEdad()
  ├─ pedir_sexo          → procesarSexoPorVoz()
  ├─ q_sintomas_describe → procesarSintomasDescribe()
  │       └─ POST /consulta "síntomas: [texto]"
  │           ├─ apto → [malestar leve] continúa
  │           └─ no_apto → restricción + resultado
  ├─ q_medicacion_detalle→ procesarMedicacionDetalle()
  │       └─ POST /consulta "medicamento: [nombre]"
  │           ├─ reconocido → aplica restricción si corresponde
  │           └─ no reconocido → reintenta o avisa
  ├─ resultado           → (ignora)
  └─ [pregunta médica]   → procesarRespuestaPregunta(fase, texto)
                                │
                         CADENA DE FILTROS
                                │
         ┌──────────────────────┼──────────────────────┐
         │ [q_sintomas_hoy]     │                       │
         │ ¿Bienestar?──────Sí──┤                       │
         │ ¿Síntoma?────────Sí──┤                       │
         │ ¿Negación?───────Sí──┘                       │
         │                                              │
         ├─ Negación directa (no/nop/nel/nunca/jamás)   │
         ├─ Medicación inline (solo q_medicacion)        │
         ├─ Afirmación directa (sí/dale/ok/claro)        │
         ├─ Tipo diabetes (solo q_diabetes_tipo)         │
         ├─ Verbo + negación / verbo afirmativo          │
         ├─ Keywords específicas por fase                │
         └─ Último recurso: POST /consulta [texto libre]
                    └─ apto/no_apto → esSi=false/true
                    └─ fuera_de_dominio → error
                                │
                     resolverFlujoMedico(fase, esSi)
                                │
              ┌─────────────────┴─────────────────┐
              │                                   │
         esSi = true                         esSi = false
              │                                   │
    POST /consulta                      POST /consulta
    [QUERIES_CORPUS]                    [QUERIES_CORPUS_NO]
              │                                   │
    ¿Corpus responde?                   ¿Corpus responde?
    ├─ Sí → muestra respuesta           ├─ Sí → muestra como prefijo
    └─ No → usa fallback hardcoded      └─ No → sin mensaje extra
              │                                   │
    addRestriccion(❌/⏳)                  (sin restricción)
              │                                   │
    ¿Es la última pregunta                ¿Es la última pregunta
     o hay restricción grave?              o es la última?
    ├─ Sí → irAResultado()              ├─ Sí → irAResultado()
    └─ No → siguiente pregunta          └─ No → siguiente pregunta
                    │
            irAResultado()
                    │
         ¿Hay restricciones?
         ├─ No → "Podés donar sangre ✓"
         ├─ Solo ⏳ → "Por el momento no podés..."
         └─ Algún ❌ → "No podés donar..."
```

---

## 15. Glosario

| Término | Significado |
|---|---|
| **Fase** | El estado actual de la conversación. Define qué pregunta se está haciendo y cómo se interpreta la respuesta. |
| **Corpus** | La base de conocimiento médica del sistema. Se accede vía el endpoint `/consulta` del backend. |
| **Query** | El texto que se envía al corpus para buscar información. No es la respuesta del usuario, sino una búsqueda construida por el sistema. |
| **Fallback** | Respuesta de respaldo hardcodeada en el código. Se usa cuando el corpus no devuelve nada relevante para una respuesta "sí". |
| **Restricción** | Un impedimento para donar sangre detectado durante la evaluación. Puede ser permanente (❌) o temporal (⏳). |
| **esSi** | Variable booleana interna (`true`/`false`) que representa si la respuesta del usuario equivale a "sí" o "no" para la pregunta actual. Todos los filtros buscan determinar este valor. |
| **`fuera_de_dominio`** | Respuesta del corpus que significa "este texto no está relacionado con donación de sangre". |
| **TTS** | Text-to-Speech. Convierte el texto de las respuestas del bot en audio reproducible. |
| **Whisper** | Modelo de OpenAI para convertir audio a texto. Se usa como alternativa al reconocimiento de voz nativo del navegador. |
| **Hook** | En React, una función especial (`useChatFlow`) que maneja el estado y la lógica de un componente. No es un componente visual en sí mismo. |
