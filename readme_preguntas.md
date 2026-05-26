# Preguntas del Asistente de Evaluación de Donantes

Flujo completo de preguntas que realiza el asistente (texto y voz) para evaluar si una persona puede donar sangre en el Instituto de Hemoterapia PBA.

---

## Flujo de inicio

| Paso | Mensaje / Pregunta | Tipo de respuesta |
|------|-------------------|-------------------|
| Bienvenida | "¿Querés comenzar con el asistente de evaluación de donantes?" | Sí / No |
| Peso | "¿Cuánto pesás?" | Número en kg |
| Edad | "¿Cuántos años tenés?" | Número |
| Sexo biológico | "¿Cuál es tu sexo biológico?" | Masculino / Femenino / Otro |

**Notas de corte en el inicio:**
- Peso < 50 kg → **No puede donar** (mínimo requerido)
- Edad < 16 años → **No puede donar**
- Edad 16-17 → Puede donar máximo 2 veces por año, requiere autorización del centro
- Edad > 65 → Puede donar presentando certificado médico de cabecera

---

## Preguntas del cuestionario médico

Las preguntas se realizan en este orden. Una respuesta **Sí** a cualquiera puede generar una restricción temporal (⏳) o permanente (❌).

### 1. Estado de salud hoy

**Pregunta:** ¿Te sentís bien hoy?

| Respuesta | Acción |
|-----------|--------|
| **Sí** / se siente bien | Continúa al paso 2 |
| **No** / describe síntomas | Se pide descripción de síntomas |

**Sub-preguntas si no se siente bien:**

- Si describe síntomas impeditivos (fiebre, diarrea, vómitos, tos, gripe, etc.) → ⏳ **Restricción temporal** — debe recuperarse completamente
- Si describe malestar leve → "Ese malestar no es un impedimento. ¿Querés continuar con la evaluación?" (Sí/No)
- Si responde No a continuar → Fin de la evaluación

---

### 2. Síntomas recientes

**Pregunta:** ¿Tuviste fiebre, diarrea o algún síntoma de enfermedad en las últimas 72 horas?

| Respuesta | Restricción | Descripción |
|-----------|-------------|-------------|
| **Sí** | ⏳ Temporal | Síntomas recientes — debe recuperarse completamente antes de donar |
| **No** | — | Continúa |

---

### 3. Medicación actual

**Pregunta:** ¿Estás tomando algún medicamento ahora mismo?

| Respuesta | Acción |
|-----------|--------|
| **No** | Continúa |
| **Sí** | Se solicita el nombre o descripción del medicamento |

**Sub-preguntas si toma medicamentos:**

- "¿Cuál o cuáles medicamentos estás tomando?" → Ingresa nombre(s) del medicamento
  - Si el medicamento es incompatible → ❌ Restricción permanente
  - Si el medicamento requiere evaluación → ⚠️ El centro verificará compatibilidad
  - Si no reconoce el medicamento → "¿Para qué condición o enfermedad lo tomás?" (ej: epilepsia, diabetes, presión alta)
    - Si la condición es impedimento → restricción según la condición
    - Si no figura como impedimento → Continúa ✓

---

### 4. Enfermedades del corazón

**Pregunta:** ¿Tuviste o tenés alguna enfermedad del corazón?
*(Infarto, angina de pecho, problemas de válvulas, arritmia, etc.)*

| Respuesta | Restricción | Descripción |
|-----------|-------------|-------------|
| **Sí** | ❌ Permanente | Enfermedad cardíaca grave |
| **No** | — | Continúa |

---

### 5. Diabetes

**Pregunta:** ¿Sos diabético?

| Respuesta | Acción |
|-----------|--------|
| **No** | Continúa |
| **Sí** | Se pregunta el tipo de diabetes |

**Sub-pregunta si es diabético:**

"¿Qué tipo de diabetes?"
- Tipo 1 (necesitás insulina / inyecciones) → ❌ **Restricción permanente**
- Tipo 2 (controlada con pastillas o dieta) → Generalmente puede donar ✓ → Continúa

---

### 6. Presión arterial

**Pregunta:** ¿Tenés presión arterial alta que requiera más de 2 medicamentos para controlarla?

| Respuesta | Restricción | Descripción |
|-----------|-------------|-------------|
| **Sí** | ❌ Permanente | Hipertensión grave con más de 2 medicamentos |
| **No** | — | Continúa |

---

### 7. Enfermedades de los riñones

**Pregunta:** ¿Tuviste o tenés una enfermedad crónica de los riñones?
*(Insuficiencia renal, diálisis)*

| Respuesta | Restricción | Descripción |
|-----------|-------------|-------------|
| **Sí** | ❌ Permanente | Enfermedad renal crónica |
| **No** | — | Continúa |

