# DONAR-APP

Sistema inteligente de consultas para donación de sangre. El usuario describe su situación (por texto o voz) y el sistema evalúa si puede donar, usando PLN, N-gramas, recuperación de información y síntesis de voz.

---

## Tecnologías

| Capa | Stack |
|---|---|
| Backend | Python 3.11+, FastAPI, SQLite |
| Frontend | Next.js 16.2.4, React 19.2.4, TypeScript 5 |
| PLN | NER propio, POS tagging, N-gramas con Add-k |
| IR | TF-IDF + similitud coseno, índice invertido |
| ASR | Web Speech API (Google, online) |
| TTS | gTTS (Google Text-to-Speech) |
| Evaluación | WER (Word Error Rate), P/R/F1 |

---

## Instalación

### Requisitos previos

- Python 3.10+
- Node.js 18+
- npm

### Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate

pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

---

## Ejecución

### 1. Iniciar el backend

```bash
cd backend
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux / Mac

uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

El servidor queda disponible en: `http://127.0.0.1:8000`

### 2. Iniciar el frontend

```bash
cd frontend
npm run dev
```

La app queda disponible en: `http://localhost:3000`

> El backend debe estar corriendo antes de abrir el frontend.

---

## Estructura del proyecto

```
DONAR-APP/
├── backend/
│   ├── main.py          # FastAPI + endpoints
│   ├── nlp.py           # NER, POS tagging, tokenización, intención
│   ├── ngrams.py        # Modelo de bigramas/trigramas con Add-k
│   ├── search.py        # Motor IR: TF-IDF + coseno + P/R/F1
│   ├── wer.py           # Cálculo de Word Error Rate
│   ├── rules.py         # Reglas de negocio (donación)
│   ├── models.py        # Modelos SQLAlchemy (legacy, no importado)
│   ├── database.py      # Config SQLAlchemy (legacy, no importado)
│   ├── donar.db         # Base de datos SQLite (se crea automáticamente)
│   └── requirements.txt
├── frontend/
│   └── app/
│       ├── page.tsx              # Navegación entre tabs (header, footer)
│       ├── types/index.ts        # Interfaces TypeScript
│       ├── lib/                  # api.ts, tokens.ts
│       ├── hooks/                # useChatFlow.ts, useIsMobile.ts
│       └── components/           # ui/, chat/, tabs/
└── README.md
```

---

## Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/consulta` | Evalúa si el usuario puede donar |
| GET | `/tts?texto=...` | Sintetiza texto a audio (MP3) |
| GET | `/wer/frases` | Lista las 12 frases de prueba ASR |
| POST | `/wer/evaluar` | Calcula WER entre referencia e hipótesis |
| GET | `/wer/resumen` | Resumen WER de todas las frases evaluadas |
| GET | `/ngramas/tabla_bigramas?k=1&top_n=10` | Tabla de probabilidades de bigramas |
| GET | `/ngramas/tabla_trigramas?k=1&top_n=10` | Tabla de probabilidades de trigramas |
| GET | `/buscar?q=...&top_k=5` | Búsqueda TF-IDF en el corpus |
| GET | `/ir/metricas` | P/R/F1 del motor de búsqueda |
| GET | `/stats` | Métricas globales del sistema |
| GET | `/stats_diario` | Consultas agrupadas por día |
| GET | `/stats_tipos` | Distribución por tipo de resultado |
| GET | `/stats_top_consultas` | Top 10 consultas más frecuentes |
| GET | `/historial` | Últimas consultas registradas |
| GET | `/corpus` | Documentos del corpus |

---

## Base de datos

SQLite (`donar.db`) con 3 tablas:

- **corpus** — documentos del dominio
- **consultas** — historial de interacciones con métricas
- **metricas** — resultados de evaluaciones (WER, etc.)

---

## Vistas de la aplicación

| Pestaña | Descripción |
|---|---|
| Consulta | Texto o voz, respuesta TTS, entidades, POS, IR snippets |
| Dashboard | Métricas globales, gráficos por día/tipo, top consultas |
| N-gramas | Tablas de bigramas/trigramas con k configurable |
| IR | Búsqueda TF-IDF, métricas P/R/F1 por consulta |
| WER | Evaluación del ASR frase por frase con resultado visual |

---

## Restricciones del corpus

**`corpus.json` es de solo lectura.** Se carga al iniciar el servidor (`json.load()`) y nunca se escribe ni modifica en runtime. El corpus tiene 14 secciones temáticas:

