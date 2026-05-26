
TECNICATURA SUPERIOR EN
CIENCIA DE DATOS E INTELIGENCIA ARTIFICIAL

TRAYECTO F — UNIDAD 11
Técnicas de Procesamiento del Habla
TRABAJO INTEGRADOR
Guía de Proyecto para Estudiantes
Modalidad: grupal   |  Duración: 2 meses
Provincia de Buenos Aires  |  Dirección General de Cultura y Educación
Educación Técnico Profesional de Nivel Superior  |  Res. 2730/22
 
INTRODUCCIÓN
Este documento describe el Trabajo Integrador de la Unidad 11 — Técnicas de Procesamiento del Habla. El objetivo es que cada grupo diseñe, desarrolle y presente un producto de software funcional que integre los cuatro bloques de la unidad: Procesamiento del Lenguaje Natural (Bloque 1), Modelos de N-gramas (Bloque 2), Recuperación de Información (Bloque 3) y Reconocimiento y Síntesis del Habla (Bloque 4).
El producto debe ser una aplicación web con interfaz gráfica (), reconocimiento de voz real (micrófono), persistencia en base de datos (SQLite), y un dashboard con estadísticas y métricas. No es un ejercicio académico: es un prototipo funcional orientado a un cliente real.

Datos generales
Aspecto	Detalle
Modalidad	Grupal
Duración	2 meses (8 semanas)
Entrega parcial	Fin de semana 4 — Pipeline funcional por consola
Entrega final	Fin de semana 8 — App web completa + informe + video demo
Defensa oral	Semana 8 o 9 — Presentación grupal de 15 minutos + preguntas
Peso en la nota	50% de la nota final de la unidad


 
REQUISITOS TÉCNICOS OBLIGATORIOS
Todos los proyectos deben cumplir los siguientes requisitos mínimos. Estos requisitos son de cumplimiento obligatorio y se evalúan con rúbrica.

1. Reconocimiento de voz (ASR)
•	Obligatorio: el usuario debe poder interactuar con la aplicación usando su voz a través del micrófono del navegador.
•	Implementar con SpeechRecognition (API de Google, online) como opción principal.
•	Opcionalmente agregar Whisper (OpenAI) como alternativa offline.
•	Mostrar la transcripción en tiempo real en la interfaz.
•	Medir el WER (Word Error Rate) sobre al menos 10 frases de prueba con transcripción de referencia.
•	Documentar las limitaciones del ASR: errores con ruido, acentos, jerga del dominio.

TIP TECNICO
Streamlit ofrece st.audio_input() para capturar audio del micrófono del navegador. Alternativamente se puede usar PyAudio para grabar y luego pasar el archivo al reconocedor. La segunda opción da más control pero requiere más código.

2. Síntesis de voz (TTS)
•	Obligatorio: el sistema debe responder al usuario con audio generado automáticamente.
•	Implementar con gTTS (Google Text-to-Speech) en español.
•	El audio generado debe reproducirse en la interfaz web (st.audio).
•	Debe ser configurable: el usuario puede elegir si quiere respuesta por texto, por voz, o ambas.

3. Procesamiento del Lenguaje Natural (Bloque 1)
•	Obligatorio: el texto transcripto debe procesarse con herramientas de PLN.
•	Tokenización del texto de entrada (con spaCy o implementación propia).
•	NER (Named Entity Recognition): extraer al menos 3 tipos de entidades relevantes para el dominio elegido.
•	POS tagging: usar las categorías gramaticales para filtrar o priorizar información.
•	Detección de intención o clasificación del tipo de consulta del usuario.

4. Modelo de lenguaje con N-gramas (Bloque 2)
•	Obligatorio: construir al menos un modelo de N-gramas entrenado con el corpus del dominio.
•	Entrenar modelos de bigramas y/o trigramas sobre el corpus específico del proyecto.
•	Implementar suavizado Add-k (con k configurable, no solo Add-1).
•	Calcular y mostrar la perplejidad de las entradas del usuario.
•	Usar la perplejidad para al menos una funcionalidad: validación de coherencia, detección de anomalías, autocompletado, o clasificación.
•	Mostrar las tablas de probabilidad de transición (al menos las top-10 por contexto).

5. Recuperación de Información (Bloque 3)
•	Obligatorio: implementar un motor de búsqueda sobre el corpus del dominio.
•	Construir un índice invertido sobre los documentos del corpus.
•	Calcular pesos TF-IDF para cada término.
•	Implementar búsqueda por similitud del coseno.
•	Evaluar la calidad de la búsqueda con Precisión, Recall y F1 sobre al menos 10 consultas de prueba con relevancia etiquetada.
•	Mostrar los resultados rankeados con snippets relevantes.

6. Persistencia en base de datos
•	Obligatorio: toda la información del sistema debe persistir entre sesiones.
•	Usar SQLite como motor de base de datos (un solo archivo .db).
•	Mínimo 3 tablas: una para el corpus/documentos, una para el historial de interacciones, y una para las métricas/estadísticas.
•	El índice invertido puede almacenarse en la base de datos o en un archivo JSON, pero debe persistir (no recalcularse en cada ejecución).
•	El historial de consultas del usuario debe almacenarse con timestamp, texto original, texto transcripto (si fue por voz), resultado obtenido y métricas asociadas.

7. Interfaz web
•	Obligatorio: la aplicación debe tener una interfaz web funcional con al menos dos vistas.

7.1 Vista principal (usuario)
•	Botón de micrófono para captura de voz.
•	Campo de texto como alternativa a la voz.
•	Área de resultados con formato claro (no texto plano crudo).
•	Reproducción de la respuesta en audio (TTS).
•	Historial de la sesión actual visible.

