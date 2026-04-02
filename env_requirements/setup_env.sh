#!/bin/bash

VENV_DIR=".venv"
REQ_FILE="requirements.txt"
APP_FILE="../tui_app.py"

# 1. Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python -m venv $VENV_DIR
fi

# 2. Activate the environment
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

# 3. Fetch and install requirements via pip
if [ -f "$REQ_FILE" ]; then
    echo "Installing modules from $REQ_FILE..."
    pip install -r $REQ_FILE
else
    echo "Warning: $REQ_FILE not found. Skipping installations."
fi

# 4. Execute the application
if [ -f "$APP_FILE" ]; then
    echo "Starting $APP_FILE..."
    python $APP_FILE
else
    echo "App file $APP_FILE not found. Environment is ready for manual use."
fi