import os
import matplotlib
import numpy as np
import scipy.signal as sig
from itertools import cycle
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d


def applyFilter(signal):
    """Applies smoothing filter"""
    # Savitzky-Golay filter with mirror mode to eliminate phase delay
    # Smoothed_signal = sig.savgol_filter(signal, window_length=501, polyorder=5, mode='mirror')
    # Gaussian filter
    smoothed_signal = gaussian_filter1d(signal, sigma=20)  # Increase sigma for stronger smoothing
    return smoothed_signal

def extractInterestDomainFrequencies(data):
    """Apply FFT and extract frequencies between 1 MHz - 5 MHz"""
    n_samples = len(data)
    
    # Compute FFT
    fft_values = np.fft.fft(data)
    freqs = np.fft.fftfreq(n_samples, d=1/100e6) # 1/Fs
    
    # Take only positive frequencies
    fft_values = np.abs(fft_values[:n_samples // 2])
    # Take only positive frequencies, half of FFT
    freqs = freqs[:n_samples // 2]
    
    # Filter values within range 1 MHz - 5 MHz
    mask = (freqs >= 1e6) & (freqs <= 5e6)
    interest_domain_frequencies = freqs[mask]
    interest_domain_fft = fft_values[mask]
 
    # Convert to dB
    interest_domain_fft_db = 20 * np.log10(interest_domain_fft)

    return (interest_domain_frequencies, interest_domain_fft_db)

def plotFFTMagnitudeAndExtractMAX(data, filename, output_dir):
    """Processes FFT, applies smoothing and then plots results to png files"""

    # Convert to dB
    interest_domain_frequencies, domain_fft_db = extractInterestDomainFrequencies(data)
    
    # Apply smoothing using Savitzky-Golay filter
    smoothed_fft_db = applyFilter(domain_fft_db)

    plt.figure(figsize=(18, 12))
    plt.plot(interest_domain_frequencies, domain_fft_db, label='FFT Magnitude in dB', color='blue', alpha=0.5)
    plt.plot(interest_domain_frequencies, smoothed_fft_db, label='Smoothed FFT Magnitude', color='yellow', linewidth=2)
    plt.title(f'FFT Magnitude in dB for {filename}')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.xscale('log')
    plt.grid(True)
    plt.legend()
    
    # Save plot to output directory
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{os.path.basename(filename).replace('.csv', '')}.png")
    plt.savefig(output_path)
    plt.close()

    return np.max(domain_fft_db)
