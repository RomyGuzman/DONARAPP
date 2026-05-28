# DONAR-APP — Instalación en PC nueva

## 1. Instalar estos programas primero

| Programa | Dónde bajarlo | Nota |
|---------|--------------|------|
| Python 3.11 | https://www.python.org/downloads/ | Tildar **"Add Python to PATH"** al instalar |
| Node.js 20 LTS | https://nodejs.org/ | Instalar con todo por defecto |
| FFmpeg | https://www.gyan.dev/ffmpeg/builds/ → `ffmpeg-release-essentials.zip` | Extraer y copiar los `.exe` de la carpeta `bin` a `C:\Windows\System32` |

---

## 2. Abrir el proyecto en VSCode

1. Abrir VSCode
2. Ir a **Archivo → Abrir carpeta** y seleccionar `C:\DONARVERSION1`
3. Abrir la consola integrada con `Ctrl + Ñ`

---

## 3. Instalar librerías del Backend

En la consola de VSCode, pegar estos comandos uno por uno:

```powershell
cd C:\DONARVERSION1\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 4. Instalar librerías del Frontend

```powershell
cd C:\DONARVERSION1\frontend
npm install
```

---

## 5. Levantar la app

```powershell
powershell -ExecutionPolicy Bypass -File C:\DONARVERSION1\run-dev.ps1
```

Se abren dos ventanas automáticamente: una con el backend y otra con el frontend.

Abrir en el navegador: **http://localhost:3000**
