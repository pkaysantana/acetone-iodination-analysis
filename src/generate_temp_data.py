import sys
if 'src' not in sys.path:
    sys.path.append('src')

import numpy as np
from dirty_data_generator import DirtyDataGenerator, load_config

def generate_arrhenius_data():
    config = load_config()
    epsilon = config['experiment']['parameters']['extinction_coefficient']
    gen = DirtyDataGenerator()
    
    # Arrhenius Parameters
    E_a = 75000 # J/mol
    R = 8.314
    A_factor = 2.8e6 # Reduced by 100x total to prevent completion within timeframe
    
    temperatures = [288, 298, 308, 318, 328] # Kelvin
    
    print("Generating Temperature Data...")
    for T in temperatures:
        # k = A * exp(-Ea / RT)
        k = A_factor * np.exp(-E_a / (R * T))
        
        filename = f"run_{T}K.csv"
        # Add a little noise
        gen.generate_dataset(filename, rate=k, noise_std=0.005, duration_s=600, epsilon=epsilon)
        print(f"  {filename}: T={T}K, Expected k={k:.2e} M/s")

if __name__ == "__main__":
    generate_arrhenius_data()
