import sys
sys.path.insert(0,'/Users/david/PycharmProjects/Demo1/Research/Repository/NuRadioMC')
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
import matplotlib
# from plot_waveform import plot_wave
candi='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Trig_Freqs'
input_dir='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate'
non_goso='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_non_goso'
# output='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_X_output/X_Ratio_Zen_TrigR8_cut/SNR_cut'
output='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/sus_wave'
best_id=['R243E512']
Sus_id=[
    'R247E1060',
    'R247E1079',
    'R243E1398',
    'R247E1053',
    'R247E1063',
    'R247E1066',
    'R247E1141',
    'R247E1140',
    'R247E1054',
    'R247E1064',
    'R247E1088',
    'R247E1095',
    'R247E1059',
    'R256E420',
    'R256E421',
    'R247E1093',
    'R256E417',
    'R256E418',
    'R256E423',
    'R247E1087',
    'R256E419',
    'R256E422',
    'R247E1098',
    'R247E1089',
    'R247E1069',
    'R247E1090']
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
sample_rate = 1*units.GHz



# input_list=[]
# output_list=[]
# readARIANNAData1=NuRadioRecoio.NuRadioRecoio(get_input(candi))
# for evt in readARIANNAData1.get_events():
#     run,id = evt.get_run_number(),evt.get_id()
#     input_list.append(f'R{run}E{id}')
# output_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate'
# readARIANNAData2=NuRadioRecoio.NuRadioRecoio(get_input(input_dir))
# eventWriter=set_writer(output_path,'Trig_X_Zen_Freqs')
# for evt in readARIANNAData2.get_events():
#     stn = evt.get_station(51)
#     run = evt.get_run_number()
#     id = evt.get_id()
#     if f'R{run}E{id}' not in input_list:
#         continue
#     largest=[0,0]
#     time = stn.get_station_time().datetime
#     # largest:[max_amp,ratio]
#     for i in range(4,7):
#         spectrum,freqs,ratio=get_low_amp_ratio(80,evt,i)
#         if ratio>largest[1]:
#             stn=evt.get_station(51)
#             chn=stn.get_channel(i)
#             trace=np.max(np.abs(chn.get_trace()/units.MeV))
#             largest=[trace,ratio]
#     if largest[1]<=0.115:
#         output_list.append(f'R{run}E{id}')
# for evt in readARIANNAData1.get_events():
#     run,id = evt.get_run_number(),evt.get_id()
#     if f'R{run}E{id}' in output_list:
#         eventWriter.run(evt)
# eventWriter.end()
# ic(len(output_list))
# exit()

Candi_list=[]
# candi='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Trig_Freqs'
candi='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/CR_BL_Simulation_weighted/'
# readARIANNAData=NuRadioRecoio.NuRadioRecoio(get_input(candi))
# ic(readARIANNAData.get_n_events())
# for evt in readARIANNAData.get_events():
#     run,id = evt.get_run_number(),evt.get_id()
#     Candi_list.append(f'R{run}E{id}')

input_list=get_input(candi)
# input_list.extend(get_input(non_goso))
readARIANNAData=NuRadioRecoio.NuRadioRecoio(input_list)
ic(readARIANNAData.get_n_events())
exit()
fig,ax = plt.subplots(figsize=(10,8),constrained_layout=True)
max_amp     = []
max_ratio   = []
Sus_amp     = []
Sus_ratio   = []
Candi_amp   = []
Candi_ratio = []
weights     = []
for evt in readARIANNAData.get_events():
    stn = evt.get_station(51)
    run = evt.get_run_number()
    id = evt.get_id()
    largest=[0,0]
    time = stn.get_station_time().datetime
    weights.append(evt.get_parameter(evtp.event_rate))
    # largest:[max_amp,ratio]
    for i in range(4,7):
        spectrum,freqs,ratio=get_low_amp_ratio(80,evt,i)
        if ratio>largest[1]:
            stn=evt.get_station(51)
            chn=stn.get_channel(i)
            trace=np.max(np.abs(chn.get_trace()/units.MeV))
            largest=[trace,ratio]
    if f'R{run}E{id}' in Sus_id:
        Sus_amp.append(largest[0])
        Sus_ratio.append(largest[1])
    elif f'R{run}E{id}' in Candi_list:
        Candi_amp.append(largest[0])
        Candi_ratio.append(largest[1])
    else:
        max_amp.append(largest[0])
        max_ratio.append(largest[1])
SNR_bins = np.logspace(np.log10(np.min(max_amp)), np.log10(np.max(max_amp)), 101)
weights=np.array(weights)*31/365
fft_bins=np.linspace(0,1,101)
hist,_,_=np.histogram2d(max_amp,max_ratio,bins=(SNR_bins,fft_bins),weights=weights)
S,X=np.meshgrid(SNR_bins,fft_bins)
pm=ax.pcolormesh(S,X,hist.T,norm=matplotlib.colors.LogNorm(),zorder=0)
ax.figure.colorbar(pm,ax=ax)
# patch = mpatches.Patch(color='lightblue', label='Your Label Here')
ax.set_xlabel(f'SNR',fontsize=40)
ax.set_ylabel(fr'$\chi$',fontsize=40)
# ax.legend(handles=[patch],fontsize=20)
ax.legend(loc='lower right',fontsize=40)

# ax.scatter(max_amp,max_ratio,label=fr'$\alpha$=0.1 {len(max_amp)}',color='red',alpha=0.1,zorder=0)
# ax.scatter(Sus_amp,Sus_ratio,label=fr'$\alpha$=0.5 {len(Sus_amp)}',color='Green',alpha=0.5,zorder=2)
# ax.scatter(Candi_amp,Candi_ratio,label=fr'$\alpha$=0.3 {len(Candi_amp)}',color='blue',alpha=0.3,zorder=1)
ax.axhline(y=0.115,color='black')
ax.legend(fontsize=20)
ax.grid()
ax.set_ylim(0,1)
ax.set_xlabel('Max_amp(MeV)',fontsize=20)
ax.set_ylabel('Freqs_ratio_below_80MHz(%)',fontsize=20)
ax.set_xscale('log')
ax.tick_params(axis='x', labelsize=20)
ax.tick_params(axis='y', labelsize=20)
plt.show()





    
