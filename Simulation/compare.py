# Trig-X-SNR-Zen-Ratio
from typing_extensions import Self
import sys
sys.path.insert(0,'/pub/tingwel4/Tingwei_Liu/NuRadioMC')
from NuRadioReco.detector import detector 
from NuRadioReco.utilities import units
from NuRadioReco.modules.ARIANNA import hardwareResponseIncorporator as ChardwareResponseIncorporator
import NuRadioReco.modules.templateDirectionFitter
from NuRadioReco.framework.parameters import stationParameters as stnp
from NuRadioReco.modules.io import NuRadioRecoio
from icecream import ic
import numpy as np
import ToolsPac
from NuRadioReco.framework.parameters import eventParameters as evtp
import os
input_path_bef='/pub/tingwel4/output/CR_BL_Simulation_weighted'
input_path_aft='/pub/tingwel4/output/Freqs'
def weight_compare(bef,aft):
    bef=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(bef))
    aft=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(aft))
    weights_bef=[]
    weights_aft=[]
    ic(bef.get_n_events())
    ic(aft.get_n_events())
    for evt in bef.get_events():
        weights_bef.append(evt.get_parameter(evtp.event_rate))
    for evt in aft.get_events():
        weights_aft.append(evt.get_parameter(evtp.event_rate))
    ic(sum(weights_bef))
    ic(sum(weights_aft))

weight_compare(input_path_bef,input_path_aft)