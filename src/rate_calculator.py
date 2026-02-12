import pandas as pd
import numpy as np
from scipy.stats import linregress
try:
    from sklearn.linear_model import RANSACRegressor
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
import yaml
import os
import sys

# Ensure src is in path if running from root
if 'src' not in sys.path:
    sys.path.append('src')

try:
    from visualizer import KineticVisualizer
except ImportError:
    # Fallback if running from src directory directly
    try:
        from src.visualizer import KineticVisualizer
    except ImportError:
        print("Warning: could not import KineticVisualizer")
        KineticVisualizer = None

def load_config(config_path="src/config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

class KineticAnalyzer:
    def __init__(self, filepath, path_length=1.0, epsilon=900, output_dir="output/plots"):
        self.filepath = filepath
        self.data = pd.read_csv(filepath)
        self.path_length = path_length
        self.epsilon = epsilon
        self.output_dir = output_dir
        
        # Robust column handling
        self._normalize_columns()

    def _normalize_columns(self):
        # Expected: 'Time (s)' or 'Time_s', 'Absorbance'
        # Map common variations to standard internal names
        col_map = {}
        for col in self.data.columns:
            if 'time' in col.lower():
                col_map[col] = 'Time_s'
            elif 'abs' in col.lower():
                col_map[col] = 'Absorbance'
        
        if col_map:
            self.data.rename(columns=col_map, inplace=True)
            
        # Fallback if mapping failed but 2 columns exist
        if 'Time_s' not in self.data.columns and len(self.data.columns) >= 2:
             print(f"Warning: Could not identify columns by name in {self.filepath}. Assuming Col 1 is Time, Col 2 is Absorbance.")
             self.data.columns.values[0] = 'Time_s'
             self.data.columns.values[1] = 'Absorbance'

    def calculate_rate(self):
        """
        Calculates reaction rate.
        Returns:
            rate (M/s): The rate of reaction (negative slope of concentration vs time).
            r_squared: Coefficient of determination for the linear fit.
        """
        # Calculate Concentration from Absorbance (Beer's Law: A = epsilon * b * c => c = A / (epsilon * b))
        self.data['concentration'] = self.data['Absorbance'] / (self.epsilon * self.path_length)
        
        # Standard Linear Regression (OLS)
        slope, intercept, r_value, p_value, std_err = linregress(
            self.data['Time_s'], self.data['concentration']
        )
        r_squared = r_value**2

        # Robust Regression (RANSAC) Check
        used_robust = False
        if SKLEARN_AVAILABLE and r_squared < 0.98: # Trigger if OLS is "suspicious"
            print(f"  [Auto-Correction] Low R^2 ({r_squared:.4f}). Attempting RANSAC...")
            
            X = self.data['Time_s'].values.reshape(-1, 1)
            y = self.data['concentration'].values
            
            ransac = RANSACRegressor(random_state=42)
            ransac.fit(X, y)
            
            # Get inlier mask
            inlier_mask = ransac.inlier_mask_
            
            # Re-calculate slope/intercept from RANSAC estimator
            robust_slope = ransac.estimator_.coef_[0]
            robust_intercept = ransac.estimator_.intercept_
            robust_score = ransac.score(X[inlier_mask], y[inlier_mask])
            
            print(f"  [RANSAC] New R^2 (inliers): {robust_score:.4f}, Slope: {robust_slope:.2e}")
            
            # Use robust values if they effectively describe the "good" data better
            # Note: RANSAC score is R^2 on inliers only.
            slope = robust_slope
            intercept = robust_intercept
            r_squared = robust_score
            used_robust = True
            
            # Update dataframe to mark outliers for visualization?
            self.data['is_outlier'] = ~inlier_mask
        else:
             self.data['is_outlier'] = False
        
        # Visualization Hook
        if KineticVisualizer:
            viz = KineticVisualizer(output_dir=self.output_dir)
            filename_base = os.path.splitext(os.path.basename(self.filepath))[0]
            if used_robust:
                filename_base += "_robust"
            plot_path = viz.plot_kinetics(self.data, slope, intercept, filename_base)
            print(f"Generated plot: {plot_path}")

        
        # Salt Effect Correction
        # Logic: k_obs = k_intrinsic * F_salt  => k_intrinsic = k_obs / F_salt
        # This is handled by calculate_intrinsic_rate called from main
        
        # Rate is negative slope
        rate = -slope
        return rate, r_squared

    def calculate_intrinsic_rate(self, k_obs, anion, salt_factors):
        factor = salt_factors.get(anion, 1.0)
        k_intrinsic = k_obs / factor
        return k_intrinsic, factor

if __name__ == "__main__":
    # Example usage logic from main
    try:
        config = load_config()
        reagents = config['experiment']['reagents']
        acid_anion = reagents.get('acid_anion', 'Cl-')
        salt_factors = reagents.get('salt_factors', {'Cl-': 1.0})
        
        # Find all CSVs in data/raw_csv
        data_dir = "data/raw_csv"
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.endswith(".csv"):
                    filepath = os.path.join(data_dir, filename)
                    print(f"Processing {filename}...")
                    analyzer = KineticAnalyzer(
                        filepath, 
                        path_length=config['experiment']['parameters']['path_length_cm'],
                        epsilon=config['experiment']['parameters'].get('extinction_coefficient', 900)
                    )
                    rate, r2 = analyzer.calculate_rate()
                    
                    # Salt Correction
                    k_intrinsic, factor = analyzer.calculate_intrinsic_rate(rate, acid_anion, salt_factors)
                    
                    print(f"  Rate (Observed): {rate:.2e} M/s, R^2: {r2:.4f}")
                    print(f"  [Hofmeister] Anion: {acid_anion} (F={factor}) -> k_intrinsic: {k_intrinsic:.2e} M/s")
                    
        else:
            print(f"Data directory {data_dir} not found.")

    except Exception as e:
        print(f"Error: {e}")
