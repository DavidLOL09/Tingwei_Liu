Vrms=(9.71+9.66+8.94)/3
import os
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from icecream import ic
from NuRadioReco.utilities import units
from NuRadioReco.modules.io import NuRadioRecoio
json_file_origin=f'/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/Stn51_sim_inAir/station51.json'
from NuRadioReco.detector import detector
det=detector.Detector(json_filename=json_file_origin)
from NuRadioReco.framework.parameters import eventParameters as evtp
import NuRadioReco.modules.io.eventWriter
eventWriter = NuRadioReco.modules.io.eventWriter.eventWriter()

import send2trash
# input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/SNR_cut1'
input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/New_temp_Xcorr/3X_SNR'
# output_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/'
output_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output/'
def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir
def set_writer(output_path,filename):
    sig = os.path.join(output_path,f'{filename}')
    try:
        os.makedirs(sig)
    except(FileExistsError):
        send2trash.send2trash(sig)
        os.makedirs(sig)
    eventWriter.begin(os.path.join(sig,f'{filename}.nur'))
    return eventWriter
def log_cut_line(x):
    # UD:
    k=3.358751507788999
    y=k*np.log10(x)-5.067864845613618
    return y

    # Bic:
    k=3.9015114425732005
    y=k*np.log10(x)-6.360165150568652
    return y
# set_writer(output_path,'sim_X_with_R')
def get_Ratio_save(input_path,eventWriter):
    evtReader = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    for evt in evtReader.get_events():
        stn = evt.get_station(51)

        trace_up = []
        for channel in stn.iter_channels(use_channels=[4,5,6]):
            trace_up.append(np.max(np.abs(channel.get_trace()/units.mV)))
        trace_up = max(trace_up)

        trace_down = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3]):
            trace_down.append(np.max(np.abs(channel.get_trace()/units.mV)))
        trace_down = max(trace_down)

        trace_bic=0
        trace_bic = np.max(np.abs(stn.get_channel(7).get_trace()/units.mV))

        evt.set_parameter(evtp.UD_Ratio,trace_up/trace_down)
        evt.set_parameter(evtp.Bic_Ratio,trace_up/trace_bic)
        Ratio=trace_up/trace_down
        trace_max=(max(trace_up,trace_down))
        if trace_max>=100 and Ratio<log_cut_line(trace_max):
            continue
        eventWriter.run(evt)
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

def Plot_Ratio_Amp(input_path,det_input):
    evtReader = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    fig,ax=plt.subplots(figsize=(8,8))
    Ratio=[]
    weights=[]
    Amp_up=[]
    Amp_down=[]
    Amp_Bic=[]
    for evt in evtReader.get_events():
        stn=evt.get_station(51)
        trace_up = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3,4,5,6,7]):
            trace_up.append(np.max(np.abs(channel.get_trace()/units.mV)))
        Amp_up.append(max(trace_up))

        trace_down=[]
        for channel in stn.iter_channels(use_channels=[0,1,2,3]):
            trace_down.append(np.max(np.abs(channel.get_trace()/units.mV)))
        Amp_down.append(max(trace_down))

        channel=stn.get_channel(7)
        Amp_Bic.append(np.max(np.abs(channel.get_trace()/units.mV)))

        weights.append(evt.get_parameter(evtp.event_rate))
    Amp_max = np.array(Amp_up)
    Amp_Bic  = np.array(Amp_Bic)
    Amp_down= np.array(Amp_down)
    Ratio=Amp_max/Amp_down
    Amp_bins=np.linspace(np.min(Amp_max),np.max(Amp_max),101)
    Ratio_bins=np.linspace(np.min(Ratio),np.max(Ratio),101)
    ax.set_xscale('log')
    ax.set_xlim(20,1.2*np.max(Amp_max))
    ax.set_ylim(0,np.max(Ratio)+3)
    # ax.set_yscale('log')
    # ax.set_ylim(0,15)
    hist,_,_=np.histogram2d(Amp_max,Ratio,bins=(Amp_bins,Ratio_bins),weights=weights)
    S,X=np.meshgrid(Amp_bins,Ratio_bins)
    pm=ax.pcolormesh(S,X,hist.T,norm=matplotlib.colors.LogNorm(),zorder=0)
    ax.figure.colorbar(pm,ax=ax)
    ax.set_xlabel(f'Amp(mV)',fontsize=20)
    ax.set_ylabel('Ratio(U/Bic)',fontsize=20)
    x=np.linspace(1,10000,1001)
    y=log_cut_line(x)
    ax.plot(x,y,color='orange',linestyle='--',zorder=3)
    # ax.axhline(y=1.23,c='orange',linestyle='--')
    evtReader=NuRadioRecoio.NuRadioRecoio(get_input(det_input))
    Amp_max=[]
    Amp_down=[]
    Amp_Bic=[]
    Ratio=[]
    Iden=[]
    for evt in evtReader.get_events():
        stn=evt.get_station(51)
        trace_max = []
        trace_down = []
        trace_up = []
        Iden.append(f'R{evt.get_run_number()}E{evt.get_id()}')
        for channel in stn.iter_channels(use_channels=[0,1,2,3,4,5,6,7]):
            trace_up.append(np.max(np.abs(channel.get_trace()/units.mV)))
        trace_up=max(trace_up)
        for channel in stn.iter_channels(use_channels=[0,1,2,3]):
            trace_down.append(np.max(np.abs(channel.get_trace()/units.mV)))
        trace_down=max(trace_down)
        channel=stn.get_channel(7)
        Amp_Bic.append(np.max(np.abs(channel.get_trace()/units.mV)))
        Amp_max.append(max([trace_up,trace_down]))
        Amp_down.append(trace_down)
    Amp_max=np.array(Amp_max)
    Amp_down=np.array(Amp_down)
    Amp_Bic=np.array(Amp_Bic)
    Ratio = Amp_max/Amp_down
    # Ratio=evt.get_parameter(evtp.UD_Ratio)
    ic(len(Amp_max),len(Ratio))
    ax.tick_params(axis='x', labelsize=20)
    ax.tick_params(axis='y', labelsize=20)

    red_max,red_R=[],[]
    grey_max,grey_R=[],[]
    for i in range(0,len(Ratio)):
        if Ratio[i]>=log_cut_line(Amp_max[i]):
            red_max.append(Amp_max[i])
            red_R.append(Ratio[i])
        else:
            grey_max.append(Amp_max[i])
            grey_R.append(Ratio[i])
    ax.scatter(red_max,red_R,s=3,c='r',label=len(red_max))
    ax.scatter(grey_max,grey_R,s=1,c='grey',label=len(grey_R))
    # annotate_scatter(ax,Amp_max,Ratio,Iden)
    ax.legend(fontsize=20)
    plt.tight_layout()
    plt.show()
    # plt.savefig('/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/UD_Ratio.png')
det_input='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/New_temp_Xcorr/3X_SNR_Ratio'
# k=(2.7-1)/(np.log10(210)-np.log10(77))
# ic(k)
# ic(log_cut_line(77))
Plot_Ratio_Amp(input_path,det_input)
# evtWriter=set_writer(output_path,'X_Zen_UD')
# get_Ratio_save(input_path,evtWriter)

# 1.25 for UD_Ratio
# 1.23 for Bic_Ratio

    

    

