import os
import send2trash
import NuRadioReco.modules.io.eventWriter
eventWriter = NuRadioReco.modules.io.eventWriter.eventWriter()
import numpy as np
from NuRadioReco.framework.parameters import channelParameters as chp
from NuRadioReco.utilities import units
import datetime
import NuRadioReco
import NuRadioReco.modules.io.NuRadioRecoio
import NuRadioReco.framework.event
from icecream import ic
import matplotlib.pyplot as plt

def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir
def set_writer(output,filename,sub_dir=True):
    if sub_dir:
        output_file = os.path.join(output,filename)
        try:
            os.makedirs(output_file)
        except(FileExistsError):
            send2trash.send2trash(output_file)
            os.makedirs(output_file)
    else:
        output_file = output
        if not os.path.isdir(output_file):
            os.mkdir(output_file)
    eventWriter.begin(os.path.join(output_file,f'{filename}.nur'))
    return eventWriter

def get_Xcorr(stn:NuRadioReco.framework.station.Station,used_chn:list):
    Xcorr=[]
    for i in used_chn:
        channel = stn.get_channel(i)
        Xcorr.append(np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr'])))
    Xcorr = np.array(Xcorr)
    Xcorr=np.max(Xcorr)
    return Xcorr

def evt_to_template(evt:NuRadioReco.framework.event.Event,Temp_id):
    stn = evt.get_station(51)
    sampling_rate=0
    chn = stn.get_channel(Temp_id)
    trace = chn.get_trace()
    for i in [0,1,2,3,4,5,6,7]:
        chn = stn.get_channel(i)
        sampling_rate = chn.get_sampling_rate()
        chn.set_trace(trace=trace,sampling_rate=sampling_rate)
    return evt


def get_Max_trace(stn:NuRadioReco.framework.station.Station,used_chn:list):
    trace_max    = []
    for channel in stn.iter_channels(use_channels=used_chn):
        trace_max.append(np.max(np.abs(channel.get_trace()/units.mV)))
    return np.max(trace_max)

def get_id_info(evt:NuRadioReco.framework.event.Event):
    return f'R{evt.get_run_number()}E{evt.get_id()}'

def makedirs(directory,exist_ok=False):
    try:
        os.makedirs(directory)
    except(FileExistsError):
        if exist_ok:
            pass
        else:
            send2trash.send2trash(directory)
            os.makedirs(directory)


def channelTemplateCorrelation_custimized(
        evt:NuRadioReco.framework.event.Event,
        stn_id:int,
        Template_reader:NuRadioReco.modules.io.NuRadioRecoio.NuRadioRecoio,
        used_channel=[4,5,6]
        ):
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
    

    Temp_trlst=[]
    for temp_evt in Template_reader.get_events():
        stn = temp_evt.get_station(stn_id)
        for i in used_channel:
            chn = stn.get_channel(i)
            Temp_trlst.append(chn.get_trace())
            break
    
    chi_info=[]
    chi_lst=[]

    stn = evt.get_station(stn_id)
    for it,temp in enumerate(Temp_trlst):
        chi_loc_lst=[]
        chi_loc_info={}
        for chn_id in used_channel:
            chn = stn.get_channel(chn_id)
            trace=chn.get_trace()
            x_info = calculate_xcorr(temp,trace)
            chi_loc_info[chn_id]=x_info
            chi_loc_lst.append(x_info['chi_max'])
            # plot_waveform_with_phase(trace,temp,x_info['chi_phase'])
        chi_lst.append(max(chi_loc_lst))
        chi_info.append(chi_loc_info)
    xcorr_info=chi_info[np.argmax(chi_lst)]




    for chn_id in used_channel:
        xcorr_chn=xcorr_info[chn_id]
        chn = stn.get_channel(chn_id)
        chn[chp.cr_xcorrelations]={}
        chn[chp.cr_xcorrelations]['cr_ref_xcorr'] = np.float64(xcorr_chn['chi_max'])
        chn[chp.cr_xcorrelations]['cr_ref_xcorr_time'] = np.float64(xcorr_chn['chi_phase'])
        # chn[chp.cr_xcorrelations]=xcorrelations
    return

def plot_waveform_with_phase(Temp_wave,trace_wave,phase,X=None,title=None):
    arr_pre = Temp_wave[:phase]
    arr_pos = Temp_wave[phase:]
    arr1    = np.concatenate((arr_pos,arr_pre))
    fig,ax = plt.subplots(figsize=(10,5))
    ax.plot(range(256),arr1,c='red',linestyle='--')
    ax.plot(range(256),trace_wave,zorder=0)
    if X == None:
        pass
    else:
        ax.set_title(fr'{title}$\chi$={X}')
    plt.show()

def plot_waveform_compare_pase(Temp_wave,trace_wave,phase,X_max=None,X_now=None,title=None):
    arr_pre = Temp_wave[:phase]
    arr_pos = Temp_wave[phase:]
    arr1    = np.concatenate((arr_pos,arr_pre))
    fig,ax = plt.subplots(figsize=(10,5))
    ax.plot(range(256),arr1,c='red',linestyle='--')
    ax.plot(range(256),trace_wave,zorder=0)
    ax.set_title(fr'Now={X_now:.4f} Max={X_max:.4f}')
    plt.show()

def annotate_scatter(ax,x,y,labels):
    for xi, yi, txt in zip(x, y, labels):
        ax.annotate(
            txt,                 # text to draw
            xy=(xi, yi),         # point to annotate
            xytext=(5, 5),       # (dx, dy) offset in points
            textcoords='offset points',
            fontsize=9, weight='bold',
            ha='left', va='bottom'
        )

def direction_plot(ax:plt.axes,zen,azi,alpha=1,zorder=0,color='r',label=None,annotate=False,iden=[],s=20):
    # azi in rad, zen in degree
    ax.set_rlim(0,90)
    if annotate:
        if iden==[]:
            raise IndexError('Need identity info.')
        else:
            annotate_scatter(ax,azi,zen,iden)
    if label is None:
        ax.scatter(azi,zen,s=s,alpha=alpha,zorder=zorder,color=color,label=f'num: {len(azi)}')
    else:
        ax.scatter(azi,zen,s=s,alpha=alpha,zorder=zorder,color=color,label=f'{label}: {len(azi)}')
    ax.legend()
    return ax

    


# xcorrelations['{}_ref_xcorr'.format(ref_str)] = np.abs(xcorrs_ch).mean()
# xcorrelations['{}_ref_xcorr_all'.format(ref_str)] = np.abs(xcorrs_ch)
# xcorrelations['{}_ref_xcorr_max'.format(ref_str)] = np.abs(xcorrs_ch[np.argmax(np.abs(xcorrs_ch))])
# xcorrelations['{}_ref_xcorr_time'.format(ref_str)] = np.mean(xcorrpos_ch[np.argmax(np.abs(xcorrs_ch))]) * dt
# xcorrelations['{}_ref_xcorr_template'.format(ref_str)] = template_key[np.argmax(np.abs(xcorrs_ch))]
# channel[chp.cr_xcorrelations] = xcorrelations

        


    
    
    