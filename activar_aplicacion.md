# Cómo activar DONAR-APP

Necesitás tener **dos ventanas de PowerShell abiertas** al mismo tiempo: una para el backend y otra para el frontend.

---

## Ventana 1 — Backend (FastAPI)

1. Abrí PowerShell
2. Navegá a la carpeta del backend:
   ```powershell
   cd C:\DONARVERSION1\backend
   ```
3. Activá el entorno virtual:
   ```powershell
   venv\Scripts\activate
   ```
   Vas a ver que el prompt cambia y aparece `(venv)` al principio.

4. Iniciá el servidor:
   ```powershell
   python -m uvicorn main:app --reload
   ```

5. Esperá hasta ver este mensaje en la consola:
   ```
   Application startup complete.
   ```
   Eso significa que el backend está corriendo en `http://localhost:8000`.

**Dejá esta ventana abierta mientras usás la aplicación.**

---

## Ventana 2 — Frontend (Next.js)

1. Abrí una segunda ventana de PowerShell (sin cerrar la primera)
2. Navegá a la carpeta del frontend:
   ```powershell
   cd C:\DONARVERSION1\frontend
   ```
3. Iniciá el servidor de desarrollo:
   ```powershell
   npm run dev
   ```
4. Esperá hasta ver este mensaje en la consola:
   ```
   ▲ Next.js
   - Local: http://localhost:3000
   ✓ Ready
   ```
   Eso significa que el frontend está corriendo en `http://localhost:3000`.

**Dejá esta ventana abierta también.**

---

## Abrir la aplicación en el navegador

1. Abrí tu navegador (Chrome, Edge, Firefox, etc.)
2. En la barra de direcciones escribí:
   ```
   http://localhost:3000
   ```
3. Presioná Enter y la aplicación va a cargar.

---

## Resumen rápido

| Paso | Ventana | Carpeta | Comandos |
|------|---------|---------|----------|
| 1 | PowerShell 1 (Backend) | `C:\DONARVERSION1\backend` | `venv\Scripts\activate` luego `python -m uvicorn main:app --reload` |
| 2 | PowerShell 2 (Frontend) | `C:\DONARVERSION1\frontend` | `npm run dev` |
| 3 | Navegador | — | Ir a `http://localhost:3000` |

---

## Para cerrar la aplicación

En cada ventana de PowerShell presioná **Ctrl + C** para detener el servidor.
