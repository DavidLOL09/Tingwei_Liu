import sys
# sys.path.insert(0,'/Users/david/PycharmProjects/Demo1/Research/Repository/NuRadioMC')
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
import ToolsPac as tp
import matplotlib
import ToolsPac
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


def fft_plot_sim(ax,input_path,criti_freqs):
    readARIANNAData=NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    weights=[]
    max_amp=[]
    max_ratio=[]
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        max_r=0
        weights.append(evt.get_parameter(evtp.event_rate))
        for i in [4,5,6]:
            spectrum,freqs,ratio=get_low_amp_ratio(criti_freqs,evt,i)
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
    ax.set_xlim(4,300)
    ax.set_ylim(0,1)
    ax.set_xlabel('Max_amp(MeV)',fontsize=20)
    ax.set_ylabel(f'Freqs_ratio_below_{criti_freqs}MHz(%)',fontsize=20)
    ax.set_xscale('log')
    ax.tick_params(axis='x', labelsize=20)
    ax.tick_params(axis='y', labelsize=20)
    return ax

def fft_plot_det(ax,input_path,criti_freqs=80,cut_line = 0.115,dot_color = 'blue', mark_evt = []):
    readARIANNAData=NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    max_amp=[]
    max_ratio=[]
    if_mark_evt = len(mark_evt)>0
    max_amp_mark = []
    max_ratio_mark=[]
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        max_r=0
        for i in [4,5,6]:
            spectrum,freqs,ratio=get_low_amp_ratio(criti_freqs,evt,i)
            if ratio>max_r:
                max_r=ratio
        amp=[]
        for i in range(8):
            chn=stn.get_channel(i)
            amp.append(np.max(np.abs(chn.get_trace()/units.mV))/Vrms)
        amp=max(amp)
        max_amp.append(amp)
        max_ratio.append(max_r)
        if if_mark_evt:
            evt_id = f'R{evt.get_run_number()}E{evt.get_id()}'
            if evt_id in mark_evt:
                max_amp_mark.append(amp)
                max_ratio_mark.append(max_r)
    SNR_bins = np.logspace(np.log10(np.min(max_amp)), np.log10(np.max(max_amp)), 101)
    fft_bins = np.linspace(0,1,101)
    ax.scatter(max_amp,max_ratio,s=3,color=dot_color)
    ax.scatter(max_amp_mark,max_ratio_mark,s=5,color='red')
    ax.set_xlabel(f'SNR',fontsize=40)
    ax.set_ylabel(fr'$\chi$',fontsize=40)
    ax.legend(loc='lower right',fontsize=40)
    ax.axhline(y=cut_line,color='black')
    ax.grid()
    ax.set_ylim(0,1)
    ax.set_xlabel('SNR',fontsize=20)
    ax.set_ylabel(f'Freqs_ratio_below_{criti_freqs}MHz(%)',fontsize=20)
    ax.set_xscale('log')
    ax.tick_params(axis='x', labelsize=20)
    ax.tick_params(axis='y', labelsize=20)
    return ax

def Freqs_ratio(evt,chn_id,criti_freqs=80):
    def get_trace_by_chn(i,evt):
        stn=evt.get_station(51)
        chn=stn.get_channel(i)
        trace_spectrum=chn.get_frequency_spectrum()
        return trace_spectrum
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
    def get_low_amp_ratio(criti_amp,evt,chn_num):
        sample_rate=1*units.GHz
        spectrum = normalize_wave(get_trace_by_chn(chn_num,evt))
        freqs = fft.freqs(256,sample_rate)/units.MHz
        index=find_closest_index(criti_amp,freqs)-1
        tot_amp = np.sum(spectrum)
        low_amp = np.sum(spectrum[0:index+1])
        ratio = low_amp/tot_amp
        return spectrum,freqs,ratio
    spectrum,freqs,ratio=get_low_amp_ratio(criti_freqs,evt,chn_id)
    return ratio