---

### 8. Enfermedades de los pulmones

**Pregunta:** ¿Tuviste o tenés una enfermedad crónica de los pulmones?
*(EPOC, tuberculosis, asma grave con broncodilatadores diarios)*

| Respuesta | Restricción | Descripción |
|-----------|-------------|-------------|
| **Sí** | ❌ Permanente | Enfermedad pulmonar crónica grave |
| **No** | — | Continúa |

---

### 9. Epilepsia o ACV

**Pregunta:** ¿Tuviste epilepsia en tratamiento o un ACV (derrame cerebral)?

| Respuesta | Restricción | Descripción |
|-----------|-------------|-------------|
| **Sí** | ❌ Permanente | Epilepsia en tratamiento o ACV |
| **No** | — | Continúa |

---

### 10. Cáncer

**Pregunta:** ¿Te diagnosticaron algún tipo de cáncer y recibiste quimioterapia o radioterapia?

| Respuesta | Restricción | Descripción |
|-----------|-------------|-------------|
| **Sí** | ❌ Permanente | Cáncer con quimio o radioterapia |
| **No** | — | Continúa |

---

### 11. Hepatitis

**Pregunta:** ¿Tuviste hepatitis, color amarillo en la piel (ictericia), o algún análisis de sangre que dio positivo para hepatitis?

| Respuesta | Restricción | Descripción |
|-----------|-------------|-------------|
| **Sí** | ❌ Permanente | Hepatitis B o C positiva en análisis (puede evaluarse si fue hace muchos años) |
| **No** | — | Continúa |

---

### 12. VIH u otras ETS

**Pregunta:** ¿Alguna vez te diagnosticaron VIH, sífilis, gonorrea u otra infección de transmisión sexual?

| Respuesta | Restricción | Descripción |
|-----------|-------------|-------------|
| **Sí** | ❌ Permanente / ⏳ 1 año | VIH → permanente. ETS tratada (sífilis, gonorrea) → espera de 1 año desde el alta |
| **No** | — | Continúa |

---

### 13. Chagas, Malaria o Brucelosis

**Pregunta:** ¿Tuviste Chagas, Malaria o Brucelosis? ¿O viajaste a zonas donde estas enfermedades son comunes (zonas rurales del norte de Argentina, Venezuela, Colombia o Brasil)?

| Respuesta | Restricción | Descripción |
|-----------|-------------|-------------|
| **Sí** | ❌ Permanente / análisis previos | Chagas/Malaria/Brucelosis → permanente. Solo viaje → puede requerir análisis o espera de hasta 3 años |
| **No** | — | Continúa |

---

### 14. Procedimientos médicos recientes

**Pregunta:** ¿Te hiciste alguna cirugía, endoscopía, cateterismo, implante dental o cualquier procedimiento médico invasivo en el último año?

| Respuesta | Restricción | Descripción |
|-----------|-------------|-------------|
| **Sí** | ⏳ Temporal | Cirugía sin transfusión → 6 meses; con transfusión → 1 año; endoscopía / implante dental → 6 meses; extracción dental sin antibióticos → 3 días; con antibióticos → 7 días |
| **No** | — | Continúa |

---

### 15. Tatuajes, piercings o estética invasiva

**Pregunta:** ¿Te hiciste tatuajes, piercings, acupuntura o algún tratamiento estético invasivo (como botox o rellenos) en el último año?

| Respuesta | Restricción | Descripción |
|-----------|-------------|-------------|
| **Sí** | ⏳ Temporal | Material descartable propio → 6 meses; material compartido o lugar sin garantía → 12 meses |
| **No** | — | Continúa |

---

### 16. Transfusión o trasplante

**Pregunta:** ¿Recibiste sangre de otra persona o un trasplante de órgano alguna vez?

| Respuesta | Restricción | Descripción |
|-----------|-------------|-------------|
| **Sí** | ⏳ 1 año | Espera de 1 año desde que lo recibió |
| **No** | — | Continúa |

---

### 17. Relaciones sexuales de riesgo

**Pregunta:** En los últimos 6 meses, ¿tuviste relaciones sexuales sin preservativo con una pareja nueva o con alguien que tenga VIH, hepatitis o esté en diálisis?

| Respuesta | Restricción | Descripción |
|-----------|-------------|-------------|
| **Sí** | ⏳ 6 meses | Espera de 6 meses |
| **No** | — | Continúa |

---

### 18. Drogas inyectables

**Pregunta:** ¿Alguna vez usaste jeringas para inyectarte drogas?

| Respuesta | Restricción | Descripción |
|-----------|-------------|-------------|
| **Sí** | ❌ Permanente | Uso de jeringas para drogas |
| **No** | — | Continúa |

---

### 19. Consumo de alcohol

