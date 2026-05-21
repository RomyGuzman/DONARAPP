# Arquitectura del Frontend — DONAR

## Stack

| Tecnología | Versión |
|---|---|
| Next.js (App Router) | 16.2.4 |
| React | 19.2.4 |
| TypeScript | 5 |
| Tailwind CSS | 4 |
| PostCSS | — |

## Estructura de archivos

```
frontend/app/
├── page.tsx                    ← enrutamiento y navegación entre tabs (50-80 líneas)
├── components/
│   ├── TabConsulta.tsx         ← asistente de texto + voz
│   ├── TabDashboard.tsx        ← estadísticas y gráficos
│   ├── TabNgramas.tsx          ← análisis n-gramas
│   ├── TabIR.tsx               ← TF-IDF / IR
│   ├── TabWER.tsx              ← Word Error Rate
│   ├── chat/
│   │   ├── useChatFlow.ts      ← hook del flujo conversacional guiado
│   │   ├── BotBurbuja.tsx      ← burbuja de mensaje del bot
│   │   └── UsuarioBurbuja.tsx  ← burbuja de mensaje del usuario
│   └── ui/
│       ├── Card.tsx            ← tarjeta reutilizable
│       ├── PieChart.tsx        ← gráfico de torta SVG
│       └── InfoTag.tsx         ← etiqueta informativa
├── data/
│   └── corpus.ts               ← base de conocimiento médico
└── lib/
    └── api.ts                  ← fetchJSON, playTTS, endpoints del backend
```

## Responsabilidades por capa

### `page.tsx`
Solo renderiza el layout principal y decide qué tab mostrar según el estado activo. Sin lógica de negocio.

### `components/Tab*.tsx`
Cada tab es un componente independiente con su propio estado local. No se comunican entre sí directamente.

### `components/chat/`
- **`useChatFlow.ts`** — hook que maneja el flujo conversacional guiado: preguntas, respuestas, validaciones de elegibilidad.
- **`BotBurbuja.tsx` / `UsuarioBurbuja.tsx`** — presentación pura de mensajes, sin lógica.

### `components/ui/`
Componentes genéricos reutilizables entre tabs: `Card`, `PieChart`, `InfoTag`.

### `data/corpus.ts`
Base de conocimiento médico embebida: criterios de elegibilidad, frecuencias de donación, medicamentos, vacunas con efecto sobre la donación.

### `lib/api.ts`
Capa de acceso al backend FastAPI (`http://127.0.0.1:8000`). Centraliza `fetchJSON`, `playTTS` y las URLs de cada endpoint.

## Endpoints consumidos

| Endpoint | Tab | Descripción |
|---|---|---|
| `POST /chat` | Consulta | Respuesta del asistente conversacional |
| `POST /tts` | Consulta | Síntesis de voz (gTTS) |
| `POST /asr` | Consulta | Reconocimiento de voz (Whisper) |
| `GET /dashboard` | Dashboard | Estadísticas de donaciones |
| `POST /ngramas` | N-gramas | Análisis de n-gramas |
| `POST /tfidf` | IR | Búsqueda TF-IDF |
| `POST /wer` | WER | Cálculo de Word Error Rate |

## Notas

- La app fuerza modo claro (`globals.css` — `color-scheme: light`).
- El corpus médico vive en el cliente, no en el backend.
- `useChatFlow` es el único hook con estado complejo; el resto de los tabs usan `useState` local simple.
