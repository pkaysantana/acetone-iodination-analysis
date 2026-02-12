import os
import glob
import re
import yaml
import pandas as pd
import sys

# Ensure src is in path
if 'src' not in sys.path:
    sys.path.append('src')

from rate_calculator import KineticAnalyzer
from arrhenius_plotter import plot_arrhenius

def load_config(config_path="src/config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def extract_temperature(filename):
    # Match pattern like "run_298K.csv" or "298K"
    match = re.search(r"(\d+)K", filename)
    if match:
        return int(match.group(1))
    return None

def main():
    print("=== Experiment 5 Orchestrator Started ===")
    
    # 1. Load Configuration
    config = load_config()
    params = config['experiment']['parameters']
    reagents = config['experiment']['reagents']
    
    path_length = params['path_length_cm']
    epsilon = params.get('extinction_coefficient', 900)
    acid_anion = reagents.get('acid_anion', 'Cl-')
    salt_factors = reagents.get('salt_factors', {'Cl-': 1.0})
    
    print(f"Configuration Loaded.")
    print(f"  Path Length: {path_length} cm")
    print(f"  Extinction Coeff: {epsilon} M-1cm-1")
    print(f"  Acid Anion: {acid_anion}")
    
    # 2. Scan Files
    data_dir = "data/raw_csv"
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
    
    if not csv_files:
        print(f"\n[INFO] No data found in {data_dir}.")
        print("       Checking 'data/examples/' for demonstration data...")
        data_dir = "data/examples"
        csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
        
        if not csv_files:
             print("\n[WARNING] No CSV files found in 'data/raw_csv/' or 'data/examples/'.")
             print("           Please place your experimental data in 'data/raw_csv/'.")
             print("           Filenames must contain the temperature (e.g., 'run_298K.csv').")
             input("\nPress Enter to exit...")
             return
        else:
            print(f"       Found {len(csv_files)} example files. Running in DEMO mode.")

    results = []
    
    print(f"\nFound {len(csv_files)} files in '{data_dir}'. Processing...")
    
    for filepath in csv_files:
        filename = os.path.basename(filepath)
        
        # Extract Temperature
        temp_k = extract_temperature(filename)
        if temp_k is None:
            print(f"  [Skipping] {filename}: No temperature found in name.")
            continue
            
        # Analyze Kinetics
        try:
            analyzer = KineticAnalyzer(filepath, path_length=path_length, epsilon=epsilon)
            k_obs, r_squared = analyzer.calculate_rate()
            
            # Salt Correction
            k_intrinsic, factor = analyzer.calculate_intrinsic_rate(k_obs, acid_anion, salt_factors)
            
            print(f"  [Processed] {filename}: T={temp_k}K, k_obs={k_obs:.2e}, k_int={k_intrinsic:.2e}, R2={r_squared:.4f}")
            
            results.append({
                "filename": filename,
                "temperature_k": temp_k,
                "k_observed": k_obs,
                "k_intrinsic": k_intrinsic,
                "r_squared": r_squared
            })
            
        except Exception as e:
            print(f"  [Error] {filename}: {e}")
            
    if not results:
        print("No valid results to process.")
        return

    # 3. Arrhenius Analysis
    print("\nPerforming Arrhenius Analysis...")
    df_results = pd.DataFrame(results)
    df_results.sort_values("temperature_k", inplace=True)
    
    # Used Intrinsic Rate for Arrhenius
    temps = df_results["temperature_k"].tolist()
    k_ints = df_results["k_intrinsic"].tolist()
    
    arrhenius_stats = plot_arrhenius(temps, k_ints, output_path="output/plots/final_arrhenius.png")
    
    print(f"  E_a: {arrhenius_stats['E_a_kJ_mol']:.2f} kJ/mol")
    print(f"  A: {arrhenius_stats['A']:.2e}")
    print(f"  Arrhenius R2: {arrhenius_stats['R_squared']:.4f}")
    
    # 4. Generate Report
    report_path = "output/reports/final_report.md"
    with open(report_path, "w") as f:
        f.write("# Experiment 5: Final Kinetic Analysis Report\n\n")
        f.write(f"**Date**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Anion Configuration**: {acid_anion} (Salt Factor: {salt_factors.get(acid_anion, 1.0)})\n\n")
        
        f.write("## 1. Thermodynamic Parameters\n")
        f.write(f"- **Activation Energy ($E_a$)**: {arrhenius_stats['E_a_kJ_mol']:.2f} kJ/mol\n")
        f.write(f"- **Pre-exponential Factor ($A$)**: {arrhenius_stats['A']:.2e} $s^{-1}$\n")
        f.write(f"- **Arrhenius Linearity ($R^2$)**: {arrhenius_stats['R_squared']:.4f}\n\n")
        f.write("![Arrhenius Plot](../plots/final_arrhenius.png)\n\n")
        
        f.write("## 2. Experimental Data Summary\n")
        f.write("| File | Temp (K) | $k_{obs}$ (M/s) | $k_{intrinsic}$ (M/s) | Linearity ($R^2$) |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        
        for _, row in df_results.iterrows():
            f.write(f"| {row['filename']} | {row['temperature_k']} | {row['k_observed']:.2e} | {row['k_intrinsic']:.2e} | {row['r_squared']:.4f} |\n")
            
    print(f"\nReport generated at {report_path}")

if __name__ == "__main__":
    main()
