import sys
# sys.path.insert(0,'/Users/david/PycharmProjects/Demo1/Research/Repository/NuRadioMC')
import NuRadioReco.modules.io.eventWriter
from NuRadioReco.modules.io.NuRadioRecoio import NuRadioRecoio
from NuRadioReco.framework.parameters import eventParameters as evtp
import numpy as np
from icecream import ic
import NuRadioReco
import os
import datetime
def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir


raw_goso='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw'
raw_ngoso='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_non_goso'
Xcorr='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_X_output/X'
Ratio='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_X_output/X_Ratio'
Zen='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_X_output/X_Ratio_Zen'

raw_sim='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_with_weights'
Freqs_sim='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Trig_Freqs'
Freqs_X_sim='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Trig_Freqs_X'
Freqs_X_SNR_sim='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Trig_Freqs_X_SNR'
Freqs_X_SNR_Ratio_sim='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Trig_Freqs_X_SNR_Ratio'

def get_read_weights(input_path):
    Read=NuRadioRecoio(get_input(input_path))
    weights=[]
    for evt in Read.get_events():
        weights.append(evt.get_parameter(evtp.event_rate))
    weights=np.array(weights)
    return np.sum(weights)
def get_read_det(input_path):
    Read=NuRadioRecoio(get_input(input_path))
    return Read.get_n_events()
def get_raw(read):
    return read.get_n_events()
# ic(f'raw_sim    : {get_read_weights(raw_sim):.2f}')
# ic(f'nGOSO  : {get_read_det(raw_ngoso)}')
# ic(f'GOSO   : {get_read_det(raw_goso)}')
# exit()
ic(f'sim                    : {get_read_weights(raw_sim)}')
ic(f'Freqs_sim              : {get_read_weights(Freqs_sim)}')
ic(f'Freqs_X_sim            : {get_read_weights(Freqs_X_sim)}')
ic(f'Freqs_X_SNR_sim        : {get_read_weights(Freqs_X_SNR_sim)}')
ic(f'Freqs_X_SNR_Ratio_sim  : {get_read_weights(Freqs_X_SNR_Ratio_sim)}')
exit()

ic(get_read_det)
exit()
for i in os.listdir(raw_goso):
    if i.endswith('.nur'):
        reader=NuRadioRecoio([os.path.join(raw_goso,i)])
        last=reader.get_n_events()
        count=0
        for evt in reader.get_events():
            if count==0:
                ic(evt.get_run_number())
                stn=evt.get_station(51)
                ic(stn.get_station_time().datetime)
            count+=1
            if count==last-1:
                # ic(evt.get_run_number())
                stn=evt.get_station(51)
                ic(stn.get_station_time().datetime)

# dir_1=get_input(raw_goso)
# dir_1.extend(get_input(raw_ngoso))
# read=NuRadioRecoio(dir_1)
# ic(f'Raw:   {get_raw(read)}')
# ic(f'Goso:  {get_read_det(raw_goso)}')
# ic(f'X:     {get_read_det(Xcorr)}')
# # ic(f'Sig:   {get_read_det(sig)}')
# ic(f'Ratio: {get_read_det(Ratio)}')
# ic(f'Zen:   {get_read_det(Zen)}')