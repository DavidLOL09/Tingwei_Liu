from NuRadioReco.modules.io import NuRadioRecoio
from icecream import ic
from NuRadioReco.modules.channelLengthAdjuster import channelLengthAdjuster
import numpy as np
from NuRadioReco.framework.parameters import showerParameters as shp
from NuRadioReco.utilities import units
import NuRadioReco.utilities.fft as fft
import sys
import send2trash
import os
import pandas as pd
Vrms=(9.71+9.66+8.94)/3
sys.path.append('/Users/david/PycharmProjects/Demo1/Research/Repository/')
import plot_waveform
from pathlib import Path
import re
import ToolsPac
savename = 'Tingwei_Stn51'
trigger_name = 'direct_LPDA_3of3_3.5sigma'
save_channels = [4, 5, 6]
station_id = 51
import matplotlib.pyplot as plt
import NuRadioReco.modules.channelResampler
import NuRadioReco.modules.channelStopFilter
channelStopFilter = NuRadioReco.modules.channelStopFilter.channelStopFilter()
channelResampler = NuRadioReco.modules.channelResampler.channelResampler()
channelResampler.begin()
from NuRadioReco.framework.parameters import stationParameters as stnp
from NuRadioReco.framework.parameters import channelParameters as chp
from NuRadioReco.framework.parameters import eventParameters as evtp
import astropy
from NuRadioReco.detector import detector
det = detector.Detector(json_filename=f'/Users/david/PycharmProjects/Demo1/Research/Repository/Simulation/station51_InfAir.json', assume_inf=False, antenna_by_depth=False)
det.update(astropy.time.Time('2018-1-1'))


output_triggered='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/front_back_sep/Waveform'
template_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/CR_BL_Template'
evt_temp=output_triggered
# output =os.path.join(output_triggered,'waveform')
# ToolsPac.makedirs(output)

def azi_cut(tar_azi,azi,azi_err):
    for i in tar_azi:
        if azimuth_distance_deg(i,azi)<=azi_err:
            return True
    return False



# template = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(Template_path)[0])

channelLengthAdjuster = channelLengthAdjuster()
channelLengthAdjuster.begin()

# Azi_err =5    #degree
# tar_azi =[22.5,67.5,202.5,247.5]#55
# tar_azi =[22.5,202.5]#33
# tar_azi =[67.5,247.5]
# # tar_zen =[0.33,0.67]
# tar_zen=0.1
# Zen_err=0.05
# # tar_en  =[16,17]

def get_input_e_s(e,e1,s,input_path):
    input_list=[]
    for path in ToolsPac.get_input(input_path):
        # Stn51_IceTop_18.4-18.5eV_0.4sin2_10cores
        if f'Stn51_IceTop_{e}-{e1}eV_{s}sin2' in path:
            input_list.append(path)
    return input_list,f'Stn51_IceTop_{e}-{e1}eV_{s}sin2' 


def get_triggered_sim_evts(input_path,output_path):
    e_range = np.arange(16, 18.6, 0.1)
    sin2Val = np.arange(0, 1.01, 0.1)
    input_files=ToolsPac.get_input(input_path)
    
    for e in e_range:
        for sin2 in sin2Val:
            run_file=[]
            for file in input_files:
                if f'Stn51_IceTop_{e:.1f}-{e+0.1:.1f}eV_{sin2:.1f}sin2' in file:
                    run_file.append(file)
            if run_file==[]:
                continue
            writer=ToolsPac.set_writer(output_path,f'Stn51_IceTop_{e:.1f}-{e+0.1:.1f}eV_{sin2:.1f}sin2_200cores',sub_dir=False)
            reader=NuRadioRecoio.NuRadioRecoio(run_file)
            for evt in reader.get_events():
                stn = evt.get_station(51)
                if not stn.has_triggered():
                    continue
                # if not stn.has_triggered():
                #     continue
                writer.run(evt)
            writer.end()



def plot_waveform_sim_check(input_path,output):
    e_range = np.arange(16, 18.6, 0.1)
    sin2Val = np.arange(0, 1.01, 0.1)
    input_files=ToolsPac.get_input(input_path)
    for e in e_range:
        for sin2 in sin2Val:
            run_file=[]
            name=f'Stn51_IceTop_{e:.1f}-{e+0.1:.1f}eV_{sin2:.1f}sin2'
            file_n=[]
            for file in input_files:
                if name in file:
                    run_file.append(file)
            if run_file==[]:
                continue
            reader = NuRadioRecoio.NuRadioRecoio(run_file)
            for evt in reader.get_events():
                station=evt.get_station(51)
                # channelLengthAdjuster.run(evt, station)
                channelResampler.run(evt, station, det, 1*units.GHz)
                channelStopFilter.run(evt, station, det, prepend=0*units.ns, append=0*units.ns)
                file=f'{name}_{evt.get_id():003}evt'
                plot_waveform.plot_wave(evt,os.path.join(output,'waveform'),filename=file)



    
# get_triggered_sim_evts(template_path,output_triggered)
# ic('complete')
# exit()




def azimuth_distance_deg(a1, a2):
    return abs((a1 - a2 + 180) % 360 - 180)