7.2 Dashboard (administrador / docente / analista)
•	Métricas globales del sistema: total de consultas, WER promedio, PP promedio, tiempo de respuesta.
•	Top 10 consultas más frecuentes.
•	Distribución de tipos de consulta o categorías (gráfico de barras o torta).
•	Evolución temporal: consultas por día/semana (gráfico de líneas).
•	Métricas de evaluación del motor de búsqueda: P, R, F1 por consulta de prueba.
•	Nube de palabras o histograma de términos más buscados.



ATENCION
El dashboard no es decorativo. Debe mostrar datos REALES extraídos de la base de datos. Gráficos vacíos o con datos inventados se califican con 0 en ese ítem.


 
8. Evaluación y métricas
•	Obligatorio: el proyecto debe incluir una evaluación cuantitativa rigurosa.

Métrica	Descripción
WER	Word Error Rate del ASR, medido sobre 10+ frases de referencia. Reportar media y desviación estándar.
Perplejidad	PP del modelo de N-gramas sobre un conjunto de test separado del de entrenamiento. Comparar MLE vs Add-k.
P / R / F1	Precisión, Recall y F1 del motor de búsqueda sobre 10+ consultas de prueba con documentos relevantes etiquetados.
Accuracy NER	Porcentaje de entidades correctamente identificadas sobre 20+ ejemplos anotados manualmente.
Tiempo de respuesta	Tiempo promedio del pipeline completo: audio → texto → NLP → búsqueda → respuesta → TTS. Medido en segundos.

9. Documentación y entrega
•	README.md con instrucciones de instalación y ejecución.
•	requirements.txt con todas las dependencias y versiones.
•	Informe técnico (3-5 páginas) con: descripción del problema, arquitectura del sistema, corpus utilizado, métricas obtenidas, limitaciones y posibles mejoras.
•	Video demo de 3-5 minutos mostrando la aplicación funcionando con voz real.
•	Código fuente organizado en módulos (no todo en un solo archivo).

REQUISITO OBLIGATORIO
Estructura de archivos sugerida: app.py (Streamlit principal), modules/asr.py, modules/nlp.py, modules/ngrams.py, modules/search.py, modules/tts.py, modules/db.py, data/corpus/, tests/eval_wer.py, tests/eval_search.py, docs/informe.pdf, README.md, requirements.txt


 
OPCIONES DE PROYECTO
Estas son algunas ideas para los proyectos

Opción A — VozSalud: Sistema de triaje telefónico para centros de salud

Descripción del producto
Un sistema donde el paciente describe sus síntomas hablando por el micrófono. El sistema transcribe la descripción, extrae los síntomas mencionados, busca en una base de protocolos médicos de triaje, clasifica la urgencia (verde/amarillo/rojo) y genera una recomendación escrita y hablada. El médico de guardia ve todas las consultas en un dashboard web en tiempo real.

Corpus del dominio
•	Base de 50+ protocolos de triaje médico (textos públicos del Ministerio de Salud de PBA o de la OMS, adaptados al español argentino).
•	Corpus de 50+ relatos de pacientes simulados para entrenar el modelo de lenguaje (redactados por el grupo en lenguaje coloquial: 'me duele acá en la boca del estómago desde ayer a la noche').
•	Diccionario de sinónimos médicos: mapear lenguaje coloquial a términos técnicos ('puntada en el pecho' → 'dolor torácico agudo').

Entidades NER del dominio
Entidad	Ejemplos
SINTOMA	dolor, fiebre, mareo, tos, vómitos, dificultad para respirar...
PARTE_CUERPO	cabeza, pecho, estómago, garganta, espalda, piernas...
DURACION	desde ayer, hace 3 días, desde la semana pasada...
MEDICAMENTO	ibuprofeno, paracetamol, amoxicilina...
SEVERIDAD	leve, fuerte, insoportable, intermitente...

Funcionalidad de N-gramas
•	Modelo entrenado con relatos de pacientes. PP para detectar transcripciones dudosas del ASR.
•	Autocompletado de síntomas: cuando el paciente dice 'dolor en el...', sugerir las continuaciones más probables.
•	Clasificación: relatos con PP alta podrían indicar un problema de transcripción o un síntoma no estándar que requiere atención humana.

Cliente potencial
CAPS (Centros de Atención Primaria de Salud) y hospitales municipales de la Provincia de Buenos Aires. Reduce la carga de la línea telefónica atendiendo consultas simples automáticamente.


Opción B — RadioGuard: Monitor inteligente de comunicaciones de emergencia

Descripción del producto
Un sistema que escucha transmisiones de radio de emergencias (bomberos, policía, ambulancias), las transcribe en tiempo real, extrae entidades críticas (ubicación, tipo de emergencia, unidades despachadas), las indexa en una base de datos y las muestra en un mapa web interactivo. El operador puede buscar eventos por texto o por voz.

Corpus del dominio
•	50+ clips de audio simulando transmisiones de radio de emergencia (grabados por los propios estudiantes con jerga real: 'Móvil 23 a Central, tenemos un 10-40 en Mitre y San Martín, solicito apoyo de dotación').
•	Transcripciones de referencia para cada clip (para medir WER).
•	Diccionario de códigos de radio: mapear códigos numéricos a tipos de emergencia ('10-40' → 'accidente de tránsito').

Entidades NER del dominio
Entidad	Ejemplos
UBICACION	calles, intersecciones, barrios, localidades
TIPO_EMERGENCIA	incendio, accidente, robo, emergencia médica, inundación...
UNIDAD	Móvil 23, Dotación 5, Ambulancia 12, Patrullero 8...
CODIGO_RADIO	10-4 (entendido), 10-40 (accidente), 10-20 (ubicación)...
VICTIMAS	personas atrapadas, heridos, cantidad estimada...

