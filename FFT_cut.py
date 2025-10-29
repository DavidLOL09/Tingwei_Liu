from icecream import ic
from NuRadioReco.modules.io import NuRadioRecoio
import numpy as np
import NuRadioReco.modules.io.eventWriter
import matplotlib.pyplot as plt
import datetime
from NuRadioReco.framework.parameters import channelParameters as chp
import NuRadioReco.utilities.units as units
eventWriter = NuRadioReco.modules.io.eventWriter.eventWriter()
from NuRadioReco.framework.parameters import showerParameters as shp
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
from NuRadioReco.framework.parameters import eventParameters as evtp
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
def FFT_plot(ax:plt.axes,trace:np.array,sample_rate,color='blue'):
    freqs = fft.freqs(len(trace),sample_rate)/units.MHz
    spec = normalize_wave(fft.time2freq(trace,sample_rate))
    ax.plot(freqs,np.abs(spec),c=color)
    ax.axvline(80,c='green')
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
Vrms=(9.71+9.66+8.94)/3
def trace_plot(ax:plt.axes,trace,time,color='blue'):
    ax.plot(time,trace,c=color)
    # ax.set_title(f'Max:{np.max(np.abs(trace)):.2f} Mean:{np.mean(trace):.2f} Std:{np.std(trace):.2f}')

def oneOf10(count):
    if count%300==0:
        return count+1,False
    else:
        return count+1,True
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
def get_Complete_FFT_plot(input_path,output_path):
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    count=0
    # SNR Drive
    # target=['R266E1720', 'R256E732', 'R256E1414', 'R256E1694', 'R256E2108', 
    #         'R243E2', 'R243E6', 'R243E89', 'R243E294', 'R243E314', 
    #         'R243E324', 'R243E330', 'R243E537', 'R243E589']
    # Ratio X SNR
    # target=['R266E2270', 'R247E1149', 'R243E15', 'R243E103', 'R243E311', 
    #         'R243E1192']
    # Both
    # target=['R263E365', 'R263E368', 'R263E739', 'R263E748', 'R263E749', 
    #         'R263E756', 'R264E224', 'R266E834', 'R266E1396', 'R249E8', 'R249E11', 
    #         'R247E17', 'R247E26', 'R247E904', 'R247E943', 'R247E1732', 'R247E1762', 
    #         'R242E10', 'R256E13', 'R256E1669', 'R256E1984', 'R256E2152', 'R243E30', 
    #         'R243E57', 'R243E91', 'R243E100', 'R243E126', 'R243E166', 'R243E312', 
    #         'R243E512', 'R243E531', 'R243E1033', 'R243E1142', 'R243E1167', 'R243E1183', 
    #         'R243E1258', 'R243E1270', 'R243E1399', 'R243E1460', 'R243E1485', 
    #         'R243E1792']
    ic(readARIANNAData.get_n_events())
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        if_big_e=ToolsPac.get_Max_trace(stn,[4,5,6])/Vrms>10
        # if not if_big_e:
        #     continue
        count,skip=oneOf10(count)
        if skip:
            continue
        # if ToolsPac.get_id_info(evt) not in target:
        #     continue
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
        # flatVolt_remove(evt)
        for i in range(8):
            chn=stn.get_channel(i)
            trace=chn.get_trace()/units.mV
            time=chn.get_times()/units.ns
            # Xmax=np.max(np.abs(chn[chp.cr_xcorrelations]['cr_ref_xcorr']))
            # Chi_list=chn[chp.cr_xcorrelations]['cr_ref_xcorr']
            # ic(len(time))
            # mean=np.mean(trace)
            # std=np.std(trace)
            sample_rate=chn.get_sampling_rate()
            ax1=axes[i,0]
            ax2=axes[i,1]
            # ax2.axhline(y=3*std,color='red')
            # ax2.axhline(y=-3*std,color='red')
            ax1.grid()
            ax2.grid()
            FFT_plot(ax1,trace,sample_rate)
            trace_plot(ax2,trace,time)
            Freqs=Freqs_ratio(evt,i)
            if i in [4,5,6]:
                channel = stn.get_channel(i)
                Xcorr=np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr']))
                ax2.set_title(f'X:{Xcorr:.3f} SNR:{np.max((channel.get_trace()/units.mV)/Vrms):.4f}')
            else:
                channel = stn.get_channel(i)
                ax2.set_title(f'SNR:{np.max((channel.get_trace()/units.mV)/Vrms):.4f}')
            ax1.set_title(f'F:{Freqs:.5f}')
        ic(f'R{run}E{id}C{count}')
        # plt.show()
        try:
            # plt.savefig(os.path.join(output_path,f'R{run}E{id}C{count}.png'))
            plt.savefig(os.path.join(output_path,f'R{run}E{id}C{count}.png'))
        except(FileNotFoundError):
            os.makedirs(output_path)
            # plt.savefig(os.path.join(output_path,f'R{run}E{id}C{count}.png'))
            plt.savefig(os.path.join(output_path,f'R{run}E{id}C{count}.png'))
    ic(readARIANNAData.get_n_events())

