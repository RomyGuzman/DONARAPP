import re

# Frases de referencia para evaluar el ASR
FRASES_PRUEBA = [
    "me hice un tatuaje hace dos meses",
    "quiero donar sangre puedo hacerlo",
    "tomé antibióticos la semana pasada",
    "tuve una cirugía hace tres meses",
    "me hice un piercing hace un mes",
    "tengo diabetes puedo donar sangre",
    "tuve dengue hace veinte días",
    "cuánto tiempo debo esperar para donar",
    "me operé hace seis meses ya puedo donar",
    "tengo fiebre desde ayer puedo donar",
    "me vacuné contra el covid hace dos semanas",
    "nunca me hice un tatuaje puedo donar",
]


def _normalizar(texto: str) -> list[str]:
    texto = texto.lower().strip()
    texto = re.sub(r"[^a-záéíóúüñ\s]", "", texto)
    return texto.split()


def calcular_wer(referencia: str, hipotesis: str) -> dict:
    """
    WER = (S + D + I) / N
    S = sustituciones, D = eliminaciones, I = inserciones, N = palabras en referencia
    Implementado con distancia de edición (Levenshtein a nivel palabra).
    """
    r = _normalizar(referencia)
    h = _normalizar(hipotesis)

    N = len(r)
    if N == 0:
        return {"wer": 0.0, "S": 0, "D": 0, "I": 0, "N": 0}

    # Matriz DP
    d = [[0] * (len(h) + 1) for _ in range(len(r) + 1)]
    for i in range(len(r) + 1):
        d[i][0] = i
    for j in range(len(h) + 1):
        d[0][j] = j

    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            if r[i - 1] == h[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                d[i][j] = 1 + min(d[i - 1][j], d[i][j - 1], d[i - 1][j - 1])

    # Backtrack para contar S/D/I
    i, j = len(r), len(h)
    S = D = I = 0
    while i > 0 or j > 0:
        if i > 0 and j > 0 and r[i - 1] == h[j - 1]:
            i -= 1; j -= 1
        elif i > 0 and j > 0 and d[i][j] == d[i - 1][j - 1] + 1:
            S += 1; i -= 1; j -= 1
        elif j > 0 and d[i][j] == d[i][j - 1] + 1:
            I += 1; j -= 1
        else:
            D += 1; i -= 1

    wer = (S + D + I) / N
    return {
        "wer": round(wer, 4),
        "wer_pct": round(wer * 100, 2),
        "S": S, "D": D, "I": I, "N": N,
        "palabras_referencia": r,
        "palabras_hipotesis": h,
    }


def resumen_wer(resultados: list[dict]) -> dict:
    if not resultados:
        return {"wer_promedio": 0.0, "wer_pct_promedio": 0.0}
    avg = sum(r["wer"] for r in resultados) / len(resultados)
    return {
        "wer_promedio": round(avg, 4),
        "wer_pct_promedio": round(avg * 100, 2),
        "total_evaluadas": len(resultados),
    }
