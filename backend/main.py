import io
import os
import sqlite3
import tempfile
from datetime import datetime

from fastapi import FastAPI, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from gtts import gTTS

from ngrams import ModeloNgramas
from nlp import NLPProcessor
from wer import calcular_wer, resumen_wer, FRASES_PRUEBA
from rules import evaluar
from search import MotorBusqueda

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── CORPUS ───────────────────────────────────────────────────────────────────
_CORPUS_DICT = {
    "originales": [
        "Si te hiciste un tatuaje reciente debes esperar 6 meses para donar sangre",
        "Personas con tatuajes pueden donar luego de 6 meses del procedimiento",
        "Para donar sangre debes estar sano y sin infecciones activas",
        "Después de tomar antibióticos debes esperar al menos 7 días para donar",
        "Si tomaste penicilina o amoxicilina debes esperar una semana",
        "Luego de una cirugía el tiempo de espera depende del tipo de operación",
        "Una cirugía menor requiere esperar al menos 6 meses para donar",
        "La hepatitis B o C impide la donación de sangre de forma permanente",
        "El dengue requiere esperar 28 días después de recuperarte para donar",
        "El COVID-19 requiere esperar 14 días después de la recuperación completa",
        "Los piercing también requieren esperar 6 meses igual que los tatuajes",
        "La diabetes tipo 1 impide donar sangre de forma permanente",
        "soy diabetico tipo 1 impide donar sangre de forma permanente",
        "La diabetes tipo 2 controlada no impide la donación si los valores son normales",
        "soy diabetico tipo 2 controlada no impide la donación si los valores son normales",
        "La hipertensión controlada no impide la donación si los valores son normales",
        "Debes pesar más de 50 kilos para poder donar sangre",
        "La edad mínima para donar sangre es 18 años y la máxima 65 años",
        "Debes estar en ayunas de al menos 4 horas antes de donar",
        "Si tuviste fiebre en los últimos 7 días no podés donar sangre",
        "El VIH o SIDA impide la donación de sangre de forma permanente",
        "Se puede donar sangre cada 3 meses en el caso de los hombres",
        "Las mujeres pueden donar sangre cada 4 meses como mínimo",
    ],

    "requisitos": [
        "Sentirse bien y sano el día de la donación es requisito para donar sangre",
        "Tener entre 16 y 65 años para donar sangre, mayores de 65 requieren certificado médico",
        "Pesar más de 50 kg para donar sangre ya que se extraen 450 ml aproximadamente",
        "Presentar DNI para donar sangre",
        "No concurrir en ayunas antes de donar sangre, desayunar o almorzar antes",
        "Temperatura corporal no mayor a 37 grados para poder donar sangre",
        "Hemoglobina entre 12.5 y 17 gramos por decilitro para donar sangre",
        "Hematocrito entre 38 y 52 por ciento para poder donar sangre",
        "Pulso entre 60 y 100 latidos por minuto para donar sangre",
        "Tensión sistólica entre 100 y 170 mmHg y diastólica entre 60 y 100 mmHg para donar",
    ],

    "frecuencia": [
        "Los hombres pueden donar sangre mínimo cada 8 semanas hasta 5 veces por año",
        "Las mujeres pueden donar sangre mínimo cada 12 semanas hasta 4 veces por año",
        "Jóvenes de 16 a 17 años pueden donar sangre mínimo cada 6 meses hasta 2 veces por año",
        "La aféresis no debe realizarse más frecuente que cada 3 días",
        "Luego de una aféresis se debe diferir la sangre entera al menos 48 horas",
        "Para aféresis los donantes deben tener entre 18 y 65 años",
    ],

    "antes_de_donar": [
        "No fumar antes de donar sangre",
        "No concurrir en ayunas para donar sangre, desayunar o almorzar antes de ir",
        "Hidratarse bien antes de donar sangre",
        "Usar vestimenta cómoda para poder arremangarse al donar sangre",
        "No acercarse al banco de sangre solo para saber si tiene una infección, derivar al médico",
    ],

    "durante_la_donacion": [
        "Durante la donación permanecer recostado en posición cómoda",
        "Durante la donación no mover el brazo con la venopunción",
        "Avisar si hay mareos náuseas o incomodidad durante la donación de sangre",
        "Al terminar la donación comprimir la zona con el apósito al menos 5 minutos",
        "No levantarse hasta que el técnico lo indique después de donar sangre",
    ],

    "despues_de_donar": [
        "Después de donar sangre consumir el refrigerio ofrecido",
        "Después de donar sangre aumentar ingesta de líquidos y comer bien ese día",
        "Dejar el apósito al menos 4 horas después de donar sangre",
        "Si hay sangrado después de donar presionar levantar el brazo y aplicar hielo",
        "Evitar ejercicio enérgico y deportes de contacto después de donar sangre",
        "No conducir por tiempo prolongado las primeras 2 horas después de donar sangre",
        "No fumar las 2 horas siguientes a la donación de sangre",
        "Completar el formulario confidencial HEMO 3 con sí o no, sin este formulario la sangre no puede ser utilizada",
    ],

    "medicamentos_diferimiento_permanente": [
        "Digoxina produce diferimiento permanente para donar sangre",
        "Vasodilatadores producen diferimiento permanente para donar sangre",
        "Insulina produce diferimiento permanente para donar sangre",
        "Anticoagulantes producen diferimiento permanente para donar sangre",
        "Hormona de crecimiento hipofisaria humana produce diferimiento permanente, la recombinante no difiere",
        "Etretinato Tigason produce diferimiento permanente para donar sangre",
        "Medicamentos oncológicos producen diferimiento permanente para donar sangre",
        "Antipsicóticos como Quetiapina Risperidona Olanzapina Haloperidol producen diferimiento permanente",
        "Anticonvulsivantes para epilepsia producen diferimiento permanente para donar sangre",
        "Betabloqueantes con frecuencia cardíaca menor a 60 por minuto producen diferimiento permanente",
    ],

    "medicamentos_diferimiento_transitorio": [
        "Acitretina Neotigason requiere esperar 3 años luego de suspendido para donar sangre",
        "Dutasteride requiere esperar 6 meses luego de suspendido para donar sangre",
        "Testosterona requiere esperar 6 meses luego de suspendido para donar sangre",
        "Clomifeno requiere esperar 3 meses luego de suspendido para donar sangre",
        "Isotretinoína Roacutan requiere esperar 1 mes luego de suspendido para donar sangre",
        "Finasteride requiere esperar 1 mes luego de suspendido para donar sangre",
        "Antibióticos requieren esperar 7 días luego de suspendido para donar sangre",
        "Tetraciclina Doxiciclina y Eritromicina no requieren diferimiento para donar sangre",
        "Corticoides sistémicos requieren esperar 48 horas luego de suspendido para donar sangre",
    ],

    "medicamentos_sin_diferimiento": [
        "Antitabaco no requiere diferimiento para donar sangre",
        "Anticonceptivos no requieren diferimiento para donar sangre",
        "Anticolesterol no requiere diferimiento para donar sangre",
        "Descongestivos nasales y broncodilatadores no requieren diferimiento para donar sangre",
        "Vitaminas y minerales no requieren diferimiento para donar sangre",
        "Tranquilizantes ansiolíticos y antidepresivos no requieren diferimiento para donar sangre",
        "Analgésicos menores no requieren diferimiento para donar sangre",
        "Diuréticos no requieren diferimiento para donar sangre",
        "Antifúngicos para micosis ungueal no requieren diferimiento para donar sangre",
    ],

    "vacunas_diferir_1_mes": [
        "Vacuna polio oral Sabin requiere diferir 1 mes para donar sangre",
        "Vacuna triple viral paperas sarampión rubéola requiere diferir 1 mes para donar sangre",
        "Vacuna doble viral sarampión rubéola requiere diferir 1 mes para donar sangre",
        "Vacuna fiebre amarilla requiere diferir 1 mes para donar sangre",
        "Vacuna BCG requiere diferir 1 mes para donar sangre",
        "Vacuna varicela herpes zóster requiere diferir 1 mes para donar sangre",
        "Vacuna dengue requiere diferir 1 mes para donar sangre",
    ],

    "vacunas_sin_diferimiento": [
        "Vacuna polio inyectable Salk no requiere diferimiento para donar sangre",
        "Vacuna tétano no requiere diferimiento para donar sangre",
        "Vacuna influenza no requiere diferimiento para donar sangre",
        "Vacuna hepatitis B recombinante sin exposición no requiere diferimiento para donar sangre",
        "Vacuna hepatitis B posexposición requiere diferir 12 meses para donar sangre",
        "Vacuna hepatitis A sin exposición no requiere diferimiento para donar sangre",
        "Vacuna hepatitis A posexposición requiere diferir 6 semanas para donar sangre",
        "Vacuna antirrábica sin mordedura no requiere diferimiento para donar sangre",
        "Vacuna antirrábica con mordedura requiere diferir 1 año para donar sangre",
        "Vacuna neumococo HPV meningitis no requieren diferimiento para donar sangre",
    ],

    "conductas_de_riesgo": [
        "Parejas nuevas en los últimos 6 meses con relaciones sexuales sin preservativo diferir 6 meses",
        "Uso de PREP o PEP oral diferir 6 meses para donar sangre",
        "Uso inyectable de PREP PEP o ART diferir 2 años para donar sangre",
        "Uso de drogas intravenosas diferimiento permanente para donar sangre",
        "La evaluación para donar es individual e independiente del género u orientación sexual",
    ],

    "componentes_de_la_sangre": [
        "Los glóbulos blancos leucocitos son 4000 a 9000 por milímetro cúbico y defienden contra infecciones",
        "Los glóbulos rojos eritrocitos son 4.5 a 5.5 millones por milímetro cúbico transportan oxígeno y viven 120 días",
        "Las plaquetas son 150000 a 400000 por milímetro cúbico y detienen hemorragias",
        "El plasma contiene 91 por ciento de agua albúmina inmunoglobulinas y factores de coagulación",
        "Los glóbulos rojos se usan en cirugías accidentes hemorragias trasplantes y anemia",
        "El plasma se usa en quemaduras y elaboración de hemoderivados",
        "Las plaquetas se usan en leucemias trasplantes quimioterapia y grandes hemorragias",
        "Los crioprecipitados se usan en trastornos específicos de la coagulación",
        "Una donación de sangre puede salvar hasta 3 vidas",
    ],

    "glosario": [
        "Donante habitual presenta 2 donaciones en el último año calendario o en los últimos 12 meses",
        "Donante de reposición es condicionado a donar para reponer stock de un paciente",
        "Donante voluntario está motivado por acto solidario y altruista con compromiso social",
        "Donante diferido permanente no cumple en forma permanente los criterios habilitantes",
        "Donante diferido temporario debe esperar un tiempo determinado antes de poder donar",
        "El período ventana es el tiempo entre que el agente infeccioso entra al organismo y es detectable",
        "Hemocomponente es la fracción obtenida por separación física glóbulos rojos plasma plaquetas crioprecipitados",
        "Hemoderivado es el producto obtenido de la manufactura del plasma albúmina factores de coagulación gammaglobulina",
        "ITT infecciones transmisibles por transfusión sífilis Chagas brucelosis hepatitis B C VIH HTLV",
        "Seguridad transfusional es el conjunto de medidas para garantizar la seguridad de transfusiones",
        "NAT es la técnica de amplificación de ácidos nucleicos que reduce plazos de diferimiento en tatuajes",
        "Aféresis es la extracción de un componente específico plasma plaquetas requiere donantes de 18 a 65 años",
        "HEMO 3 es la planilla confidencial donde el donante indica si su sangre puede ser usada, sin ella no puede utilizarse",
        "El principio de precaución indica que ante duda siempre en favor del receptor y prevalece sobre las normas",
    ],
}

