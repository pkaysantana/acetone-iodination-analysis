import pandas as pd
import numpy as np
import os
import yaml

def load_config(config_path="src/config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

class DirtyDataGenerator:
    def __init__(self, output_dir="data/raw_csv"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate_dataset(self, filename, duration_s=600, points=30, rate=2e-6, 
                         noise_std=0.02, outlier_prob=0.05, delay_s=0, 
                         initial_absorbance=2.0, path_length=1.0, epsilon=900):
        """
        Generates a synthetic kinetic dataset with defects.
        """
        time = np.linspace(0, duration_s, points)
        
        # True Concentration [I2]
        c0 = initial_absorbance / (epsilon * path_length)
        concentration = c0 - rate * time
        concentration = np.maximum(concentration, 0) # Floor at 0
        
        # Convert to Absorbance
        absorbance = concentration * epsilon * path_length
        
        # 1. Add Mixing Delay
        # Before delay_s, absorbance is constant (or erratic)
        if delay_s > 0:
            delay_mask = time < delay_s
            absorbance[delay_mask] = initial_absorbance
            
            # Shift the reaction part
            reaction_time = time[~delay_mask] - delay_s
            c_reaction = c0 - rate * reaction_time
            c_reaction = np.maximum(c_reaction, 0)
            absorbance[~delay_mask] = c_reaction * epsilon * path_length

        # 2. Add Gaussian Noise
        noise = np.random.normal(0, noise_std, size=len(time))
        absorbance = absorbance + noise
        
        # 3. Add Outliers (Bubbles/Spikes)
        # Randomly pick indices to spike
        n_outliers = int(len(time) * outlier_prob)
        if n_outliers > 0:
            outlier_indices = np.random.choice(len(time), n_outliers, replace=False)
            # Spikes can be positive (bubbles?) or negative
            spikes = np.random.choice([-1, 1], n_outliers) * np.random.uniform(0.2, 0.5, n_outliers)
            absorbance[outlier_indices] += spikes

        # Create DataFrame
        df = pd.DataFrame({
            'Time (s)': time,
            'Absorbance': absorbance
        })
        
        filepath = os.path.join(self.output_dir, filename)
        df.to_csv(filepath, index=False)
        print(f"Generated {filepath} (Delay={delay_s}s, Noise={noise_std}, Outliers={n_outliers})")
        return filepath

if __name__ == "__main__":
    np.random.seed(42) # Reproducibility
    config = load_config()
    epsilon = config['experiment']['parameters']['extinction_coefficient']
    
    gen = DirtyDataGenerator()
    
    # 1. Baseline (Clean-ish)
    gen.generate_dataset("stress_baseline.csv", noise_std=0.01, outlier_prob=0.0, delay_s=0, epsilon=epsilon)
    
    # 2. High Noise
    gen.generate_dataset("stress_high_noise.csv", noise_std=0.1, outlier_prob=0.0, delay_s=0, epsilon=epsilon)
    
    # 3. Outliers (Bubbles)
    gen.generate_dataset("stress_outliers.csv", noise_std=0.01, outlier_prob=0.1, delay_s=0, epsilon=epsilon)
    
    # 4. Mixing Delay
    gen.generate_dataset("stress_delay.csv", noise_std=0.01, outlier_prob=0.0, delay_s=60, epsilon=epsilon)
    
    # 5. Everything Everywhere All At Once
    gen.generate_dataset("stress_chaos.csv", noise_std=0.05, outlier_prob=0.1, delay_s=40, epsilon=epsilon)
