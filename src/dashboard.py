import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import plotly.express as px
import plotly.graph_objects as go
import re

# Ensure src is in path
if 'src' not in sys.path:
    sys.path.append('src')

from rate_calculator import KineticAnalyzer
from arrhenius_plotter import plot_arrhenius
import yaml

# --- Config & Setup ---
st.set_page_config(page_title="Kinetic Engine", layout="wide", page_icon="🧪")

def load_config_defaults():
    try:
        with open("src/config.yaml", "r") as f:
            return yaml.safe_load(f)['experiment']
    except Exception:
        return {}

defaults = load_config_defaults()
default_reagents = defaults.get('reagents', {})
default_params = defaults.get('parameters', {})

# --- Sidebar ---
st.sidebar.header("🧪 Experiment Config")

# Molarities
st.sidebar.subheader("Reagents")
conc_acetone = st.sidebar.number_input("[Acetone]₀ (M)", value=default_reagents.get('acetone_stock_molarity', 4.0))
conc_hcl = st.sidebar.number_input("[H⁺]₀ (M)", value=default_reagents.get('hcl_stock_molarity', 1.0))
conc_iodine = st.sidebar.number_input("[I₂]₀ (M)", value=default_reagents.get('iodine_stock_molarity', 0.005), format="%.4f")

# Salt Effect
st.sidebar.subheader("Salt Effect (Hofmeister)")
anion_options = ["Cl-", "SO4--", "ClO4-"]
default_anion = default_reagents.get('acid_anion', 'Cl-')
if default_anion not in anion_options:
    anion_options.append(default_anion)
acid_anion = st.sidebar.selectbox("Acid Anion", anion_options, index=anion_options.index(default_anion))

salt_factors = default_reagents.get('salt_factors', {"Cl-": 1.0, "SO4--": 1.4, "ClO4-": 0.9})
st.sidebar.info(f"Salt Factor ({acid_anion}): **{salt_factors.get(acid_anion, 1.0)}**")

# Constants
st.sidebar.subheader("Parameters")
epsilon = st.sidebar.number_input("Extinction Coeff (ε)", value=default_params.get('extinction_coefficient', 900))
path_length = st.sidebar.number_input("Path Length (cm)", value=default_params.get('path_length_cm', 1.0))

# File Uploader
st.sidebar.subheader("Data Upload")
uploaded_files = st.sidebar.file_uploader("Upload CSVs (Filename must contain Temp, e.g. 'run_298K.csv')", 
                                        type="csv", accept_multiple_files=True)

# --- Main Interface ---
st.title("⚗️ Kinetic Engine: Iodination of Acetone")
st.markdown("""
This dashboard automates the kinetic analysis of the acid-catalyzed iodination of acetone.
It calculates **Reaction Rates**, **Activation Energy ($E_a$)**, and corrects for **Salt Effects**.
""")

# Equations
col1, col2 = st.columns(2)
with col1:
    st.latex(r"Rate = k_{obs}[Acetone]^1 [H^+]^1 [I_2]^0")
with col2:
    st.latex(r"\ln k = -\frac{E_a}{R} \left( \frac{1}{T} \right) + \ln A")

