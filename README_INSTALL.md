# DONAR-APP — Guía de instalación completa en PC nueva

> Esta guía está pensada para alguien que arranca desde cero, sin ningún programa instalado.  
> Seguí cada paso **en orden**. No saltar pasos.

---

## ¿Qué es esta app?

Es un sistema que permite consultar si una persona puede donar sangre. Tiene chat por texto y por voz, respuesta en audio, dashboard con estadísticas y análisis de lenguaje natural.

La app tiene **dos partes** que hay que levantar por separado:

| Parte | Tecnología | Puerto |
|-------|-----------|--------|
| **Backend** | Python + FastAPI | `http://localhost:8000` |
| **Frontend** | Next.js (React) | `http://localhost:3000` |

Necesitás tener **dos terminales abiertas al mismo tiempo**: una para cada parte.

---

## PASO 0 — Instalar los programas base

### 0.1 — Python 3.11

1. Abrir el navegador e ir a: **https://www.python.org/downloads/**
2. Buscar y descargar **Python 3.11.x** (la versión 3.11, NO la 3.12 ni la 3.13)
3. Ejecutar el instalador que se descargó
4. **MUY IMPORTANTE:** en la primera pantalla del instalador, tildar la casilla que dice **"Add Python to PATH"** (está abajo del todo). Si no la tildás, nada va a funcionar.
5. Hacer clic en **"Install Now"**
6. Esperar que termine y cerrar el instalador

**Verificar que se instaló bien:** Abrir una terminal nueva (buscar "PowerShell" en el menú inicio) y escribir:
```
python --version
```
Tiene que aparecer algo como: `Python 3.11.9`  
Si dice que el comando no se reconoce, el Python no se instaló correctamente o faltó tildar el PATH.

---

### 0.2 — Node.js 20

Node.js es el entorno que necesita el frontend para funcionar.

1. Ir a: **https://nodejs.org/**
2. Descargar el botón verde que dice **"LTS"** (es la versión estable recomendada)
3. Ejecutar el instalador y hacer clic en "Next" en todas las pantallas (dejar todo por defecto)
4. Al final hacer clic en "Finish"

**Verificar:** Abrir una terminal nueva y escribir:
```
node --version
npm --version
```
Tienen que aparecer números de versión (por ejemplo `v20.x.x`).  
Si no aparecen, reiniciar la PC y probar de nuevo.

---

### 0.3 — FFmpeg (necesario para usar el micrófono con Whisper)

FFmpeg es una herramienta de audio/video que Whisper necesita para procesar el audio del micrófono.

1. Ir a: **https://www.gyan.dev/ffmpeg/builds/**
2. Buscar la sección "release builds" y descargar **ffmpeg-release-essentials.zip**
3. Una vez descargado, hacer click derecho sobre el archivo zip → **Extraer todo**
4. Elegir una carpeta para extraer (por ejemplo `C:\ffmpeg`) y hacer clic en Extraer
5. Ir a la carpeta donde se extrajo, entrar a la subcarpeta `bin`
6. Dentro de `bin` vas a ver 3 archivos: `ffmpeg.exe`, `ffplay.exe`, `ffprobe.exe`
7. Seleccionar los 3, copiarlos (Ctrl+C)
8. Ir a `C:\Windows\System32` y pegarlos ahí (Ctrl+V). Puede pedir permiso de administrador, aceptar.

**Verificar:** Abrir una terminal nueva y escribir:
```
ffmpeg -version
```
Tiene que aparecer información sobre la versión de FFmpeg.  
Si dice que el comando no se reconoce, revisar que los archivos se pegaron en `C:\Windows\System32`.

---

## PASO 1 — Copiar el proyecto a la nueva PC

Copiar la carpeta **DONARVERSION1** completa a la nueva PC. Puede ser por pendrive, red local, o como sea conveniente.

La estructura de carpetas tiene que quedar exactamente así:

```
C:\DONARVERSION1\
├── backend\
│   ├── main.py
│   ├── requirements.txt
│   ├── corpus.json          <-- este archivo es OBLIGATORIO
│   ├── database.py
│   ├── models.py
│   ├── ngrams.py
│   ├── nlp.py
│   ├── rules.py
│   ├── search.py
│   └── wer.py
├── frontend\
│   ├── app\
│   │   └── ... (varios archivos)
│   ├── package.json
│   └── ... (resto de archivos)
└── README.md
```