Funcionalidad de N-gramas
•	Modelo entrenado con lenguaje de radio de emergencias. PP para detectar transcripciones erradas (audio ruidoso = muchos errores de ASR).
•	Corrector automático: si un bigrama tiene PP muy alta, sugerir la corrección más probable basada en el contexto.
•	Autocompletado de búsquedas: el operador empieza a escribir 'incendio zona...' y el sistema sugiere completaciones.

Funcionalidad de mapa
•	Mostrar los eventos en un mapa interactivo con Folium o pydeck integrado en Streamlit.
•	Los eventos se marcan con iconos según tipo (fuego, ambulancia, patrullero).
•	Mapa de calor: zonas con más eventos en las últimas 24 horas.
•	Click en un marcador: muestra la transcripción completa, el audio original reproducible, y las entidades extraídas.

Cliente potencial
Centros de despacho de emergencias (107, bomberos, defensa civil). La Provincia de Buenos Aires tiene 135 municipios con sistemas de emergencia mayormente analógicos. También aplicable a empresas de seguridad privada y medios periodísticos que monitorean frecuencias.


 
Opción C — ProfeBot: Asistente de estudio por voz para la tecnicatura

Descripción del producto
Un tutor virtual que los estudiantes usan hablando: hacen preguntas sobre los contenidos de la carrera, el sistema busca en los apuntes de la tecnicatura, responde por voz con citas textuales, y genera preguntas de repaso tipo quiz. El docente ve un dashboard con las dudas más frecuentes y los temas con baja comprensión.

Corpus del dominio
•	Los propios apuntes de la tecnicatura (los archivos .docx de las unidades 11 y 12, más cualquier otro material disponible).
•	Parseados a texto plano, segmentados por sección/tema.
•	Corpus de preguntas-respuestas: 30+ pares armados por el grupo como FAQs de la materia.

Entidades NER del dominio
Entidad	Ejemplos
CONCEPTO	perplejidad, TF-IDF, N-grama, tokenización, WER, clustering...
ALGORITMO	Naive Bayes, K-Means, k-NN, Q-Learning, Add-1...
METRICA	accuracy, F1, precisión, recall, RMSE, silhouette...
HERRAMIENTA	scikit-learn, spaCy, Streamlit, SpeechRecognition, gTTS...
UNIDAD	Unidad 11, Bloque 2, Trayecto F...

Funcionalidad de N-gramas
•	Modelo entrenado con el texto de los apuntes. Generador de preguntas de repaso tipo fill-in-the-blank usando bigramas: 'La perplejidad mide qué tan ___ está el modelo'.
•	Validador de respuestas: comparar la respuesta del estudiante contra la respuesta correcta usando similitud coseno y PP.
•	Autocompletado de preguntas: mientras el estudiante escribe (o habla), sugerir completaciones.

Funcionalidad de quiz
•	Generar preguntas aleatorias de cada bloque/tema.
•	El estudiante responde por voz o por texto.
•	El sistema valida y explica la respuesta correcta con la cita del apunte.
•	Llevar un registro de aciertos/errores por estudiante y por tema.

Cliente potencial
Institutos de educación superior (tecnicaturas, terciarios, universidades). La Provincia de Buenos Aires tiene 400+ institutos superiores. Cada uno podría cargar sus propios apuntes. También vendible como herramienta de accesibilidad: estudiantes con dislexia o discapacidad visual pueden estudiar por voz.


 
CRONOGRAMA — 8 SEMANAS

Mes 1 — Semanas 1 a 4: Pipeline funcional

Semana 1 — Setup y corpus
•	Formar el grupo y elegir la opción de proyecto.
•	Crear el repositorio Git.
•	Recopilar y curar el corpus del dominio (mínimo 50 documentos/relatos/clips).
•	Diseñar el esquema de la base de datos SQLite (mínimo 3 tablas).
•	Entregable: repositorio con corpus cargado en la base de datos + esquema documentado.

Semana 2 — PLN + NER + Índice invertido
•	Implementar la tokenización y el NER del dominio.
•	Construir el índice invertido sobre el corpus.
•	Implementar TF-IDF y búsqueda por coseno.
•	Motor de búsqueda funcional por consola.
•	Entregable: módulos nlp.py, search.py funcionando por consola con 5 consultas de prueba.

Semana 3 — Modelo de N-gramas + ASR
•	Entrenar el modelo de bigramas/trigramas sobre el corpus.
•	Implementar suavizado Add-k con k configurable.
•	Integrar ASR con SpeechRecognition: grabar → transcribir → procesar.
•	Medir WER sobre 10 frases de referencia.
•	Entregable: módulos ngrams.py, asr.py funcionando. Pipeline audio → texto → NLP → búsqueda por consola.

Semana 4 — Integración + entrega parcial
•	Integrar todos los módulos en un pipeline end-to-end funcional.
•	Agregar TTS (gTTS) para la respuesta.
•	Pipeline completo: micrófono → ASR → NLP → N-gramas → búsqueda → respuesta → TTS.
•	Toda la actividad debe quedar registrada en la base de datos.

REQUISITO OBLIGATORIO
ENTREGA PARCIAL (semana 4): pipeline completo funcionando por consola + base de datos con historial + métricas WER y PP calculadas. Esta entrega vale el 30% de la nota del integrador.


Mes 2 — Semanas 5 a 8: Interfaz y evaluación

Semana 5 — Interfaz web (vista principal)
•	Crear la app Streamlit con la vista del usuario.
•	Botón de micrófono, campo de texto, área de resultados, reproducción de audio TTS.
•	Historial de la sesión visible.
•	Conectar todos los módulos al frontend.
•	Entregable: app.py con vista principal funcional (se puede hablar y obtener respuestas).