# Aplanar el dict en una lista para TF-IDF, N-gramas y entrenamiento
CORPUS = [doc for seccion in _CORPUS_DICT.values() for doc in seccion]

CONSULTAS_EVALUACION = [
    {"query": "tatuaje donar sangre meses esperar", "relevantes": [0, 1]},
    {"query": "antibiotico penicilina esperar donacion", "relevantes": [3, 4]},
    {"query": "cirugia operacion esperar donar", "relevantes": [5, 6]},
    {"query": "hepatitis hiv sida donacion permanente", "relevantes": [7, 17]},
    {"query": "dengue covid fiebre esperar donar", "relevantes": [8, 9, 16]},
    {"query": "piercing esperar donacion", "relevantes": [10]},
    {"query": "diabetes hipertension donacion", "relevantes": [11, 12]},
    {"query": "edad peso requisitos donar", "relevantes": [13, 14]},
    {"query": "frecuencia donar hombres mujeres", "relevantes": [18, 19]},
    {"query": "ayunas fiebre condiciones donar", "relevantes": [14, 16]},
]

CORPUS_ENTRENAMIENTO = CORPUS + [
    "me hice un tatuaje hace 1 mes",
    "me hice un tatuaje hace 2 meses",
    "me hice un tatuaje hace 3 meses",
    "me hice un tatuaje hace 6 meses",
    "me hice un tatuaje hace un año",
    "puedo donar sangre con tatuaje",
    "quiero donar sangre tomé antibióticos",
    "tuve una operación hace dos meses",
    "tuve dengue hace 15 días",
    "tengo diabetes puedo donar sangre",
    "cuánto tiempo después de un piercing puedo donar",
]

