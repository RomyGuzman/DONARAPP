Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\DONARAPP\backend; .\venv\Scripts\Activate.ps1; uvicorn main:app --reload"

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\DONARAPP\frontend; npm run dev"