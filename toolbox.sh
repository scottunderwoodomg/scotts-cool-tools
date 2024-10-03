#!/bin/bash

# Replace "/path/to/venv" with the path to your virtual environment
BASE_DIR="/path/to/venv"
VENV_DIR="$BASE_DIR/venv"

# Take the Python script path as a user input
TOOL_NAME=$1
SCRIPT_PATH="tools/$TOOL_NAME.py"

# Activate the virtual environment and run the script
source "$VENV_DIR/bin/activate" && python "$BASE_DIR/$SCRIPT_PATH"