def plot_wave(evt,suptitle,output='Nothing'):
    def normalize_wave(trace):
        trace=np.abs(trace)
        return trace/np.sqrt(np.dot(trace,trace))
    def FFT_plot(ax:plt.axes,trace:np.array,sample_rate,color='blue'):
        freqs = fft.freqs(len(trace),sample_rate)/units.MHz
        spec = normalize_wave(fft.time2freq(trace,sample_rate))
        ax.plot(freqs,np.abs(spec),c=color)
        ax.axvline(80,c='green')
    def trace_plot(ax:plt.axes,trace,time,color='blue'):
        ax.plot(time,trace,c=color)
    def Freqs_ratio(evt,chn_id):
        def get_trace_by_chn(i,evt):
            stn=evt.get_station(51)
            chn=stn.get_channel(i)
            trace_spectrum=chn.get_frequency_spectrum()
            return trace_spectrum
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
        def get_low_amp_ratio(criti_amp,evt,chn_num):
            sample_rate=1*units.GHz
            spectrum = normalize_wave(get_trace_by_chn(chn_num,evt))
            freqs = fft.freqs(256,sample_rate)/units.MHz
            index=find_closest_index(criti_amp,freqs)-1
            tot_amp = np.sum(spectrum)
            low_amp = np.sum(spectrum[0:index+1])
            ratio = low_amp/tot_amp
            return spectrum,freqs,ratio
        spectrum,freqs,ratio=get_low_amp_ratio(80,evt,chn_id)
        return ratio
    stn = evt.get_station(51)
    fig,axes = plt.subplots(figsize=(10,8),constrained_layout=True,nrows=8, ncols=2, sharex='col', sharey='col')
    fig.suptitle(suptitle)
    id = ToolsPac.get_id_info(evt)
    for i in range(8):
        chn=stn.get_channel(i)
        trace=chn.get_trace()/units.mV
        time=chn.get_times()/units.ns
        sample_rate=chn.get_sampling_rate()
        ax1=axes[i,0]
        ax2=axes[i,1]
        ax1.grid()
        ax2.grid()
        FFT_plot(ax1,trace,sample_rate)
        trace_plot(ax2,trace,time)
        Freqs=Freqs_ratio(evt,i)
        if i in [4,5,6]:
            channel = stn.get_channel(i)
            ax2.set_title(f'SNR:{np.max((channel.get_trace()/units.mV)/Vrms):.4f}')
        else:
            channel = stn.get_channel(i)
            ax2.set_title(f'SNR:{np.max((channel.get_trace()/units.mV)/Vrms):.4f}')
        ax1.set_title(f'F:{Freqs:.5f}')
    if output=='Nothing':
        plt.show()
    else:
        plt.savefig(os.path.join(output,f'{id}.png'))
    ic(f'{id}')


def fft_plot_cut_det(ax,readARIANNAData,criti_freqs,vip_evts=np.array([])):
    # readARIANNAData=NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    max_amp_r   =[]
    max_ratio_r =[]
    max_amp_g   =[]
    max_ratio_g =[]
    vip_amp     =[]
    vip_ratio   =[]
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        run = evt.get_run_number()
        id = evt.get_id()
        time = stn.get_station_time().datetime
        # largest:[max_amp,ratio]
        max_r=0
        for i in [4,5,6]:
            spectrum,freqs,ratio=get_low_amp_ratio(criti_freqs,evt,i)
            if ratio>max_r:
                max_r=ratio
        amp=[]
        for i in range(8):
            chn=stn.get_channel(i)
            amp.append(np.max(np.abs(chn.get_trace()/units.mV))/Vrms)
        amp=max(amp)
        if f'R{run}E{id}' in vip_evts:
            vip_amp.append(amp)
            vip_ratio.append(max_r)
        if max_r<=0.115:
            max_amp_r.append(amp)
            max_ratio_r.append(max_r)
        else:
            # if max_r>0.2:
                # plot_wave(evt,suptitle=f'R{run}E{id} R_f:(50mHz):{max_r:.5f}')
                # break
            max_amp_g.append(amp)
            max_ratio_g.append(max_r)
        # max_amp.append(amp)
        # max_ratio.append(max_r)
    # ax.scatter(max_amp,max_ratio,label=f'Candi:{len(max_amp)}')
    ax.scatter(max_amp_r,max_ratio_r,label=f'Pass:{len(max_amp_r)}',c='red',alpha=0.2)
    ax.scatter(max_amp_g,max_ratio_g,label=f'Not Pass:{len(max_amp_g)}',c='grey',alpha=0.2)
    ax.scatter(vip_amp,vip_ratio,label=f'VIP:{len(vip_amp)}',c='orange',s=80,alpha=1)
    ax.set_xlabel(f'SNR',fontsize=40)
    ax.set_ylabel(fr'$\chi$',fontsize=40)
    ax.legend(loc='lower right',fontsize=40)
    ax.axhline(y=0.115,color='black')
    ax.legend(fontsize=20)
    ax.grid()
    ax.set_ylim(0,1)
    ax.set_xlim(4,300)
    ax.set_xlabel('Max_amp(SNR)',fontsize=20)
    ax.set_ylabel(f'$R_f(criti\_freqs={criti_freqs}mHz)$',fontsize=20)
    ax.set_xscale('log')
    ax.tick_params(axis='x', labelsize=20)
    ax.tick_params(axis='y', labelsize=20)
    return ax