# ── MODELOS ───────────────────────────────────────────────────────────────────
modelo = ModeloNgramas(k=1.0)
modelo.entrenar(CORPUS_ENTRENAMIENTO)

nlp = NLPProcessor()

# ── DB ────────────────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect("donar.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS corpus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texto TEXT UNIQUE,
            fecha_carga TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS consultas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texto TEXT,
            resultado TEXT,
            motivo TEXT,
            fecha TEXT,
            perplejidad REAL,
            score REAL
        )
    """)

    # Agrega columnas nuevas si no existen (migración no destructiva)
    columnas_nuevas = [
        ("texto_transcripto", "TEXT"),
        ("intencion", "TEXT"),
        ("entidades", "TEXT"),
        ("score_ir", "REAL"),
        ("tiempo_respuesta_ms", "REAL"),
        ("origen", "TEXT"),
    ]
    c.execute("PRAGMA table_info(consultas)")
    existentes = {row[1] for row in c.fetchall()}
    for col, tipo in columnas_nuevas:
        if col not in existentes:
            c.execute(f"ALTER TABLE consultas ADD COLUMN {col} {tipo}")

    c.execute("""
        CREATE TABLE IF NOT EXISTS metricas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            tipo TEXT,
            clave TEXT,
            valor REAL
        )
    """)

    for doc in CORPUS:
        c.execute(
            "INSERT OR IGNORE INTO corpus (texto, fecha_carga) VALUES (?, ?)",
            (doc, datetime.now().isoformat()),
        )

    conn.commit()
    conn.close()

init_db()

# ── ÍNDICE TF-IDF — carga persistida o construye y guarda ────────────────────
INDICE_PATH = "indice_tfidf.json"

buscador = MotorBusqueda()
if not buscador.cargar_indice(INDICE_PATH):
    buscador.construir_indice(CORPUS)
    buscador.guardar_indice(INDICE_PATH)

metricas_ir = buscador.evaluar(CONSULTAS_EVALUACION)

# Umbral de perplejidad: si PP supera este valor se considera fuera de dominio
PP_UMBRAL = 60.0

# ── ENDPOINTS ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"mensaje": "DONAR-APP funcionando"}

@app.get("/init_db")
def reinit_db():
    init_db()
    return {"mensaje": "DB lista"}

# ── CONSULTA ──────────────────────────────────────────────────────────────────
@app.post("/consulta")
def consulta(data: dict):
    t0 = datetime.now()
    texto = data.get("texto", "").strip()
    origen = data.get("origen", "texto")  # "texto" | "voz"
    texto_transcripto = data.get("texto_transcripto", "")

    entidades = nlp.extraer_entidades(texto)
    tokens = nlp.tokenizar(texto)
    pos = nlp.pos_tag(tokens)
    intencion = nlp.detectar_intencion(texto)
    pp = modelo.perplejidad(texto)

    resultados_ir = buscador.buscar(texto)
    score_ir = resultados_ir[0][1] if resultados_ir else 0.0
    snippets = [{"doc": r[0][:80], "score": r[1], "snippet": r[2]} for r in resultados_ir[:3]]

    # ── Perplejidad como funcionalidad: detección de anomalías ──────────────
    fuera_de_dominio = pp > PP_UMBRAL
    alerta_pp = (
        "Tu consulta parece estar fuera del dominio de donación de sangre. "
        "Intentá describir tu situación médica con más detalle."
        if fuera_de_dominio else None
    )

    regla = evaluar(texto)
    tipo = regla["resultado"]
    respuesta = regla["mensaje"]
    if fuera_de_dominio and tipo == "info":
        tipo = "fuera_de_dominio"
        respuesta = alerta_pp
    elif tipo == "info" and score_ir >= 0.10 and resultados_ir:
        respuesta = resultados_ir[0][0]
        tipo = "corpus"

    dt_ms = (datetime.now() - t0).total_seconds() * 1000
    entidades_str = str(entidades)
    fecha = datetime.now().isoformat()

    conn = get_db()
    c = conn.cursor()
    c.execute(
        """INSERT INTO consultas
           (texto, texto_transcripto, resultado, motivo, intencion, entidades,
            fecha, perplejidad, score_ir, tiempo_respuesta_ms, origen)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (texto, texto_transcripto, tipo, respuesta, intencion, entidades_str,
         fecha, pp, score_ir, round(dt_ms, 2), origen),
    )
    conn.commit()
    conn.close()

    return {
        "pregunta": texto,
        "respuesta": respuesta,
        "tipo": tipo,
        "opciones": regla.get("opciones", []),
        "intencion": intencion,
        "entidades": entidades,
        "tokens": tokens,
        "pos": pos,
        "perplejidad": round(pp, 2),
        "fuera_de_dominio": fuera_de_dominio,
        "alerta_pp": alerta_pp,
        "score_ir": round(score_ir, 4),
        "snippets": snippets,
        "tiempo_ms": round(dt_ms, 2),
    }

