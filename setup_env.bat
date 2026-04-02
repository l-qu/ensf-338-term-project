@echo off
SETLOCAL

SET "VENV_DIR=%~dp0.venv"
SET "REQ_FILE=%~dp0requirements.txt"
SET "APP_FILE=%~dp0tui_app.py"

REM 1. Create virtual environment if it doesn't exist
IF NOT EXIST "%VENV_DIR%" (
  echo Creating virtual environment...
  python -m venv "%VENV_DIR%"
)

REM 2. Activate the environment
echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate"

REM 3. Fetch and install requirements via pip
IF EXIST "%REQ_FILE%" (
  echo Installing modules from %REQ_FILE%...
  pip install -r "%REQ_FILE%"
) ELSE (
  echo Warning: %REQ_FILE% not found. Skipping installations.
)

REM 4. Execute the application
IF EXIST "%APP_FILE%" (
  echo Starting %APP_FILE%...
  python "%APP_FILE%"
) ELSE (
  echo App file %APP_FILE% not found. Environment is ready for manual use.
)

ENDLOCAL