Semana 6 — Dashboard
•	Crear la segunda vista (dashboard) con Streamlit.
•	Gráficos con datos reales de la base de datos (no inventados).
•	Métricas globales, top consultas, distribución por categoría, evolución temporal.
•	Métricas de evaluación del motor de búsqueda (P, R, F1).
•	Entregable: dashboard funcional con al menos 5 visualizaciones basadas en datos reales.

Semana 7 — Evaluación y ajustes
•	Evaluación end-to-end: simular 20+ interacciones completas y medir todo el pipeline.
•	Ajustar umbrales, parámetros del modelo, y UX basándose en los resultados.
•	Completar las métricas: WER, PP, P/R/F1, accuracy NER, tiempo de respuesta.
•	Escribir el informe técnico (3-5 páginas).
•	Entregable: evaluación completa documentada + informe borrador.

Semana 8 — Entrega final y defensa
•	Grabar el video demo (3-5 minutos).
•	Finalizar el informe técnico con análisis de limitaciones y mejoras posibles.
•	Limpiar el código, agregar docstrings, completar el README.
•	Preparar la presentación para la defensa oral (15 minutos).

REQUISITO OBLIGATORIO
ENTREGA FINAL (semana 8): repositorio completo + app desplegada + informe + video + presentación. Esta entrega vale el 70% de la nota del integrador.


 
POSIBLE STACK TECNOLÓGICO

Tecnología	Uso en el proyecto
Python 3.10+	Lenguaje principal del proyecto.
Streamlit	Framework para la interfaz web y el dashboard.
spaCy + es_core_news_sm	Tokenización, POS tagging, NER. Modelo de español.
SpeechRecognition	ASR — reconocimiento de voz con API de Google (online).
Whisper (opcional)	ASR alternativo — modelo local de OpenAI (offline).
gTTS	Text-to-Speech — síntesis de voz en español.
SQLite	Base de datos relacional embebida (sin servidor).
matplotlib / plotly	Gráficos para el dashboard.
Folium (solo RadioGuard)	Mapas interactivos integrados en Streamlit.
python-docx (solo ProfeBot)	Lectura de apuntes .docx para indexar.
PyAudio	Captura de audio del micrófono (alternativa a st.audio_input).
Git / GitHub	Control de versiones. Commits semanales obligatorios.

NOTA
No se permite el uso de APIs de LLMs (ChatGPT, Claude, Gemini, etc.) para generar las respuestas del sistema. El objetivo es que el sistema funcione con las técnicas de la unidad: N-gramas, TF-IDF, NER. Los LLMs se pueden usar como herramienta de desarrollo (para generar código, debuggear, etc.) pero no como componente del producto.


 
RÚBRICA DE EVALUACIÓN
La calificación se compone de la entrega parcial (30%) y la entrega final (70%). Cada ítem se evalúa de 0 a 10.

Entrega parcial (semana 4) — 30%
Componente	Criterios de aprobación
Corpus (10%)	Cantidad, calidad y relevancia del corpus. Mínimo 50 documentos/relatos.
PLN + NER (25%)	Tokenización funcional. NER con al menos 3 tipos de entidades. Accuracy NER ≥ 70%.
N-gramas (25%)	Modelo entrenado. Add-k implementado. PP calculada sobre test set.
Búsqueda TF-IDF (25%)	Índice invertido. Búsqueda por coseno funcional. Al menos 5 consultas demo.
ASR + pipeline (15%)	Audio → texto funcional. WER medido. Pipeline end-to-end por consola.

Entrega final (semana 8) — 70%
Componente	Criterios de aprobación
Interfaz web (20%)	Vista principal funcional con voz + texto. UX clara y sin errores. Respuesta TTS.
Dashboard (15%)	Mínimo 5 visualizaciones con datos reales. Métricas de evaluación visibles.
Base de datos (10%)	Esquema con 3+ tablas. Persistencia real. Historial consultable.
Evaluación (20%)	WER, PP, P/R/F1, accuracy NER, tiempo de respuesta. Todo documentado con valores numéricos.
Informe (15%)	3-5 páginas. Arquitectura, métricas, limitaciones, mejoras. Redacción clara y profesional.
Video demo (5%)	3-5 minutos. Muestra el producto funcionando con voz real.
Código (10%)	Organizado en módulos. Documentado con docstrings. README completo.
Defensa oral (5%)	Presentación clara de 15 min. Todos los integrantes participan. Responden preguntas técnicas.

Criterios de desaprobación automática
•	El sistema no funciona en la demostración en vivo.
•	El reconocimiento de voz no está implementado (no hay ASR real).
•	No hay base de datos (todo se pierde al cerrar la app).
•	Se usaron APIs de LLMs (ChatGPT/Claude/etc.) como motor de respuestas.
•	Plagio de código de otro grupo o de repositorios sin atribución.
•	Un integrante no puede explicar ninguna parte del código en la defensa oral.


 
CONSEJOS PARA UN BUEN PROYECTO

Sobre el corpus
•	Más datos = mejor modelo. 50 documentos es el mínimo, pero 100+ es mucho mejor.
•	La calidad importa más que la cantidad. Un corpus limpio y bien segmentado vale más que miles de documentos sucios.
•	Usen lenguaje real del dominio. Si hacen VozSalud, los relatos de pacientes deben sonar como habla un paciente real en Argentina, no como un paper médico.

Sobre el ASR
•	El ASR va a cometer errores. Eso no es un problema: es una oportunidad para mostrar cómo el modelo de N-gramas ayuda a detectar y corregir esos errores.
•	Prueben en condiciones reales: con ruido de fondo, con diferentes acentos, hablando rápido.
•	Documenten los errores y las limitaciones. Un proyecto que dice 'el WER es 15% y estos son los tipos de errores más comunes' es mucho mejor que uno que dice 'funciona perfecto'.