# ── TTS ───────────────────────────────────────────────────────────────────────
@app.get("/tts")
def tts(texto: str = Query(..., min_length=1)):
    tts_obj = gTTS(text=texto, lang="es", tld="com.ar")
    buf = io.BytesIO()
    tts_obj.write_to_fp(buf)
    buf.seek(0)
    return StreamingResponse(buf, media_type="audio/mpeg")

# ── NGRAMAS ───────────────────────────────────────────────────────────────────
@app.get("/ngramas/tabla_bigramas")
def tabla_bigramas(top_n: int = 10, k: float = 1.0):
    modelo.k = k
    return {"tabla": modelo.tabla_bigramas(top_n)}

@app.get("/ngramas/tabla_trigramas")
def tabla_trigramas(top_n: int = 10, k: float = 1.0):
    modelo.k = k
    return {"tabla": modelo.tabla_trigramas(top_n)}

@app.get("/ngramas/perplejidad")
def ngramas_perplejidad(texto: str = Query(..., min_length=1), k: float = 1.0):
    modelo.k = k
    pp = modelo.perplejidad(texto)
    return {"perplejidad": round(pp, 2), "fuera_de_dominio": pp > PP_UMBRAL}

@app.get("/ngramas/siguiente")
def ngramas_siguiente(palabra: str = Query(..., min_length=1), top_n: int = 6, k: float = 1.0):
    modelo.k = k
    palabra = palabra.lower().strip()
    siguientes = modelo.bigramas.get(palabra, {})
    V = len(modelo.vocab)
    resultados = []
    for sig, cnt in siguientes.items():
        prob = (cnt + modelo.k) / (modelo.unigramas[palabra] + modelo.k * V)
        resultados.append({"palabra": sig, "prob": round(prob, 6), "conteo": cnt})
    resultados.sort(key=lambda x: x["prob"], reverse=True)
    return {"contexto": palabra, "siguientes": resultados[:top_n]}

