import re

class NLPProcessor:

    NUMEROS = {
        "un": 1, "uno": 1, "dos": 2, "tres": 3,
        "cuatro": 4, "cinco": 5, "seis": 6,
        "siete": 7, "ocho": 8, "nueve": 9, "diez": 10,
        "once": 11, "doce": 12,
    }

    STOPWORDS = {
        "me", "hice", "un", "una", "hace", "desde", "el", "la", "los", "las",
        "de", "que", "y", "en", "a", "con", "por", "para", "es", "se",
        "del", "al", "mi", "tu", "su", "tengo", "tuve", "tomar", "tome",
        "estoy", "estuve", "puedo", "quiero", "puede", "como",
    }

    TIPOS = {
        # ── procedimientos en piel ──────────────────────────────────────────
        "tatuaje": [
            "tatuaje", "tattoo", "tatuarme", "tatuajes", "maquillaje permanente",
        ],
        "piercing": ["piercing", "arito", "pendiente", "piercings"],
        "botox": [
            "botox", "relleno", "rellenos", "plasma rico en plaquetas",
            "escarificacion", "escarificación", "tratamiento cosmético",
        ],
        "acupuntura": ["acupuntura"],

        # ── medicamentos ────────────────────────────────────────────────────
        "medicamento": [
            "antibiotico", "antibiótico", "antibioticos", "antibióticos",
            "penicilina", "amoxicilina", "ibuprofeno", "pastilla", "medicamento",
            "medicacion", "medicación",
        ],
        "anticoagulante": [
            "anticoagulante", "anticoagulantes", "warfarina", "acenocumarol",
            "rivaroxaban", "apixaban",
        ],
        "betabloqueante": [
            "betabloqueante", "betabloqueantes", "atenolol", "propranolol",
            "metoprolol", "bisoprolol", "carvedilol",
        ],
        "anticonvulsivante": [
            "anticonvulsivante", "anticonvulsivantes", "carbamazepina",
            "fenitoina", "lamotrigina", "gabapentina", "pregabalina",
            "valproato", "levetiracetam",
        ],
        "antipsicótico": [
            "antipsicótico", "antipsicóticos", "quetiapina", "risperidona",
            "olanzapina", "haloperidol", "clozapina", "aripiprazol",
        ],
        "isotretinoina": [
            "roacutan", "roacutane", "isotretinoin", "isotretinoina",
            "isotretinoína", "acne", "acné",
        ],
        "acitretina": [
            "acitretina", "neotigason", "tigason",
        ],
        "finasteride": [
            "finasteride", "proscar", "propecia", "alopecia", "calvicie",
        ],
        "dutasteride": ["dutasteride", "avodart"],
        "insulina": [
            "insulina", "insulinodependiente",
            "diabetico", "diabético", "diabetica", "diabética",
            "diabetes tipo 1", "diabetes 1", "diabetico tipo 1",
            "diabetes tipo 2", "diabetes 2", "diabetico tipo 2",
        ],
        "hormona_crecimiento": [
            "hormona de crecimiento", "growth hormone", "somatropina",
        ],
        "ansiolítico": [
            "ansiolítico", "ansiolíticos", "ansiolítico", "clonazepam",
            "alprazolam", "lorazepam", "diazepam", "antidepresivo",
            "antidepresivos", "tranquilizante", "sertralina", "fluoxetina",
        ],
        "prep_pep": [
            "prep", "pep", "profilaxis vih", "profilaxis hiv",
            "art", "tratamiento antirretroviral",
        ],

        # ── enfermedades y condiciones ──────────────────────────────────────
        "enfermedad": [
            "gripe", "fiebre", "dengue", "covid", "hepatitis", "hiv", "sida",
            "diabetes", "anemia", "hipertension", "hipertensión", "cancer",
            "cáncer", "infeccion", "infección",
        ],
        "herpes": [
            "herpes", "culebrilla", "herpes labial", "herpes zoster",
            "herpes zóster", "herpes simple", "herpes genital",
        ],
        "talasemia": ["talasemia", "talasémico", "talasemico"],
        "epilepsia": [
            "epilepsia", "epiléptico", "epileptico", "convulsiones",
            "crisis epiléptica", "crisis convulsiva",
        ],
        "fibrilacion": [
            "fibrilacion auricular", "fibrilación auricular",
            "fibrilacion", "fibrilación", "arritmia",
        ],
        "psoriasis": ["psoriasis", "psoriásico", "psoriasico"],
        "asma": [
            "asma", "asmático", "asmatico", "broncoespasmo",
        ],
        "paludismo": [
            "paludismo", "malaria", "plasmodium",
        ],
        "chagas": ["chagas", "trypanosoma"],
        "hepatitis_b": ["hepatitis b", "hepatitis b"],
        "hepatitis_c": ["hepatitis c", "hepatitis c"],
        "vih_sida": ["vih", "hiv", "sida", "aids"],
        "brucelosis": ["brucelosis"],
        "sifilis": ["sifilis", "sífilis"],
        "tuberculosis": ["tuberculosis", "tbc", "koch"],
        "cancer_dx": [
            "cancer", "cáncer", "oncológico", "oncologico", "tumor maligno",
            "leucemia", "linfoma", "melanoma", "carcinoma",
        ],
        "trombofilia": ["trombofilia", "trombófilico"],
        "pti": [
            "pti", "púrpura trombocitopénica", "purpura trombocitopenica",
        ],

        # ── procedimientos / cirugías ───────────────────────────────────────
        "cirugia": [
            "cirugia", "cirugía", "operacion", "operación", "operar",
            "operé", "opere", "intervención", "intervencion", "laparoscopia",
            "laparoscopía",
        ],
        "cirugia_bariatrica": [
            "bariatrica", "bariátrica", "manga gastrica", "bypass gastrico",
            "banda gastrica", "sleeve", "manga gástrica", "bypass gástrico",
        ],
        "cardiopatia_congenita": [
            "cardiopatia congenita", "cardiopatía congénita",
            "cia", "civ", "comunicacion interauricular", "comunicación interventricular",
        ],
        "endoscopia": [
            "endoscopia", "endoscopía", "endoscopia", "colonoscopia",
            "colonoscopía", "veda", "vcc", "gastroscopia",
        ],
        "transfusion": [
            "transfusion", "transfusión", "me transfundieron", "recibí sangre",
        ],

        # ── situaciones vitales ─────────────────────────────────────────────
        "embarazo": [
            "embarazo", "embarazada", "embarazado", "lactancia",
            "amamantando", "parto", "cesarea", "cesárea", "postparto",
        ],
        "parto_reciente": [
            "tuve un bebe", "tuve un bebé", "di a luz", "parí",
        ],
        "viaje": [
            "viaje", "viajé", "viajo", "visité", "visitar",
            "africa", "tropical",
        ],

        # ── vacunas ─────────────────────────────────────────────────────────
        "vacuna": [
            "vacuna", "vacunas", "vacunado", "vacunada", "vacunarse",
            "dosis", "refuerzo",
        ],
    }

    INTENCIONES = {
        "querer_donar": [
            "puedo donar", "quiero donar", "donar sangre",
            "soy apto", "puedo ser donante",
        ],
        "consulta_tiempo": [
            "cuanto tiempo", "cuánto tiempo", "cuando puedo", "cuándo puedo",
            "cuanto falta", "cuánto falta",
        ],
        "informacion": [
            "que necesito", "qué necesito", "requisitos", "condiciones",
            "que piden", "qué piden",
        ],
    }

    VERBOS = {
        "hice", "hizo", "tuve", "tome", "tomé", "opero", "operó",
        "puedo", "quiero", "puede", "donar", "esperar",
    }
    SUSTANTIVOS = (
        set(TIPOS.keys())
        | {"sangre", "donante", "centro", "mes", "meses", "año", "años",
           "semana", "semanas", "día", "dias", "diferimiento"}
    )
    ADJETIVOS = {"apto", "sano", "enfermo", "reciente", "permanente", "temporal"}

    # Modismos y variantes coloquiales del español rioplatense
    _AFIRMACIONES = {
        "dale", "obvio", "claro", "por supuesto", "joya", "re",
        "exacto", "correcto", "afirmativo", "así es", "asi es",
        "sip", "sep", "yep", "oka", "ok", "okay", "bueno",
        "seguro", "obvio que si", "obvio que sí", "claro que si",
        "claro que sí", "por supuesto que si", "sí claro",
    }
    _NEGACIONES = {
        "nope", "nel", "nah", "para nada", "negativo",
        "de ninguna manera", "jamás", "jamas", "nanai",
        "ni en pedo", "para nada", "ni loco", "ni loca",
    }

    def normalizar_coloquialismos(self, texto: str) -> str:
        """Colapsa caracteres repetidos y mapea modismos rioplatenses."""
        texto_lower = texto.strip().lower()

        # Patrones de repetición silábica: siisisisisi / nononono / síísíísí
        if re.fullmatch(r"(s[ií]+\s*)+", texto_lower):
            return "sí"
        if re.fullmatch(r"(no+\s*)+", texto_lower):
            return "no"

        # Colapsar cualquier carácter consecutivo repetido (siii→si, nooo→no)
        texto_norm = re.sub(r"(.)\1+", r"\1", texto.strip())
        texto_lower = texto_norm.lower().strip()

        # Expresión completa es una afirmación o negación conocida
        for expr in sorted(self._AFIRMACIONES, key=len, reverse=True):
            if texto_lower == expr:
                return "sí"
        for expr in sorted(self._NEGACIONES, key=len, reverse=True):
            if texto_lower == expr:
                return "no"

        # Reemplazar modismos dentro de texto más largo
        for expr in sorted(self._AFIRMACIONES, key=len, reverse=True):
            texto_norm = re.sub(
                r"(?<!\w)" + re.escape(expr) + r"(?!\w)",
                "sí", texto_norm, flags=re.IGNORECASE,
            )
        for expr in sorted(self._NEGACIONES, key=len, reverse=True):
            texto_norm = re.sub(
                r"(?<!\w)" + re.escape(expr) + r"(?!\w)",
                "no", texto_norm, flags=re.IGNORECASE,
            )
        return texto_norm

    def tokenizar(self, texto: str) -> list[str]:
        return re.findall(r"[a-záéíóúüñ]+", texto.lower())

    def pos_tag(self, tokens: list[str]) -> list[dict]:
        resultado = []
        for t in tokens:
            if t in self.VERBOS:
                pos = "VERB"
            elif t in self.SUSTANTIVOS:
                pos = "NOUN"
            elif t in self.ADJETIVOS:
                pos = "ADJ"
            elif t in self.STOPWORDS:
                pos = "STOP"
            elif t.isdigit():
                pos = "NUM"
            else:
                pos = "OTHER"
            resultado.append({"token": t, "pos": pos})
        return resultado

    def extraer_entidades(self, texto: str) -> list[dict]:
        texto_lower = texto.lower()
        entidades = []

        for tipo, palabras_clave in self.TIPOS.items():
            for kw in palabras_clave:
                if kw in texto_lower:
                    entidades.append({"tipo": "TIPO", "valor": tipo})
                    break

        # TIEMPO: meses numérico
        m = re.search(r"(\d+)\s*(mes|meses)", texto_lower)
        if m:
            entidades.append({"tipo": "TIEMPO", "unidad": "meses", "valor": int(m.group(1))})

        # TIEMPO: meses en texto
        m = re.search(
            r"(un|uno|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce)\s*(mes|meses)",
            texto_lower,
        )
        if m:
            entidades.append({"tipo": "TIEMPO", "unidad": "meses", "valor": self.NUMEROS[m.group(1)]})

        # TIEMPO: años numérico
        m = re.search(r"(\d+)\s*(año|años)", texto_lower)
        if m:
            entidades.append({"tipo": "TIEMPO", "unidad": "meses", "valor": int(m.group(1)) * 12})

        # TIEMPO: años en texto
        m = re.search(r"(un|uno|dos|tres|cuatro|cinco)\s*(año|años)", texto_lower)
        if m:
            entidades.append({"tipo": "TIEMPO", "unidad": "meses", "valor": self.NUMEROS[m.group(1)] * 12})

        # TIEMPO: semanas
        m = re.search(r"(\d+)\s*(semana|semanas)", texto_lower)
        if m:
            entidades.append({"tipo": "TIEMPO", "unidad": "meses", "valor": round(int(m.group(1)) / 4, 1)})

        # TIEMPO: días
        m = re.search(r"(\d+)\s*(d[ií]a|dias|días)", texto_lower)
        if m:
            entidades.append({"tipo": "TIEMPO", "unidad": "meses", "valor": round(int(m.group(1)) / 30, 1)})

        # TIEMPO: expresiones relativas
        if re.search(r"\bayer\b", texto_lower):
            entidades.append({"tipo": "TIEMPO", "unidad": "meses", "valor": round(1 / 30, 2)})
        elif re.search(r"\banteayer\b", texto_lower):
            entidades.append({"tipo": "TIEMPO", "unidad": "meses", "valor": round(2 / 30, 2)})
        elif re.search(r"semana\s+pasada", texto_lower):
            entidades.append({"tipo": "TIEMPO", "unidad": "meses", "valor": 0.25})
        elif re.search(r"mes\s+pasado", texto_lower):
            entidades.append({"tipo": "TIEMPO", "unidad": "meses", "valor": 1})
        elif re.search(r"a[ñn]o\s+pasado", texto_lower):
            entidades.append({"tipo": "TIEMPO", "unidad": "meses", "valor": 12})
        elif re.search(r"hace\s+poco|hace\s+unos\s+d[ií]as|hace\s+algunos\s+d[ií]as", texto_lower):
            entidades.append({"tipo": "TIEMPO", "unidad": "meses", "valor": 0.5})
        elif re.search(r"hace\s+unas\s+semanas|hace\s+algunas\s+semanas", texto_lower):
            entidades.append({"tipo": "TIEMPO", "unidad": "meses", "valor": 1})
        elif re.search(r"hace\s+unos\s+meses|hace\s+algunos\s+meses", texto_lower):
            entidades.append({"tipo": "TIEMPO", "unidad": "meses", "valor": 3})
        elif re.search(r"hace\s+mucho", texto_lower):
            entidades.append({"tipo": "TIEMPO", "unidad": "meses", "valor": 13})
        elif re.search(r"\brecién\b|\brecien\b|\brecientemente\b|hace\s+nada", texto_lower):
            entidades.append({"tipo": "TIEMPO", "unidad": "meses", "valor": round(1 / 30, 2)})

        # PESO
        m = re.search(r"(\d+)\s*kg", texto_lower)
        if m:
            entidades.append({"tipo": "PESO", "valor": int(m.group(1))})

        # EDAD
        m = re.search(
            r"(?:tengo|tiene|soy\s+de|tengo\s+\w+\s+de)?\s*(\d+)\s*años?\s*(?:de\s+edad)?",
            texto_lower,
        )
        if m and re.search(r"tengo|soy|mi\s+edad|años\s+de\s+edad|tiene\s+\d+\s*años|cumpl", texto_lower):
            edad = int(m.group(1))
            if 10 <= edad <= 100:
                entidades.append({"tipo": "EDAD", "valor": edad})

        return entidades

    def detectar_intencion(self, texto: str) -> str:
        texto_lower = texto.lower()
        for intencion, frases in self.INTENCIONES.items():
            for frase in frases:
                if frase in texto_lower:
                    return intencion
        return "consulta_general"

    def interpretar(self, entidades: list[dict]) -> tuple:
        tipo = None
        tiempo = None
        peso = None
        edad = None
        for e in entidades:
            if e["tipo"] == "TIPO":
                tipo = e["valor"]
            if e["tipo"] == "TIEMPO":
                tiempo = e["valor"]
            if e["tipo"] == "PESO":
                peso = e["valor"]
            if e["tipo"] == "EDAD":
                edad = e["valor"]
        return tipo, tiempo, peso, edad