def select_template(template_path):
    filename=f'Template_{22.5}&{67.5}azi{Azi_err}_{456}chn'
    # output =os.path.join(output_triggered,f'{filename}_waveform')
    # ToolsPac.makedirs(output)
    writer=ToolsPac.set_writer(output_triggered,filename,sub_dir=False)
    template=ToolsPac.get_input(template_path)
    template = NuRadioRecoio.NuRadioRecoio(template)
    zen_lst=[]
    azi_lst=[]
    azi_drop=0
    zen_drop=0
    count=0
    for i, evt in enumerate(template.get_events()):
        sim_shower = evt.get_sim_shower(0)
        station = evt.get_station(station_id)
        # ic(f'Event parameters are: Eng {sim_shower[shp.energy]/units.eV}eV, Zen {sim_shower[shp.zenith]/units.deg}deg, Azi {sim_shower[shp.azimuth]/units.deg}deg')
        if not station.has_triggered():
            continue
        if not station.has_triggered(trigger_name):
            continue
        energy  = sim_shower[shp.energy]/units.eV
        zen     = np.sin(sim_shower[shp.zenith]/units.rad)**2
        azi     = sim_shower[shp.azimuth]/units.deg

        Azi_err=5-5*zen
        # azi pass
        
        if not azi_cut(azi,azi,Azi_err):
            azi_drop+=1
            # ic(azi,azi_drop)
            continue

        # if np.abs(zen-tar_zen)>Zen_err:
        #     zen_drop+=1
        #     # ic(zen,zen_drop)
        #     continue
        # if energy < tar_en[0] or energy > tar_en[1]:
        #     continue
        # ic(ToolsPac.get_id_info(evt))
        channelLengthAdjuster.run(evt, station)
        zen_lst.append(sim_shower[shp.zenith]/units.deg)
        azi_lst.append(sim_shower[shp.azimuth]/units.rad)
        # plot_waveform.plot_wave(evt,output,filename=f'{tar_azi[0]}azi{count}',plt_close=True)
        # writer.run(evt)
        count+=1
    ic(azi_drop,zen_drop)
    ic(template.get_n_events())

    fig,ax = plt.subplots(1,1,figsize=(10,8),layout='constrained',subplot_kw={'projection': 'polar'})
    ax=ToolsPac.direction_plot(ax,zen_lst,azi_lst,label='Trig_Temp')
    plt.show()
    


def evt_to_template(input_path,output,filename:str,chn:int):
    input_files=ToolsPac.get_input(input_path)
    used_files=[]
    for file in input_files:
        if filename in file:
            used_files.append(file)
    ic(used_files)
    reader = NuRadioRecoio.NuRadioRecoio(used_files)
    output_filename=f'Template45_chn{chn}'
    writer = ToolsPac.set_writer(output,output_filename,False)
    n=0
    for evt in reader.get_events():
        evt= ToolsPac.evt_to_template(evt,chn)
        sim_shower = evt.get_sim_shower(0)
        zen=sim_shower[shp.zenith]/units.deg
        azi=sim_shower[shp.azimuth]/units.deg
        plot_waveform.plot_wave(evt,os.path.join(output,output_filename),f'Temp{n}',suptitle=f'Z:{zen:.1f} A:{azi:.1f}')
        writer.run(evt)
        n+=1
    writer.end()


def plot_wave_b_detail(evt,temp_output='Nothing',filename=None,plt_close=False,suptitle=f'waveform'):
    stn = evt.get_station(51)
    run = evt.get_run_number()
    id = evt.get_id()
    trace_list=[]
    frontlope=[]
    backlope=[]
    frontback=[]
    chn=stn.get_channel(0)
    frontback=chn.get_trace()/units.mV
    chn=stn.get_channel(3)
    backlope=chn.get_trace()[:len(frontback)]/units.mV
    chn=stn.get_channel(4)
    frontlope=chn.get_trace()[:len(frontback)]/units.mV
    time = np.arange(0,len(frontlope),1)
    fig = plt.figure(figsize=(15,6))
    axes = fig.subplots(nrows=3,ncols=2,sharex=True,sharey=True)
    
    ax= axes[0,1]
    ax.plot(time,frontback,label='f+b')

    ax= axes[1,1]
    ax.plot(time,backlope,label='b')

    ax= axes[2,1]
    ax.plot(time,frontlope,label='f')

    ax= axes[0,0]
    ax.plot(time,frontback,label='f+b')
    ax.plot(time,backlope,label='b')
    xcorr=calculate_xcorr(backlope,frontback)
    ax.set_title(fr'$\chi$:{xcorr['chi_max']:.2f} $\chi$_phase:{xcorr['chi_phase']}')

    ax= axes[1,0]
    ax.plot(time,frontback,label='f+b')
    ax.plot(time,frontlope,label='f')
    xcorr=calculate_xcorr(frontback,frontlope)
    ax.set_title(fr'$\chi$:{xcorr['chi_max']:.2f} $\chi$_phase:{xcorr['chi_phase']}')

    ax= axes[2,0]
    ax.plot(time,frontlope,label='f')
    ax.plot(time,backlope,label='b')
    xcorr=calculate_xcorr(frontlope,backlope)
    ax.set_title(fr'$\chi$:{xcorr['chi_max']:.2f} $\chi$_phase:{xcorr['chi_phase']}')

    for i in axes:
        for j in i:
            j.grid()
            j.legend()

    plt.show()

