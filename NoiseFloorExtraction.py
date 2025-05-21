import os
import csv
import numpy as np
from scipy.signal import welch
import matplotlib.pyplot as plt


def extract_noise_floor(signal, sample_rate, freq_range=(1e6, 5e6), bandwidth=100e3):
    """
    Extract the noise floor from a frequency domain signal in specified frequency range and bandwidth.

    Parameters:
    - signal: The time-domain signal (1D numpy array).
    - sample_rate: The sampling rate of the signal (in Hz).
    - freq_range: Tuple (f_min, f_max) specifying the frequency range of interest (in Hz).
    - bandwidth: The bandwidth for each frequency bin (in Hz).

    Returns:
    - noise_floor: A dictionary where keys are frequency bins (in Hz) and values are the noise floor levels (in dB/Hz).
    """
    # Compute the Power Spectral Density (PSD) using Welch's method
    frequencies, psd = welch(signal, fs=sample_rate, nperseg=1024, scaling='spectrum')

    # Convert PSD to dB/Hz
    psd_db = 10 * np.log10(psd)

    # Initialize the noise floor dictionary
    noise_floor = {}

    # Iterate over the frequency range in increments of the specified bandwidth
    f_min, f_max = freq_range
    current_freq = f_min
    while current_freq < f_max:
        # Find indices of frequencies within the current bin
        bin_indices = np.where((frequencies >= current_freq) & (frequencies < current_freq + bandwidth))[0]

        if len(bin_indices) > 0:
            # Calculate the mean noise floor for this bin
            noise_floor[current_freq] = np.mean(psd_db[bin_indices])
        else:
            # If no frequencies fall in this bin, set the noise floor to NaN
            noise_floor[current_freq] = np.nan

        # Move to the next frequency bin
        current_freq += bandwidth

    return noise_floor, frequencies, psd_db

def plot_noise_floor(noise_floor, frequencies, psd_db, filename, output_dir):
    """Plot the noise floor and save the plot as a PNG file"""
    plt.figure(figsize=(18, 12))
    plt.plot(frequencies, psd_db, label='PSD (dB/Hz)', color='blue', alpha=0.5)
    plt.plot(list(noise_floor.keys()), list(noise_floor.values()), label='Noise Floor (100 kHz bins)', color='red', marker='o', linestyle='--')
    plt.title(f'Noise Floor for {filename}')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude (dB/Hz)')
    plt.xscale('log')
    plt.grid(True)
    plt.legend()

    # Save plot to output directory
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{os.path.basename(filename).replace('.csv', '')}_noise_floor.png")
    plt.savefig(output_path)
    plt.close()

def save_noise_floor_to_csv(noise_floor, filename, output_dir):
    """Save the noise floor dictionary to a CSV file"""
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{os.path.basename(filename).replace('.csv', '')}_noise_floor.csv")
    
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Frequency (Hz)', 'Noise Floor (dB/Hz)'])
        for freq, noise in noise_floor.items():
            writer.writerow([freq, noise])