Sobre la interfaz
•	Simple es mejor. Una interfaz limpia que funciona bien es mejor que una llena de features que fallan.
•	Prueben la app con alguien que no sea del grupo. Si esa persona no entiende cómo usarla en 30 segundos, la UX necesita trabajo.
•	El dashboard debe contar una historia. No pongan 10 gráficos al azar: cada visualización debe responder una pregunta concreta.

Sobre la evaluación
•	Separen train y test desde el principio. Nunca evalúen el modelo con los mismos datos que usaron para entrenar.
•	No maquillen las métricas. Un F1 de 0.7 bien medido y explicado vale más que un F1 de 0.95 sospechoso.
•	Analicen los errores. ¿Dónde falla el sistema? ¿Por qué? ¿Cómo se podría mejorar?


 
EJEMPLOS GUÍA POR PROYECTO
A continuación se presenta, para cada opción de proyecto, un ejemplo completo de cómo funciona el sistema en un caso de uso real, un esquema de cómo debería verse la interfaz, y un diagrama de la arquitectura técnica. Estos ejemplos son orientativos: cada grupo puede adaptarlos a su implementación.


Ejemplo A — VozSalud

Caso de uso: María llama por dolor abdominal
A continuación se muestra paso a paso cómo un paciente interactúa con el sistema desde que habla por el micrófono hasta que recibe la recomendación:

Paso	Acción del usuario / sistema	Procesamiento interno
Paso 1	María hace click en el botón de micrófono y dice: 'Hola, me duele mucho la panza desde ayer a la noche, también tengo fiebre y náuseas'	El sistema graba el audio y lo envía al módulo ASR (SpeechRecognition).
Paso 2	El ASR transcribe: 'hola me duele mucho la panza desde ayer a la noche también tengo fiebre y náuseas'	La transcripción aparece en pantalla. Se almacena en la tabla historial de SQLite.
Paso 3	El módulo NLP tokeniza el texto y ejecuta el NER. Entidades detectadas: SINTOMA('dolor panza'), SINTOMA('fiebre'), SINTOMA('náuseas'), DURACION('desde ayer a la noche'), SEVERIDAD('mucho')	Se mapea 'dolor de panza' → 'dolor abdominal agudo' usando el diccionario de sinónimos.
Paso 4	El modelo de N-gramas calcula la PP del relato: PP = 28.4. Como PP < 50 (umbral), el relato se considera coherente.	Si la PP fuera > 50, el sistema marcaría la transcripción como dudosa y pediría repetir.
Paso 5	El motor de búsqueda TF-IDF busca en los protocolos de triaje con la query 'dolor abdominal agudo fiebre náuseas'. Top resultado: 'Protocolo de Abdomen Agudo' (coseno = 0.82).	Se muestran los 3 protocolos más relevantes con snippets.
Paso 6	El clasificador de urgencia combina las entidades + la PP + el protocolo encontrado. Resultado: AMARILLO (urgencia moderada). Recomendación: 'Acudir a guardia dentro de las próximas 2 horas'.	Se genera el audio con gTTS y se reproduce: 'Basándonos en sus síntomas...'.
Paso 7	Todo se almacena en SQLite: paciente_id, timestamp, texto transcripto, entidades, protocolo, urgencia, PP, tiempo de respuesta.	El médico de guardia ve la nueva consulta en el dashboard.

NOTA
Este caso de uso toca los 4 bloques: B1 (tokenización + NER de síntomas), B2 (PP para validar coherencia), B3 (TF-IDF para buscar protocolos), B4 (ASR de entrada + TTS de respuesta). Si algún bloque no aparece en el flujo, falta integración.


Wireframe de la interfaz — Vista Paciente
A continuación se describe cómo debería verse la pantalla principal. No es un diseño gráfico exacto sino un esquema de los elementos y su ubicación:

Zona	Contenido
Barra superior	Logo 'VozSalud' + selector de idioma + botón 'Dashboard' (solo visible para el médico con contraseña).
Zona izquierda (60%)	Área de conversación tipo chat. Cada mensaje muestra quién habla (Paciente / Sistema), el texto, y un botón de play para reproducir el audio. Los mensajes del sistema incluyen un badge de color con el nivel de urgencia.
Zona derecha (40%)	Panel de contexto: muestra las entidades NER extraídas en tiempo real (chips de colores: SINTOMA en rojo, DURACION en azul, SEVERIDAD en naranja). Debajo: el protocolo sugerido con el score de similitud. Debajo: la PP del relato con una barra visual (verde < 30, amarillo < 50, rojo > 50).
Barra inferior	Botón de micrófono grande (rojo cuando graba), campo de texto alternativo, botón 'Enviar'. Toggle 'Respuesta por voz: sí/no'.
Sidebar Streamlit	Sección 'Configuración': selector de suavizado Add-k (slider k=0.01 a k=1.0), selector de ASR (Google / Whisper), cantidad de resultados de búsqueda (1-10).

Wireframe de la interfaz — Dashboard Médico
Zona	Contenido
Fila superior	4 tarjetas de métricas: Total consultas hoy, WER promedio, PP promedio, Tiempo de respuesta promedio.
Fila media izquierda	Gráfico de torta: distribución de urgencias (verde/amarillo/rojo) del último mes.
Fila media derecha	Gráfico de líneas: cantidad de consultas por día de la última semana.
Fila inferior izquierda	Tabla: Top 10 síntomas más reportados con frecuencia y porcentaje.
Fila inferior derecha	Tabla: últimas 10 consultas con timestamp, síntomas, urgencia y PP. Click en una fila para ver el detalle completo.
Sidebar	Filtros: rango de fechas, nivel de urgencia, rango de PP.


Arquitectura técnica — VozSalud
El siguiente esquema muestra los módulos del sistema, sus responsabilidades, y cómo se conectan entre sí:

Módulo	Responsabilidad
app.py	Punto de entrada Streamlit. Renderiza las dos vistas (paciente / dashboard). Coordina la comunicación entre módulos. No contiene lógica de negocio.
modules/asr.py	Clase ASREngine con métodos: grabar_audio() → bytes, transcribir(audio) → texto, calcular_wer(referencia, hipótesis) → float. Soporta Google y Whisper.
modules/nlp.py	Clase NLPProcessor: tokenizar(texto), extraer_entidades(texto) → lista de (texto, tipo, posición), clasificar_intencion(texto) → string, mapear_sinonimos(entidades) → entidades_normalizadas.
modules/ngrams.py	Clase ModeloNgramas: entrenar(corpus, n=2), probabilidad(w, contexto, k=0.1), perplejidad(texto) → float, autocompletar(contexto, top_n=5) → lista, tablas_transicion() → dict.
modules/search.py	Clase MotorBusqueda: construir_indice(documentos), tfidf(termino, doc) → float, buscar(query, top_n=5) → lista de (doc, score, snippet), evaluar(queries_test) → dict con P, R, F1.
modules/tts.py	Clase TTSEngine: sintetizar(texto) → bytes de audio MP3, reproducir(audio). Wrapper simple sobre gTTS.
modules/db.py	Clase BaseDatos: crear_tablas(), guardar_consulta(...), guardar_metrica(...), obtener_historial(filtros), obtener_estadisticas() → dict para el dashboard. Wrapper sobre sqlite3.
data/corpus/	Carpeta con los protocolos médicos en .txt (uno por archivo). El script init_db.py los carga en SQLite y construye el índice invertido.
tests/	eval_wer.py: mide WER sobre 10 frases. eval_search.py: mide P/R/F1 sobre 10 queries. eval_ner.py: mide accuracy NER sobre 20 ejemplos.

Flujo de datos
1.	Micrófono → asr.py → texto transcripto
2.	Texto → nlp.py → tokens + entidades NER + intención
3.	Entidades → ngrams.py → PP del relato + autocompletado
4.	Entidades normalizadas → search.py → protocolos rankeados por TF-IDF
5.	Protocolo + entidades + PP → clasificador de urgencia → nivel verde/amarillo/rojo
6.	Recomendación → tts.py → audio MP3
7.	Todo → db.py → SQLite (historial + métricas)
8.	Dashboard → db.py → lee SQLite → gráficos Streamlit


Esquema de base de datos
Tabla	Columnas	Descripción
protocolos	id, titulo, texto, categoria, fecha_carga	Almacena los protocolos de triaje médico. Se carga una vez al inicio.
consultas	id, timestamp, audio_path, texto_transcripto, texto_original, entidades_json, protocolo_id, urgencia, pp, wer, tiempo_respuesta_ms	Una fila por cada consulta del paciente. Las entidades se guardan como JSON.
metricas	id, fecha, wer_promedio, pp_promedio, total_consultas, precision_busqueda, recall_busqueda, f1_busqueda	Métricas agregadas diarias para el dashboard.


 
Ejemplo B — RadioGuard

Caso de uso: el operador recibe un reporte de incendio

Paso	Acción	Procesamiento interno
Paso 1	Se carga un archivo .wav de audio de radio simulado (o se graba en vivo desde el micrófono). El audio dice: 'Central, Móvil 23, tenemos un 10-45 en Mitre y Belgrano, edificio de tres pisos, humo visible, necesitamos dotación de bomberos'	El sistema muestra un indicador de 'Procesando audio...'.
Paso 2	ASR (Whisper) transcribe: 'central móvil 23 tenemos un 10-45 en mitre y belgrano edificio de tres pisos humo visible necesitamos dotación de bomberos'	Se muestra la transcripción. WER se calcula si hay referencia disponible.
Paso 3	NER extrae: UNIDAD('Móvil 23'), CODIGO('10-45' → 'incendio estructural'), UBICACION('Mitre y Belgrano'), DETALLE('edificio tres pisos, humo visible'), SOLICITUD('dotación de bomberos')	Las entidades aparecen como chips de colores en el panel lateral.
Paso 4	El modelo N-grama calcula PP = 18.2 (lenguaje de radio estándar, baja perplejidad). Si la PP fuera > 40, se marcaría como 'transcripción dudosa: verificar audio original'.	Se activa el corrector automático si detecta bigramas con PP anómala.
Paso 5	Se indexa el evento con TF-IDF en la base de datos. Se geolocaliza 'Mitre y Belgrano' (coordenadas predefinidas en un diccionario de calles locales).	El evento aparece como un marcador rojo de fuego en el mapa Folium.
Paso 6	El operador puede buscar eventos anteriores por voz: dice 'incendios en zona sur esta semana'. El ASR transcribe → TF-IDF busca en el índice → devuelve los eventos rankeados.	Los resultados se muestran en la tabla y se destacan en el mapa.
Paso 7	Todo se almacena en SQLite: timestamp, audio_path, transcripción, entidades, tipo_emergencia, ubicación, coordenadas, urgencia.	El dashboard muestra la nueva emergencia en tiempo real.


Wireframe de la interfaz — Vista Operador
Zona	Contenido
Zona superior (100%)	Barra de herramientas: botón 'Cargar audio .wav', botón de micrófono (para búsqueda por voz), campo de búsqueda de texto, filtros (tipo de emergencia, fecha, zona). Toggle: 'Alertas TTS: sí/no'.
Zona izquierda (55%)	Mapa interactivo (Folium/pydeck) con marcadores de eventos. Colores por tipo: rojo = incendio, azul = emergencia médica, amarillo = accidente, gris = otro. Mapa de calor superpuesto opcional.
Zona derecha (45%)	Timeline de eventos (lista cronológica inversa). Cada evento: hora, tipo (con ícono), ubicación, snippet de la transcripción, badge de urgencia. Click en un evento: expande mostrando la transcripción completa, las entidades NER, y un botón de play para reproducir el audio original.
Panel inferior	Últimas alertas críticas con TTS automático. El sistema lee en voz alta las emergencias de alta urgencia.