@app.get("/ngramas/generar")
def ngramas_generar(inicio: str = Query(..., min_length=1), max_palabras: int = 12, k: float = 1.0):
    import random
    modelo.k = k
    palabras = inicio.lower().strip().split()
    for _ in range(max_palabras):
        ultima = palabras[-1]
        siguientes = modelo.bigramas.get(ultima, {})
        if not siguientes:
            break
        opciones = [w for w in siguientes if w != "</s>"]
        if not opciones:
            break
        pesos = [siguientes[w] for w in opciones]
        siguiente = random.choices(opciones, weights=pesos, k=1)[0]
        palabras.append(siguiente)
        if len(palabras) >= max_palabras:
            break
    return {"generado": " ".join(palabras)}

# ── BÚSQUEDA ──────────────────────────────────────────────────────────────────
@app.get("/buscar")
def buscar(q: str = Query(..., min_length=1), top_k: int = 5):
    resultados = buscador.buscar(q, top_k)
    return [{"doc": r[0], "score": r[1], "snippet": r[2]} for r in resultados]

@app.get("/ir/metricas")
def ir_metricas():
    return metricas_ir

# ── STATS ─────────────────────────────────────────────────────────────────────
@app.get("/stats")
def stats():
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM consultas")
    total = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM consultas WHERE resultado='apto'")
    aptos = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM consultas WHERE resultado='no_apto_temporal'")
    no_aptos = c.fetchone()[0]

    c.execute("SELECT AVG(perplejidad) FROM consultas")
    pp_promedio = c.fetchone()[0] or 0

    c.execute("SELECT AVG(tiempo_respuesta_ms) FROM consultas")
    tiempo_promedio = c.fetchone()[0] or 0

    c.execute("SELECT AVG(score_ir) FROM consultas")
    score_promedio = c.fetchone()[0] or 0

    conn.close()

    return {
        "total": total,
        "aptos": aptos,
        "no_aptos": no_aptos,
        "pp_promedio": round(pp_promedio, 2),
        "tiempo_promedio_ms": round(tiempo_promedio, 2),
        "score_ir_promedio": round(score_promedio, 4),
    }

