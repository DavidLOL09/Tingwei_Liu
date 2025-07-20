import numpy as np
import NuRadioReco.utilities.units as units
from icecream import ic
import matplotlib
import NuRadioReco
from NuRadioReco.framework.parameters import stationParameters as stnp
from NuRadioReco.framework.parameters import channelParameters as chp
import datetime
import matplotlib.pyplot as plt
import NuRadioReco.modules.io.NuRadioRecoio as NuRadioRecoio
from NuRadioReco.detector import detector
from NuRadioReco.detector import generic_detector
import send2trash
import matplotlib.pyplot as plt
from NuRadioReco.framework.parameters import eventParameters as evtp
from NuRadioReco.modules.channelStopFilter import channelStopFilter
channelStopFilter=channelStopFilter()
import NuRadioReco.modules.channelBandPassFilter
channelBandPassFilter = NuRadioReco.modules.channelBandPassFilter.channelBandPassFilter()
json_file_origin=f'/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/Stn51_sim_inAir/station51.json'
det=detector.Detector(json_filename=json_file_origin)
import NuRadioReco.modules.io.eventWriter
eventWriter = NuRadioReco.modules.io.eventWriter.eventWriter()
goso=[242,243,247,249,256,260,263,264,266]
import os
import math
ic(NuRadioRecoio.__file__)
Vrms=(9.71+9.66+8.94)/3
import ToolsPac

sim = '/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Trig_Freqs_X_SNR_with_direct/Candi_with_direct/withTemp_R243E512'
detected = '/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Trig_Freqs'

def get_corr(arr1:np.array,arr2:np.array):
    return np.abs(np.dot(arr1,arr2)/np.sqrt(np.dot(arr1,arr1)*np.dot(arr2,arr2)))
def calculate_xcorr(arr1:np.array,arr2:np.array):
    if len(arr1)!=len(arr2):
        raise IndexError('arr1 and arr2 have different length')
    chi_max     = 0
    chi_phase   = 0
    xcorrelation= []
    for i in range(len(arr1)):
        arr_pre = arr1[:i]
        arr_pos = arr1[i:]
        arr1    = np.concatenate((arr_pos,arr_pre))
        Xcorr   = get_corr(arr1,arr2)
        xcorrelation.append(Xcorr)
        if Xcorr > chi_max:
            chi_max     = Xcorr
            chi_phase   = i
    return {'xcorrelation':xcorrelation,'chi_max':chi_max,'chi_phase':chi_phase}
# {'xcorrelation':chi,'chi_max':chi_max,'max_phase':chi_phase}

Temp_id='R243E512'
input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Candi_with_direct'
output_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/New_temp_Xcorr'
def get_Temp_input_path(Temp_id):
    return f'/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Candi_with_direct/event_sep/{Temp_id}'
def get_path_with_Temp(Temp_id):
    return f'/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Candi_with_direct/withTemp_{Temp_id}'

# def get_max_xcorr_info(Temp_corr:dict)

def set_writer(output,filename):    
    try:
        os.makedirs(output)
    except(FileExistsError):
        send2trash.send2trash(output)
        os.makedirs(output)
    eventWriter.begin(os.path.join(output,f'{filename}.nur'))
    return eventWriter

def Get_Xcorr_with_Temp(input_path,Temp_path):
    Data_reader=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))
    Temp_reader=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(Temp_path))

    Temp_trace={}
    Temp_id=''
    for evt in Temp_reader.get_events():
        stn=evt.get_station(51)
        Temp_id=f'R{evt.get_run_number()}E{evt.get_id()}'
        for i in [4,5,6]:
            chn = stn.get_channel(i)
            trace=chn.get_trace()/units.mV
            Temp_trace[f'ch_{i}']=trace
        
    Writer=ToolsPac.set_writer(output_path,f"withTemp_{Temp_id}")
    # Writer=set_writer(input_path,'with_Temp')
    for evt in Data_reader.get_events():
        stn=evt.get_station(51)
        # ic(evt[evtp.Pass_cut_line][Temp_id_1])
        channelStopFilter.run(evt,stn,det,append=0,prepend=0)
        channelBandPassFilter.run(evt, stn, det, passband=[80 * units.MHz, 500 * units.MHz], filter_type='butter', order = 10)
        for i in [4,5,6]:
            chn = stn.get_channel(i)
            trace   = chn.get_trace()/units.mV
            Temp_amp = Temp_trace[f'ch_{i}']
            try:
                chn[chp.Chi_Temp][Temp_id]=calculate_xcorr(Temp_amp,trace)
            except(KeyError):
                chn[chp.Chi_Temp]={Temp_id:calculate_xcorr(Temp_amp,trace)}
            # chn[chp.Chi_Temp]={'xcorrelation':chi,'xcorrelation_max':chi_max,'max_phase':chi_phase}
        Writer.run(evt)
    return os.path.join(output_path,f"withTemp_{Temp_id}")

