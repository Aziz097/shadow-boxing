@echo off
REM Shadow Boxing Game Launcher for Windows
REM This script checks dependencies and runs the game

echo ========================================
echo   Shadow Boxing Game Launcher
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher
    pause
    exit /b 1
)

echo [1/3] Checking Python installation...
python --version
echo.

REM Check if required packages are installed
echo [2/3] Checking dependencies...
python -c "import opencv as cv2" >nul 2>&1
if errorlevel 1 (
    echo Dependencies not found. Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo Dependencies installed successfully!
) else (
    python -c "import mediapipe" >nul 2>&1
    if errorlevel 1 (
        echo Dependencies not found. Installing requirements...
        pip install -r requirements.txt
        if errorlevel 1 (
            echo ERROR: Failed to install dependencies
            pause
            exit /b 1
        )
        echo Dependencies installed successfully!
    ) else (
        python -c "import pygame" >nul 2>&1
        if errorlevel 1 (
            echo Dependencies not found. Installing requirements...
            pip install -r requirements.txt
            if errorlevel 1 (
                echo ERROR: Failed to install dependencies
                pause
                exit /b 1
            )
            echo Dependencies installed successfully!
        ) else (
            echo All dependencies are installed.
        )
    )
)

echo.
echo [3/3] Starting Shadow Boxing...
echo.
echo ========================================
echo   Game Controls:
echo   SPACE - Start game
echo   ESC   - Pause/Resume
echo   Q     - Quit game
echo ========================================
echo.

REM Run the game
python main.py

if errorlevel 1 (
    echo.
    echo ERROR: Game crashed or exited with an error
    pause
    exit /b 1
)

echo.
echo Game closed successfully.
pause