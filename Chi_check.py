from icecream import ic
from NuRadioReco.modules.io import NuRadioRecoio
import numpy as np
import NuRadioReco.modules.io.eventWriter
import matplotlib.pyplot as plt
import datetime
from radiotools import helper as hp
from NuRadioReco.framework.parameters import channelParameters as chp
import NuRadioReco.utilities.units as units
import NuRadioReco.utilities.units as units
eventWriter = NuRadioReco.modules.io.eventWriter.eventWriter()
import os 
import NuRadioReco.utilities.fft as fft
import NuRadioReco.utilities.io_utilities as io_utilities
import send2trash
input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Trig_X_Zen/sample'
def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir

def get_Chi(trace1:np.array,trace2:np.array):
    return np.dot(trace1,trace2)/(np.sqrt(np.dot(trace1,trace1)*np.dot(trace2,trace2)))

def get_Cross_Chi(trace1:np.array,trace2:np.array):
    Chi=[]
    for i in range(0,len(trace1)):
        trace=np.append(trace1[i:len(trace1)],trace1[0:i])
        Chi.append(np.abs(get_Chi(trace,trace2)))
    return max(Chi)

def normalize_wave(trace):
    trace=np.abs(trace)
    return trace/np.sqrt(np.dot(trace,trace))
def FFT_plot(ax:plt.axes,trace:np.array,sample_rate):
    freqs = fft.freqs(len(trace),sample_rate)/units.MHz
    spec = normalize_wave(fft.time2freq(trace,sample_rate))
    trace=np.abs(spec)
    ax.plot(freqs,np.abs(spec))
    ax.set_title(f'Max:{np.max(np.abs(trace)):.2f} Mean:{np.mean(trace):.2f} Std:{np.std(trace):.5f}')
def trace_plot(ax:plt.axes,trace,time,chi=1):
    ax.plot(time,trace)
    ax.set_title(f'Max:{np.max(np.abs(trace)):.2f} Mean:{np.mean(trace):.2f} Std:{np.std(trace):.2f} Chi:{chi:.2f}')
def diff_devi(arr1,arr2):
    return np.mean((arr1-arr2)**2)

pickle_reader=io_utilities.read_pickle('/Users/david/PycharmProjects/Demo1/Research/2020cr_search/templates/templates_cr_station_51.pickle')
fig,axes = plt.subplots(figsize=(10,8),constrained_layout=True,nrows=8, ncols=2, sharex='col', sharey='col')
trace_sample={}
for i in pickle_reader:
    for azimuth in i.values():
        for evt in azimuth.values():
            for i in range(8):
                trace=evt[i]
                time = np.arange(0,256,0.5)
                sample_rate=2*units.GHz
                ax1=axes[i,0]
                ax2=axes[i,1]
                # ax2.axhline(y=3*std,color='red')
                # ax2.axhline(y=-3*std,color='red')
                ax1.grid()
                ax2.grid()
                if i in range(4,7):
                    trace_sample[i]=trace
                FFT_plot(ax1,trace,sample_rate)
                trace_plot(ax2,trace,time)
            break
        break
    break
# plt.show()
fig2,axes = plt.subplots(figsize=(10,8),constrained_layout=True,nrows=8, ncols=2, sharex='col', sharey='col')
read=NuRadioRecoio.NuRadioRecoio(get_input(input_path))
for evt in read.get_events():
    stn=evt.get_station(51)
    for i in range(8):
        channel=stn.get_channel(i)
        trace_pre_resample = channel.get_trace()
        time_presample = channel.get_times()
        freq_presample = channel.get_frequencies()/units.MHz
        freq_spec_presample = channel.get_frequency_spectrum()
        # chn.resample(2*units.GHz)
        trace=chn.get_trace()/units.mV
        time=chn.get_times()/units.ns
        ic(len(trace))
        sample_rate=2*units.GHz
        ax1=axes[i,0]
        ax2=axes[i,1]
        # ax2.axhline(y=3*std,color='red')
        # ax2.axhline(y=-3*std,color='red')
        ax1.grid()
        ax2.grid()
        FFT_plot(ax1,trace,sample_rate)
        trace_plot(ax2,trace,time)
        # if i in range(4,7):
        trace=trace[36:135]
        freqs= fft.freqs(len(trace),sample_rate)/units.MHz
        spec = normalize_wave(fft.time2freq(trace,sample_rate))
        freq_trace=np.abs(spec)

        if i not in range(4,5,6):
            Tem_tr=trace_sample[4][36:135]
        else:
            Tem_tr=trace_sample[i][36:135]
        freqs_Tem=fft.freqs(len(trace),sample_rate)/units.MHz
        spec_Tem = normalize_wave(fft.time2freq(Tem_tr,sample_rate))
        freq_trace_Tem=np.abs(spec_Tem)

        diff_d=diff_devi(freq_trace,freq_trace_Tem)
        ic(i,diff_d)


plt.show()
        # Xmax=chn[chp.cr_xcorrelations]['cr_ref_xcorr']
        # ic(Xmax)
        # ic(len(trace))
