import sys
sys.path.insert(0,'/Users/david/PycharmProjects/Demo1/Research/Repository/NuRadioMC')
from NuRadioReco.detector import detector 
from NuRadioReco.utilities import units
from NuRadioReco.modules.ARIANNA import hardwareResponseIncorporator as ChardwareResponseIncorporator
from NuRadioReco.framework.parameters import stationParameters as stnp
from NuRadioReco.modules.io import NuRadioRecoio
import numpy as np
from brokenaxes import brokenaxes
import datetime
import NuRadioReco.modules.io.eventWriter
from NuRadioReco.framework.parameters import eventParameters as evtp
import matplotlib.pyplot as plt
import datetime
import os
import send2trash
import NuRadioReco.utilities.fft as fft
from NuRadioReco.framework.parameters import channelParameters as chp
import NuRadioReco.modules.correlationDirectionFitter
eventWriter = NuRadioReco.modules.io.eventWriter.eventWriter()
from icecream import ic
import matplotlib
Vrms=(9.71+9.66+8.94)/3

def get_trace_by_chn(i,evt):
    stn=evt.get_station(51)
    chn=stn.get_channel(i)
    trace_spectrum=chn.get_frequency_spectrum()
    return trace_spectrum
def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir
def normalize_wave(trace):
    trace=np.abs(trace)
    return trace/np.sqrt(np.dot(trace,trace))
def find_closest_index(criti_num,arr:np.array):
    try:
        for i in range(len(arr)):
            if criti_num-arr[i]<=0:
                return i
        raise ValueError
    except ValueError:
        ic('Critical Number is bigger than every elemtns in array')
sample_rate=1*units.GHz
def get_low_amp_ratio(criti_amp,evt,chn_num):
    spectrum = normalize_wave(get_trace_by_chn(chn_num,evt))
    freqs = fft.freqs(256,sample_rate)/units.MHz
    index=find_closest_index(criti_amp,freqs)-1
    tot_amp = np.sum(spectrum)
    low_amp = np.sum(spectrum[0:index+1])
    ratio = low_amp/tot_amp
    return spectrum,freqs,ratio

def set_writer(output,filename):
    output_file = os.path.join(output,filename)
    try:
        os.makedirs(output_file)
    except(FileExistsError):
        send2trash.send2trash(output_file)
        os.makedirs(output_file)
    eventWriter.begin(os.path.join(output_file,f'{filename}.nur'))
    return eventWriter


def fft_plot_sim(ax,input_path):
    readARIANNAData=NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    weights=[]
    max_amp=[]
    max_ratio=[]
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        max_r=0
        weights.append(evt.get_parameter(evtp.event_rate))
        for i in [4,5,6]:
            spectrum,freqs,ratio=get_low_amp_ratio(80,evt,i)
            if ratio>max_r:
                max_r=ratio
        amp=[]
        for i in range(8):
            chn=stn.get_channel(i)
            amp.append(np.max(np.abs(chn.get_trace()/units.mV))/Vrms)
        amp=max(amp)
        max_amp.append(amp)
        max_ratio.append(max_r)
    SNR_bins = np.logspace(np.log10(np.min(max_amp)), np.log10(np.max(max_amp)), 101)
    weights=np.array(weights)*31/365
    fft_bins=np.linspace(0,1,101)
    hist,_,_=np.histogram2d(max_amp,max_ratio,bins=(SNR_bins,fft_bins),weights=weights)
    S,X=np.meshgrid(SNR_bins,fft_bins)
    pm=ax.pcolormesh(S,X,hist.T,norm=matplotlib.colors.LogNorm(),zorder=0)
    ax.figure.colorbar(pm,ax=ax)
    ax.set_xlabel(f'SNR',fontsize=40)
    ax.set_ylabel(fr'$\chi$',fontsize=40)
    ax.legend(loc='lower right',fontsize=40)
    ax.axhline(y=0.115,color='black')
    ax.legend(fontsize=20)
    ax.grid()
    ax.set_ylim(0,1)
    ax.set_xlabel('Max_amp(MeV)',fontsize=20)
    ax.set_ylabel('Freqs_ratio_below_80MHz(%)',fontsize=20)
    ax.set_xscale('log')
    ax.tick_params(axis='x', labelsize=20)
    ax.tick_params(axis='y', labelsize=20)
    return ax

def fft_plot_det(ax,input_path):
    readARIANNAData=NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    max_amp=[]
    max_ratio=[]
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        run = evt.get_run_number()
        id = evt.get_id()
        time = stn.get_station_time().datetime
        # largest:[max_amp,ratio]
        max_r=0
        for i in [4,5,6]:
            spectrum,freqs,ratio=get_low_amp_ratio(80,evt,i)
            if ratio>max_r:
                max_r=ratio
        amp=[]
        for i in range(8):
            chn=stn.get_channel(i)
            amp.append(np.max(np.abs(chn.get_trace()/units.mV))/Vrms)
        amp=max(amp)
        max_amp.append(amp)
        max_ratio.append(max_r)
    ax.scatter(max_amp,max_ratio)
    ax.set_xlabel(f'SNR',fontsize=40)
    ax.set_ylabel(fr'$\chi$',fontsize=40)
    ax.legend(loc='lower right',fontsize=40)
    ax.axhline(y=0.115,color='black')
    ax.legend(fontsize=20)
    ax.grid()
    ax.set_ylim(0,1)
    ax.set_xlabel('Max_amp(MeV)',fontsize=20)
    ax.set_ylabel('Freqs_ratio_below_80MHz(%)',fontsize=20)
    ax.set_xscale('log')
    ax.tick_params(axis='x', labelsize=20)
    ax.tick_params(axis='y', labelsize=20)
    return ax