| Sección | Contenido |
|---|---|
| `originales` | Frases base del dominio |
| `requisitos` | Requisitos físicos y documentales |
| `frecuencia` | Intervalos entre donaciones |
| `antes_de_donar` | Preparación previa |
| `durante_la_donacion` | Conducta durante el proceso |
| `despues_de_donar` | Cuidados post-donación (incluye formulario HEMO 3) |
| `medicamentos_diferimiento_permanente` | Fármacos que impiden donar permanentemente |
| `medicamentos_diferimiento_transitorio` | Fármacos con espera definida |
| `medicamentos_sin_diferimiento` | Fármacos que no impiden donar |
| `vacunas_diferir_1_mes` | Vacunas con espera de 1 mes |
| `vacunas_sin_diferimiento` | Vacunas sin espera (con excepciones posexposición) |
| `conductas_de_riesgo` | PREP/PEP, drogas IV, parejas nuevas |
| `componentes_de_la_sangre` | Información educativa sobre hemocomponentes |
| `glosario` | Términos técnicos: aféresis, NAT, HEMO 3, período ventana |

---

## Avances completados

- [x] Corpus externalizado a `corpus.json` (solo lectura en runtime)
- [x] Motor de reglas (`rules.py`) con más de 30 condiciones cubiertas
- [x] Normalización de modismos argentinos en `nlp.py` — dos etapas:
  1. Regex `fullmatch` para repetición silábica (`siisisisisi` → `sí`)
  2. Colapso de caracteres + lookup en sets (`dale`, `nope`, `nel`, `obvio`, `joya`, etc.)
- [x] Manejo de sí/no sin contexto: responde con opciones para que el usuario amplíe
- [x] Detección de fuera de dominio vía perplejidad (umbral `PP_UMBRAL = 60.0`)

### Condiciones cubiertas en `rules.py`

| Categoría | Condiciones |
|---|---|
| Datos básicos | Peso, edad, ayunas |
| ITT permanentes | VIH/SIDA, Hepatitis B/C, Chagas, Brucelosis, Sífilis, HTLV |
| Enfermedades con espera | COVID-19, dengue, gripe, fiebre, varicela, mononucleosis, toxoplasmosis, tuberculosis, paludismo/malaria, fiebre amarilla |
| Enfermedades crónicas | Diabetes T1/T2, hipertensión, asma, anemia, epilepsia, talasemia, trombofilia, PTI |
| Cardíacas | Cardiopatía congénita CIA/CIV, fibrilación auricular |
| Dermatología | Herpes simple/zóster, psoriasis |
| Procedimientos | Tatuaje, piercing, botox, acupuntura, maquillaje permanente |
| Cirugías | General, cardíaca, oncológica, neurológica, bariátrica, dental, ocular, con transfusión |
| Maternidad | Embarazo, parto/cesárea, aborto, lactancia |
| Medicamentos permanentes | Antipsicóticos, anticoagulantes, anticonvulsivantes para epilepsia, insulina, betabloqueantes con bradicardia |
| Medicamentos con espera | Roacután (1 mes), Finasteride (1 mes), Dutasteride (6 meses), Acitretina (3 años), antibióticos (7 días), corticoides (48 h) |
| Medicamentos sin espera | Ansiolíticos, antidepresivos, anticonvulsivantes para dolor |
| Vacunas vivas (1 mes) | Varicela, triple viral, BCG, Sabin, fiebre amarilla, dengue |
| Vacunas inactivadas | Gripe, tétanos, neumococo, HPV, hepatitis A/B preventiva |
| Vacunas posexposición | Hepatitis B (12 meses), hepatitis A (6 semanas), antirrábica (1 año) |
| Conductas de riesgo | PREP/PEP oral (6 meses), PREP/PEP inyectable (2 años) |
| Otros | Endoscopía, transfusión previa, frecuencia por género/edad, viajes a zonas endémicas, requisitos generales |

---

## Pendiente

### Condiciones sin cobertura en `rules.py`

#### Medicamentos sin diferimiento (actualmente caen al fallback)
- [ ] Anticonceptivos (pastilla, parche, inyección, anillo vaginal)
- [ ] Anticolesterol (estatinas: atorvastatina, rosuvastatina)
- [ ] Vitaminas y minerales (hierro, calcio, vitamina D, complejo B)
- [ ] Analgésicos menores (ibuprofeno, paracetamol, naproxeno)
- [ ] Descongestivos nasales / antihistamínicos (loratadina, cetirizina, fexofenadina)
- [ ] Antifúngicos para micosis ungueal (itraconazol, terbinafina tópica)
- [ ] Antitabaco (parches de nicotina, vareniclina)
- [ ] Antiácidos / omeprazol / pantoprazol
- [ ] Diuréticos (furosemida, hidroclorotiazida)

