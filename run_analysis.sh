#!/bin/bash
echo "========================================================"
echo "  Experiment 5: Iodination of Acetone - Kinetic Engine"
echo "========================================================"
echo ""
echo "[1/3] Checking environment..."
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 could not be found."
    exit 1
fi

echo "[2/3] Running Analysis Orchestrator..."
python3 src/orchestrator.py

echo ""
echo "[3/3] Analysis Complete."
echo "      Report generated at: output/reports/final_report.md"
echo ""
read -p "Press Enter to exit..."