def get_corr(arr1:np.array,arr2:np.array):
    return np.abs(np.dot(arr1,arr2)/np.sqrt(np.dot(arr1,arr1)*np.dot(arr2,arr2)))
def calculate_xcorr(arr2:np.array,arr1:np.array):
    if len(arr1)!=len(arr2):
        raise IndexError('arr1 and arr2 have different length')
    chi_max     = 0
    chi_phase   = 0
    xcorrelation= []
    for i in range(len(arr1)):
        arr_pre = arr1[:i]
        arr_pos = arr1[i:]
        Temp_arr1    = np.concatenate((arr_pos,arr_pre))
        Xcorr   = get_corr(Temp_arr1,arr2)
        xcorrelation.append(Xcorr)
            # plot_waveform_compare_pase(arr1,arr2,phase=i,X_max=chi_max,X_now=Xcorr)
        if Xcorr > chi_max:
            chi_max     = Xcorr
            chi_phase   = i
    # plot_waveform_with_phase(arr1,arr2,phase=i,X=chi_max,title='Final')
    return {'xcorrelation':xcorrelation,'chi_max':chi_max,'chi_phase':chi_phase}

def check_delayed_backlope_detail(input_path,output_path,tar):
    try:
        input_files=[]
        for i in os.listdir(input_path):
            if tar in i:
                input_files.append(os.path.join(input_path,i))
        reader = NuRadioRecoio.NuRadioRecoio(input_files)
    except NotADirectoryError:
        ic('here')
        reader = NuRadioRecoio.NuRadioRecoio(input_path)
    for evt in reader.get_events():
        if evt.get_id()!=9:
            continue
        plot_wave_b_detail(evt)

def extract_template(input_path,template_file,template_id,ch_id,template_path):
    # template_file=['Stn51_IceTop_17.5-17.6eV_0.9sin2']
    # template_id=['Stn51_IceTop_17.5-17.6eV_0.9sin2_009evt']
    # ch_id=9
    output=template_path
    filename=f'{template_id}_{ch_id}ch'
    writer=ToolsPac.set_writer(output,filename,sub_dir=False)
    e_range = np.arange(16, 18.6, 0.1)
    sin2Val = np.arange(0, 1.01, 0.1)
    input_files=ToolsPac.get_input(input_path)
    template_trace=None
    template_sampling_rate=None
    for file in input_files:
        if template_file not in file:
            continue
        ic(file)
        reader=NuRadioRecoio.NuRadioRecoio([file])
        for evt in reader.get_events():
            id=evt.get_parameter(evtp.evt_id)
            if f'{template_file}_{id}'!=template_id:
                continue
            stn=evt.get_station(51)
            chn=stn.get_channel(ch_id)
            template_trace=chn.get_trace()
            template_sampling_rate=chn.get_sampling_rate()
            for ch in range(8):
                chn=stn.get_channel(ch)
                chn.set_trace(template_trace,template_sampling_rate)
            writer.run(evt)
# Stn51_IceTop_18.0-18.1eV_0.7sin2_017evt

# exit()

def evaluate_template(input_path,template_path):
    input_files = ToolsPac.get_input(input_path)
    template_files,template_filename = ToolsPac.get_input(template_path,True)
    reader_input = NuRadioRecoio.NuRadioRecoio(input_files)
    reader_temp = NuRadioRecoio.NuRadioRecoio(template_files)
    xcorr_lst = []
    for it,temp in enumerate(reader_temp.get_events()):
        xcorr_temp = []
        stn = temp.get_station(51)
        chn = stn.get_channel(4)
        temp_wave = chn.get_trace()
        for ie,evt in enumerate(reader_input.get_events()):
            stn = evt.get_station(51)
            xcorr = []
            for ch in [4,5,6]:
                chn = stn.get_channel(ch)
                wave = chn.get_trace()
                xcorr.append(calculate_xcorr(wave,temp_wave)['chi_max'])
            xcorr_temp.append(max(xcorr))
        xcorr_temp = np.array(xcorr_temp)
        # ic(xcorr_temp)
        xcorr_lst.append(xcorr_temp)
        # ic(np.mean(xcorr_temp),np.median(xcorr_temp),np.std(xcorr_temp))
    return xcorr_lst,template_filename

def get_statistic_attrs(lst:np.array):
    return [np.mean(lst),np.median(lst),np.std(lst)]

