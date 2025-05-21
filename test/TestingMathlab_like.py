import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, freqz
from scipy.fft import fft, fftfreq
from scipy.signal import argrelextrema

# Define the signal and sampling frequency
sampling_frequency = 100e6  # 100 MHz
num_samples = 1000000
t = np.linspace(0, (num_samples - 1) * 1e-8, num_samples)  # Time vector

# Generate a sample signal (replace this with your actual signal)
semnal_achizitionat = np.random.randn(num_samples)

# Define the bandpass filter parameters
f_low = 2e6  # 2 MHz
f_high = 3e6  # 3 MHz
nyquist = 0.5 * sampling_frequency
low = f_low / nyquist
high = f_high / nyquist
order = 4  # Filter order

# Design the Butterworth bandpass filter
b, a = butter(order, [low, high], btype='band')

# Apply the filter to the signal
semnal_filtrat = filtfilt(b, a, semnal_achizitionat)

# Calculate the integral of the filtered signal
integrala = np.trapz(semnal_filtrat)
print(f'Integrala semnalului filtrat este: {integrala}')

# Calculate the FFT of the filtered signal
N = len(semnal_filtrat)
f = fftfreq(N, 1/sampling_frequency)[:N//2]
Y = fft(semnal_filtrat)[:N//2]
amplitude_spectrum = np.abs(Y)
amplitude_spectrum_dB = 20 * np.log10(amplitude_spectrum)

# Find local maxima (upper envelope) in the amplitude spectrum (in dB)
upper_envelope_indices = argrelextrema(amplitude_spectrum, np.greater)[0]
upper_envelope = amplitude_spectrum_dB[upper_envelope_indices]

# Interpolate the upper envelope to match the frequency resolution
from scipy.interpolate import interp1d
interp_func = interp1d(f[upper_envelope_indices], upper_envelope, kind='linear', fill_value="extrapolate")
upper_envelope_interpolated = interp_func(f)

# Plot the FFT of the filtered signal in dB with the upper envelope
plt.figure()
plt.plot(f, amplitude_spectrum_dB, 'r', linewidth=1.5, label='FFT Filtrat (dB)')
plt.plot(f, upper_envelope_interpolated, 'b', alpha=0.3, linewidth=2, label='Upper Envelope')
plt.title('FFT al Semnalului Filtrat si Upper Envelope')
plt.xlabel('Frecventa (Hz)')
plt.ylabel('Amplitudine (dB)')
plt.legend(loc='best')
plt.grid(True)
plt.show()
