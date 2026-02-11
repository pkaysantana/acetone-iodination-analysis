import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import yaml

def load_config(config_path="src/config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def plot_arrhenius(temperature_k, k_obs, output_path="output/plots/arrhenius.png"):
    """
    Plots ln(k) vs 1/T.
    temperature_k: list or array of temperatures in Kelvin
    k_obs: list or array of observed rate constants
    """
    temp_inv = 1 / np.array(temperature_k)
    ln_k = np.log(np.array(k_obs))
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(temp_inv, ln_k)
    
    # R = 8.314 J/(mol*K)
    R = 8.314
    E_a = -slope * R # J/mol
    A = np.exp(intercept)
    
    plt.figure(figsize=(8, 6))
    plt.scatter(temp_inv, ln_k, label='Data')
    plt.plot(temp_inv, slope * temp_inv + intercept, color='red', label=f'Fit (R²={r_value**2:.4f})')
    
    plt.xlabel('1/T ($K^{-1}$)')
    plt.ylabel('ln($k_{obs}$)')
    plt.title(f'Arrhenius Plot\n$E_a$ = {E_a/1000:.2f} kJ/mol, A = {A:.2e}')
    plt.legend()
    plt.grid(True)
    
    plt.savefig(output_path)
    plt.close()
    
    return {"E_a_kJ_mol": E_a/1000, "A": A, "R_squared": r_value**2}

if __name__ == "__main__":
    # Example usage
    # temps = [293, 303, 313] # Kelvin
    # rates = [0.002, 0.005, 0.012] # Arbitrary units
    # result = plot_arrhenius(temps, rates)
    # print(result)
    pass