# check:

def check_Chi_Temp(input_path):
    Reader=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))
    for evt in Reader.get_events():
        id=ToolsPac.get_id_info(evt)
        stn=evt.get_station(51)
        ic(id)
        for i in [4,5,6]:
            chn=stn.get_channel(i)
            ic(chn[chp.Chi_Temp])
    exit()

def SNR_Xcorr_Scatter_sim(ax:plt.axes,readARIANNAData:NuRadioReco.modules.io):
    SNR_dic = []
    X_dic   = []
    # ax.set_title(f'{name} chn{chn}')
    ax.set_ylabel('Xcorr')
    weights=[]
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        Xcorr=[] 
        for chn in [4,5,6]:  
            channel = stn.get_channel(chn)
            Xcorr.append(np.max(np.abs(channel[chp.Chi_Temp]['R243E512']['chi_max'])))
        trace_up    = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3,4,5,6,7]):
            trace_up.append(np.max(np.abs(channel.get_trace()/units.mV)))
        # if np.max(Xcorr)<=SNR_cut_line_cut(max(trace_up)/Vrms):
        #     continue
        X_dic.append(np.max(Xcorr))
        SNR_dic.append(max(trace_up)/Vrms)
        weights.append(evt.get_parameter(evtp.event_rate))
    ic(len(SNR_dic),len(X_dic))
    # ax.set_xscale('log')
    # SNR_bins=np.linspace(np.min(SNR_dic),np.max(SNR_dic),101)
    SNR_bins = np.logspace(np.log10(np.min(SNR_dic)), np.log10(np.max(SNR_dic)), 101)
    weights=np.array(weights)*(datetime.timedelta(days=31, seconds=8844)/datetime.timedelta(days=365))
    # for i in weights:
    #     ic(i,type(i))
    X_bins=np.linspace(0,1,101)
    ax.set_xlim(3,900)
    ax.set_ylim(0.2,1)
    hist,_,_=np.histogram2d(SNR_dic,X_dic,bins=(SNR_bins,X_bins),weights=weights)
    S,X=np.meshgrid(SNR_bins,X_bins)
    pm=ax.pcolormesh(S,X,hist.T,norm=matplotlib.colors.LogNorm(),zorder=0)
    ax.figure.colorbar(pm,ax=ax)
    # patch = mpatches.Patch(color='lightblue', label='Your Label Here')
    ax.set_xlabel(f'SNR:{np.sum(weights):.3g}',fontsize=40)
    ax.set_ylabel(fr'$\chi$',fontsize=40)
    # ax.legend(handles=[patch],fontsize=20)
    ax.legend(loc='lower right',fontsize=40)


def SNR_cut_line_cut(x):
    k=0.21622342843989703
    y=k*np.log10(x)+0.2444278883161825
    y=np.zeros_like(x)
    for i,elmt in enumerate(x):
        if elmt >= 10:
            y[i] = SNR_cut_line_cut_10_2753(x[i])
        if elmt < 10:
            y[i] = SNR_cut_line_cut_0_10(x[i])
    y[y <= 0.35] = 0.35
    y[y >= 0.6] = 0.6
    return y

def SNR_cut_line_cut_10_2753(x):
    k=0.3183220163182149
    y=k*np.log10(x)+0.14167798368178514
    return y

def SNR_cut_line_cut_0_10(x):
    k=0.7101265859394174
    y=k*np.log10(x)-0.2501265859394173
    return y


def SNR_cut_line(ax):
    x=np.linspace(1,1000,1001)
    y = SNR_cut_line_cut(x)
    ax.plot(x,y,color='blue',linestyle='--',zorder=3)

def make_cut(Reader:NuRadioReco.modules.io,Temp_id,output):
    eventWriter=ToolsPac.set_writer(output,'R243E512_cut')
    for evt in Reader.get_events():
        stn = evt.get_station(51)
        Xcorr=[]    
        for i in [4,5,6]:
            channel = stn.get_channel(i)
            Xcorr.append(np.max(np.abs(channel[chp.Chi_Temp][Temp_id]['chi_max'])))
        trace_up    = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3,4,5,6,7]):
            trace_up.append(np.max(np.abs(channel.get_trace()/units.mV)))
        Xcorr=np.max(Xcorr)
        trace_up=np.max(trace_up)/Vrms
        # ic(trace_up,Xcorr)
        # ic(Xcorr>SNR_cut_line_cut(trace_up))
        try:
            evt[evtp.Pass_cut_line][Temp_id] = Xcorr>SNR_cut_line_cut(trace_up)
        except(KeyError):
            evt[evtp.Pass_cut_line]={Temp_id:Xcorr>SNR_cut_line_cut(trace_up)}
        eventWriter.run(evt)
        
        
        # {Template id:True/False}
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

