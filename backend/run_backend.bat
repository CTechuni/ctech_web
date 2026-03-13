@echo off
echo Starting CTech Backend...
set VENV_PATH=.\.venv
if not exist %VENV_PATH% (
    echo Error: %VENV_PATH% folder not found.
    echo Please ensure you are in the 'backend' directory.
    pause
    exit /b 1
)
echo Using virtual environment: %VENV_PATH%
%VENV_PATH%\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
