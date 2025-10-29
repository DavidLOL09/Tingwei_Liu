from NuRadioReco.modules.io import NuRadioRecoio
import os
import numpy as np
from NuRadioReco.utilities import units
import matplotlib.pyplot as plt
from NuRadioReco.framework.parameters import eventParameters as evtp
Vrms=(9.71+9.66+8.94)/3
import datetime
from icecream import ic

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
        ic('No events in this path')
        return []
    max_trace=[]
    for evt in readARIANNAData.get_events():
        stn=evt.get_station(51)
        # if not evt[evtp.Pass_cut_line]['R243E512']:
        #     continue
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
        # if not evt[evtp.Pass_cut_line]['R243E512']:
        #     continue
        trace_up=[]
        weights.append(evt.get_parameter(evtp.event_rate))
        for channel in stn.iter_channels(use_channels=[4,5,6]):
            trace_up.append(np.max(np.abs(channel.get_trace()/units.mV)))
        max_trace.append(max(trace_up))
    return max_trace,np.array(weights)*(datetime.timedelta(days=31, seconds=8844)/datetime.timedelta(days=365))
def E_scatter(trace,ax,bins,name=None,weights=None):
    # bins=np.array(bins)/Vrms
    if trace==[]:
        return
    trace=np.array(trace)/Vrms

    if weights is None:
        ax.set_title(name)
        ax.hist(trace,bins,alpha=0.8,color='r',label=len(trace))
        ax.set_xscale('log')
        ax.grid()
        # ax.legend()
    else:
        ax.hist(trace,bins,zorder=0,weights=weights)
        ax.set_xlabel(f'total:{sum(weights)}')

def trace_hist(     
        path1,name1,
        path2,name2,
        path3,name3,
        path4,name4,
        sim1,sim2,sim3,sim4,
        norm1=False,
        norm2=False,
        norm3=False,
        norm4=False,
                    ):
    def normalize(norm,trace,weights):
        if norm:
            weights=np.array(weights)
            num=len(trace)
            weights=(weights*num)/np.sum(weights)
        return weights
        
    fig,Axes = plt.subplots(2,2,figsize=(10,8),layout='constrained')
    trace1=get_trace_real(path1)
    trace2=get_trace_real(path2)
    trace3=get_trace_real(path3)
    trace4=get_trace_real(path4)

    sim_tra1,weights1=get_trace_sim(sim1)
    sim_tra2,weights2=get_trace_sim(sim2)
    sim_tra3,weights3=get_trace_sim(sim3)
    sim_tra4,weights4=get_trace_sim(sim4)

    weights1=normalize(norm1,trace1,weights1)
    weights2=normalize(norm2,trace2,weights2)
    weights3=normalize(norm3,trace3,weights3)
    weights4=normalize(norm4,trace4,weights4)

    bins=np.logspace(np.log10(1),np.log10(101), 20)

    E_scatter(trace1,Axes[0][0],bins,name1)
    E_scatter(trace2,Axes[0][1],bins,name2)
    E_scatter(trace3,Axes[1][0],bins,name3)
    E_scatter(trace4,Axes[1][1],bins,name4)



    E_scatter(sim_tra1,Axes[0][0],bins,weights=weights1)
    E_scatter(sim_tra2,Axes[0][1],bins,weights=weights2)
    E_scatter(sim_tra3,Axes[1][0],bins,weights=weights3)
    E_scatter(sim_tra4,Axes[1][1],bins,weights=weights4)
    plt.legend()
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

det_Trig_Freqs_335='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_Freqs_335'
sim_weights='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/CR_BL_Simulation_weighted'
sim_335='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/sim/335'
sim_Trig_Freqs_335='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/sim/Trig_335sig_Freqs'
det_SNR='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs_X_SNR'
sim_SNR='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/sim/Trig_335_Freqs_X_SNR'

# trace_hist(Xcorr,'X',Ratio,'X_Ratio',Ratio,'X_Ratio_Zen','Nothing','Nothing',
#                sim_Xcorr,sim_Ratio,sim_Zen,'Nothing')
trace_hist('Nothing','X',
           'Nothing','X_Ratio',
           'Nothing','X_Ratio_Zen',
           det_SNR,'SNR',
               'Nothing',
               'Nothing',
               'Nothing',
               sim_SNR)
