#!/bin/bash
# Shadow Boxing Game Launcher for Linux/Mac
# This script checks dependencies and runs the game

echo "========================================"
echo "  Shadow Boxing Game Launcher"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

echo "[1/3] Checking Python installation..."
python3 --version
echo ""

# Check if required packages are installed
echo "[2/3] Checking dependencies...
if ! python3 -c "import cv2" &> /dev/null; then
    echo "Dependencies not found. Installing requirements..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
    echo "Dependencies installed successfully!"
elif ! python3 -c "import mediapipe" &> /dev/null; then
    echo "Dependencies not found. Installing requirements..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
    echo "Dependencies installed successfully!"
elif ! python3 -c "import pygame" &> /dev/null; then
    echo "Dependencies not found. Installing requirements..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
    echo "Dependencies installed successfully!"
else
    echo "All dependencies are installed."
fi

echo ""
echo "[3/3] Starting Shadow Boxing..."
echo ""
echo "========================================"
echo "  Game Controls:"
echo "  SPACE - Start game"
echo "  ESC   - Pause/Resume"
echo "  Q     - Quit game"
echo "========================================"
echo ""

# Run the game
python3 main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Game crashed or exited with an error"
    exit 1
fi

echo ""
echo "Game closed successfully."