def SNR_Xcorr_Scatter(ax:plt.axes,name:str,readARIANNAData:NuRadioReco.modules.io,Temp_id,Temp_id_1,zorder=1,color='r',alfa=1,has_cutline=False):
    # ax.set_title('SNR')
    # ax.set_xlabel('SNR')
    SNR_dic=[]
    X_dic=[]
    ax.set_ylabel('Xcorr')
    # evt[evtp.Pass_cut_line][Temp_id]
    SNR_dic_g=[]
    X_dic_g=[]
    iden=[]
    weights=[]
    for evt in readARIANNAData.get_events():   
        stn = evt.get_station(51)
        Xcorr=[]    
        for i in [4,5,6]:
            channel = stn.get_channel(i)
            Xcorr.append(np.max(np.abs(channel[chp.Chi_Temp][Temp_id]['chi_max'])))
        trace_up    = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3,4,5,6,7]):
            trace_up.append(np.max(np.abs(channel.get_trace()/units.mV)))
        Xcorr=np.max(Xcorr)
        trace_up=np.max(trace_up)
        if has_cutline:
            if evt[evtp.Pass_cut_line][Temp_id_1]:
                SNR_dic.append(trace_up/Vrms)
                X_dic.append(Xcorr)
                iden.append(ToolsPac.get_id_info(evt))
            else:
                SNR_dic_g.append(trace_up/Vrms)
                X_dic_g.append(Xcorr)
        else:
            SNR_dic.append(trace_up/Vrms)
            X_dic.append(Xcorr)
            iden.append(ToolsPac.get_id_info(evt))
    # annotate_scatter(ax,SNR_dic,X_dic,iden)
    ax.set_ylim(0.2,1)
    ax.set_xlim(3,900)
    ax.scatter(SNR_dic,X_dic,s=20,c=color,label=f'{len(SNR_dic)}',zorder=zorder,alpha=alfa)
    # ax.scatter(SNR_dic_g,X_dic_g,s=20,c='grey',label=f'failed: {Temp_id}',zorder=0)
    # ax.scatter(SNR_dic_g,X_dic_g,s=5,c='grey',label=f'No-pass:{len(SNR_dic_g)}',zorder=zorder,alpha=alfa)
    ax.set_xscale('log')
Temp_id='R243E512'
Temp_id_1='R243E512'
# reader=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input('/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Candi_with_direct/withTemp_R243E512'))

# make_cut(reader,'R243E512',output_path)
# exit()
# input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Candi_with_direct/R243E512_cut'
input_sim='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/New_temp_Xcorr/withTemp_R243E512'
input_sim='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/New_temp_Xcorr/3X_SNR_Ratio'
# input_sim='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/New_temp_Xcorr/3X'
# test_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Candi_with_direct/withTemp_R242E10'
Temp_path=get_Temp_input_path(Temp_id)
# check_Chi_Temp(input_path)
# exit()
# Get_Xcorr_with_Temp(input_sim,Temp_path)
# Get_Xcorr_with_Temp(test_path,Temp_path)
# detected=Get_Xcorr_with_Temp(detected,Temp_path)
detected='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/New_temp_Xcorr/withTemp_R243E512'
# detected='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/New_temp_Xcorr/3X'
# detected='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/New_temp_Xcorr/3X_SNR'
detected='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/New_temp_Xcorr/3X_SNR_Ratio'
reader=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(detected))

fig,ax = plt.subplots(figsize=(10,8),layout='constrained')
# reader=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))

sim_Reader = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_sim))

SNR_Xcorr_Scatter_sim(ax,sim_Reader)

SNR_Xcorr_Scatter(ax,'SNR',reader,Temp_id,Temp_id_1)
ax.grid()
ax.set_xscale('log')
# ax.tick_params(axis='x', labelsize=40)
# ax.tick_params(axis='y', labelsize=40)
SNR_cut_line(ax)
plt.legend()
plt.savefig(os.path.join(output_path,'Trig-rate_Freqs_3X_SNR_Ratio.png'))
plt.show()

    