# Processing Logic
if uploaded_files:
    results = []
    plot_data = {} # Store data for plotting
    
    with st.spinner("Analyzing Kinetics..."):
        for uploaded_file in uploaded_files:
            # Save to temp for Analyzer
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                # Extract Temp
                match = re.search(r"(\d+)K", uploaded_file.name)
                temp_k = int(match.group(1)) if match else None
                
                # Analyze
                analyzer = KineticAnalyzer(temp_path, path_length=path_length, epsilon=epsilon)
                k_obs, r_squared = analyzer.calculate_rate()
                
                # Salt Correction
                k_intrinsic, factor = analyzer.calculate_intrinsic_rate(k_obs, acid_anion, salt_factors)
                
                results.append({
                    "Filename": uploaded_file.name,
                    "Temp (K)": temp_k,
                    "k_obs (M/s)": k_obs,
                    "k_int (M/s)": k_intrinsic,
                    "R²": r_squared
                })
                
                # Store for plotting
                plot_data[uploaded_file.name] = analyzer.data
                
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {e}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

    if results:
        df_results = pd.DataFrame(results)
        
        # --- Tab View ---
        tab1, tab2, tab3 = st.tabs(["📊 Results", "📈 Kinetic Traces", "🔥 Arrhenius Plot"])
        
        with tab1:
            st.dataframe(df_results.style.format({
                "k_obs (M/s)": "{:.2e}",
                "k_int (M/s)": "{:.2e}",
                "R²": "{:.4f}"
            }))
            
            # CSV Download
            csv = df_results.to_csv(index=False).encode('utf-8')
            st.download_button("Download Results CSV", csv, "kinetic_results.csv", "text/csv")
            
            # Markdown Report Generation
            def generate_markdown_report(df, ea, a, r2_arr):
                md = f"# Kinetic Analysis Report\n\n"
                md += f"**Date**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                md += f"## Thermodynamic Parameters\n"
                md += f"- **Activation Energy ($E_a$)**: {ea/1000:.2f} kJ/mol\n"
                md += f"- **Pre-exponential Factor ($A$)**: {a:.2e} s⁻¹\n"
                md += f"- **Arrhenius Linearity ($R^2$)**: {r2_arr:.4f}\n\n"
                md += f"## Data Summary\n"
                md += df.to_markdown(index=False)
                return md

            if 'E_a' in locals():
                report_md = generate_markdown_report(df_results, E_a, A, r_val**2)
                st.download_button("Download Full Report (MD)", report_md, "final_report.md", "text/markdown")


        with tab2:
            st.subheader("Concentration vs. Time")
            selected_file = st.selectbox("Select Run", df_results["Filename"])
            if selected_file:
                dat = plot_data[selected_file]
                fig = px.scatter(dat, x="Time_s", y="concentration", title=f"Kinetics: {selected_file}")
                
                # Add fit line
                # Recalculate fit for plotting
                row = df_results[df_results["Filename"] == selected_file].iloc[0]
                rate = row["k_obs (M/s)"]
                # slope is -rate. Intercept we estimate from data
                # Simple OLS for viz line
                from scipy.stats import linregress
                slope, intercept, _, _, _ = linregress(dat["Time_s"], dat["concentration"])
                
                fig.add_trace(go.Scatter(x=dat["Time_s"], y=slope*dat["Time_s"]+intercept, mode='lines', name='Fit'))
                st.plotly_chart(fig, use_container_width=True)

        with tab3:
            st.subheader("Arrhenius Analysis")
            df_arrhenius = df_results.dropna(subset=["Temp (K)"]).copy()
            if len(df_arrhenius) > 2:
                df_arrhenius = df_arrhenius.sort_values("Temp (K)")
                temps = df_arrhenius["Temp (K)"].values
                k_ints = df_arrhenius["k_int (M/s)"].values
                
                # Calculate Ea
                temp_inv = 1 / temps
                ln_k = np.log(k_ints)
                from scipy import stats
                slope, intercept, r_val, _, _ = stats.linregress(temp_inv, ln_k)
                E_a = -slope * 8.314
                A = np.exp(intercept)
                
                st.metric("Activation Energy ($E_a$)", f"{E_a/1000:.2f} kJ/mol")
                st.metric("Pre-exponential Factor ($A$)", f"{A:.2e} s⁻¹")
                st.metric("Arrhenius Linearity ($R^2$)", f"{r_val**2:.4f}")
                
                # Plot
                fig_arr = px.scatter(x=temp_inv, y=ln_k, labels={"x": "1/T (K⁻¹)", "y": "ln(k)"}, title="Arrhenius Plot")
                fig_arr.add_trace(go.Scatter(x=temp_inv, y=slope*temp_inv+intercept, mode='lines', name='Fit'))
                st.plotly_chart(fig_arr, use_container_width=True)
            else:
                st.warning("Need at least 3 runs with Temperatures to calculate Arrhenius parameters.")

else:
    st.info("👆 Upload CSV files to begin analysis. Use the examples in `data/examples` if you don't have data yet.")
    
    # Show example data structure
    st.markdown("### Example Data Format")
    st.code("Time (s), Absorbance\n0, 0.850\n10, 0.845\n...", language="csv")