def temp_comprehensive_check(input_path,template_path):
    temp_reader=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(template_path))
    temp_signal=[]
    for temp in temp_reader.get_events():
        stn=temp.get_station(51)
        chn=stn.get_channel(0)
        temp_signal.append(chn.get_trace()/units.mV)

    xcorr=[]
    evt_lst=[]
    e_range = np.arange(16, 18.6, 0.1)
    sin2Val = np.arange(0, 1.01, 0.1)
    input_files=ToolsPac.get_input(input_path)
    for e in e_range:
        for sin2 in sin2Val:
            run_file=[]
            name=f'Stn51_IceTop_{e:.1f}-{e+0.1:.1f}eV_{sin2:.1f}sin2'
            for file in input_files:
                if name in file:
                    run_file.append(file)
            if run_file==[]:
                continue
            test_evts = NuRadioRecoio.NuRadioRecoio(run_file)
            for evt in test_evts.get_events():
                evt_id=f'{name}_{evt.get_parameter(evtp.evt_id)}'
                xcorr_evt=[]
                stn=evt.get_station(51)
                for ch_id in [4,5,6]:
                    chn=stn.get_channel(ch_id)
                    trace=chn.get_trace()/units.mV
                    xcorr_evt_chn=[]
                    for template in temp_signal:
                        xcorr_evt_chn.append(calculate_xcorr(trace,template)['chi_max'])
                    xcorr_evt_chn=max(xcorr_evt_chn)
                    xcorr_evt.append(xcorr_evt_chn)
                xcorr_evt=max(xcorr_evt)
                xcorr.append(xcorr_evt)
                evt_lst.append([evt,evt_id])
    xcorr_min=1
    evt_x_min=None
    for ix,xcorr_each in enumerate(xcorr):
        if xcorr_each<xcorr_min:
            xcorr_min=xcorr_each
            evt_x_min=evt_lst[ix]
    ic(xcorr_min)
    ic(evt_x_min[1])
    plot_wave(evt_x_min[0])

def plot_wave(evt,temp_output='Nothing',filename=None,plt_close=False,suptitle=f'waveform'):
    Vrms=(9.71+9.66+8.94)/3
    stn = evt.get_station(51)
    run = evt.get_run_number()
    id = evt.get_id()
    trace_list=[]
    for i in range(8):
        chn=stn.get_channel(i)
        trace=chn.get_trace()/units.mV
        trace_list.append(np.max(np.abs(trace)))
    trace_max=np.max(np.array(trace_list))


    n_chns = 8
    if n_chns == 4:
        fig = plt.figure(figsize=(10, 8))
        axes = fig.subplots(nrows=2, ncols=2, sharex=True, sharey=True)
    elif n_chns == 8:
        fig = plt.figure(figsize=(10, 8))
        axes = fig.subplots(nrows=4, ncols=2, sharex=True, sharey=True)

    for i in range(n_chns):
        chn = stn.get_channel(i)
        amplitude = chn.get_trace()/units.mV
        if i == 0:
            ax = axes[0, 0]
            color = '0.5'
            ax.set_ylabel('Amplitude (mV)')
        elif i == 1:
            ax = axes[0, 1]
            color = '0.5'
        elif i == 2:
            ax = axes[1, 0]
            color = '0.5'
            ax.set_ylabel('Amplitude (mV)')
        elif i == 3:
            ax = axes[1, 1]
            color = '0.5'
        elif i == 4:
            ax = axes[2, 0]
            color = 'green'
            channel = stn.get_channel(i)
            ratio=Freqs_ratio(evt,i)
            # X=np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr']))
            # ax.set_title(f'A:{np.max(np.abs(amplitude)):.2f} X:{X:.2f}')
            # ax.set_title(f'A:{np.max(np.abs(amplitude)):.2f} F:{ratio:.3f} X:{X:.3f}')
            ax.set_title(f'A:{np.max(np.abs(amplitude)):.2f} F:f{ratio:.3f}')
            ax.set_ylabel('Amplitude (mV)')
        elif i == 5:
            ax = axes[2, 1]
            color = 'blue'
            channel = stn.get_channel(i)
            # X=np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr']))
            # ax.set_title(f'A:{np.max(np.abs(amplitude)):.2f} X:{X:.2f}')
            ratio=Freqs_ratio(evt,i)
            # ax.set_title(f'A:{np.max(np.abs(amplitude)):.2f} F:f{ratio:.3f} X:{X:.3f}')
            ax.set_title(f'A:{np.max(np.abs(amplitude)):.2f} F:f{ratio:.3f}')
            ax.set_ylabel('Amplitude (mV)')
        elif i == 6:
            ax = axes[3, 0]
            color = 'red'
            #antenna_type = 'upward LPDA'
            ax.set_ylabel('Amplitude (mV)')
            ax.set_xlabel('Time (ns)')
            channel = stn.get_channel(i)
            # X=np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr']))
            # ax.set_title(f'A:{np.max(np.abs(amplitude)):.2f} X:{X:.2f}')
            ratio=Freqs_ratio(evt,i)
            # ax.set_title(f'A:{np.max(np.abs(amplitude)):.2f} F:f{ratio:.3f} X:{X:.3f}')
            ax.set_title(f'A:{np.max(np.abs(amplitude)):.2f} F:f{ratio:.3f}')
            ax.set_ylabel('Amplitude (mV)')
        elif i == 7:
            ax = axes[3, 1]
            color = '0.5'
            #antenna_type = 'dipole'
            ax.set_xlabel('Time (ns)')
        time = chn.get_times()/units.ns
        max_index = np.argmax(amplitude)
        max = np.max(np.abs(amplitude))
        ax.plot(time, amplitude, color=color, lw=1)
        if i in [0,1,2,3,7]:
            ax.set_title(f'A:{np.max(np.abs(amplitude)):.2f}')
        ax.grid()
    stn=evt.get_station(51)
    SNR=trace_max/Vrms
    Xcorr=[]     
    for i in [4,5,6]:
        channel = stn.get_channel(i)
    id=evt.get_id()
    run=evt.get_run_number()
    evt_time=stn.get_station_time().datetime
    suptitle=f'R{run}E{id} SNR:{SNR:.2f} {trace_max:.2f}/{Vrms:.2f}'
    fig.suptitle(suptitle)
    if temp_output is 'Nothing':
        plt.show()
        return 
    if filename == None:
        filename=f'R{run}E{id}.png'
    else:
        filename=f'{filename}.png'
    try:
        plt.savefig(os.path.join(temp_output,filename))
    except(FileNotFoundError):
        os.makedirs(temp_output)
        plt.savefig(os.path.join(temp_output,filename))
    if plt_close:
        plt.close()

