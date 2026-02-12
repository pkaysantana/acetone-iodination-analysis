@echo off
echo ========================================================
echo   Experiment 5: Iodination of Acetone - Kinetic Engine
echo ========================================================
echo.
echo [1/3] Checking environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b
)

echo [2/3] Running Analysis Orchestrator...
python src/orchestrator.py

echo.
echo [3/3] Analysis Complete.
echo       Report generated at: output/reports/final_report.md
echo.
pause