> Podés ponerla en otra letra o ruta (por ejemplo `D:\DONARVERSION1`), pero en todos los comandos de abajo reemplazá `C:\DONARVERSION1` por la ruta real que usaste.

---

## PASO 2 — Configurar y levantar el Backend (Python)

### 2.1 — Abrir una terminal en la carpeta del backend

Opción A — Desde el Explorador de Archivos:
1. Abrir el Explorador de Archivos y navegar hasta `C:\DONARVERSION1\backend`
2. Hacer clic en la barra de direcciones (donde dice la ruta), escribir `powershell` y presionar Enter

Opción B — Desde PowerShell directamente:
1. Buscar "PowerShell" en el menú inicio y abrirlo
2. Escribir el siguiente comando y presionar Enter:
```powershell
cd C:\DONARVERSION1\backend
```

---

### 2.2 — Crear el entorno virtual de Python

Un entorno virtual es un espacio aislado donde se instalan las librerías de esta app sin mezclarlas con el resto del sistema. Es una buena práctica y evita conflictos.

En la terminal, escribir:
```powershell
python -m venv venv
```

Esto crea una carpeta llamada `venv` dentro de `backend`. No pasa nada visible, simplemente crea la carpeta. No da ningún mensaje si funciona bien.

---

### 2.3 — Activar el entorno virtual

Esto le dice a Python que use el entorno virtual que acabás de crear.

**Si usás PowerShell (recomendado):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Si usás CMD (Símbolo del sistema):**
```cmd
venv\Scripts\activate.bat
```

Cuando se activa correctamente, vas a ver que al principio de la línea aparece `(venv)`:
```
(venv) PS C:\DONARVERSION1\backend>
```

Ese `(venv)` al principio significa que el entorno virtual está activo. Es importante que esté activo para el siguiente paso.

> **Error frecuente en PowerShell: "la ejecución de scripts está deshabilitada"**
>
> Si aparece ese error, ejecutar este comando primero:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Cuando pregunte si confirmar, escribir `S` y presionar Enter.  
> Después volver a intentar activar el venv con el comando de arriba.

---

### 2.4 — Instalar las librerías de Python

Con el `(venv)` activo en la terminal, escribir:
```powershell
pip install -r requirements.txt
```

Este comando lee el archivo `requirements.txt` y descarga automáticamente todas las librerías que necesita el backend. Las librerías que instala son:

- **FastAPI** — el framework web del servidor
- **Uvicorn** — el servidor que corre FastAPI
- **gTTS** — convierte texto a audio (Text-to-Speech)
- **openai-whisper** — transcripción de voz offline con IA
- **python-multipart** — para recibir archivos de audio
- **pydantic** — validación de datos
- **requests** — para hacer llamadas HTTP

La instalación puede tardar **5 a 15 minutos** dependiendo de la velocidad de internet. Es normal que tarde.

> **Nota importante sobre Whisper:** La librería de Whisper se instala ahora, pero el **modelo de IA** (el archivo que usa para transcribir) se descarga la **primera vez que se usa el micrófono** en la app. Ese archivo pesa aproximadamente **72 MB** y se descarga automáticamente. Necesitás internet esa primera vez.

---

### 2.5 — Iniciar el servidor del backend