def plot_temp_waveform(input_path):
    e_range = np.arange(16.0, 18.6, 0.1)
    sin2Val = np.arange(0, 1.01, 0.1)
    for e in e_range[:-1]:
        e1=f'{e+0.1:.1f}'
        e=f'{e:.1f}'
        for s in sin2Val:
            s=f'{s:.1f}'
            input_files,filename=get_input_e_s(e,e1,s,input_path)
            if input_files==[]:
                continue
            reader=NuRadioRecoio.NuRadioRecoio(input_files)
            for evt in reader.get_events():
                plot_wave(evt,temp_output=os.path.join(input_path,'waveform'),filename=f'{filename}_{evt.get_parameter(evtp.evt_id)}')

def Trig_threshold(evt):
    Vrms=(9.71+9.66+8.94)/3
    stn = evt.get_station(51)
    trig=[]
    for ch in [4,5,6]:
        chn=stn.get_channel(ch)
        trace=np.max(np.abs(chn.get_trace()/units.mV))/Vrms
        trig.append(trace)
    trig=min(trig)
    ic(trig,trig>5)
    return trig>5

def Analyze_Freqs(evt):
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

    stn = evt.get_station(51)
    run = evt.get_run_number()
    id = evt.get_id()
    largest=[0,0]
    time = stn.get_station_time().datetime
    # largest:[max_amp,ratio]
    for i in range(4,7):
        spectrum,freqs,ratio=get_low_amp_ratio(80,evt,i)
        if ratio>largest[1]:
            stn=evt.get_station(51)
            chn=stn.get_channel(i)
            trace=np.max(np.abs(chn.get_trace()/units.MeV))
            largest=[trace,ratio]
    return largest[1]<0.115
        # no_pass_w.append(evt.get_parameter(evtp.event_rate))
        # pass_weight.append(evt.get_parameter(evtp.event_rate))





    

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

def SNR_cut(SNR,Xcorr):
    def Logeqs(k,b,x):
        return k*np.log10(x)+b
    x=SNR
    y1=np.full_like(x[x<6.3536],0.4569)

    x2=x[(x>6.3536)&(x<9.0836)]
    y2=Logeqs(k=0.46921,b=0.08011,x=x2)

    x3=x[(x>9.0836)&(x<10.5488)]
    y3=Logeqs(k=2.39910,b=-1.76947,x=x3)

    x4=x[(x>10.5488)&(x<20.118)]
    y4=Logeqs(k=0.50146,b=0.17221,x=x4)
    
    x5=x[(x>20.118)&(x<38.5077)]
    y5=Logeqs(k=0.26280,b=0.48331,x=x5)

    y6=np.full_like(x[x>38.5077],0.9)
    y=np.concatenate((y1,y2,y3,y4,y5,y6))
    return Xcorr>y


input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/template_with2backlope'
output_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/template_with2backlope_template_candi'

input_det_Freqs='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs'
output_det='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs/bad_7_wave'
bad_evts=['R266E2270', 'R247E1149', 'R243E15', 'R243E103', 'R243E311', 'R243E1192', 'R243E1473']
# reader=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_det_Freqs))
# for evt in reader.get_events():
#     iden=ToolsPac.get_id_info(evt)
#     if iden not in bad_evts:
#         continue
#     plot_wave(evt,output_det,iden)
# exit()




# e_range = np.arange(16.0, 18.6, 0.1)
# sin2Val = np.arange(0, 1.01, 0.1)
# input_files,filename=get_input_e_s(16.7,16.8,0.5,template_path)


def get_filename(filename):
# Your filename
    # filename = 'Stn51_IceTop_18.0-18.1eV_0.9sin2_64_6ch'

    # Define the pattern to match:
    #  _   : a literal underscore
    #  \d+ : one or more digits (this is your 'x')
    #  ch  : the literal string 'ch'
    #  $   : ensures this pattern is at the very end of the string
    parts = filename.rsplit('_', 1)
    # The string you want is the first part of that list
    result_string = parts[0]
    # Use re.sub() to replace the matched pattern with an empty string
    return result_string




