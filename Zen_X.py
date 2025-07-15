Vrms=(9.71+9.66+8.94)/3
import os
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from icecream import ic
from NuRadioReco.framework.parameters import stationParameters as stnp
input_path = '/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_output/'
from NuRadioReco.utilities import units
import NuRadioReco.modules.channelBandPassFilter
channelBandPassFilter = NuRadioReco.modules.channelBandPassFilter.channelBandPassFilter()
from NuRadioReco.modules.ARIANNA import hardwareResponseIncorporator as ChardwareResponseIncorporator
hardwareResponseIncorporator = ChardwareResponseIncorporator.hardwareResponseIncorporator()
hardwareResponseIncorporator.begin(debug=False)
from NuRadioReco.modules.io import NuRadioRecoio
from NuRadioReco.detector import detector
from NuRadioReco.modules.channelStopFilter import channelStopFilter
channelStopFilter=channelStopFilter()
import NuRadioReco.modules.channelResampler
channelResampler = NuRadioReco.modules.channelResampler.channelResampler()
ic(NuRadioReco.modules.channelResampler.__file__)
# channelResampler.begin(debug=False)
from NuRadioReco.framework.parameters import eventParameters as evtp
import NuRadioReco.modules.channelSignalReconstructor
channelSignalReconstructor=NuRadioReco.modules.channelSignalReconstructor.channelSignalReconstructor()
import NuRadioReco.modules.channelTemplateCorrelation
channelTemplateCorrelation = NuRadioReco.modules.channelTemplateCorrelation.channelTemplateCorrelation(template_directory='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/templates/')
channelTemplateCorrelation.begin(debug=False)
import NuRadioReco.modules.io.eventWriter
eventWriter = NuRadioReco.modules.io.eventWriter.eventWriter()
import datetime
import NuRadioReco.modules.templateDirectionFitter
templateDirectionFitter = NuRadioReco.modules.templateDirectionFitter.templateDirectionFitter()
templateDirectionFitter.begin()
json_file_origin=f'/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/Stn51_sim_inAir/station51.json'
det=detector.Detector(json_filename=json_file_origin)
from NuRadioReco.framework.parameters import channelParameters as chp
import ToolsPac

Candi='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Final_Candi'
Candi='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Final_Candi'
# zen_diff='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/zen_diff'
sim='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Trig_Freqs_X_SNR'
output_path=''
cut=0

def get_Zen(input_path):
    Data = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))
    zen_list    = []
    for evt in Data.get_events():
        stn     = evt.get_station(51)
        zen_list.append(stn.get_parameter(stnp.zenith)/units.deg)
    return np.array(zen_list)

def get_Xcorr(input_path):
    Data = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))
    Xcorr_list  = []
    for evt in Data.get_events():
        stn     = evt.get_station(51)
        Xcorr_list.append(ToolsPac.get_Xcorr(stn,[4,5,6]))
    return np.array(Xcorr_list)

def get_weights(input_path):
    Data = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))
    weights=[]
    count=0
    for evt in Data.get_events():
        stn=evt.get_station(51)
        trace_max=ToolsPac.get_Max_trace(stn,np.linspace(0,7,8))
        if trace_max<=cut:
            continue
        try:
            weights.append(evt.get_parameter(evtp.event_rate))
        except(KeyError):
            count+=1
    ic(count)
    ic(Data.get_n_events())
    return np.array(weights)

def get_trace(input_path):
    Data = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))
    trace=[]
    for evt in Data.get_events():
        stn=evt.get_station(51)
        trace_max=ToolsPac.get_Max_trace(stn,np.linspace(0,7,8))
        if trace_max<=cut:
            continue
        trace.append(trace_max)
    return np.array(trace)



    



# for Data:
det_trace   = get_trace(Candi)/Vrms
# ic(min(det_trace))

# for suspicious: 
# sus_trace   = get_trace(zen_diff)

# for sim:
sim_trace   = get_trace(sim)/Vrms
sim_weights = get_weights(sim)*31/365
ic(np.sum(sim_weights))
# sim_weights = get_weights(sim)
# ic(np.sum(sim_weights))
# ic(np.min(sim_trace),np.max(sim_trace))

fig,ax = plt.subplots(1,1,figsize=(10,8),layout='constrained')

# X-Zen:
# ax.set_xlabel(r'zenith($\theta$)')
# ax.set_ylabel(r'$\chi$')
# ax.scatter(det_zen,det_X,c='r',s=10,label=f'Candi:{len(det_zen)}')
# ax.scatter(sus_zen,sus_X,c='b',s=5,label=f'Sus:{len(sus_zen)}')
# zen_bins = np.linspace(0,90,91)
# X_bins=np.linspace(0,1,101)
# ax.set_xlim(0,91)
# ax.set_ylim(0,1)
# hist,_,_=np.histogram2d(sim_zen,sim_X,bins=(zen_bins,X_bins),weights=weights)
# S,X=np.meshgrid(zen_bins,X_bins)
# pm=ax.pcolormesh(S,X,hist.T,norm=matplotlib.colors.LogNorm(),zorder=0)
# ax.figure.colorbar(pm,ax=ax)

# Amp_hist:
bins=np.linspace(cut,300,21)/Vrms
# exit()
ax.set_xlabel('SNR',fontsize=28)
# ax.set_ylabel(r'$\chi$',fontsize=28)
ax.hist(det_trace,bins=bins,color='r',alpha=1,label=f'Candi:{len(det_trace)}',zorder=0)
# ax.hist(det_trace,bins=bins,histtype='step',color='black',stacked=True,fill=False)
# ax.hist(sus_trace,bins=bins,color='b',alpha=0.3,label=f'Sus:{len(sus_trace)}',zorder=1)
ax.hist(sim_trace,bins=bins,histtype='step',color='black',stacked=True,fill=False,label=f'sim:{int(np.sum(sim_weights))+1}',zorder=1,weights=sim_weights)
ax.tick_params(axis='both', labelsize=28)
ax.legend(fontsize=30)
ax.grid()
# plt.show()
plt.savefig('/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Amp_hist.png')


    

    

