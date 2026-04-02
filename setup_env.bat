@echo off

SET "VENV_DIR=.venv"
SET "REQ_FILE=requirements.txt"
SET "APP_FILE=%CD%\tui_app.py"

REM 1. Create virtual environment if it doesn't exist
IF NOT "-d" "%VENV_DIR%" (
  echo "Creating virtual environment..."
  python "-m" "venv" "%VENV_DIR%"
)

REM 2. Activate the environment
echo "Activating virtual environment..."
source "%VENV_DIR%\bin\activate"

REM 3. Fetch and install requirements via pip
IF "-f" "%REQ_FILE%" (
  echo "Installing modules from %REQ_FILE%..."
  pip "install" "-r" "%REQ_FILE%"
) ELSE (
  echo "Warning: %REQ_FILE% not found. Skipping installations."
)

REM 4. Execute the application
IF "-f" "%APP_FILE%" (
  echo "Starting %APP_FILE%..."
  python "%APP_FILE%"
) ELSE (
  echo "App file %APP_FILE% not found. Environment is ready for manual use."
)