#### Hormonal con espera
- [ ] Testosterona → esperar 6 meses después de suspender
- [ ] Clomifeno → esperar 3 meses después de suspender

#### Enfermedades crónicas sin cobertura
- [ ] Hipotiroidismo / Hipertiroidismo controlado → sin diferimiento
- [ ] Lupus (LES): activo → permanente; en remisión → consultar
- [ ] Artritis reumatoide: depende del tratamiento (biológicos/metotrexato → permanente)
- [ ] Fibromialgia sola → sin diferimiento
- [ ] Esclerosis múltiple en tratamiento activo → permanente
- [ ] Hemofilia / Von Willebrand → permanente

#### Alergias e infecciones menores
- [ ] Alergia / Rinitis alérgica → sin diferimiento; antihistamínicos OK
- [ ] Gastroenteritis / Diarrea → esperar hasta resolución + 7 días si hubo antibióticos
- [ ] Infección urinaria / Cistitis → 7 días después de antibióticos
- [ ] Otitis → 7 días después de antibióticos
- [ ] Conjuntivitis bacteriana → 7 días; viral/alérgica → sin diferimiento
- [ ] Sinusitis viral → sin diferimiento; bacteriana con antibióticos → 7 días
- [ ] Hipotensión → consultar (requiere sistólica ≥ 100, diastólica ≥ 60)

#### Procedimientos estéticos y quirúrgicos
- [ ] Microblading / Tatuaje de cejas → 6 meses
- [ ] Implantes mamarios → 6 meses
- [ ] Implantes dentales → 2 meses
- [ ] DIU / Implante subdérmico anticonceptivo → sin diferimiento si ya tiene >6 meses
- [ ] Apendicectomía → 6 meses
- [ ] Colecistectomía (vesícula) → 6 meses
- [ ] Hernia → 6 meses
- [ ] Histerectomía → 6 meses
- [ ] Tiroidectomía → 6 meses

#### Hábitos y sustancias
- [ ] Tabaquismo → sin diferimiento (pero no fumar 2 h antes ni 2 h después)
- [ ] Alcohol moderado → sin diferimiento; intoxicación / alcoholismo crónico → consultar
- [ ] Cannabis no IV → consultar; IV → permanente

#### Preguntas informativas frecuentes sin handler
- [ ] Tipos de sangre (A, B, AB, O, Rh positivo/negativo)
- [ ] Aféresis: qué es, quién puede, frecuencia permitida
- [ ] Formulario HEMO 3: qué es y por qué es obligatorio
- [ ] Donante habitual vs. voluntario vs. reposición
- [ ] Período ventana: definición y relevancia clínica
- [ ] Técnica NAT y su efecto en los plazos de diferimiento
- [ ] Duración aproximada de la donación
- [ ] Dónde donar / cómo encontrar un banco de sangre

### Mejoras en `nlp.py`
- [ ] Agregar al dict `TIPOS` las palabras clave de las nuevas condiciones:
  - `tiroides`, `hipotiroidismo`, `hipertiroidismo`
  - `autoinmune`, `lupus`, `artritis`, `esclerosis`
  - `hemofilia`, `von willebrand`
  - `testosterona`, `clomifeno`
  - `implante`, `microblading`, `apendicitis`, `vesícula`, `hernia`, `histerectomía`
  - `tabaquismo`, `cigarro`, `cannabis`, `marihuana`
- [ ] Ampliar `_AFIRMACIONES` / `_NEGACIONES` con nuevos modismos según feedback de uso

### Calidad general
- [ ] Actualizar el mensaje del fallback en `rules.py` para listar todos los temas nuevos
- [ ] Agregar frases nuevas al `CORPUS_ENTRENAMIENTO` en `main.py` por cada condición nueva (mejora la perplejidad del dominio)
- [ ] Revisar el umbral `PP_UMBRAL = 60.0` contra consultas reales una vez que haya historial

---

> El chatbot no reemplaza la evaluación médica. Ante cualquier duda aplica el principio de precaución: derivar al centro de donación.