Wireframe de la interfaz — Dashboard de estadísticas
Zona	Contenido
Fila superior	4 tarjetas: Total eventos hoy, Eventos activos, WER promedio (radio ruidosa), Tiempo promedio de procesamiento.
Fila media izquierda	Gráfico de barras: cantidad de eventos por tipo (incendio, accidente, emergencia médica, otro) en la última semana.
Fila media centro	Mapa de calor: zonas con mayor concentración de eventos.
Fila media derecha	Gráfico de líneas: eventos por hora del día (para detectar patrones temporales).
Fila inferior	Tabla comparativa: WER de Whisper vs Google Speech sobre los mismos 10 audios de referencia. Gráfico de barras con los dos valores.


Arquitectura técnica — RadioGuard
Módulo	Responsabilidad
app.py	Streamlit principal. Dos tabs: 'Monitor' (vista operador) y 'Estadísticas' (dashboard). Sidebar con configuración.
modules/asr.py	Soporte dual: Whisper (local, para audio de radio ruidoso) y Google Speech (online, para búsqueda por voz del operador). Método comparar_asr(audio) para medir WER de ambos.
modules/nlp.py	NER especializado en lenguaje de radio: regex + spaCy para detectar unidades ('Móvil N'), códigos ('10-XX'), ubicaciones (calles, intersecciones). Diccionario de códigos de radio.
modules/ngrams.py	Modelo entrenado con transcripciones de radio. PP para validar transcripción + corrector de bigramas dudosos + autocompletado de búsquedas.
modules/search.py	Índice invertido sobre eventos almacenados. TF-IDF + coseno para búsquedas. Filtrado por fecha, tipo, zona.
modules/geo.py	Diccionario de calles/intersecciones → coordenadas. Resolución de ubicaciones mencionadas en las transmisiones. Generación de marcadores para Folium.
modules/tts.py	gTTS para leer alertas críticas en voz alta. Configurable on/off.
modules/db.py	SQLite con tablas: eventos, audios, métricas. Queries para el dashboard.

Esquema de base de datos
Tabla	Columnas	Descripción
eventos	id, timestamp, audio_path, transcripcion, tipo_emergencia, ubicacion_texto, latitud, longitud, unidades_json, urgencia, pp, wer, procesado	Un evento = una transmisión de radio procesada.
codigos_radio	codigo, descripcion, tipo_emergencia, urgencia_default	Diccionario de códigos de radio (10-4, 10-40, etc.).
metricas	id, fecha, total_eventos, wer_whisper, wer_google, pp_promedio, eventos_por_tipo_json, tiempo_procesamiento_promedio	Métricas diarias para el dashboard.
calles	id, nombre, latitud, longitud, barrio, localidad	Diccionario de calles para geocoding offline.


 
Ejemplo C — ProfeBot

Caso de uso: Lucas pregunta sobre perplejidad

Paso	Acción	Procesamiento interno
Paso 1	Lucas hace click en el micrófono y dice: 'Che, no entiendo bien qué es la perplejidad, cómo se calcula?'	El sistema graba y envía a Google Speech API.
Paso 2	ASR transcribe: 'che no entiendo bien qué es la perplejidad cómo se calcula'	Se muestra la transcripción en el chat. Se guarda en SQLite con timestamp y usuario.
Paso 3	NER detecta: CONCEPTO('perplejidad'). Clasificador de intención: DEFINICION + FORMULA.	El sistema sabe que Lucas pregunta tanto la definición como el cálculo.
Paso 4	TF-IDF busca en los apuntes indexados. Top resultado: sección 'Bloque 2 — Perplejidad' del apunte de U11 (coseno = 0.91).	Se extrae el snippet más relevante: 'La perplejidad mide qué tan sorprendido está el modelo ante una secuencia de palabras...'.
Paso 5	El modelo N-grama del apunte calcula la PP de la pregunta: PP = 34.2. No es anómala (la pregunta es coherente).	Si fuera muy alta, el sistema pediría reformular la pregunta.
Paso 6	El sistema genera la respuesta combinando el snippet del apunte con un template: 'Según el apunte del Bloque 2, la perplejidad mide qué tan sorprendido está el modelo. Se calcula como PP = 2 elevado a la entropía cruzada negativa promedio. Cuanto menor la PP, mejor el modelo.'	gTTS genera el audio y se reproduce.
Paso 7	El sistema ofrece un quiz: 'La perplejidad mide qué tan ___ está el modelo ante una secuencia'. Lucas responde 'sorprendido'. El sistema valida con coseno contra la respuesta correcta: similitud = 1.0 (correcto).	Se registra el acierto en la tabla quiz_resultados.
Paso 8	En el dashboard docente: 'perplejidad' sube al puesto 2 de conceptos más consultados. El tema 'Bloque 2 - N-gramas' muestra 85% de aciertos en quizzes.	El docente ve qué temas necesitan más explicación en clase.


