# Kinetic Engine: Experiment 5 (Iodination of Acetone)

## Overview

This **Kinetic Engine** is an automated analysis pipeline designed for Experiment 5. It transforms raw spectrophotometer data into publication-ready kinetic reports. It features **Automatic Rate Calculation**, **Salt Effect Normalisation** (Hofmeister Series), and **Robust Regression (RANSAC)** to handle experimental noise.

## Quick Start

1. **Drop Data**: Place your `.csv` files in `data/raw_csv/`.
2. **Configure**: Edit `src/config.yaml` if you changed stock solution molarities.
3. **Run (CLI)**: Double-click `run_analysis.bat`.
4. **Run (Web Dashboard)**:

    ```bash
    # 1. Activate Environment
    # Windows:
    .\.venv\Scripts\activate
    # Mac/Linux:
    source .venv/bin/activate
    
    # 2. Launch (Robust command)
    python -m streamlit run src/dashboard.py
    ```

5. **View Report**: Open `output/reports/final_report.md`.

---

## Naming Convention (CRITICAL)

The orchestrator relies on filenames to extract temperature data for the Arrhenius plot. You **MUST** include the temperature in Kelvin in the filename.

- ✅ **Good**: `run_298K.csv`, `acetone_308K_trial1.csv`
- ❌ **Bad**: `trial1.csv`, `monday_lab.csv`

---

## Directory Structure

- `data/raw_csv/`: **INPUT**. Place your experimental files here.
- `data/examples/`: Contains synthetic demo data (used if raw_csv is empty).
- `output/plots/`: Generated kinetic graphs and Arrhenius plot.
- `output/reports/`: Final Markdown summary.
- `src/`: Source code (`config.yaml`, `rate_calculator.py`, etc.).

## Configuration (`src/config.yaml`)

- **Reagents**: Set molarities of Acetone, HCl, and Iodine stocks.
- **Anion Effect**: Change `acid_anion` to `Cl-`, `SO4--`, or `ClO4-` to automatically apply Hofmeister corrections.

## Robustness

If your data is noisy ($R^2 < 0.98$), the engine automatically engages **RANSAC** (Robust Regression) to ignore outliers (bubbles, mixing artifacts) and salvage the rate constant.

---
