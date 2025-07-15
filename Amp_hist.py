from NuRadioReco.modules.io import NuRadioRecoio
import os
import numpy as np
from NuRadioReco.utilities import units
import matplotlib.pyplot as plt
from NuRadioReco.framework.parameters import eventParameters as evtp


input_dir='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_X_output/X_Ratio_Zen_TrigR8_cut'
def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir

def get_trace_real(input_dir):
    try:
        readARIANNAData=NuRadioRecoio.NuRadioRecoio(get_input(input_dir))
    except:
        return []
    max_trace=[]
    for evt in readARIANNAData.get_events():
        stn=evt.get_station(51)
        trace_up=[]
        for channel in stn.iter_channels(use_channels=[4,5,6]):
            trace_up.append(np.max(np.abs(channel.get_trace()/units.mV)))
        max_trace.append(max(trace_up))
    return max_trace
def get_trace_sim(input_dir):
    try:
        readARIANNAData=NuRadioRecoio.NuRadioRecoio(get_input(input_dir))
    except:
        return [],[]
    max_trace=[]
    weights=[]
    for evt in readARIANNAData.get_events():
        stn=evt.get_station(51)
        trace_up=[]
        weights.append(evt.get_parameter(evtp.event_rate))
        for channel in stn.iter_channels(use_channels=[4,5,6]):
            trace_up.append(np.max(np.abs(channel.get_trace()/units.mV)))
        max_trace.append(max(trace_up))
    return max_trace,weights
def E_scatter(trace,bins,ax,name=None,weights=None):
    if weights==None:
        ax.set_title(name)
        ax.hist(trace,bins,alpha=0.8,color='r')
        ax.set_xscale('log')
        ax.grid()
        # ax.legend()
    else:
        ax.hist(trace,bins,zorder=0,weights=weights)

def trace_hist(     path1,name1,
                    path2,name2,
                    path3,name3,
                    path4,name4,
                    sim1,sim2,sim3,sim4):
    fig,Axes = plt.subplots(2,2,figsize=(10,8),layout='constrained',sharex=True)
    low=100
    high=100
    trace1=get_trace_real(path1)
    trace2=get_trace_real(path2)
    trace3=get_trace_real(path3)
    trace4=get_trace_real(path4)

    sim_tra1,weights1=get_trace_sim(sim1)
    sim_tra2,weights2=get_trace_sim(sim2)
    sim_tra3,weights3=get_trace_sim(sim3)
    sim_tra4,weights4=get_trace_sim(sim4)
    for i in [trace1,trace2,trace3,trace4,sim_tra1,sim_tra2,sim_tra3,sim_tra4]:
        try:
            if low>min(i):
                low=min(i)
            if high<max(i):
                high=max(i)
        except:
            pass
    bins=np.logspace(np.log10(low),np.log10(high), 100)
    E_scatter(trace1,bins,Axes[0][0],name1)
    E_scatter(trace2,bins,Axes[0][1],name2)
    E_scatter(trace3,bins,Axes[1][0],name3)
    E_scatter(trace4,bins,Axes[1][1],name4)



    E_scatter(sim_tra1,bins,Axes[0][0],weights=weights1)
    E_scatter(sim_tra2,bins,Axes[0][1],weights=weights2)
    E_scatter(sim_tra3,bins,Axes[1][0],weights=weights3)
    E_scatter(sim_tra4,bins,Axes[1][1],weights=weights4)
    plt.show()

Xcorr='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_X_output/X'
Ratio='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_X_output/X_Ratio'
Zen='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_X_output/X_Ratio_Zen'
candi='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_X_output/X_Ratio_Zen_TrigR10_cut'
candiR12='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_X_output/X_Ratio_Zen_TrigR12_cut'
candiR10='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_X_output/X_Ratio_Zen_TrigR10_cut'
candiR8='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_X_output/X_Ratio_Zen_TrigR8_cut'
SNR_R8='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_X_output/X_Ratio_Zen_TrigR8_cut/SNR_cut'
candiR6='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_X_output/X_Ratio_Zen_TrigR6_cut'

sim_Xcorr='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_3Xcorr/X_33Xcorr'
sim_Ratio='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_3Xcorr/X_Ratio'
sim_Zen='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_3Xcorr/X_Ratio_Zen'

# trace_hist(Xcorr,'X',Ratio,'X_Ratio',Ratio,'X_Ratio_Zen','Nothing','Nothing',
#                sim_Xcorr,sim_Ratio,sim_Zen,'Nothing')
trace_hist('Nothing','X','Nothing','X_Ratio','Nothing','X_Ratio_Zen',SNR_R8,'Candi8',
               'Nothing','Nothing','Nothing',sim_Zen)







