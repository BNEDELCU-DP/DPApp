import os
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

from ReadCSVFiles import *
from CoefExtraction import *
from FFTdBExtraction import *
from NoiseFloorExtraction import *
    
    
"""def plot_data(data):
    plt.figure(figsize=(18, 12))
    
    # Plot the original signal first
    plt.plot(data, label='Original Signal', color='blue', alpha=0.5)
    
    # Find peaks in the signal
    # The 'distance' parameter ensures peaks are sufficiently separated
    peaks, _ = find_peaks(data, distance=len(data)//50)
    peak_values = data[peaks]
    
    # Select the top 4 highest peaks
    if len(peaks) > 4:
        top_peaks = peaks[np.argsort(peak_values)[-4:]]  # Indices of 4 highest peaks
    else:
        top_peaks = peaks
    
    # Copy original data to modify it
    modified_data = data.copy()
    replaced_chunks = []  # Store replaced segments for visualization
    
    # Replace 100 samples before and 800 samples after each peak with nearby data
    for peak in top_peaks:
        start = max(0, peak - 100)  # Ensure start is within bounds
        end = min(len(data), peak + 800)  # Ensure end is within bounds
        
        # Determine possible left and right source regions for replacement
        # We attempt to copy data from a nearby segment of the same length
        left_source_start = max(0, start - (end - start))  # Check if there is enough space on the left
        right_source_end = min(len(data), end + (end - start))  # Check if there is enough space on the right
        
        # Copy data from the left region if enough data is available
        if left_source_start >= 0 and start - left_source_start >= (end - start):
            replacement = data[left_source_start:left_source_start + (end - start)]
        # Otherwise, try copying from the right region if possible
        elif right_source_end <= len(data) and right_source_end - end >= (end - start):
            replacement = data[right_source_end - (end - start):right_source_end]
        else:
            continue  # Skip if a valid replacement region is not found
        
        # Apply the replacement to the modified data
        modified_data[start:end] = replacement
        replaced_chunks.append((start, end, replacement))
    
    # Plot modified signal on top of the original
    # plt.plot(modified_data, label='Modified Signal', color='green', alpha=0.5)
    
    # Highlight replaced chunks in a different color for visibility
    for start, end, replacement in replaced_chunks:
        plt.plot(range(start, end), replacement, color='red', alpha=0.7, label='Replaced Chunks' if start == replaced_chunks[0][0] else "")
    
    # Configure and display the plot
    plt.title('Signal with Replaced Peaks')
    plt.xlabel('Voltage')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.legend()
    plt.show()
"""

def plot_data(data, filename, output_dir):
    os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists
    
    plt.figure(figsize=(18, 12))
    
    # Plot the original signal first
    plt.plot(data, label='Original Signal', color='blue', alpha=0.5)
    
    # Find peaks in the signal
    peaks, _ = find_peaks(data, distance=len(data)//50)  # Adjust distance for peak separation
    peak_values = data[peaks]
    
    # Select the top 4 highest peaks
    if len(peaks) > 4:
        top_peaks = peaks[np.argsort(peak_values)[-4:]]  # Indices of 4 highest peaks
    else:
        top_peaks = peaks
    
    # Copy original data to modify it
    modified_data = data.copy()
    replaced_chunks = []  # Store replaced segments for visualization
    
    # Replace 100 samples before and 800 samples after each peak with nearby data
    for peak in top_peaks:
        start = max(0, peak - 100)  # Ensure start is within bounds
        end = min(len(data), peak + 800)  # Ensure end is within bounds
        
        # Determine possible left and right source regions for replacement
        left_source_start = max(0, start - (end - start))  # Check if there is enough space on the left
        right_source_end = min(len(data), end + (end - start))  # Check if there is enough space on the right
        
        # Copy data from the left region if enough data is available
        if left_source_start >= 0 and start - left_source_start >= (end - start):
            replacement = data[left_source_start:left_source_start + (end - start)]
        # Otherwise, try copying from the right region if possible
        elif right_source_end <= len(data) and right_source_end - end >= (end - start):
            replacement = data[right_source_end - (end - start):right_source_end]
        else:
            continue  # Skip if a valid replacement region is not found
        
        # Apply the replacement to the modified data
        modified_data[start:end] = replacement
        replaced_chunks.append((start, end, replacement))
    
    # Highlight replaced chunks in a different color for visibility
    for start, end, replacement in replaced_chunks:
        plt.plot(range(start, end), replacement, color='red', alpha=0.7, label='Replaced Chunks' if start == replaced_chunks[0][0] else "")
    
    # Configure and display the plot
    plt.title(f'Signal with Replaced Peaks - {filename}')
    plt.xlabel('Samples')
    plt.ylabel('Amplitude (V)')
    plt.grid(True)
    plt.legend()
    
    # Save the plot as a PNG file
    output_path = os.path.join(output_dir, f"{os.path.basename(filename).replace('.csv', '')}_noise.png")
    plt.savefig(output_path)
    plt.close()
    
    # Save modified data to CSV file
    csv_output_path = os.path.join(output_dir, f"{os.path.basename(filename).replace('.csv', '')}_noise.csv")
    with open(csv_output_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Index', 'Modified Data'])
        for i, value in enumerate(modified_data):
            writer.writerow([i, value])

    
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
            plot_data(data, file, output_directory + 'only_noise_files')
            print(f"Processed file: {os.path.basename(file)}.")
