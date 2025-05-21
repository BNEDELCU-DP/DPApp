import os
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

from ReadCSVFiles import *
from CoefExtraction import *
from FFTdBExtraction import *
from NoiseFloorExtraction import *

def plot_data1(data):
    plt.figure(figsize=(18, 12))
    plt.plot(data, label='Signal', color='blue', alpha=0.5)
    
    # Find peaks
    peaks, _ = find_peaks(data, distance=len(data)//50)  # Adjust distance for peak separation
    peak_values = data[peaks]
    
    # Get top 3 peaks
    if len(peaks) > 3:
        top_peaks = peaks[np.argsort(peak_values)[-5:]]  # Get indices of 5 highest peaks
    else:
        top_peaks = peaks
    
    # Plot highest peaks
    plt.scatter(top_peaks, data[top_peaks], color='red', label='Top 5 Peaks', zorder=3)
    
    plt.title('Signal')
    plt.xlabel('Voltage')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.legend()
    plt.show()



def plot_data2(data):  
    # Find peaks
    peaks, _ = find_peaks(data, distance=len(data)//50)  # Adjust distance for peak separation
    peak_values = data[peaks]
    
    # Get top 2 peaks
    if len(peaks) > 2:
        top_peaks = peaks[np.argsort(peak_values)[-2:]]  # Get indices of 2 highest peaks
    else:
        top_peaks = peaks
    
    # Replace 100 samples before and 500 samples after each peak with zero
    for peak in top_peaks:
        start = max(0, peak - 100)
        end = min(len(data), peak + 500)
        data[start:end] = 0
    
        
    """"# Replace 100 samples before and 500 samples after each peak with zero
    for peak in top_peaks:
        start = max(0, peak - 100)
        end = min(len(data), peak + 500)

        # Extract surrounding data for mean and std
        surrounding_data = np.concatenate((data[max(0, start-100):start], data[end:min(len(data), end+100)]))
        if len(surrounding_data) > 0:
            mean_val = np.mean(surrounding_data)
            std_val = np.std(surrounding_data)
            data[start:end] = np.random.normal(mean_val, std_val, end - start) 
    """        
    
    """# Define filter specifications
    fs = 20e6  # Sampling frequency (20 MHz, adjust as needed)
    lowcut = 1e6  # Lower cutoff frequency (1 MHz)
    highcut = 5e6  # Upper cutoff frequency (5 MHz)
    order = 4  # Filter order

    # Normalize the frequencies (convert to Nyquist scale)
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq

    # Design Butterworth bandpass filter
    b, a = signal.butter(order, [low, high], btype='band')

    # Apply the filter to the data
    filtered_data = signal.filtfilt(b, a, data)    
    """
    
    plt.figure(figsize=(18, 12))
    plt.plot(data, label='Signal', color='blue', alpha=0.5)
    #plt.plot(filtered_data, label='Filtered Signal', color='red', alpha=0.5)
        
    # Plot highest peaks
    plt.scatter(top_peaks, data[top_peaks], color='red', label='Top 5 Peaks', zorder=3)
    
    plt.title('Signal')
    plt.xlabel('Voltage')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.legend()
    plt.show()
    
    
# Main function
if __name__ == '__main__':

    sample_rate = 100e6  # 100 MHz sample rate
    
    output_directory = 'Results\\'

    calibration_sets = {
        'A': 'DPCalibrationData\\A',
        'B': 'DPCalibrationData\\B',
        'C': 'DPCalibrationData\\C'
    }

    for label, path in calibration_sets.items():
        files = getCSVFiles(path)

        fft_dB_max_values = []
        
        for file in files:
            # readCSVFile(filename, row_num, skip_rows, delimiter)
            data = readCSVFile(file, 1, skip_rows=9)  
            plot_data1(data)