# for e in e_range[:-1]:
#     e1=f'{e+0.1:.1f}'
#     e=f'{e:.1f}'
#     for s in sin2Val:
#         s=f'{s:.1f}'
#         input_files,filename=get_input_e_s(e,e1,s,template_path)
#         ic(filename)
#         writer=ToolsPac.set_writer(output_path,filename,sub_dir=False)
#         if input_files==[]:
#             continue
#         reader=NuRadioRecoio.NuRadioRecoio(input_files)
#         event_id=0
#         for evt in reader.get_events():
#             Freqs=Analyze_Freqs(evt)
#             thresh=Trig_threshold(evt)
#             stn=evt.get_station(51)
#             if not stn.has_triggered():
#                 continue
#             if Freqs and thresh:
#                 evt.set_parameter(evtp.evt_id,event_id)
#                 event_id+=1
#                 writer.run(evt)
# input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/CR_BL_Template_processed'
# output_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/CR_BL_Template_final'
# plot_temp_waveform(input_path)
# exit()

input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze4/CR_BL_4_backlope_Template'
template_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/CR_BL_2backlope_Template_final'
template_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze4/template_4_backlope'
template_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze4/template_4_backlope'
template_data,template_name=evaluate_template(input_path,template_path)
data = {}
for it,temp in enumerate(template_data):
    ic(f'{template_name[it]}:\n{get_statistic_attrs(temp)}\n')
    data[template_name[it]] = get_statistic_attrs(temp)
output_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Template_modify/'
df = pd.DataFrame(data)
df = df.T
df.to_excel(os.path.join(output_path,'template_check.xlsx'), header=['mean','median','std'])

exit()

# 4backlope
# Stn51_IceTop_18.0-18.1eV_0.8sin2
# extract_template(input_path,'Stn51_IceTop_18.2-18.3eV_0.6sin2','Stn51_IceTop_18.2-18.3eV_0.6sin2_9',6,template_path)
# extract_template(input_path,'Stn51_IceTop_18.0-18.1eV_0.9sin2','Stn51_IceTop_18.0-18.1eV_0.9sin2_67',4,template_path)
# extract_template(input_path,'Stn51_IceTop_18.2-18.3eV_0.8sin2','Stn51_IceTop_18.2-18.3eV_0.8sin2_3',6,template_path)
# extract_template(input_path,'Stn51_IceTop_17.5-17.6eV_0.9sin2','Stn51_IceTop_17.5-17.6eV_0.9sin2_10',5,template_path)
# extract_template(input_path,'Stn51_IceTop_18.0-18.1eV_0.5sin2','Stn51_IceTop_18.0-18.1eV_0.5sin2_2',6,template_path)

# extract_template(input_path,'Stn51_IceTop_18.0-18.1eV_0.0sin2','Stn51_IceTop_18.0-18.1eV_0.0sin2_2',5,template_path)
# extract_template(input_path,'Stn51_IceTop_17.6-17.7eV_0.7sin2','Stn51_IceTop_17.6-17.7eV_0.7sin2_7',5,template_path)
# extract_template(input_path,'Stn51_IceTop_18.2-18.3eV_0.4sin2','Stn51_IceTop_18.2-18.3eV_0.4sin2_2',5,template_path)
# extract_template(input_path,'Stn51_IceTop_17.3-17.4eV_0.8sin2','Stn51_IceTop_17.3-17.4eV_0.8sin2_2',5,template_path)
# extract_template(input_path,'Stn51_IceTop_17.6-17.7eV_0.6sin2','Stn51_IceTop_17.6-17.7eV_0.6sin2_3',5,template_path)

# extract_template(input_path,'Stn51_IceTop_17.9-18.0eV_0.9sin2','Stn51_IceTop_17.9-18.0eV_0.9sin2_65',5,template_path)
# extract_template(input_path,'Stn51_IceTop_17.5-17.6eV_0.7sin2','Stn51_IceTop_17.5-17.6eV_0.7sin2_6',4,template_path)
# extract_template(input_path,'Stn51_IceTop_18.1-18.2eV_0.1sin2','Stn51_IceTop_18.1-18.2eV_0.1sin2_2',6,template_path)
# extract_template(input_path,'Stn51_IceTop_17.5-17.6eV_0.8sin2','Stn51_IceTop_17.5-17.6eV_0.8sin2_16',6,template_path)
# extract_template(input_path,'Stn51_IceTop_18.0-18.1eV_0.9sin2','Stn51_IceTop_18.0-18.1eV_0.9sin2_39',6,template_path)
# 4backlope:0.9011593070702327






# 2backlope
# extract_template(input_path,'Stn51_IceTop_17.7-17.8eV_0.9sin2','Stn51_IceTop_17.7-17.8eV_0.9sin2_11',5,template_path)
# extract_template(input_path,'Stn51_IceTop_18.2-18.3eV_0.7sin2','Stn51_IceTop_18.2-18.3eV_0.7sin2_3',5,template_path)
# extract_template(input_path,'Stn51_IceTop_17.8-17.9eV_0.9sin2','Stn51_IceTop_17.8-17.9eV_0.9sin2_21',6,template_path)
# extract_template(input_path,'Stn51_IceTop_18.1-18.2eV_0.7sin2','Stn51_IceTop_18.1-18.2eV_0.7sin2_14',5,template_path)
# extract_template(input_path,'Stn51_IceTop_17.5-17.6eV_0.5sin2','Stn51_IceTop_17.5-17.6eV_0.5sin2_3',4,template_path)

