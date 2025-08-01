import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from icecream import ic
input_path='/Users/david/Desktop/sweep_test_2_+0000mV_f_1.csv'
def plot_fft(input_path):
    # Read the CSV file
    df = pd.read_csv(input_path)

    # Display the first few rows
    count=0
    current = np.array(df['Current (nA)'])

    t = np.linspace(0, 1, 20000, endpoint=False)  # 1 second at 20000 Hz

    # Perform FFT
    fft_result = np.fft.fft(current)

    # Frequency axis
    freq = np.fft.fftfreq(len(t), d=1/20000)  # d=1/sampling rate

    # Plot the magnitude spectrum
    plt.plot(freq[:len(freq)//2], np.abs(fft_result)[:len(freq)//2])
    plt.title("FFT Spectrum")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
plot_fft(input_path)