Con el `(venv)` activo, escribir:
```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Si todo funcionó bien, vas a ver algo parecido a esto en la terminal:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [XXXX]
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Muy importante:** Dejar esta terminal abierta. El backend tiene que estar corriendo mientras usás la app. Si la cerrás, el backend se apaga.

**Verificar que funciona:** Abrir el navegador y entrar a:
```
http://localhost:8000
```
Tiene que aparecer en pantalla: `{"mensaje":"DONAR-APP funcionando"}`

Si eso aparece, el backend está funcionando correctamente.

---

## PASO 3 — Configurar y levantar el Frontend (Next.js)

Abrir una **segunda terminal** (NO cerrar la del backend). Repetir el proceso de abrir PowerShell pero esta vez navegando a la carpeta del frontend.

### 3.1 — Ir a la carpeta del frontend

```powershell
cd C:\DONARVERSION1\frontend
```

---

### 3.2 — Instalar las dependencias de JavaScript

```powershell
npm install
```

Este comando lee el archivo `package.json` y descarga todas las librerías de JavaScript/React necesarias. Las guarda en una carpeta llamada `node_modules` que se crea automáticamente.

Puede tardar entre 2 y 5 minutos. Es normal ver mucho texto pasando en la pantalla.

Al terminar vas a ver algo como:
```
added XXX packages in Xs
```

---

### 3.3 — Iniciar el servidor del frontend

```powershell
npm run dev
```

Si todo está bien, vas a ver algo como:
```
▲ Next.js 16.x.x
- Local:        http://localhost:3000
- Ready in X.Xs
```

**Muy importante:** Dejar esta terminal abierta también. Si la cerrás, el frontend se apaga.

---

## PASO 4 — Usar la aplicación

Con **ambas terminales corriendo** (la del backend y la del frontend), abrir el navegador y entrar a:

```
http://localhost:3000
```

La app debería cargar completamente. Vas a ver la interfaz de DONAR-APP con las pestañas: Consulta, Dashboard, N-gramas, IR/TF-IDF y WER.

---

## Resumen rápido para la próxima vez

Una vez que ya instalaste todo (Pasos 0, 1, 2.1-2.4, 3.1-3.2), la próxima vez solo necesitás hacer esto:

**Terminal 1 — Backend (no olvidar activar el venv):**
```powershell
cd C:\DONARVERSION1\backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend:**
```powershell
cd C:\DONARVERSION1\frontend
npm run dev
```

Abrir en el navegador: **http://localhost:3000**

---

## Solución de problemas frecuentes

### "python no se reconoce como un comando interno o externo"
Python no se agregó al PATH durante la instalación. Solución: desinstalar Python desde Panel de Control → Programas, y volver a instalarlo desde python.org asegurándose de tildar **"Add Python to PATH"** en la primera pantalla.

### "npm no se reconoce como un comando interno o externo"
Node.js no se instaló correctamente. Descargar de nuevo desde nodejs.org e instalar. Si sigue sin funcionar, reiniciar la PC.

### El frontend carga en http://localhost:3000 pero da error o no responde
El backend no está corriendo. Verificar que la Terminal 1 (backend) esté abierta y muestre el mensaje de "Application startup complete". Si no está corriendo, iniciarlo siguiendo el Paso 2.5.

### Error al activar el entorno virtual en PowerShell: "scripts deshabilitados"
Ejecutar este comando y confirmar con S:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Después intentar activar el venv de nuevo.

### Error relacionado con Whisper o el micrófono offline
FFmpeg no está instalado o no está en el PATH del sistema. Volver al Paso 0.3 y verificar que `ffmpeg -version` funciona en una terminal nueva.

### El modelo de Whisper no se descarga / da error de conexión
El modelo de Whisper necesita descargarse de internet la primera vez. Verificar que tenés conexión a internet y volver a intentar usar el micrófono en la app. El modelo se guarda localmente y no vuelve a descargar después de la primera vez.

### "No se encuentra corpus.json"
El archivo `corpus.json` es obligatorio y tiene que estar dentro de `backend\`. Verificar que se copió junto con el resto del proyecto.

### La base de datos da errores
El archivo `donar.db` se crea automáticamente la primera vez que inicia el backend. Si hay errores de base de datos, se puede borrar el archivo `donar.db` que está en `backend\` y reiniciar el servidor. Se crea solo de nuevo.

---

## Puertos y URLs de la app

| Servicio | URL | Para qué sirve |
|---------|-----|---------------|
| Frontend | http://localhost:3000 | Interfaz principal (abrir en el navegador) |
| Backend API | http://localhost:8000 | Servidor Python (no abrir directamente) |
| Docs interactivas | http://localhost:8000/docs | Documentación y prueba de la API |

---

## Versiones de software utilizadas

| Software | Versión |
|---------|---------|
| Python | 3.11.x |
| FastAPI | 0.136.0 |
| Uvicorn | 0.44.0 |
| Node.js | 20.x (LTS) |
| Next.js | 16.2.4 |
| React | 19.2.4 |
