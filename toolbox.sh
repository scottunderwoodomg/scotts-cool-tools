#!/bin/bash

# TODO: Add stept to setup script to define $sct_home in setup script 
BASE_DIR=$SCT_HOME
VENV_DIR="$BASE_DIR/venv"

# Take the Python script path as a user input
TOOL_NAME=$1
SCRIPT_PATH="tools/$TOOL_NAME/run.py"

# Activate the virtual environment, update pythonpath and run the script
source "$VENV_DIR/bin/activate" && PYTHONPATH=$PYTHONPATH:$BASE_DIR && python "$BASE_DIR/$SCRIPT_PATH"