def get_Complete_FFT_plot_with_simDir(evt,temp_file_name,temp_ch_id,output_path):
    stn = evt.get_station(51)
    fig,axes = plt.subplots(figsize=(10,8),constrained_layout=True,nrows=8, ncols=2, sharex='col', sharey='col')
    run = evt.get_run_number()
    id = evt.get_id()
    sim_shower=evt.get_sim_shower(0)
    sim_zen=sim_shower[shp.zenith]/units.deg
    sim_azi=sim_shower[shp.azimuth]/units.deg
    fig.suptitle(f'{sim_zen:.2f} {sim_azi:.2f}')
    for i in range(8):
        chn=stn.get_channel(i)
        trace=chn.get_trace()/units.mV
        time=chn.get_times()/units.ns
        sample_rate=chn.get_sampling_rate()
        ax1=axes[i,0]
        ax2=axes[i,1]
        ax1.grid()
        ax2.grid()
        amp=np.max(np.abs(trace))
        ax2.set_title(f'A:{amp:.2f}mV SNR:{amp/Vrms:.2f}')
        if i==temp_ch_id:
            FFT_plot(ax1,trace,sample_rate,'red')
            trace_plot(ax2,trace,time,'red')
        else:
            FFT_plot(ax1,trace,sample_rate)
            trace_plot(ax2,trace,time)
    output_path=os.path.join(output_path,'waveform')
    try:
        # plt.savefig(os.path.join(output_path,f'R{run}E{id}C{count}.png'))
        plt.savefig(os.path.join(output_path,f'{temp_file_name}.png'))
    except(FileNotFoundError):
        os.makedirs(output_path)
        # plt.savefig(os.path.join(output_path,f'R{run}E{id}C{count}.png'))
        plt.savefig(os.path.join(output_path,f'{temp_file_name}.png'))

def flatVolt_remove(evt,sample_rate=1*units.GHz):
    stn=evt.get_station(51)
    for ch in range(8):
        chn = stn.get_channel(ch)
        volt_fft=chn.get_frequency_spectrum()
        sample_rate=chn.get_sampling_rate()
        correction=np.ones_like(volt_fft)
        correction[0]=0
        volt_fft=correction*volt_fft
        chn.set_frequency_spectrum(volt_fft,sample_rate)


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

def find_template_event(input_path,template_path):
    e_range = np.arange(16, 18.6, 0.1)
    sin2Val = np.arange(0, 1.01, 0.1)
    template_evts=[]
    for template in os.listdir(template_path):
        for e in e_range:
            for sin2 in sin2Val:
                files=[]
                name=f'Stn51_IceTop_{e:.1f}-{e+0.1:.1f}eV_{sin2:.1f}sin2'
                if name not in template:
                    continue
                for file in os.listdir(input_path):
                    if name in file:
                        files.append(os.path.join(input_path,file))
                reader=NuRadioRecoio.NuRadioRecoio(files)
                for evt in reader.get_events():
                    id=evt.get_parameter(evtp.evt_id)
                    if f'{name}_{id}_' not in template:
                        continue
                    template_evts.append([evt,f'{name}_{id}_'])
                    temp_chn=0
                    for ch in [4,5,6]:
                        if f'{name}_{id}_{ch}ch' in template:
                            temp_chn=ch
                    get_Complete_FFT_plot_with_simDir(evt,f'{name}_{id}_',temp_chn,template_path)
                    plt.close()
    return template_evts

def plot_direct(direct,ax,alfa=1,zorder=0,color='red'):
    ax.set_rlim(0,90)
    direct=np.array(direct)
    zen=direct[:,0]
    azi=direct[:,1]
    ax.scatter(azi,zen,s=20,alpha=alfa,zorder=zorder,color=color,label=f'direct:{len(direct)}')
    ax.legend()

# # template_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/CR_BL_1backL_Template_processed'
# template_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/CR_BL_Template_final'
# # events_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/template_with_backlope'
# events_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/CR_BL_Template_processed'
# events=find_template_event(events_path,template_path)
# direct=[]
# for [evt,id] in events:
#     sim_shower=evt.get_sim_shower(0)
#     sim_zen=sim_shower[shp.zenith]/units.deg
#     sim_azi=sim_shower[shp.azimuth]/units.rad
#     direct.append([sim_zen,sim_azi])

# fig,ax = plt.subplots(figsize=(10,8),layout='constrained',subplot_kw={'projection': 'polar'})

# plot_direct(direct,ax)

# plt.show()

# ic(len(events))
# for [evt,id] in events:
#     ic(id)
# exit()
# check_FFT_Chi(input_path)
# get_cut_example(input_path)

# input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs_X_SNR'
# output_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs_X_SNR/waveform'
# input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/sim/Trig_335_Freqs_X_SNR'
# output_path=os.path.join(input_path,'waveform')
# get_Complete_FFT_plot(input_path,output_path)