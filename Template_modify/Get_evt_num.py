import sys
sys.path.append('/Users/david/PycharmProjects/Demo1/Research/Repository/')
sys.path.append('/Users/david/PycharmProjects/Demo1/Research/Repository/Simulation')
import NuRadioReco
from NuRadioReco.framework.parameters import eventParameters as evtp
from NuRadioReco.modules.io import NuRadioRecoio
import os
import ToolsPac as tp
from icecream import ic
from NuRadioReco.framework.parameters import channelParameters as chp
import numpy as np
channels_to_use=[4,5,6]
import datetime
from NuRadioReco.utilities import units
from NuRadioReco.framework.parameters import stationParameters as stnp

Vrms=(9.71+9.66+8.94)/3
def get_event_num_det(input_path):
    reader=NuRadioRecoio.NuRadioRecoio(tp.get_input(input_path))
    return reader.get_n_events()

def get_mean_chi_det(input_path):
    reader=NuRadioRecoio.NuRadioRecoio(tp.get_input(input_path))
    chi_lst=[]
    for evt in reader.get_events():
        x_chn=[]
        stn=evt.get_station(51)
        for i in channels_to_use:
            chn=stn.get_channel(i)
            x_chn.append(chn[chp.cr_xcorrelations]['cr_ref_xcorr'])
        chi_lst.append(np.max(x_chn))
    return np.mean(chi_lst)

def get_plot_info_sim(reader:NuRadioReco.modules.io, if_weights = False):
    SNR_dic = []
    X_dic   = []
    weights = []
    id = []
    for evt in reader.get_events():
        stn = evt.get_station(51)
        trace_up    = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3,4,5,6,7]):
            trace_up.append(np.max(np.abs(channel.get_trace()/units.mV)))
        Xcorr=[] 
        for chn in [4,5,6]:  
            channel = stn.get_channel(chn)
            Xcorr.append(channel[chp.cr_xcorrelations]['cr_ref_xcorr'])
        X_dic.append(np.max(Xcorr))
        SNR_dic.append(max(trace_up)/Vrms)
        id.append(f'R{evt.get_run_number()}E{evt.get_id()}')
        if if_weights:
            weights.append(evt.get_parameter(evtp.event_rate))
    if if_weights:
        weights = np.array(weights)*(datetime.timedelta(days=31, seconds=21201)/datetime.timedelta(days=365))
        SNR_dic = np.array(SNR_dic)
        X_dic   = np.array(X_dic)
        return SNR_dic,X_dic,id,weights   
    else:
        SNR_dic = np.array(SNR_dic)
        X_dic   = np.array(X_dic) 
        return SNR_dic,X_dic,id


# input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze4/det/Trig_335_Freqs_X_SNR'
input_path_71='/Users/david/PycharmProjects/Demo1/Research/Repository/candidate_events/analyze4/analyze_candi'
# ic(f'{get_event_num_det(input_path)} analyze4 num')
det_path0 = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze/det/Trig_335_Freqs_X_SNR'
det_path1 = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze1/det/Trig_335_Freqs_X_SNR'
det_path2 = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs_X_SNR'
det_path4 = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze4/det/Trig_335_Freqs_X_SNR'

sim_path0 = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze/sim/Trig_335_Freqs_X_SNR'
sim_path1 = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze1/sim/Trig_335_Freqs_X_SNR'
sim_path2 = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/sim/Trig_335_Freqs_X_SNR'
sim_path4 = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze4/sim/Trig_335_Freqs_X_SNR'

det_path = [det_path0,det_path1,det_path2,det_path4]
sim_path = [sim_path0,sim_path1,sim_path2,sim_path4]

# for input_path in sim_path:
#     snr,chi,id,weights = get_plot_info_sim(NuRadioRecoio.NuRadioRecoio(tp.get_input(input_path)),True)
#     ic(np.sum(weights))

sim_direct = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/sim/Trig_335_Freqs_X_direct/new_phase_algorithm'
reader = NuRadioRecoio.NuRadioRecoio(tp.get_input(sim_direct))
total = reader.get_n_events()
zen_lst = []
for evt in reader.get_events():
    stn = evt.get_station(51)
    zen=stn.get_parameter(stnp.zenith)/units.deg
    zen_lst.append(zen)
fail_num = np.sum(np.array(zen_lst)>85)
a=np.array([0,1,2,3,4])
ic(np.sum(a>2))
ic(fail_num,total,fail_num/total)
