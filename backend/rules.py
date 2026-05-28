import re
from nlp import NLPProcessor

_nlp = NLPProcessor()


def _levenshtein(a: str, b: str) -> int:
    if len(a) > len(b):
        a, b = b, a
    dp = list(range(len(a) + 1))
    for c in b:
        prev, dp[0] = dp[0], dp[0] + 1
        for i, ca in enumerate(a):
            prev, dp[i + 1] = dp[i + 1], min(dp[i] + 1, dp[i + 1] + 1, prev + (ca != c))
    return dp[-1]


def _fuzzy(texto: str, keywords: list, umbral: int = 2) -> bool:
    """True si algún token del texto está a ≤ umbral ediciones de algún keyword."""
    for token in texto.split():
        if len(token) < 4:
            continue
        for kw in keywords:
            if abs(len(token) - len(kw)) <= umbral and _levenshtein(token, kw) <= umbral:
                return True
    return False


def _meses_texto(meses: float) -> str:
    if meses >= 1:
        m = round(meses)
        return f"{m} mes{'es' if m != 1 else ''}"
    dias = round(meses * 30)
    return f"{dias} días"


def _apto(msg):   return {"resultado": "apto",               "mensaje": msg}
def _temp(msg):   return {"resultado": "no_apto_temporal",   "mensaje": msg}
def _perm(msg):   return {"resultado": "no_apto_permanente", "mensaje": msg}
def _consul(msg, opciones=None): return {"resultado": "consultar", "mensaje": msg, "opciones": opciones or []}
def _info(msg):   return {"resultado": "info",               "mensaje": msg}


def _evaluar_tiempo(tiempo_meses, espera_meses, nombre_condicion):
    if tiempo_meses is None:
        return _temp(
            f"Después de {nombre_condicion} debés esperar "
            f"{_meses_texto(espera_meses)} antes de donar."
        )
    if tiempo_meses >= espera_meses:
        return _apto(
            f"Con {_meses_texto(tiempo_meses)} desde {nombre_condicion} "
            f"ya podrías donar. Confirmalo en el centro de donación."
        )
    faltan = round(espera_meses - tiempo_meses, 1)
    return _temp(
        f"Después de {nombre_condicion} debés esperar {_meses_texto(espera_meses)}. "
        f"Te faltan aproximadamente {_meses_texto(faltan)} más."
    )


