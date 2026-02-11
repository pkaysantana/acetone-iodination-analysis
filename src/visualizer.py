import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

class KineticVisualizer:
    def __init__(self, output_dir="output/plots"):
        self.output_dir = output_dir
        # Ensure output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Set Publication-Grade Style
        # Using a style that mimics seaborn-whitegrid but forces specific font sizes/latex if avail
        try:
            sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
        except Exception:
            # Fallback if seaborn has issues
            plt.style.use('ggplot')

    def plot_kinetics(self, df, slope, intercept, filename_base):
        """
        Generates a dual-axis plot:
        - Left Y: Absorbance (Raw Data)
        - Right Y: [I2] (Calculated)
        - Bottom X: Time (s)
        - Top X: Residuals (Separate subplot)
        
        Args:
            df: DataFrame with 'Time_s', 'Absorbance', 'concentration'
            slope: Linear regression slope (for plotting the fit line)
            intercept: Linear regression intercept
            filename_base: Base name for the output file
        """
        
        # Calculate predicted values for the fit line
        df['fit_concentration'] = slope * df['Time_s'] + intercept
        df['residuals'] = df['concentration'] - df['fit_concentration']
        
        # Setup Figure with GridSpec for Residuals
        fig = plt.figure(figsize=(10, 8))
        gs = fig.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.3)
        
        # --- Main Plot (Kinetics) ---
        ax_main = fig.add_subplot(gs[0])
        
        # Primary Axis: Concentration (The Scientific Truth)
        sns.scatterplot(data=df, x='Time_s', y='concentration', ax=ax_main, label='Experimental Data', color='blue', s=60, edgecolor='w')
        ax_main.plot(df['Time_s'], df['fit_concentration'], color='red', linestyle='--', linewidth=2, label=f'Linear Fit (Rate={-slope:.2e} M/s)')
        
        ax_main.set_ylabel(r'$[I_2]$ / M', fontsize=14)
        ax_main.set_xlabel('Time / s', fontsize=12) # Shared x-axis label might be redundant but good for clarity
        ax_main.set_title(f'Kinetics Analysis: {filename_base}', fontsize=16, pad=15)
        ax_main.legend(loc='upper right', frameon=True)
        ax_main.grid(True, linestyle=':', alpha=0.6)

        # Secondary Axis: Absorbance (The Raw Signal)
        # We need to map the Concentration limits back to Absorbance
        # A = epsilon * b * C -> Scale factor is epsilon * b
        # However, purely geometric twinx is easier for visualization alignment
        
        # Let's derive the scaling factor from the data logic
        # Ratio = Absorbance / Concentration (assuming constant path length & epsilon)
        # We can just set the limits of twinx to be limits of ax_main * (Mean Abs / Mean Conc)
        # Or better, just plot Absorbance on twin axis to show the relationship directly
        
        ax_raw = ax_main.twinx()
        # We don't plot data here to avoid duplication, we just sync the limits
        # Get current ylim of concentration
        y1, y2 = ax_main.get_ylim()
        
        # Calculate conversion factor (epsilon) roughly from data
        # epsilon ~ Abs / Conc
        # typical_epsilon = df['Absorbance'].mean() / df['concentration'].mean()
        # y1_abs = y1 * typical_epsilon
        # y2_abs = y2 * typical_epsilon
        
        # Actually, let's just create a dummy plot to set the axis correctly if we want "Raw Absorbance" on the right
        # But twinx is independent.
        # Let's simple plotting:
        # ax_raw.set_ylim(y1 * typical_epsilon, y2 * typical_epsilon) 
        # But this assumes 0 intercept for Beer's law. Safe enough for this exp.
        
        # Alternative: Just label it "Equivalent Absorbance"
        # Let's try to find the epsilon used. It's not passed here.
        # Let's infer it from the data ratio
        if df['concentration'].mean() != 0:
            ratio = df['Absorbance'].mean() / df['concentration'].mean()
            ax_raw.set_ylim(y1 * ratio, y2 * ratio)
            ax_raw.set_ylabel('Absorbance @ 410nm', fontsize=14, color='gray')
            ax_raw.tick_params(axis='y', labelcolor='gray')
            ax_raw.grid(False) # Don't overlap grids
        
        # --- Residual Plot ---
        ax_res = fig.add_subplot(gs[1], sharex=ax_main)
        sns.residplot(data=df, x='Time_s', y='concentration', lowess=False, color='green', ax=ax_res, scatter_kws={'s': 40, 'edgecolor': 'w'})
        ax_res.axhline(0, color='black', linestyle='-', linewidth=1)
        ax_res.set_ylabel('Residuals / M', fontsize=10)
        ax_res.set_xlabel('Time / s', fontsize=12)
        ax_res.grid(True, linestyle=':', alpha=0.6)

        # Save
        save_path = os.path.join(self.output_dir, f"{filename_base}_kinetics.png")
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path

if __name__ == "__main__":
    # Test stub
    pass
