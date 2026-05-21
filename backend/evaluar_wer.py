"""
Evaluación WER con hipótesis simuladas de ASR.
Representa errores típicos de Google ASR y Whisper tiny en español:
  - Pérdida de tildes (accentuation loss)
  - Confusión en palabras técnicas
  - Números transcritos como dígitos
  - Palabras faltantes o agregadas
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from wer import calcular_wer, resumen_wer, FRASES_PRUEBA

# Hipótesis simuladas: [google_asr, whisper_tiny]
# Basadas en errores documentados de ambos sistemas con español rioplatense.
HIPOTESIS = [
    # 1 "me hice un tatuaje hace dos meses"
    (
        "me hice un tatuaje hace dos meses",          # Google: perfecto
        "me hice un tatuaje hace 2 meses",            # Whisper: "dos" → "2"
    ),
    # 2 "quiero donar sangre puedo hacerlo"
    (
        "quiero donar sangre puedo hacerlo",           # Google: perfecto
        "quiero donar sangre puedo hacerlo",           # Whisper: perfecto
    ),
    # 3 "tomé antibióticos la semana pasada"
    (
        "tome antibióticos la semana pasada",          # Google: pierde tilde en tomé
        "tome antibioticos la semana pasada",          # Whisper: pierde ambas tildes
    ),
    # 4 "tuve una cirugía hace tres meses"
    (
        "tuve una cirugía hace tres meses",            # Google: perfecto
        "tuve una cirugia hace tres meses",            # Whisper: pierde tilde cirugía
    ),
    # 5 "me hice un piercing hace un mes"
    (
        "me hice un piercing hace un mes",             # Google: perfecto
        "me hice un piercing hace un mes",             # Whisper: perfecto
    ),
    # 6 "tengo diabetes puedo donar sangre"
    (
        "tengo diabetes puedo donar sangre",           # Google: perfecto
        "tengo diabetes puedo donar sangre",           # Whisper: perfecto
    ),
    # 7 "tuve dengue hace veinte días"
    (
        "tuve dengue hace veinte días",                # Google: perfecto
        "tuve dengue hace 20 días",                   # Whisper: "veinte" → "20"
    ),
    # 8 "cuánto tiempo debo esperar para donar"
    (
        "cuanto tiempo debo esperar para donar",       # Google: pierde tilde cuánto
        "cuanto tiempo debo esperar para donar",       # Whisper: igual
    ),
    # 9 "me operé hace seis meses ya puedo donar"
    (
        "me opere hace seis meses ya puedo donar",     # Google: pierde tilde operé
        "me opere hace 6 meses ya puedo donar",        # Whisper: operé→opere + seis→6
    ),
    # 10 "tengo fiebre desde ayer puedo donar"
    (
        "tengo fiebre desde ayer puedo donar",         # Google: perfecto
        "tengo fiebre desde ayer puedo donar",         # Whisper: perfecto
    ),
    # 11 "me vacuné contra el covid hace dos semanas"
    (
        "me vacune contra el covid hace dos semanas",  # Google: pierde tilde vacuné
        "me vacune contra el covid hace 2 semanas",    # Whisper: vacuné→vacune + dos→2
    ),
    # 12 "nunca me hice un tatuaje puedo donar"
    (
        "nunca me hice un tatuaje puedo donar",        # Google: perfecto
        "nunca me hice un tatuaje puedo donar",        # Whisper: perfecto
    ),
]

assert len(HIPOTESIS) == len(FRASES_PRUEBA), "Cantidad de hipótesis no coincide"

print("=" * 80)
print("EVALUACIÓN WER — DONAR-APP")
print("=" * 80)
print(f"{'#':<3} {'Referencia':<42} {'Google':<8} {'Whisper':<8}")
print("-" * 80)

resultados_google  = []
resultados_whisper = []

for i, (ref, (hip_g, hip_w)) in enumerate(zip(FRASES_PRUEBA, HIPOTESIS), 1):
    rg = calcular_wer(ref, hip_g)
    rw = calcular_wer(ref, hip_w)
    resultados_google.append(rg)
    resultados_whisper.append(rw)
    ref_short = ref if len(ref) <= 40 else ref[:37] + "..."
    print(f"{i:<3} {ref_short:<42} {rg['wer_pct']:>5.1f}%   {rw['wer_pct']:>5.1f}%")

print("-" * 80)
rg_sum = resumen_wer(resultados_google)
rw_sum = resumen_wer(resultados_whisper)
print(f"{'PROMEDIO':<46} {rg_sum['wer_pct_promedio']:>5.1f}%   {rw_sum['wer_pct_promedio']:>5.1f}%")
print("=" * 80)

# Detalle S/D/I por frase
print("\nDETALLE S/D/I — Google ASR:")
print(f"{'#':<3} {'S':>4} {'D':>4} {'I':>4} {'N':>4}  {'WER':>7}")
for i, r in enumerate(resultados_google, 1):
    print(f"{i:<3} {r['S']:>4} {r['D']:>4} {r['I']:>4} {r['N']:>4}  {r['wer_pct']:>6.1f}%")

print("\nDETALLE S/D/I — Whisper tiny:")
print(f"{'#':<3} {'S':>4} {'D':>4} {'I':>4} {'N':>4}  {'WER':>7}")
for i, r in enumerate(resultados_whisper, 1):
    print(f"{i:<3} {r['S']:>4} {r['D']:>4} {r['I']:>4} {r['N']:>4}  {r['wer_pct']:>6.1f}%")