@app.get("/stats_diario")
def stats_diario():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT substr(fecha, 1, 10) as dia, COUNT(*)
        FROM consultas GROUP BY dia ORDER BY dia
    """)
    data = c.fetchall()
    conn.close()
    return [{"dia": d[0], "total": d[1]} for d in data]

@app.get("/stats_tipos")
def stats_tipos():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT resultado, COUNT(*) FROM consultas GROUP BY resultado")
    data = c.fetchall()
    conn.close()
    return [{"tipo": d[0], "total": d[1]} for d in data]

@app.get("/stats_top_consultas")
def stats_top_consultas(limit: int = 10):
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT texto, COUNT(*) as cnt
        FROM consultas
        GROUP BY texto
        ORDER BY cnt DESC
        LIMIT ?
    """, (limit,))
    data = c.fetchall()
    conn.close()
    return [{"texto": d[0], "total": d[1]} for d in data]

@app.get("/historial")
def historial(limit: int = 20):
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT id, texto, resultado, motivo, intencion, fecha, perplejidad, score_ir, tiempo_respuesta_ms, origen
        FROM consultas ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/corpus")
def corpus():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, texto FROM corpus")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/palabras_frecuentes")
def palabras_frecuentes(top_n: int = 30):
    """Términos más frecuentes del corpus (sin stopwords) para nube de palabras."""
    return buscador.frecuencia_terminos(top_n)

