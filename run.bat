@echo off
REM Script to start all project components on Windows

setlocal enabledelayedexpansion

echo ======================================
echo 🚀 Starting Temporal QnA Agent
echo ======================================
echo.

REM Check if .env exists
if not exist .env (
    echo ❌ .env file not found!
    echo Please copy .env.example to .env and configure your credentials
    exit /b 1
)

REM Check if venv exists
if not exist .venv (
    echo ❌ Virtual environment not found!
    echo Run: python setup.py
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

echo ✅ Virtual environment activated
echo.

REM Start worker in new window
echo 🔧 Starting Temporal Worker...
start "Temporal Worker" cmd /k "call .venv\Scripts\activate.bat && python worker.py"
timeout /t 3 /nobreak >nul

REM Start API in new window
echo 🌐 Starting FastAPI...
start "FastAPI" cmd /k "call .venv\Scripts\activate.bat && python api/main.py"
timeout /t 3 /nobreak >nul

REM Start frontend
echo 🎨 Starting Streamlit...
streamlit run frontend/app.py

endlocal
