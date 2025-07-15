from icecream import ic
from NuRadioReco.modules.io import NuRadioRecoio
import numpy as np
import NuRadioReco.modules.io.eventWriter
import matplotlib.pyplot as plt
import datetime
from NuRadioReco.framework.parameters import channelParameters as chp
import NuRadioReco.utilities.units as units
eventWriter = NuRadioReco.modules.io.eventWriter.eventWriter()
import os 
import NuRadioReco.utilities.fft as fft
import send2trash
input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate'
# input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/plots'
import ToolsPac
# input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Trig_X_Zen/sample'
# input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Trig_X_Zen'
output_path='/Users/david/PycharmProjects/Demo1/Research/Repository/aftResample/X_Zen/FFT_plot'
# output_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Trig_X_Zen/FFT_plot'
try:
    os.makedirs(output_path)
except(FileExistsError):
    send2trash.send2trash(output_path)
    os.makedirs(output_path)
def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir
sample_rate=1*units.GHz
def get_event_sample(input_path):
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    # sam = os.path.join(output_path,'sample')
    sam=output_path
    try:
        os.makedirs(sam)
    except(FileExistsError):
        send2trash.send2trash(sam)
        os.makedirs(sam)
    eventWriter.begin(os.path.join(sam,'sample.nur'))
    count=0
    for evt in readARIANNAData.get_events():
        count+=1
        if count%100==0:
            eventWriter.run(evt)
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
    # ax.set_title(f'Fourier Transform')
    # ax.fill_between(freqs,np.abs(spec),0,color='r',alpha=0.5,label='Low Frequency area')

def FFT_Area_plot(ax:plt.axes,trace:np.array,sample_rate,Area_min,Area_max,color):
    FFT_plot(ax,trace,sample_rate)
    freqs = fft.freqs(len(trace),sample_rate)/units.MHz
    spec = normalize_wave(fft.time2freq(trace,sample_rate))
    min=0
    max=0
    for i in range(0,len(freqs)):
        if freqs[i]>Area_min:
            min=i-1
            break
    for i in range(0,len(freqs)):
        if freqs[i]>Area_max:
            max=i
            break
    if max==0:
        max=len(freqs)
    ax.fill_between(freqs[min:max],np.abs(spec)[min:max],0,color=color,alpha=0.5)
    ax.tick_params(axis='x', labelsize=20)
    ax.tick_params(axis='y', labelsize=20)

def trace_plot(ax:plt.axes,trace,time):
    ax.plot(time,trace)
    # ax.set_title(f'Max:{np.max(np.abs(trace)):.2f} Mean:{np.mean(trace):.2f} Std:{np.std(trace):.2f}')
def get_Complete_FFT_plot(input_path):
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        fig,axes = plt.subplots(figsize=(10,8),constrained_layout=True,nrows=8, ncols=2, sharex='col', sharey='col')
        run = evt.get_run_number()
        id = evt.get_id()
        # statis=[[],[]]
        # for i in range(4):
        #     chn=stn.get_channel(i)
        #     trace=chn.get_trace()/units.mV
        #     # time=chn.get_times()/units.ns
        #     statis[0].append(np.mean(trace))
        #     statis[1].append(np.std(trace))
        # ic(statis)
        # exit()
        for i in range(8):
            chn=stn.get_channel(i)
            trace=chn.get_trace()/units.mV
            time=chn.get_times()/units.ns
            # Xmax=np.max(np.abs(chn[chp.cr_xcorrelations]['cr_ref_xcorr']))
            # Chi_list=chn[chp.cr_xcorrelations]['cr_ref_xcorr']
            # ic(len(time))
            # mean=np.mean(trace)
            # std=np.std(trace)
            sample_rate=1*units.GHz
            ax1=axes[i,0]
            ax2=axes[i,1]
            # ax2.axhline(y=3*std,color='red')
            # ax2.axhline(y=-3*std,color='red')
            ax1.grid()
            ax2.grid()
            FFT_plot(ax1,trace,sample_rate)
            trace_plot(ax2,trace,time)
        ic(f'R{run}E{id}')
        plt.show()
        # plt.savefig(os.path.join(output_path,f'R{run}E{id}.png'))

def get_cut_example(input_path):
    Reader  = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    for evt in Reader.get_events():
        if ToolsPac.get_id_info(evt)!='R243E572':
            continue
        stn = evt.get_station(51)
        fig,axes    = plt.subplots(figsize=(10,4),constrained_layout=True,nrows=2, ncols=2, sharex='col', sharey='col')
        chn = stn.get_channel(4)
        trace   = chn.get_trace()/units.mV
        time    = chn.get_times()/units.ns
        sample_rate = 1*units.GHz
        ax1 = axes[0]
        ax2 = axes[1]
        for i in range(2):
            ax1[i].grid()
            ax2[i].grid()
        ax1[0].set_title('Fourier Transform',fontsize=20)
        ax1[1].set_title('Radio Wave',fontsize=20)
        FFT_Area_plot(ax1[0],trace,sample_rate,0,80,'red')
        trace_plot(ax1[1],trace,time)
        FFT_Area_plot(ax2[0],trace,sample_rate,0,500,'green')
        trace_plot(ax2[1],trace,time)
        break
    # plt.title('Fourier Transform of channel 4', fontsize=15)
    plt.show()

def get_trace_by_chn(i,evt):
    stn=evt.get_station(51)
    chn=stn.get_channel(i)
    trace=chn.get_trace()/units.mV
    return trace


def check_FFT_Chi(input_path):
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    count=0
    for evt in readARIANNAData.get_events():
        run=evt.get_run_number()
        id=evt.get_id()

        trace4 = get_trace_by_chn(0,evt)
        trace5 = get_trace_by_chn(1,evt)
        spec4 = np.abs(fft.time2freq(trace4,sample_rate))
        spec5 = np.abs(fft.time2freq(trace5,sample_rate))
        Chi_trace=get_Cross_Chi(trace4,trace5)
        Chi_freqs=get_Chi(spec4,spec5)
        # ic(spec4,spec5)
        ic(f'{np.abs(Chi_trace):.2f},{np.abs(Chi_freqs):.2f}')
        ic(f'R{run}E{id}')
        break
# check_FFT_Chi(input_path)
get_cut_example(input_path)









    
        