# extract_template(input_path,'Stn51_IceTop_18.0-18.1eV_0.9sin2','Stn51_IceTop_18.0-18.1eV_0.9sin2_64',6,template_path)
# extract_template(input_path,'Stn51_IceTop_17.6-17.7eV_0.9sin2','Stn51_IceTop_17.6-17.7eV_0.9sin2_23',6,template_path)
# extract_template(input_path,'Stn51_IceTop_18.3-18.4eV_0.0sin2','Stn51_IceTop_18.3-18.4eV_0.0sin2_0',6,template_path)
# extract_template(input_path,'Stn51_IceTop_18.1-18.2eV_0.2sin2','Stn51_IceTop_18.1-18.2eV_0.2sin2_0',5,template_path)
# extract_template(input_path,'Stn51_IceTop_17.9-18.0eV_0.8sin2','Stn51_IceTop_17.9-18.0eV_0.8sin2_6',5,template_path)

# extract_template(input_path,'Stn51_IceTop_18.4-18.5eV_0.2sin2','Stn51_IceTop_18.4-18.5eV_0.2sin2_3',5,template_path)
# extract_template(input_path,'Stn51_IceTop_18.2-18.3eV_0.8sin2','Stn51_IceTop_18.2-18.3eV_0.8sin2_17',5,template_path)
# extract_template(input_path,'Stn51_IceTop_17.7-17.8eV_0.9sin2','Stn51_IceTop_17.7-17.8eV_0.9sin2_14',5,template_path)
# extract_template(input_path,'Stn51_IceTop_17.3-17.4eV_0.8sin2','Stn51_IceTop_17.3-17.4eV_0.8sin2_0',6,template_path)
# extract_template(input_path,'Stn51_IceTop_17.3-17.4eV_0.8sin2','Stn51_IceTop_17.3-17.4eV_0.8sin2_0',6,template_path)
# 2backlope:0.9080050602198289




# 1backL
# extract_template(input_path,'Stn51_IceTop_18.4-18.5eV_0.3sin2','Stn51_IceTop_18.4-18.5eV_0.3sin2_2',5,template_path)
# extract_template(input_path,'Stn51_IceTop_18.0-18.1eV_0.9sin2','Stn51_IceTop_18.0-18.1eV_0.9sin2_12',5,template_path)
# extract_template(input_path,'Stn51_IceTop_17.6-17.7eV_0.9sin2','Stn51_IceTop_17.6-17.7eV_0.9sin2_5',6,template_path)
# extract_template(input_path,'Stn51_IceTop_17.8-17.9eV_0.9sin2','Stn51_IceTop_17.8-17.9eV_0.9sin2_23',6,template_path)
# extract_template(input_path,'Stn51_IceTop_18.3-18.4eV_0.8sin2','Stn51_IceTop_18.3-18.4eV_0.8sin2_29',5,template_path)

# extract_template(input_path,'Stn51_IceTop_18.0-18.1eV_0.9sin2','Stn51_IceTop_18.0-18.1eV_0.9sin2_42',6,template_path)
# extract_template(input_path,'Stn51_IceTop_18.1-18.2eV_0.7sin2','Stn51_IceTop_18.1-18.2eV_0.7sin2_3',5,template_path)
# extract_template(input_path,'Stn51_IceTop_17.9-18.0eV_0.6sin2','Stn51_IceTop_17.9-18.0eV_0.6sin2_7',6,template_path)
# extract_template(input_path,'Stn51_IceTop_17.9-18.0eV_0.0sin2','Stn51_IceTop_17.9-18.0eV_0.0sin2_0',5,template_path)
# extract_template(input_path,'Stn51_IceTop_18.4-18.5eV_0.2sin2','Stn51_IceTop_18.4-18.5eV_0.2sin2_4',6,template_path)

# extract_template(input_path,'Stn51_IceTop_18.4-18.5eV_0.2sin2','Stn51_IceTop_18.4-18.5eV_0.2sin2_0',6,template_path)
# extract_template(input_path,'Stn51_IceTop_18.1-18.2eV_0.7sin2','Stn51_IceTop_18.1-18.2eV_0.7sin2_14',6,template_path)
# extract_template(input_path,'Stn51_IceTop_17.8-17.9eV_0.9sin2','Stn51_IceTop_17.8-17.9eV_0.9sin2_26',6,template_path)
# extract_template(input_path,'Stn51_IceTop_17.9-18.0eV_0.8sin2','Stn51_IceTop_17.9-18.0eV_0.8sin2_7',5,template_path)
# extract_template(input_path,'Stn51_IceTop_18.3-18.4eV_0.0sin2','Stn51_IceTop_18.3-18.4eV_0.0sin2_0',6,template_path)
# 1backlope:0.9213655562458981






