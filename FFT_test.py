import numpy as np
import matplotlib.pyplot as plt
from icecream import ic

# Parameters
sampling_rate = 1000  # Hz
T = 1.0 / sampling_rate  # Sample spacing
N = 1000  # Number of samples
x = np.linspace(0.0, N*T, N, endpoint=False)

# Create a signal with two sine wave components
signal = np.sin(2.0 * np.pi * 50.0 * x) + 0.5 * np.sin(2.0 * np.pi * 120.0 * x)

# Compute the real FFT and corresponding frequency bins
spectrum = np.fft.rfft(signal)
ic(spectrum)
freqs = np.fft.rfftfreq(N, T)
ic(freqs)

# Plotting
plt.figure(figsize=(14, 5))

# Plot time-domain signal
plt.subplot(1, 2, 1)
plt.plot(x, signal)
plt.title("Time Domain Signal")
plt.xlabel("Time [s]")
plt.ylabel("Amplitude")

# Plot frequency-domain (magnitude spectrum)
plt.subplot(1, 2, 2)
plt.plot(freqs, np.abs(spectrum))
plt.title("Frequency Domain Spectrum")
plt.xlabel("Frequency [Hz]")
plt.ylabel("Magnitude")

plt.tight_layout()
plt.show()
