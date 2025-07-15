import ToolsPac
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from NuRadioReco.modules.io import NuRadioRecoio
import os
from NuRadioReco.utilities import units
from NuRadioReco.framework.parameters import stationParameters as stnp
from NuRadioReco.framework.parameters import eventParameters as evtp
import NuRadioReco
import random
from icecream import ic
input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Trig_Freqs_X_SNR_with_direct'
def get_weights(readARIANNAData:NuRadioReco.modules.io):
    direct=[]
    weights=[]
    for evt in readARIANNAData.get_events():
        stn=evt.get_station(51)
        zen = stn.get_parameter(stnp.zenith)/units.rad
        azi = stn.get_parameter(stnp.azimuth)/units.rad
        direct.append([zen,azi])
        weights.append(evt.get_parameter(evtp.event_rate))
    direct  = np.array(direct)
    weights = np.array(weights)
    zen = direct[:,0]
    azi = direct[:,1]
    return direct,weights

def get_repeat_possi(direct,weights,times=1000):

    count=0
    selected = random.choices(direct, weights=weights, k=times)
    for i in selected:
        selected_2 = random.choices(direct,weights=weights,k=times)
        for j in selected_2:
            if np.array_equal(i,j):
                count+=1
    return count
# readARIANNAData=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))
# direct,weights=get_weights(readARIANNAData)
times=1000
# ic(get_repeat_possi(direct,weights))
ic(1-2800/1000000)
# 2870 2721