def evaluar(texto: str) -> dict:
    texto = _nlp.normalizar_coloquialismos(texto)
    entidades = _nlp.extraer_entidades(texto)
    _, tiempo_meses, peso, edad = _nlp.interpretar(entidades)
    t = texto.lower()

    # ── RESPUESTA SIN CONTEXTO (solo sí / no / modismo) ──────────────────────
    if t.strip() in ("sí", "si", "no"):
        return _consul(
            "Entendí tu respuesta, pero necesito más contexto para ayudarte. "
            "Contame tu situación completa. Por ejemplo: "
            "'Me hice un tatuaje hace 2 meses, ¿puedo donar?' o "
            "'Tomo antibióticos, ¿tengo que esperar?'",
            opciones=[
                "tatuaje o piercing",
                "medicamento o vacuna",
                "enfermedad o cirugía",
                "requisitos para donar",
            ],
        )

    # ── PESO ─────────────────────────────────────────────────────────────────
    if peso is not None or any(k in t for k in ["peso", "kg", "kilo", "kilos", "pesar"]):
        if peso is not None:
            if peso < 50:
                return _perm(f"Con {peso} kg no cumplís el peso mínimo de 50 kg para donar.")
            return _apto(f"Con {peso} kg cumplís el requisito de peso mínimo (50 kg).")
        return _info("Para donar necesitás pesar al menos 50 kg.")

    # ── EDAD ──────────────────────────────────────────────────────────────────
    if edad is not None or any(k in t for k in ["edad", "cuántos años", "cuantos años"]):
        if edad is not None:
            if edad < 16:
                return _perm(f"Con {edad} años no podés donar. La edad mínima es 16 años.")
            if edad in (16, 17):
                return _temp(
                    f"Con {edad} años podés donar, pero solo cada 6 meses "
                    f"(máximo 2 veces por año). Necesitás autorización del centro."
                )
            if edad > 65:
                return _consul(
                    f"Con {edad} años superás el rango habitual (hasta 65). "
                    f"Podés donar presentando certificado de tu médico de cabecera."
                )
            return _apto(f"Con {edad} años cumplís el requisito de edad para donar.")
        return _info(
            "La edad para donar es entre 16 y 65 años. "
            "Los mayores de 65 pueden donar con certificado médico."
        )

    # ── AYUNAS ────────────────────────────────────────────────────────────────
    if any(k in t for k in ["ayuno", "ayunas", "en ayunas", "sin comer", "comer antes"]):
        return _info(
            "No debés concurrir en ayunas. "
            "Desayuná o almorzá antes de ir al centro de donación."
        )

    # ═════════════════════════════════════════════════════════════════════════
    # HERPES
    # ═════════════════════════════════════════════════════════════════════════

    if any(k in t for k in ["herpes labial", "herpes simple", "herpes genital", "fuego en la boca"]):
        return _apto("El herpes simple (labial o genital) no genera diferimiento. Podés donar.")

    if any(k in t for k in ["herpes zoster", "herpes zóster", "culebrilla"]):
        return _evaluar_tiempo(tiempo_meses, 1, "el herpes zóster (culebrilla)")

    if "herpes" in t:
        return _consul(
            "¿Qué tipo de herpes tenés? "
            "Herpes simple (labial o genital): PODÉS DONAR sin diferimiento. "
            "Herpes zóster (culebrilla): debés esperar 1 mes.",
            opciones=["herpes simple", "herpes zóster"],
        )

    # ═════════════════════════════════════════════════════════════════════════
    # TALASEMIA
    # ═════════════════════════════════════════════════════════════════════════

    if "talasemia" in t and any(k in t for k in ["menor", "leve", "rasgo", "portador"]):
        return _apto(
            "La talasemia menor sin anemia no genera diferimiento. "
            "Podés donar y sos candidato ideal para plaquetoaféresis."
        )

    if "talasemia" in t and any(k in t for k in ["mayor", "grave", "severa"]):
        return _perm("La talasemia mayor genera diferimiento permanente.")

    if "talasemia" in t:
        return _consul(
            "¿Es talasemia mayor o menor? "
            "Talasemia mayor: NO PODÉS DONAR (permanente). "
            "Talasemia menor sin anemia: PODÉS DONAR.",
            opciones=["talasemia menor", "talasemia mayor"],
        )

    # ═════════════════════════════════════════════════════════════════════════
    # EPILEPSIA
    # ═════════════════════════════════════════════════════════════════════════

    if "epilepsia" in t and any(k in t for k in [
        "antecedente", "sin tratamiento", "no tomo", "no toma",
        "sin medicacion", "sin medicación", "hace años", "hace mucho", "superada"
    ]):
        return _apto(
            "El antecedente de epilepsia sin tratamiento actual y sin crisis "
            "en los últimos 3 años no genera diferimiento. Podés donar."
        )

    if "epilepsia" in t and any(k in t for k in [
        "tomo", "tomando", "tratamiento", "medicacion", "medicación", "anticonvulsivante"
    ]):
        return _perm("La epilepsia en tratamiento actual genera diferimiento permanente.")

    if "epilepsia" in t:
        return _consul(
            "¿Estás en tratamiento actualmente? "
            "Epilepsia con tratamiento activo: NO PODÉS DONAR (permanente). "
            "Antecedente sin tratamiento y sin crisis en 3 años: PODÉS DONAR.",
            opciones=["epilepsia sin tratamiento", "epilepsia con tratamiento"],
        )

    # ═════════════════════════════════════════════════════════════════════════
    # TROMBOFILIA / PTI
    # ═════════════════════════════════════════════════════════════════════════

    if "trombofilia" in t:
        if any(k in t for k in ["anticoagulante", "anticoagulantes", "warfarina"]):
            return _perm(
                "La trombofilia con tratamiento anticoagulante genera diferimiento permanente "
                "(por los anticoagulantes)."
            )
        return _apto("La trombofilia sin tratamiento anticoagulante no genera diferimiento. Podés donar.")

    if any(k in t for k in ["pti", "púrpura trombocitopénica", "purpura trombocitopenica"]):
        if any(k in t for k in ["remision", "remisión", "curado", "curada", "5 años", "cinco años"]):
            return _apto(
                "La PTI en remisión curada sin recaídas por más de 5 años no genera diferimiento. "
                "Podés donar."
            )
        return _consul(
            "La PTI activa o reciente genera diferimiento. "
            "Si estás en remisión hace más de 5 años sin recaídas, podés donar.",
            opciones=["pti en remisión hace 5 años", "pti activa reciente"],
        )

    # ═════════════════════════════════════════════════════════════════════════
    # CARDIOPATÍA CONGÉNITA / FIBRILACIÓN AURICULAR
    # ═════════════════════════════════════════════════════════════════════════

    if re.search(r'\bcia\b', t) or re.search(r'\bciv\b', t) or "cardiopatia congenita" in t or "cardiopatía congénita" in t:
        if any(k in t for k in ["operad", "corregid", "cerrad"]):
            return _apto(
                "La cardiopatía congénita CIA/CIV operada no genera diferimiento. Podés donar."
            )
        return _consul(
            "La cardiopatía congénita CIA/CIV operada no difiere. "
            "Consultá si aún no fue operada.",
            opciones=["cardiopatía congénita operada"],
        )

    if any(k in t for k in ["fibrilacion auricular", "fibrilación auricular"]):
        if any(k in t for k in ["cardiologo", "cardiólogo", "autorización", "autorizacion"]):
            return _consul(
                "Con fibrilación auricular podés donar SOLO con autorización escrita de tu cardiólogo. "
                "Presentala en el centro de donación."
            )
        return _perm(
            "La fibrilación auricular genera diferimiento permanente. "
            "Excepción: podés donar con autorización escrita de tu cardiólogo."
        )

    # ═════════════════════════════════════════════════════════════════════════
    # ASMA
    # ═════════════════════════════════════════════════════════════════════════

    if "asma" in t:
        if any(k in t for k in ["severo", "severa", "grave"]):
            return _perm("El asma severo con broncodilatadores diarios genera diferimiento permanente.")

        if any(k in t for k in ["corticoides", "cortisona", "prednisona", "dexametasona"]):
            return _evaluar_tiempo(tiempo_meses, 0.5, "el asma leve con corticoides sistémicos")

        if any(k in t for k in ["leve", "controlado", "controlada", "mantenimiento"]):
            return _apto(
                "El asma leve en tratamiento de mantenimiento sin corticoides orales "
                "no genera diferimiento. Podés donar."
            )

        return _consul(
            "¿Es asma severo o leve? "
            "Severo con broncodilatadores diarios: NO PODÉS DONAR (permanente). "
            "Leve sin corticoides orales: PODÉS DONAR. "
            "Leve con corticoides sistémicos recientes: esperar 15 días.",
            opciones=["asma severo", "asma leve sin corticoides", "asma leve con corticoides"],
        )

    # ═════════════════════════════════════════════════════════════════════════
    # ITT — INFECCIONES TRANSMISIBLES POR TRANSFUSIÓN
    # ═════════════════════════════════════════════════════════════════════════

    if "chagas" in t:
        return _perm("El Chagas confirmado genera diferimiento permanente.")

    if "brucelosis" in t:
        return _perm("La Brucelosis confirmada genera diferimiento permanente.")

    if any(k in t for k in ["sifilis", "sífilis"]) and "vacun" not in t:
        return _perm("La Sífilis confirmada genera diferimiento permanente.")

    if any(k in t for k in ["vih", "hiv", "sida", "aids"]):
        return _perm("El VIH/SIDA genera diferimiento permanente.")

    if "htlv" in t:
        return _perm("El HTLV I o II genera diferimiento permanente.")

    # ═════════════════════════════════════════════════════════════════════════
    # HEPATITIS
    # ═════════════════════════════════════════════════════════════════════════

    if any(k in t for k in ["hepatitis b", "hepatitis c", "hbsag", "hvc", "hvb"]) and "vacun" not in t:
        return _perm("La Hepatitis B o C confirmada genera diferimiento permanente.")

    if "hepatitis a" in t and "vacun" not in t:
        return _consul(
            "La hepatitis A resuelta no genera diferimiento permanente. "
            "Consultá en el centro según el tiempo transcurrido desde la curación."
        )

    if "hepatitis" in t and "vacun" not in t:
        return _consul(
            "¿Es hepatitis A, B o C? "
            "Hepatitis B o C confirmada: NO PODÉS DONAR (permanente). "
            "Hepatitis A resuelta: no genera diferimiento permanente.",
            opciones=["hepatitis a", "hepatitis b", "hepatitis c"],
        )

    # ═════════════════════════════════════════════════════════════════════════
    # ANTIPSICÓTICOS / ANTICOAGULANTES / BETABLOQUEANTES / ANTICONVULSIVANTES
    # ═════════════════════════════════════════════════════════════════════════

    if any(k in t for k in ["quetiapina", "risperidona", "olanzapina", "haloperidol", "clozapina", "aripiprazol"]):
        return _perm("Los antipsicóticos generan diferimiento permanente.")

    if any(k in t for k in ["anticoagulante", "warfarina", "acenocumarol", "rivaroxaban", "apixaban"]):
        return _perm("Los anticoagulantes generan diferimiento permanente.")

    if any(k in t for k in ["betabloqueante", "atenolol", "propranolol", "metoprolol", "bisoprolol"]):
        if any(k in t for k in ["cefalea", "migraña", "dolor de cabeza"]):
            return _apto(
                "Los betabloqueantes para cefaleas/migraña no generan diferimiento, "
                "siempre que la frecuencia cardíaca sea mayor a 60/min."
            )
        if any(k in t for k in ["bradicardia", "fc baja", "frecuencia baja", "menos de 60", "menor a 60"]):
            return _perm(
                "Los betabloqueantes con frecuencia cardíaca menor a 60/min "
                "generan diferimiento permanente."
            )
        return _consul(
            "Con betabloqueantes el resultado depende del motivo y la frecuencia cardíaca. "
            "¿Para qué los tomás?",
            opciones=["betabloqueante para cefalea", "betabloqueante con bradicardia"],
        )

    if any(k in t for k in ["anticonvulsivante", "carbamazepina", "lamotrigina", "gabapentina", "pregabalina", "valproato"]):
        if any(k in t for k in ["epilepsia", "convulsiones", "crisis"]):
            return _perm(
                "Los anticonvulsivantes para epilepsia generan diferimiento permanente. "
                "El diferimiento es por la epilepsia, no por el medicamento."
            )
        if any(k in t for k in ["dolor", "fibromialgia", "neuropatia", "neuropatía"]):
            return _apto(
                "Los anticonvulsivantes para dolor crónico no generan diferimiento. Podés donar."
            )
        return _consul(
            "¿Para qué tomás el anticonvulsivante? "
            "Para epilepsia: NO PODÉS DONAR. Para dolor crónico: PODÉS DONAR.",
            opciones=["anticonvulsivante para epilepsia", "anticonvulsivante para dolor"],
        )

    if any(k in t for k in ["ansiolítico", "antidepresivo", "tranquilizante", "clonazepam", "alprazolam", "sertralina", "fluoxetina"]):
        return _apto("Los ansiolíticos y antidepresivos no generan diferimiento. Podés donar.")

    if any(k in t for k in ["metotrexato", "methotrexate"]):
        return _evaluar_tiempo(tiempo_meses, 3, "el tratamiento con metotrexato")

    if any(k in t for k in ["litio", "carbonato de litio"]):
        return _consul(
            "El litio en sí no genera diferimiento, pero la condición que lo requiere (trastorno bipolar severo, etc.) "
            "puede generarlo. Consultá directamente en el centro de donación.",
            opciones=["trastorno bipolar controlado"],
        )

    if any(k in t for k in ["estatina", "atorvastatina", "rosuvastatina", "simvastatina", "colesterol alto", "dislipemia"]):
        return _apto(
            "Las estatinas para el colesterol no generan diferimiento. "
            "Si el colesterol está controlado y te sentís bien, podés donar."
        )

    if any(k in t for k in ["levotiroxina", "eutirox", "tiroidea", "tiroideo", "hipotiroidismo", "hipertiroidismo", "tiroides"]):
        if any(k in t for k in ["controlado", "controlada", "normal", "tratamiento"]):
            return _apto(
                "El hipotiroidismo o hipertiroidismo controlado con medicación no genera diferimiento. Podés donar."
            )
        if any(k in t for k in ["descompensado", "descontrolado", "alto", "bajo"]):
            return _consul(
                "Si la tiroides está descompensada, diferir hasta normalizarse. "
                "Consultá en el centro de donación con valores recientes de TSH."
            )
        return _consul(
            "Las enfermedades de tiroides controladas no generan diferimiento. "
            "¿Está tu tiroides controlada con medicación?",
            opciones=["tiroides controlada con medicación", "tiroides descompensada"],
        )

    # ═════════════════════════════════════════════════════════════════════════
    # ENFERMEDADES AUTOINMUNES
    # ═════════════════════════════════════════════════════════════════════════

    if any(k in t for k in ["lupus", "les", "lupus eritematoso"]):
        if any(k in t for k in ["remision", "remisión", "controlado", "controlada", "estable"]):
            return _consul(
                "El lupus en remisión estable puede permitir la donación, "
                "pero depende del órgano comprometido y el tratamiento. "
                "Consultá en el centro de donación con tu historia clínica.",
            )
        return _perm("El lupus eritematoso sistémico activo genera diferimiento permanente.")

    if any(k in t for k in ["artritis reumatoide", "artritis reumatoidea"]):
        if any(k in t for k in ["metotrexato", "leflunomida", "rituximab", "infliximab", "adalimumab", "etanercept", "biologico", "biológico"]):
            return _evaluar_tiempo(tiempo_meses, 3, "el tratamiento biológico o metotrexato para artritis reumatoide")
        if any(k in t for k in ["ibuprofeno", "naproxeno", "aine", "antiinflamatorio"]):
            return _apto(
                "La artritis reumatoide tratada solo con AINEs (ibuprofeno, naproxeno) "
                "no genera diferimiento. Podés donar."
            )
        return _consul(
            "¿Qué tratamiento tomás para la artritis reumatoide? "
            "Solo AINEs (ibuprofeno, naproxeno): PODÉS DONAR. "
            "Metotrexato o biológicos: diferimiento de 3 meses.",
            opciones=["artritis con AINEs", "artritis con metotrexato o biológico"],
        )

    if any(k in t for k in ["esclerosis multiple", "esclerosis múltiple"]):
        if any(k in t for k in ["interferon", "interferón", "natalizumab", "ocrelizumab", "siponimod", "fingolimod"]):
            return _perm("Los tratamientos modificadores de la esclerosis múltiple generan diferimiento permanente.")
        return _consul(
            "La esclerosis múltiple sin tratamiento modificador activo puede permitir donar "
            "en períodos de remisión. Consultá en el centro con tu historia clínica.",
        )

    if any(k in t for k in ["fibromialgia"]):
        return _apto(
            "La fibromialgia sin tratamiento inmunosupresor no genera diferimiento. Podés donar."
        )

    # ═════════════════════════════════════════════════════════════════════════
    # HEMOFILIA / INSUFICIENCIA RENAL / TRASPLANTE
    # ═════════════════════════════════════════════════════════════════════════

    if any(k in t for k in ["hemofilia", "hemofilico", "hemofílico", "factor viii", "factor ix"]):
        return _perm("La hemofilia genera diferimiento permanente.")

    if any(k in t for k in ["dialisis", "diálisis", "hemodiálisis", "hemodialisis", "peritoneal"]):
        return _perm("La diálisis genera diferimiento permanente para donar sangre.")

    if any(k in t for k in ["insuficiencia renal", "renal cronico", "renal crónico", "nefropatia", "nefropatía"]):
        return _consul(
            "La insuficiencia renal sin diálisis requiere evaluación médica antes de donar. "
            "Consultá en el centro de donación con tus análisis recientes de función renal (creatinina, urea)."
        )

    if any(k in t for k in ["trasplante", "transplante"]):
        if any(k in t for k in ["medula", "médula", "progenitores", "hematopoyetico", "hematopoyético"]):
            return _evaluar_tiempo(tiempo_meses, 24, "el trasplante de médula ósea/progenitores hematopoyéticos")
        return _perm(
            "El trasplante de órganos sólidos (riñón, hígado, corazón, etc.) "
            "genera diferimiento permanente por el tratamiento inmunosupresor."
        )

    # ═════════════════════════════════════════════════════════════════════════
    # CONDUCTAS DE RIESGO
    # ═════════════════════════════════════════════════════════════════════════

    if any(k in t for k in ["droga", "drogas", "heroina", "heroína", "cocaina", "cocaína"]):
        if any(k in t for k in ["inyectable", "inyectado", "jeringa", "endovenoso", "intravenoso", "pinchado"]):
            return _perm("El uso de drogas inyectables genera diferimiento permanente.")
        return _consul(
            "¿Las drogas fueron inyectables (jeringa/aguja)? "
            "Si fueron inyectables: NO PODÉS DONAR (permanente). "
            "Si fueron por otra vía: consultá en el centro según el tiempo transcurrido.",
            opciones=["drogas inyectables", "drogas no inyectables"],
        )

    if any(k in t for k in ["relacion sexual", "relación sexual", "hsh", "sexo sin proteccion", "sexo sin protección"]):
        return _evaluar_tiempo(tiempo_meses, 4, "la última relación sexual de riesgo sin protección")

    # ═════════════════════════════════════════════════════════════════════════
    # DIABETES
    # ═════════════════════════════════════════════════════════════════════════

    _kw_t1 = [
        "insulina", "insulinodependiente",
        "diabetes tipo 1", "diabetes 1",
        "diabetico tipo 1", "diabético tipo 1",
        "diabetica tipo 1", "diabética tipo 1",
        "tengo diabetes tipo 1",
    ]
    if any(k in t for k in _kw_t1):
        return _perm("La diabetes tipo 1 insulinodependiente genera diferimiento permanente.")

    _kw_t2 = [
        "diabetes tipo 2", "diabetes 2",
        "diabetico tipo 2", "diabético tipo 2",
        "diabetica tipo 2", "diabética tipo 2",
        "tengo diabetes tipo 2",
    ]
    if any(k in t for k in _kw_t2):
        return _apto(
            "La diabetes tipo 2 no insulinodependiente no genera diferimiento por sí sola. "
            "Podés donar si está controlada, los valores del día son normales "
            "y no tomás insulina."
        )

    if any(k in t for k in ["diabetes", "diabetico", "diabético", "diabetica", "diabética"]):
        return _consul(
            "¿Es diabetes tipo 1 o tipo 2? "
            "Tipo 1 insulinodependiente: NO PODÉS DONAR (permanente). "
            "Tipo 2 no insulinodependiente: PODÉS DONAR si está controlada.",
            opciones=["diabetes tipo 1", "diabetes tipo 2"],
        )

    # ═════════════════════════════════════════════════════════════════════════
    # CÁNCER / HORMONA DE CRECIMIENTO
    # ═════════════════════════════════════════════════════════════════════════

    if any(k in t for k in ["cancer", "cáncer", "oncológico", "quimioterapia", "radioterapia", "leucemia", "linfoma"]):
        return _perm("El diagnóstico de cáncer y los tratamientos oncológicos generan diferimiento permanente.")

    if any(k in t for k in ["hormona de crecimiento", "somatropina"]):
        if "recombinante" in t:
            return _apto("La hormona de crecimiento recombinante no genera diferimiento. Podés donar.")
        return _perm("La hormona de crecimiento hipofisaria humana genera diferimiento permanente.")

    # ═════════════════════════════════════════════════════════════════════════
    # PALUDISMO / MALARIA
    # ═════════════════════════════════════════════════════════════════════════

    if any(k in t for k in ["paludismo", "malaria"]):
        if any(k in t for k in ["diagnosticado", "tuve", "positivo", "confirmado"]):
            return _perm("El diagnóstico confirmado de paludismo/malaria genera diferimiento permanente.")
        if any(k in t for k in ["vivo", "resido", "residente", "venezuela", "colombia", "brasil"]):
            return _evaluar_tiempo(tiempo_meses, 36, "residir en zona endémica de paludismo")
        return _evaluar_tiempo(tiempo_meses, 3, "el viaje a zona endémica de paludismo")

    # ═════════════════════════════════════════════════════════════════════════
    # PREP / PEP / ART
    # ═════════════════════════════════════════════════════════════════════════

    if any(k in t for k in ["prep", "pep", "profilaxis vih", "antirretroviral"]):
        if any(k in t for k in ["inyectable", "inyectado", "pinchado"]):
            return _evaluar_tiempo(tiempo_meses, 24, "el uso inyectable de PREP/PEP/ART")
        return _evaluar_tiempo(tiempo_meses, 6, "el uso oral de PREP/PEP")

    # ═════════════════════════════════════════════════════════════════════════
    # TATUAJE / PIERCING / BOTOX / ACUPUNTURA
    # ═════════════════════════════════════════════════════════════════════════

    if any(k in t for k in ["tatuaje", "tattoo", "maquillaje permanente"]):
        if any(k in t for k in ["nat", "ácidos nucleicos"]):
            return _evaluar_tiempo(tiempo_meses, 6, "el tatuaje (con NAT)")
        if any(k in t for k in ["propio", "descartable", "estéril", "esteril"]):
            return _evaluar_tiempo(tiempo_meses, 6, "el tatuaje con material propio descartable")
        return _evaluar_tiempo(tiempo_meses, 12, "el tatuaje")

    if "piercing" in t:
        return _evaluar_tiempo(tiempo_meses, 6, "el piercing")

    if any(k in t for k in ["botox", "relleno", "plasma rico en plaquetas", "escarificacion"]):
        if any(k in t for k in ["nat", "ácidos nucleicos"]):
            return _evaluar_tiempo(tiempo_meses, 3, "el tratamiento cosmético invasivo (con NAT)")
        return _evaluar_tiempo(tiempo_meses, 6, "el tratamiento cosmético invasivo")

    if "acupuntura" in t:
        if any(k in t for k in ["propio", "descartable"]):
            return _evaluar_tiempo(tiempo_meses, 6, "la acupuntura con material propio")
        return _evaluar_tiempo(tiempo_meses, 12, "la acupuntura")

    # ═════════════════════════════════════════════════════════════════════════
    # VACUNAS
    # ═════════════════════════════════════════════════════════════════════════

    _vacunas_vivas = [
        "fiebre amarilla", "varicela", "triple viral", "sarampion", "sarampión",
        "rubéola", "rubeola", "paperas", "bcg", "rotavirus", "sabin", "polio oral"
    ]
    for v in _vacunas_vivas:
        if v in t:
            return _evaluar_tiempo(tiempo_meses, 1, f"la vacuna contra {v}")

    if any(k in t for k in ["hepatitis b"]) and any(k in t for k in ["vacun", "dosis"]):
        if any(k in t for k in ["exposicion", "exposición", "contagio", "posexposicion"]):
            return _evaluar_tiempo(tiempo_meses, 12, "la vacuna antihepatitis B posexposición")
        return _apto("La vacuna antihepatitis B preventiva no genera diferimiento. Podés donar.")

    if "hepatitis a" in t and any(k in t for k in ["vacun", "dosis"]):
        if any(k in t for k in ["exposicion", "exposición", "contagio", "posexposicion"]):
            return _evaluar_tiempo(tiempo_meses, 1.5, "la vacuna antihepatitis A posexposición")
        return _apto("La vacuna antihepatitis A preventiva no genera diferimiento. Podés donar.")

    if any(k in t for k in ["antirrábica", "antirrabica", "rabia"]) and any(k in t for k in ["vacun", "dosis"]):
        if any(k in t for k in ["mordedura", "mordio", "mordió"]):
            return _evaluar_tiempo(tiempo_meses, 12, "la vacuna antirrábica post-mordedura")
        return _apto("La vacuna antirrábica preventiva (sin mordedura) no genera diferimiento. Podés donar.")

    if any(k in t for k in ["dengue"]) and any(k in t for k in ["vacun", "dosis"]):
        return _evaluar_tiempo(tiempo_meses, 1, "la vacuna contra el dengue")

    if any(k in t for k in ["vacun", "vacuna", "dosis", "refuerzo"]):
        if any(k in t for k in ["influenza", "gripe"]):
            return _apto("La vacuna contra la gripe/influenza no genera diferimiento. Podés donar.")
        if any(k in t for k in ["tetano", "tétano", "tétanos"]):
            return _apto("La vacuna contra el tétanos no genera diferimiento. Podés donar.")
        if any(k in t for k in ["neumococo", "hpv", "meningitis", "hepatitis"]):
            return _apto("Esa vacuna inactivada no genera diferimiento. Podés donar.")
        return _consul(
            "¿Qué vacuna te aplicaste? "
            "Vivas (varicela, triple viral, fiebre amarilla): esperar 1 mes. "
            "Inactivadas (gripe, tétanos, neumococo, HPV): sin diferimiento.",
            opciones=[
                "vacuna varicela",
                "vacuna triple viral",
                "vacuna fiebre amarilla",
                "vacuna influenza",
                "vacuna tétano",
            ],
        )

    # ═════════════════════════════════════════════════════════════════════════
    # PSORIASIS
    # ═════════════════════════════════════════════════════════════════════════

    if "psoriasis" in t:
        if any(k in t for k in ["acitretina", "neotigason", "tigason"]):
            return _evaluar_tiempo(tiempo_meses, 36, "el tratamiento con Acitretina/Neotigason")
        return _evaluar_tiempo(tiempo_meses, 6, "el brote de psoriasis")

    # ═════════════════════════════════════════════════════════════════════════
    # MEDICAMENTOS ESPECÍFICOS
    # ═════════════════════════════════════════════════════════════════════════

    if any(k in t for k in ["roacutan", "isotretinoina", "isotretinoína"]):
        return _evaluar_tiempo(tiempo_meses, 1, "el tratamiento con Roacután")

    if any(k in t for k in ["acitretina", "neotigason"]):
        return _evaluar_tiempo(tiempo_meses, 36, "el tratamiento con Acitretina/Neotigason")

    if any(k in t for k in ["finasteride", "proscar", "propecia"]):
        return _evaluar_tiempo(tiempo_meses, 1, "el tratamiento con Finasteride")

    if "dutasteride" in t:
        return _evaluar_tiempo(tiempo_meses, 6, "el tratamiento con Dutasteride")

    if any(k in t for k in ["tetraciclina", "doxiciclina", "eritromicina"]):
        return _apto("Ese antibiótico no genera diferimiento. Podés donar.")

    _KW_ANTIBIOTICO = ["antibiotico", "antibiótico", "penicilina", "amoxicilina"]
    if any(k in t for k in _KW_ANTIBIOTICO) or _fuzzy(t, _KW_ANTIBIOTICO):
        return _evaluar_tiempo(tiempo_meses, 0.25, "el tratamiento con antibióticos")

    _KW_AINE = [
        "ibuprofeno", "naproxeno", "diclofenac", "diclofenaco",
        "paracetamol", "acetaminofen", "acetaminofén",
        "aspirina", "acido acetilsalicilico", "ácido acetilsalicílico",
        "aine", "antiinflamatorio",
    ]
    if any(k in t for k in _KW_AINE) or _fuzzy(t, _KW_AINE):
        return _apto(
            "El ibuprofeno, paracetamol, aspirina y otros antiinflamatorios (AINEs) "
            "no generan diferimiento para donar sangre. "
            "Si los tomás por una condición crónica (artritis, etc.), "
            "esa condición puede tener sus propias restricciones — consultá en el centro."
        )

    # ═════════════════════════════════════════════════════════════════════════
    # CIRUGÍAS
    # ═════════════════════════════════════════════════════════════════════════

    if any(k in t for k in ["bariátrica", "bariatrica", "manga gastrica", "bypass gastrico"]):
        if any(k in t for k in ["transfusion", "transfusión"]):
            return _evaluar_tiempo(tiempo_meses, 12, "la cirugía bariátrica con transfusiones")
        return _evaluar_tiempo(tiempo_meses, 6, "la cirugía bariátrica")

    if any(k in t for k in ["cirugia", "cirugía", "operacion", "operación"]):
        if any(k in t for k in ["cardiaca", "cardíaca", "corazon", "corazón"]):
            return _perm("La cirugía cardíaca genera diferimiento permanente.")
        if any(k in t for k in ["cancer", "cáncer", "tumor", "oncológica"]):
            return _perm("La cirugía por cáncer genera diferimiento permanente.")
        if any(k in t for k in ["neuro", "cerebro", "neurocirugía"]):
            return _perm("Las neurocirugías generan diferimiento permanente.")
        if any(k in t for k in ["transfusion", "transfusión"]):
            return _evaluar_tiempo(tiempo_meses, 12, "la cirugía con transfusiones")
        if any(k in t for k in ["dental", "muela", "extraccion", "extracción"]):
            if any(k in t for k in ["antibiótico", "antibiotico"]):
                return _evaluar_tiempo(tiempo_meses, 0.5, "la cirugía odontológica con antibióticos")
            return _evaluar_tiempo(tiempo_meses, 0.1, "la extracción dental")
        if any(k in t for k in ["miopía", "miopia", "cataratas", "láser", "laser"]):
            return _evaluar_tiempo(tiempo_meses, 2, "la cirugía de miopía/cataratas")
        return _evaluar_tiempo(tiempo_meses, 6, "la cirugía")

    # ═════════════════════════════════════════════════════════════════════════
    # PARTO / CESÁREA / ABORTO / EMBARAZO
    # ═════════════════════════════════════════════════════════════════════════

    if any(k in t for k in ["embarazada", "embarazo"]):
        return _perm("No podés donar sangre durante el embarazo.")

    if any(k in t for k in ["amamantando", "lactancia"]):
        return _apto(
            "La lactancia no impide donar. Podés donar a partir de los 6 meses del parto "
            "si cumplís el peso y la hemoglobina mínima."
        )

    if any(k in t for k in ["parto", "cesárea", "cesarea", "aborto"]):
        if any(k in t for k in ["transfusion", "transfusión"]):
            return _evaluar_tiempo(tiempo_meses, 12, "el parto/cesárea con transfusiones")
        return _evaluar_tiempo(tiempo_meses, 6, "el parto/cesárea/aborto")

    # ═════════════════════════════════════════════════════════════════════════
    # TRANSFUSIONES / ENDOSCOPIAS
    # ═════════════════════════════════════════════════════════════════════════

    if any(k in t for k in ["transfusion", "transfusión", "me transfundieron", "recibí sangre"]):
        return _evaluar_tiempo(tiempo_meses, 12, "haber recibido una transfusión")

    if any(k in t for k in ["endoscopia", "colonoscopia", "gastroscopia", "veda", "vcc"]):
        return _evaluar_tiempo(tiempo_meses, 6, "la endoscopía")

    # ═════════════════════════════════════════════════════════════════════════
    # ENFERMEDADES CON ESPERA ESPECÍFICA
    # ═════════════════════════════════════════════════════════════════════════

    if "dengue" in t:
        if any(k in t for k in ["hemorrágico", "hemorragico"]):
            return _evaluar_tiempo(tiempo_meses, 4, "el dengue hemorrágico")
        return _evaluar_tiempo(tiempo_meses, 1, "el dengue")

    if "mononucleosis" in t:
        return _evaluar_tiempo(tiempo_meses, 6, "la mononucleosis infecciosa")

    if "varicela" in t:
        return _evaluar_tiempo(tiempo_meses, 1, "la varicela")

    if "toxoplasmosis" in t:
        return _evaluar_tiempo(tiempo_meses, 12, "la toxoplasmosis")

    if any(k in t for k in ["tuberculosis", "tbc"]):
        return _evaluar_tiempo(tiempo_meses, 24, "la tuberculosis (luego de curación)")

    if "fiebre amarilla" in t:
        return _evaluar_tiempo(tiempo_meses, 1, "la fiebre amarilla")

    if any(k in t for k in ["covid", "coronavirus"]):
        return _evaluar_tiempo(tiempo_meses, 0.5, "el COVID-19")

    if any(k in t for k in ["gripe", "influenza"]):
        return _evaluar_tiempo(tiempo_meses, 0.25, "la gripe")

    if any(k in t for k in ["diarrea", "vómito", "vomito", "náusea", "nausea"]) and "fiebre" not in t:
        return _evaluar_tiempo(tiempo_meses, 0.5, "la diarrea u otros síntomas digestivos")

    if "fiebre" in t:
        if any(k in t for k in ["diarrea", "vómito", "vomito", "síntoma", "sintoma", "malestar"]):
            return _evaluar_tiempo(tiempo_meses, 0.5, "la fiebre o diarrea")
        return _evaluar_tiempo(tiempo_meses, 0.5, "la fiebre")

    if "anemia" in t:
        return _consul(
            "La anemia requiere evaluación. "
            "La hemoglobina mínima para donar es 12.5 g/dl. "
            "Consultá en el centro de donación."
        )

    if any(k in t for k in ["hipertension", "hipertensión", "presión alta", "presion alta"]):
        if any(k in t for k in ["controlada", "controlado", "medicada", "medicado"]):
            return _apto(
                "La hipertensión controlada con valores normales al momento de la donación "
                "no impide donar."
            )
        if any(k in t for k in ["sin controlar", "elevada", "alta hoy"]):
            return _temp(
                "Si la presión está elevada el día de la donación, diferí 1 mes "
                "y volvé cuando esté normalizada."
            )
        return _consul(
            "Si la presión está elevada el día de la donación: diferir 1 mes. "
            "Si está controlada y los valores son normales: podés donar.",
            opciones=["hipertensión controlada"],
        )

    # ═════════════════════════════════════════════════════════════════════════
    # FRECUENCIA / VIAJE / REQUISITOS GENERALES
    # ═════════════════════════════════════════════════════════════════════════

    if any(k in t for k in ["cada cuánto", "cada cuanto", "frecuencia", "cuántas veces", "cuantas veces"]):
        if any(k in t for k in ["hombre", "varón", "varon"]):
            return _info("Los hombres pueden donar cada 8 semanas (hasta 5 veces por año).")
        if any(k in t for k in ["mujer", "femenino"]):
            return _info("Las mujeres pueden donar cada 12 semanas (hasta 4 veces por año).")
        return _info(
            "Hombres: cada 8 semanas, hasta 5 veces por año. "
            "Mujeres: cada 12 semanas, hasta 4 veces por año. "
            "Jóvenes de 16-17: cada 6 meses, hasta 2 veces por año."
        )

    if any(k in t for k in ["viaje", "viajé", "visité"]):
        return _consul(
            "¿A qué zona viajaste? "
            "Zona endémica de paludismo: esperar 3 meses. "
            "Si residís allí (Venezuela, Colombia, Brasil): esperar 3 años."
        )

    if any(k in t for k in ["requisitos", "qué necesito", "que necesito", "cómo donar", "como donar", "quiero donar"]):
        return _info(
            "Requisitos: tener 16-65 años · pesar más de 50 kg · "
            "sentirse bien y sano · no ir en ayunas · "
            "temperatura menor a 37°C · hemoglobina entre 12.5 y 17 g/dl · "
            "pulso entre 60 y 100 lpm · presentar DNI."
        )

    # ── FALLBACK ──────────────────────────────────────────────────────────────
    return _info(
        "No entendí tu consulta. Podés preguntarme sobre medicamentos, enfermedades, "
        "procedimientos médicos o requisitos para donar sangre."
    )
