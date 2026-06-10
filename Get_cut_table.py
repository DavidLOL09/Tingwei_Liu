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


det_Trig_Freqs='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/New_temp_Xcorr/withTemp_R243E512'
det_Trig_Freqs_3X='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/New_temp_Xcorr/3X'
det_Trig_Freqs_3X_SNR='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/New_temp_Xcorr/3X_SNR'
det_Trig_Freqs_3X_SNR_Ratio='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/New_temp_Xcorr/3X_SNR_Ratio'

sim_Trig_Freqs='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/sim/Trig_335_Freqs'
sim_Trig_Freqs_3X='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/sim/Trig_335_Freqs_X'
sim_Trig_Freqs_3X_SNR='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/sim/Trig_335_Freqs_X_SNR'

def get_read_weights(input_path):
    Read=NuRadioRecoio(get_input(input_path))
    weights=[]
    for evt in Read.get_events():
        weights.append(evt.get_parameter(evtp.event_rate))
    weights=np.array(weights)
    return np.sum(weights)*(datetime.timedelta(days=31, seconds=21201)/datetime.timedelta(days=365))
def get_read_det(input_path):
    Read=NuRadioRecoio(get_input(input_path))
    return Read.get_n_events()
def get_raw(read):
    return read.get_n_events()

ic(f'Freqs_sim              : {get_read_weights(sim_Trig_Freqs)}')
ic(f'Freqs_X_sim            : {get_read_weights(sim_Trig_Freqs_3X)}')
ic(f'Freqs_X_SNR_sim        : {get_read_weights(sim_Trig_Freqs_3X_SNR)}')