**Pregunta:** ¿Consumís alcohol en grandes cantidades con frecuencia? (más de 1 litro por día)

| Respuesta | Restricción | Descripción |
|-----------|-------------|-------------|
| **Sí** | ❌ Permanente | Alcoholismo crónico |
| **No** | — | Continúa |

---

### 20. Vacunas recientes

**Pregunta:** ¿Recibiste alguna vacuna en el último mes?
*(Especialmente: triple viral, fiebre amarilla, varicela, BCG, polio oral, dengue, rotavirus)*

| Respuesta | Restricción | Descripción |
|-----------|-------------|-------------|
| **Sí** | ⏳ 1 mes | Vacunas de virus vivos → espera de 1 mes. Las inactivadas (tétano, gripe, hepatitis B) no requieren espera |
| **No** | — | Continúa |

---

### 21. Embarazo *(solo mujeres)*

**Pregunta:** ¿Estás embarazada actualmente?

| Respuesta | Restricción | Descripción |
|-----------|-------------|-------------|
| **Sí** | ❌ No puede donar | Embarazo actual |
| **No** | — | Continúa |

---

### 22. Parto, cesárea o aborto reciente *(solo mujeres)*

**Pregunta:** ¿Tuviste un parto, cesárea o aborto en los últimos 6 meses?

| Respuesta | Restricción | Descripción |
|-----------|-------------|-------------|
| **Sí** | ⏳ Temporal | Parto/cesárea sin transfusión → 6 meses; con transfusión → 1 año; aborto → 6 meses |
| **No** | — | Continúa |

---

## Resultado final

Al finalizar todas las preguntas, el asistente emite uno de tres resultados:

| Resultado | Condición | Mensaje |
|-----------|-----------|---------|
| ✅ **Apto** | Sin restricciones | "Podés donar sangre. Acercate al banco de sangre más cercano." |
| ❌ **No apto permanente** | Al menos una restricción ❌ | "No podés donar sangre. Te recomendamos hablar con el médico del banco de sangre." |
| ⏳ **No apto temporal** | Solo restricciones ⏳, ninguna ❌ | "Por el momento no podés donar. Cuando estés recuperado/a y se cumplan los tiempos de espera, acercate al banco." |

---

## Resumen de restricciones

| Condición | Tipo | Espera |
|-----------|------|--------|
| Peso < 50 kg | ❌ Permanente | Hasta alcanzar 50 kg |
| Edad < 16 años | ❌ Permanente | Hasta los 16 |
| Síntomas recientes | ⏳ Temporal | Hasta recuperación completa |
| Medicación incompatible | ❌ Permanente | — |
| Enfermedad cardíaca grave | ❌ Permanente | — |
| Diabetes tipo 1 (insulina) | ❌ Permanente | — |
| Hipertensión grave (>2 medicamentos) | ❌ Permanente | — |
| Enfermedad renal crónica | ❌ Permanente | — |
| Enfermedad pulmonar crónica | ❌ Permanente | — |
| Epilepsia en tratamiento / ACV | ❌ Permanente | — |
| Cáncer con quimio/radioterapia | ❌ Permanente | — |
| Hepatitis positiva en análisis | ❌ Permanente | — |
| VIH positivo | ❌ Permanente | — |
| ETS tratada (sífilis, gonorrea) | ⏳ Temporal | 1 año desde el alta |
| Chagas / Malaria / Brucelosis | ❌ Permanente | — |
| Viaje a zona endémica | ⏳ Temporal | Hasta 3 años o análisis previos |
| Cirugía sin transfusión | ⏳ Temporal | 6 meses |
| Cirugía con transfusión | ⏳ Temporal | 1 año |
| Endoscopía / implante dental | ⏳ Temporal | 6 meses |
| Extracción dental sin antibióticos | ⏳ Temporal | 3 días |
| Extracción dental con antibióticos | ⏳ Temporal | 7 días |
| Tatuaje / piercing / acupuntura (descartable) | ⏳ Temporal | 6 meses |
| Tatuaje / piercing (material compartido) | ⏳ Temporal | 12 meses |
| Transfusión o trasplante recibido | ⏳ Temporal | 1 año |
| Relaciones de riesgo sin preservativo | ⏳ Temporal | 6 meses |
| Drogas inyectables | ❌ Permanente | — |
| Alcoholismo crónico (>1 L/día) | ❌ Permanente | — |
| Vacuna de virus vivos | ⏳ Temporal | 1 mes |
| Embarazo actual | ❌ No puede donar | Durante el embarazo |
| Parto / cesárea sin transfusión | ⏳ Temporal | 6 meses |
| Parto / cesárea con transfusión | ⏳ Temporal | 1 año |
| Aborto | ⏳ Temporal | 6 meses |
