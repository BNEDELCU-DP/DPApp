import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


def exponentialModel(x, a, b):
    """Define exponential model: y = a * e^(b * x)"""
    return a * np.exp(b * x)

def fitExponentialCurve(x, y):
    """Fit an exponential curve to experimental data set"""
    params, covariance = curve_fit(exponentialModel, x, y, p0=[1, 0.01])
    a, b = params
    return a, b

def calculateExponentialCoefficientsForDataset(max_db_list): 
    """Calculates exponential coefficients for a given data set"""
    # We need at least 2 points to interpolate
    if len(max_db_list) < 2:
        print("Not enough data provided to compute exponential coefficients!!!")
        return
    
    # Create x_data as a sequence of indices (0, 1, 2, ...)
    x_data = np.arange(len(max_db_list))  # Generates indices [0, 1, 2, ..., n]
    y_data = np.array(max_db_list)  # Converts input list to a NumPy array
    
    # Fit the exponential curve
    a, b = fitExponentialCurve(x_data, y_data)
    
    return (a, b)

def plotFittedCurve(max_db_list, filename, output_dir):
    """
    Calculates exponential coefficients and plots the fitted curve
    Plot the original data and the fitted exponential curve
    """
    
    a, b = calculateExponentialCoefficientsForDataset(max_db_list)
    
    # Print coefficients
    print(f"Exponential Coefficients: a = {a:.2f}, b = {b:.6f}")

    x = np.arange(len(max_db_list))  # Generates indices [0, 1, 2, ..., n]
    y = np.array(max_db_list)  # Take the values from the list
      
    plt.figure(figsize=(18, 12))
    plt.scatter(x, y, label="Max FFT Values in dB", color='blue', alpha=0.5, marker='o')  # Original points
    x_fit = np.linspace(min(x), max(x), 100)  # Generate smooth x values for plotting
    y_fit = exponentialModel(x_fit, a, b)  # Compute corresponding y values using fitted model
    plt.plot(x_fit, y_fit, label=f"Fitted Curve: y = {a:.2f} * e^({b:.6f} * x)", color='green')
    plt.title("Exponential Curve Fitting")
    plt.xlabel("X Values")
    plt.ylabel("Y Values")
    plt.legend()
    #plt.grid(True)

    # Save plot to output directory
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename+'.png')
    plt.savefig(output_path)
    plt.close()

    return (a, b)

def saveFittedCurveToCSV(exp_coef_a, exp_coef_b, filename, output_dir):
    """Save the fitted curve exponential coefficients to a CSV file"""
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{os.path.basename(filename).replace('.csv', '')}_exponential_coeffs.csv")
    
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Exponential coeff a', 'Exponential coeff b'])
        writer.writerow([exp_coef_a, exp_coef_b])    
