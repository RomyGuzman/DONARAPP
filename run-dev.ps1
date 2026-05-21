Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\DONARVERSION1\backend; .\venv\Scripts\Activate.ps1; uvicorn main:app --reload"

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\DONARVERSION1\frontend; npm run dev"