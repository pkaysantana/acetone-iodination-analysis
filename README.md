# Experiment 5: Iodination of Acetone - Kinetic Investigation

**Research-Founder Mode Architecture**

## 1. Project Overview

This repository hosts a "System" approach to the classic acid-catalysed iodination of acetone. It is architected into three layers to maximise pedagogical, industrial, and scientific leverage:

* **Layer A (Scientific)**: rigorous mechanistic decoupling of rate laws (Pseudo-Zero-Order w.r.t. $I_2$).
* **Layer B (Engineering)**: A Python-based "Kinetic Engine" for automated data processing and Arrhenius modelling.
* **Layer C (Strategic)**: Analysis of industrial scalability (tear gas synthesis, process control) and innovation loops (salt effects).

## 2. Directory Structure

* `data/`:
  * `raw_csv/`: Place spectrometer output CSVs here.
  * `metadata/`: Store temperature logs and conditions.
* `src/`:
  * `rate_calculator.py`: Core logic for determining rates ($k_{obs}$) from absorbance data.
  * `arrhenius_plotter.py`: Calculates Activation Energy ($E_a$) and Frequency Factor ($A$).
  * `config.yaml`: Central experiment configuration (molarities, extinction coefficients).
* `output/`: Generated plots and reports.

## 3. Installation

Ensure you have Python 3.9+ installed.

```bash
pip install pandas numpy scipy pyyaml matplotlib
```

## 4. Usage

### Step 1: Configuration

Edit `src/config.yaml` to match your specific conditions:

```yaml
experiment:
  reagents:
    acetone_stock_molarity: 4.0
    acid_anion: "Cl-" # Important for salt effect analysis
  parameters:
    wavelength_nm: 410
    extinction_coefficient: 900 # Update based on calibration
```

### Step 2: Data Ingestion

Drop your raw CSV files into `data/raw_csv/`.

* **Required Format**: Columns must include `Time (s)` and `Absorbance`.
* *Note*: The engine auto-detects column variations like `Time_s`.

### Step 3: Run Analysis

**Calculate Reaction Rates:**

```bash
python src/rate_calculator.py
```

*This will process all CSVs in the data folder and output rates ($M/s$) and linearity ($R^2$).*

**Generate Arrhenius Plot:**

```bash
python src/arrhenius_plotter.py
```

*Requires temperature data points to be manually input into the script or a separate metadata file (feature incoming).*

## 5. Strategic Insights

See `output/reports/strategic_analysis.md` for a deep dive into:

* **Pedagogical Leverage**: Using "Zero Order" results to challenge collision theory mental models.
* **Industrial Application**: Controlling hazardous halogenation via distinct pH modulation.
* **Innovation Loop**: Future improvements for "Salt Effect" variance and Stopped-Flow integration.