# fig,axes = plt.subplots(1,2,figsize=(18,8))
input_det_threshold='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335/BandPass_50'
det_freqs = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs'
det_freqs_failed = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs/Trig_335_Freqs_failed'
input_det_candi='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs_X_SNR'
# reader = NuRadioRecoio.NuRadioRecoio(get_input(input_det_threshold))
# candi_lst = []
# for evt in reader.get_events():
#     candi_lst.append(f'R{evt.get_run_number()}E{evt.get_id()}')
# ax = axes[0]
# fft_plot_det(ax,input_det_threshold,100,dot_color='blue',mark_evt=candi_lst)
# fft_plot_det(ax,det_freqs,80,cut_line=0.15, dot_color='blue')
# ax = axes[1]
# fft_plot_det(ax,det_freqs_failed,80,cut_line=0.15, dot_color='blue')
# fig,ax = plt.subplots(1,1,figsize = (10,8))
# fft_plot_sim(ax,input_det_threshold)
# plt.show()

# input_det = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs_X_SNR/Trig_335_Freqs_X_SNR_failed'
# output_path = os.path.join(input_det,'waveform_freqs_survivie')
# try:
#     os.mkdir(output_path)
# except(FileExistsError):
#     send2trash.send2trash(output_path)
#     os.mkdir(output_path)
# reader = NuRadioRecoio.NuRadioRecoio(get_input(input_det))
# for evt in reader.get_events():
#     plot_wave(evt,f'freqs_fail_survive',output_path)

# input_det = '/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw'
# reader = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_det))
# vip_lst = ['R243E512']
# max = 10
# for evt in reader.get_events():
#     for ch in [4,5,6]:
#         ratio = Freqs_ratio(evt,ch)
#         if ratio>0.2:
#             plot_wave(evt,ToolsPac.get_id_info(evt))
#             max-=1
#             if max==0:
#                 quit()

# for evt in reader.get_events():
#     id = ToolsPac.get_id_info(evt)
#     if id in vip_lst:
#         plot_wave(evt,id)

# freqs_sur = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs_X_SNR/Trig_335_Freqs_X_SNR_failed'
# freqs_sur = input_det_candi
# reader = NuRadioRecoio.NuRadioRecoio(get_input(freqs_sur))
# vip = []
# for evt in reader.get_events():
#     vip.append(tp.get_id_info(evt))

# fig,ax = plt.subplots(1,1,figsize=(10,8))
# reader = NuRadioRecoio.NuRadioRecoio(get_input(input_det_threshold))
# fft_plot_cut_det(ax,reader,85,vip_evts=vip)
# plt.show()

# freqs_sur = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs_X_SNR/Trig_335_Freqs_X_SNR_failed'
# # freqs_sur = input_det_candi
# reader = NuRadioRecoio.NuRadioRecoio(get_input(freqs_sur))
# vip = []
# for evt in reader.get_events():
#     vip.append(tp.get_id_info(evt))
# input_sim_SNR = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/sim/Trig_335_Freqs'
# fig,ax = plt.subplots(1,1,figsize=(10,8))
# reader = NuRadioRecoio.NuRadioRecoio(get_input(input_sim_SNR))
# fft_plot_sim(ax,input_sim_SNR,80)
# plt.show()

