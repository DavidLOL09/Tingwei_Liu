from NuRadioReco.modules.io import NuRadioRecoio
from NuRadioReco.framework.parameters import eventParameters as evtp
import NuRadioReco.modules.io.eventWriter
eventWriter = NuRadioReco.modules.io.eventWriter.eventWriter()
import numpy as np
from NuRadioReco.utilities import units
from NuRadioReco.framework.parameters import channelParameters as chp
from icecream import ic
import os
import send2trash
Vrms=(9.71+9.66+8.94)/3
def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir
num_per_h=8
input_path=f'/Users/david/PycharmProjects/Demo1/Research/Repository/raw_X_output/X_Ratio_Zen_TrigR{num_per_h}_cut'
input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Trig_X_Zen'
Zen_sim='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output/X_335sig_Ratio_Zen'
output_path=f'/Users/david/PycharmProjects/Demo1/Research/Repository/raw_X_output/X_Ratio_Zen_TrigR{num_per_h}_cut/SNR_cut/'
output_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/SNR_cut1'
try:
    os.makedirs(output_path)
except(FileExistsError):
    send2trash.send2trash(output_path)
    os.makedirs(output_path)
eventWriter.begin(os.path.join(output_path,'SNR_cut.nur'))
# candi=['R256E13', 'R256E588', 'R256E628', 'R256E735', 'R256E736', 'R256E1973', 'R256E2152', 'R256E2177', 'R263E368', 'R263E734', 'R263E736', 'R263E762', 'R263E764', 'R266E7', 'R266E59', 'R266E60', 'R266E1236', 'R266E1423', 'R266E1517', 'R266E1990', 'R260E112', 'R249E9', 'R249E13', 'R249E251', 'R249E355', 'R249E394', 'R243E110', 'R243E531', 'R243E542', 'R243E555', 'R243E589', 'R243E590', 'R243E591', 'R243E995', 'R243E1064', 'R243E1120', 'R243E1126', 'R243E1142', 'R243E1270', 'R243E1403', 'R243E1441', 'R243E1447', 'R243E1460', 'R243E1720', 'R243E1823', 'R243E1848', 'R264E8', 'R264E17', 'R264E244', 'R264E466', 'R264E476', 'R264E483', 'R264E496', 'R247E818', 'R247E821', 'R247E1193', 'R247E1281', 'R247E1319', 'R247E1482', 'R247E1732']
readARIANNAData=NuRadioRecoio.NuRadioRecoio(get_input(input_path))
candi=[]
def SNR_cut_line(x):
    k=0.3
    y=k*np.log10(x)+0.2
    return y
    
for evt in readARIANNAData.get_events():
    stn = evt.get_station(51)
    run=evt.get_run_number()
    id=evt.get_id()
    Xcorr=[]     
    for i in [4,5,6]:
        channel = stn.get_channel(i)
        Xcorr.append(np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr'])))
    X=np.max(Xcorr)
    trace_up    = []
    for channel in stn.iter_channels(use_channels=[4,5,6]):
        trace_up.append(np.max(np.abs(channel.get_trace()/units.mV)))
    trace_up=max(trace_up)
    X_exp=SNR_cut_line(trace_up/Vrms)
    ic(X,X_exp)
    if X<=X_exp:
        continue
    eventWriter.run(evt)