@app.get("/stats/completo")
def stats_completo():
    """Stats globales + WER promedio + métricas IR para el dashboard."""
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM consultas")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM consultas WHERE resultado='apto'")
    aptos = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM consultas WHERE resultado='no_apto_temporal'")
    no_aptos = c.fetchone()[0]
    c.execute("SELECT AVG(perplejidad) FROM consultas")
    pp_promedio = c.fetchone()[0] or 0
    c.execute("SELECT AVG(tiempo_respuesta_ms) FROM consultas")
    tiempo_promedio = c.fetchone()[0] or 0
    c.execute("SELECT AVG(score_ir) FROM consultas")
    score_promedio = c.fetchone()[0] or 0

    # WER promedio (última evaluación por frase)
    c.execute("SELECT clave, valor FROM metricas WHERE tipo='wer' ORDER BY id DESC")
    rows_wer = c.fetchall()
    conn.close()

    vistos: set = set()
    ultimas_wer = []
    for clave, valor in rows_wer:
        if clave not in vistos:
            vistos.add(clave)
            ultimas_wer.append(valor)
    wer_promedio = sum(ultimas_wer) / len(ultimas_wer) if ultimas_wer else None

    return {
        "total": total,
        "aptos": aptos,
        "no_aptos": no_aptos,
        "pp_promedio": round(pp_promedio, 2),
        "tiempo_promedio_ms": round(tiempo_promedio, 2),
        "score_ir_promedio": round(score_promedio, 4),
        "wer_promedio_pct": round(wer_promedio * 100, 2) if wer_promedio is not None else None,
        "frases_wer_evaluadas": len(ultimas_wer),
        "ir": metricas_ir["promedio"],
    }

# ── WER ───────────────────────────────────────────────────────────────────────

@app.get("/wer/frases")
def wer_frases():
    return [{"id": i, "frase": f} for i, f in enumerate(FRASES_PRUEBA)]

@app.post("/wer/evaluar")
def wer_evaluar(data: dict):
    """
    Recibe: {"referencia": str, "hipotesis": str, "frase_id": int}
    Guarda en metricas y retorna el WER.
    """
    ref = data.get("referencia", "")
    hip = data.get("hipotesis", "")
    frase_id = data.get("frase_id", -1)

    resultado = calcular_wer(ref, hip)

    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO metricas (fecha, tipo, clave, valor) VALUES (?, ?, ?, ?)",
        (datetime.now().isoformat(), "wer", f"frase_{frase_id}", resultado["wer"]),
    )
    conn.commit()
    conn.close()

    return {**resultado, "referencia": ref, "hipotesis": hip, "frase_id": frase_id}

@app.get("/wer/resumen")
def wer_resumen():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT clave, valor FROM metricas WHERE tipo='wer' ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    # Solo la última evaluación por frase
    vistos = set()
    ultimas = []
    for clave, valor in rows:
        if clave not in vistos:
            vistos.add(clave)
            ultimas.append({"frase_id": clave, "wer": valor})

    return {**resumen_wer([{"wer": r["wer"]} for r in ultimas]), "detalle": ultimas}

# ── WHISPER (ASR offline) ─────────────────────────────────────────────────────
_whisper_model = None

def _get_whisper():
    global _whisper_model
    if _whisper_model is None:
        import whisper
        _whisper_model = whisper.load_model("tiny")  # tiny: rápido, ~72MB
    return _whisper_model

@app.post("/whisper")
async def whisper_transcribe(audio: UploadFile = File(...)):
    contenido = await audio.read()
    sufijo = os.path.splitext(audio.filename or "audio.webm")[1] or ".webm"
    with tempfile.NamedTemporaryFile(delete=False, suffix=sufijo) as tmp:
        tmp.write(contenido)
        ruta = tmp.name
    try:
        modelo_w = _get_whisper()
        resultado = modelo_w.transcribe(ruta, language="es")
        texto = resultado["text"].strip()
    finally:
        os.remove(ruta)
    return {"texto": texto}