# NobackL
# extract_template(input_path,'Stn51_IceTop_17.4-17.5eV_0.6sin2','Stn51_IceTop_17.4-17.5eV_0.6sin2_0',6,template_path)
# extract_template(input_path,'Stn51_IceTop_17.8-17.9eV_0.6sin2','Stn51_IceTop_17.8-17.9eV_0.6sin2_2',5,template_path)
# extract_template(input_path,'Stn51_IceTop_17.8-17.9eV_0.8sin2','Stn51_IceTop_17.8-17.9eV_0.8sin2_27',6,template_path)
# extract_template(input_path,'Stn51_IceTop_17.6-17.7eV_0.9sin2','Stn51_IceTop_17.6-17.7eV_0.9sin2_7',4,template_path)
# extract_template(input_path,'Stn51_IceTop_18.4-18.5eV_0.8sin2','Stn51_IceTop_18.4-18.5eV_0.8sin2_30',5,template_path)

# extract_template(input_path,'Stn51_IceTop_18.3-18.4eV_0.2sin2','Stn51_IceTop_18.3-18.4eV_0.2sin2_0',5,template_path)
# extract_template(input_path,'Stn51_IceTop_18.4-18.5eV_0.0sin2','Stn51_IceTop_18.4-18.5eV_0.0sin2_3',5,template_path)
# extract_template(input_path,'Stn51_IceTop_18.1-18.2eV_0.4sin2','Stn51_IceTop_18.1-18.2eV_0.4sin2_2',6,template_path)
# extract_template(input_path,'Stn51_IceTop_18.1-18.2eV_0.4sin2','Stn51_IceTop_18.1-18.2eV_0.4sin2_3',6,template_path)
# extract_template(input_path,'Stn51_IceTop_18.2-18.3eV_0.3sin2','Stn51_IceTop_18.2-18.3eV_0.3sin2_2',6,template_path)

# extract_template(input_path,'Stn51_IceTop_17.5-17.6eV_0.8sin2','Stn51_IceTop_17.5-17.6eV_0.8sin2_2',6,template_path)
# extract_template(input_path,'Stn51_IceTop_18.3-18.4eV_0.6sin2','Stn51_IceTop_18.3-18.4eV_0.6sin2_2',5,template_path)
# extract_template(input_path,'Stn51_IceTop_18.3-18.4eV_0.3sin2','Stn51_IceTop_18.3-18.4eV_0.3sin2_2',4,template_path)
# extract_template(input_path,'Stn51_IceTop_18.1-18.2eV_0.7sin2','Stn51_IceTop_18.1-18.2eV_0.7sin2_1',6,template_path)
# extract_template(input_path,'Stn51_IceTop_18.2-18.3eV_0.2sin2','Stn51_IceTop_18.2-18.3eV_0.2sin2_0',5,template_path)
# NoBacklope:0.9404616652891498





# Stn51_IceTop_17.4-17.5eV_0.6sin2_0.png
    # template_file=['Stn51_IceTop_17.5-17.6eV_0.9sin2']
    # template_id=['Stn51_IceTop_17.5-17.6eV_0.9sin2_009evt']
    # ch_id=9

# for evt in reader.get_events():
#     stn=evt.get_station(51)
#     trace_max    = []
#     for channel in stn.iter_channels(use_channels=[0,1,2,3,4,5,6,7]):
#         trace_max.append(np.max(np.abs(channel.get_trace()/units.mV)))
#     trace_max=np.max(trace_max)/Vrms
#     Xcorr=[]
#     # for i in [4,5,6]:
#         # channel = stn.get_channel(i)
#         # Xmax=np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr']))
#         # Xcorr.append(Xmax)
#     # Xcorr=np.max(Xcorr)
#     # if not SNR_cut(trace_max,Xcorr):
#         # continue
#     # if Xcorr<=0.85:
#     #     continue
#     plot_wave(evt,output_path)
# plot_temp_waveform(template_path)
# temp_comprehensive_check(input_path,template_path)
# template_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/template_with_4backlope'
# 0.9060442795326014
# 0.9028635416812816



        


# filename='Stn51_IceTop_18.0-18.1eV_0.9sin2_64_6ch.nur'

input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/CR_BL_Template_final'

tar_files=[]
for file in os.listdir(input_path):
    if file.endswith('.nur'):
        ic(get_filename(file))
        tar_files.append(get_filename(file))
template_evts='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/CR_BL_Template_processed'
output_temp='/Users/david/PycharmProjects/Demo1/Research/Repository/nobl_temp_evts'
os.makedirs(output_temp)
for file in tar_files:
    tar_events=[]
    e_s_id=file.rsplit('_',1)[0]
    ic(e_s_id)
    for e_s in ToolsPac.get_input(template_evts):
        if e_s_id in e_s:
            tar_events.append(e_s)
        if e_s_id==[]:
            continue
    # ic(tar_events)
    # print()
    reader=NuRadioRecoio.NuRadioRecoio(tar_events)
    writer=ToolsPac.set_writer(output_temp,file,sub_dir=False)
    for evt in reader.get_events():
        evt_id=evt.get_parameter(evtp.evt_id)
        if f'{e_s_id}_{evt_id}'==file:
            writer.run(evt)