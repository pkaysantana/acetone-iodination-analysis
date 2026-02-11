import pandas as pd
import numpy as np
from scipy.stats import linregress
import yaml
import os

def load_config(config_path="src/config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

class KineticAnalyzer:
    def __init__(self, filepath, path_length=1.0, epsilon=900):
        self.filepath = filepath
        self.data = pd.read_csv(filepath)
        self.path_length = path_length
        self.epsilon = epsilon
        
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
        
        # Zero Order check approach: Slope of Conc vs Time for Iodine consumption
        # Note: Rate of reaction is defined as -d[I2]/dt. 
        # Since [I2] decreases linearly, the slope is negative. Rate is positive.
        
        slope, intercept, r_value, p_value, std_err = linregress(
            self.data['Time_s'], self.data['concentration']
        )
        
        # Rate is negative slope
        rate = -slope
        return rate, r_value**2

if __name__ == "__main__":
    # Example usage logic from main
    try:
        config = load_config()
        # Create a dummy call standard if file exists, else just print usage
        # analyzer = KineticAnalyzer("data/raw_csv/test.csv", 
        #                            path_length=config['experiment']['parameters']['path_length_cm'],
        #                            epsilon=config['experiment']['parameters'].get('extinction_coefficient', 900))
        # rate, r2 = analyzer.calculate_rate()
        # print(f"Rate: {rate:.2e} M/s, R^2: {r2:.4f}")
        pass
    except Exception as e:
        print(f"Error: {e}")