Wireframe de la interfaz — Vista Estudiante
Zona	Contenido
Barra superior	Logo 'ProfeBot' + nombre del estudiante + selector de materia/unidad. Botón 'Modo Quiz'.
Zona principal (65%)	Chat conversacional. Mensajes del estudiante (burbujas a la derecha, gris), respuestas del sistema (burbujas a la izquierda, azul). Las respuestas incluyen la cita textual del apunte en un recuadro con referencia (Bloque, sección, página). Botón de play en cada respuesta del sistema.
Panel lateral (35%)	Panel 'Fuentes encontradas': muestra los 3 fragmentos más relevantes del apunte con su score de similitud TF-IDF. Click en uno expande el fragmento completo. Debajo: 'Tu progreso' con barra de aciertos del quiz por bloque.
Barra inferior	Botón de micrófono grande + campo de texto + botón 'Enviar'. Toggle 'Respuesta por voz'.
Modo Quiz	Al activar 'Modo Quiz', el chat cambia: el sistema hace preguntas tipo fill-in-the-blank. El estudiante responde por voz o texto. Feedback inmediato (correcto/incorrecto + explicación).

Wireframe de la interfaz — Dashboard Docente
Zona	Contenido
Fila superior	4 tarjetas: Total consultas, Estudiantes activos, Accuracy promedio del quiz, Concepto más consultado.
Fila media izquierda	Ranking de los 10 conceptos más preguntados (gráfico de barras horizontal). Cada barra es clickeable: lleva al detalle del concepto.
Fila media derecha	Heatmap de aciertos por bloque y por estudiante. Filas = estudiantes, columnas = bloques/temas, color = % de aciertos (verde oscuro = 100%, rojo = 0%).
Fila inferior izquierda	Gráfico de líneas: consultas por día + aciertos de quiz por día. Para ver la tendencia de estudio.
Fila inferior derecha	Tabla: últimas 20 preguntas con timestamp, estudiante, concepto, respuesta del sistema, score de similitud. Exportable a CSV.
Sidebar	Filtros: rango de fechas, estudiante específico, bloque/unidad, tipo de consulta (pregunta libre / quiz).


Arquitectura técnica — ProfeBot
Módulo	Responsabilidad
app.py	Streamlit con 3 vistas: 'Estudiar' (chat por voz), 'Quiz' (preguntas de repaso), 'Dashboard' (vista docente, protegida con contraseña simple).
modules/asr.py	Google Speech como ASR principal. Captura desde st.audio_input o PyAudio. WER medido sobre 10 preguntas de referencia.
modules/nlp.py	NER para conceptos académicos (regex + diccionario + spaCy). Clasificador de intención: DEFINICION, FORMULA, EJEMPLO, COMPARACION, PROCEDIMIENTO. Mapeo de sinónimos ('qué onda con' → 'qué es').
modules/ngrams.py	Modelo entrenado con el texto de los apuntes. Generador de preguntas fill-in-the-blank: elige un bigrama frecuente y reemplaza una de las palabras con '___'. Validador de respuestas del quiz por similitud coseno.
modules/search.py	Índice invertido sobre los apuntes segmentados por sección. TF-IDF + coseno. Cada resultado incluye la referencia exacta (unidad, bloque, sección, número de página).
modules/quiz.py	Clase QuizEngine: generar_pregunta(bloque=None) → pregunta + respuesta_correcta, validar_respuesta(respuesta_estudiante, respuesta_correcta) → (correcto: bool, similitud: float, explicación: str).
modules/tts.py	gTTS para respuestas y para leer las preguntas del quiz.
modules/db.py	SQLite con tablas: secciones_apunte, consultas, quiz_resultados, estudiantes, métricas.
scripts/init_corpus.py	Script que lee los .docx de los apuntes con python-docx, los segmenta por sección, y los carga en SQLite + construye el índice invertido.

Esquema de base de datos
Tabla	Columnas	Descripción
secciones	id, unidad, bloque, seccion, titulo, texto, n_tokens	Cada fila = una sección del apunte, pre-segmentada.
consultas	id, timestamp, estudiante_id, audio_path, texto_transcripto, concepto_detectado, intencion, seccion_resultado_id, similitud_coseno, pp, wer, tiempo_ms	Una fila por consulta del estudiante.
quiz_resultados	id, timestamp, estudiante_id, bloque, pregunta, respuesta_correcta, respuesta_estudiante, similitud, es_correcto	Registro de cada pregunta del quiz.
estudiantes	id, nombre, fecha_registro, total_consultas, total_quiz, aciertos_quiz	Perfil de cada estudiante.
metricas	id, fecha, consultas_dia, quiz_dia, accuracy_quiz, concepto_top, bloque_peor_accuracy	Métricas diarias para el dashboard docente.


 
Resumen comparativo de las tres opciones

Aspecto	VozSalud	RadioGuard
Dificultad	Media-alta: NER médico requiere diccionario amplio	Alta: audio ruidoso + geocoding + mapa
Corpus	Protocolos médicos + relatos de pacientes simulados	Audio de radio grabado + transcripciones + diccionario de calles
ASR	Google Speech (audio limpio de pacientes)	Whisper (audio ruidoso de radio) + Google Speech (voz del operador)
NER	Síntomas, partes del cuerpo, duración, medicamentos, severidad	Unidades, códigos de radio, ubicaciones, tipo de emergencia, víctimas
Feature N-gramas	PP para validar coherencia del relato + autocompletado de síntomas	PP para detectar errores de transcripción + corrector automático
Feature RI	Búsqueda de protocolos de triaje por TF-IDF	Búsqueda de eventos pasados + filtros por tipo/zona/fecha
Mapa	No	Sí — Folium con marcadores + mapa de calor
Impacto social	Alto — salud pública	Alto — seguridad y emergencias
Cliente	CAPS y hospitales municipales	Centros de despacho de emergencias

NOTA
Las tres opciones tienen la misma complejidad técnica en cuanto a los requisitos obligatorios. La diferencia está en el dominio y en la dificultad del corpus. RadioGuard es la más desafiante por el audio ruidoso y el geocoding; ProfeBot es la más accesible porque el corpus ya existe.


 
— Fin de la Guía del Trabajo Integrador —
Tecnicatura Superior en Ciencia de Datos e IA  
