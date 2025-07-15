from typing_extensions import Self
import sys
from NuRadioReco.detector import detector 
from NuRadioReco.utilities import units
from NuRadioReco.modules.ARIANNA import hardwareResponseIncorporator as ChardwareResponseIncorporator
import NuRadioReco.modules.templateDirectionFitter
from NuRadioReco.framework.parameters import stationParameters as stnp
from NuRadioReco.modules.io import NuRadioRecoio
from icecream import ic
import numpy as np
import datetime
import NuRadioReco.modules.io.eventWriter
import matplotlib.pyplot as plt
import datetime

from icecream import ic
import os
import datetime
from NuRadioReco.framework.parameters import channelParameters as chp
import NuRadioReco.modules.correlationDirectionFitter
import NuRadioReco.modules.channelLengthAdjuster
channelLengthAdjuster = NuRadioReco.modules.channelLengthAdjuster.channelLengthAdjuster()
channelLengthAdjuster.begin()

hardwareResponseIncorporator = ChardwareResponseIncorporator.hardwareResponseIncorporator()
hardwareResponseIncorporator.begin(debug=False)

import NuRadioReco.modules.channelResampler
channelResampler = NuRadioReco.modules.channelResampler.channelResampler()
# channelResampler.begin(debug=False)

import NuRadioReco.modules.channelBandPassFilter
channelBandPassFilter = NuRadioReco.modules.channelBandPassFilter.channelBandPassFilter()

from NuRadioReco.modules.channelStopFilter import channelStopFilter
channelStopFilter=channelStopFilter()

import NuRadioReco.modules.channelTemplateCorrelation
channelTemplateCorrelation = NuRadioReco.modules.channelTemplateCorrelation.channelTemplateCorrelation(template_directory='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/templates/')
channelTemplateCorrelation.begin(debug=False)

import NuRadioReco.modules.channelSignalReconstructor
channelSignalReconstructor = NuRadioReco.modules.channelSignalReconstructor.channelSignalReconstructor()

from NuRadioReco.modules import channelTimeWindow as cTWindow
cTW=cTWindow.channelTimeWindow()
cTW.begin(debug=False)

import NuRadioReco.modules.channelBandPassFilter
channelBandPassFilter = NuRadioReco.modules.channelBandPassFilter.channelBandPassFilter()

templateDirectionFitter = NuRadioReco.modules.templateDirectionFitter.templateDirectionFitter()
templateDirectionFitter.begin()

json_file_origin=f'/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/Stn51_sim_inAir/station51.json'
det=detector.Detector(json_filename=json_file_origin)
# det.update(datetime.datetime(2018,10,1))
import send2trash

input_path   = '/Users/david/PycharmProjects/Demo1/Research/Repository/sim_with_weights'
output_path  = '/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output'

def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir

def Analyze_X(input):
    # X
    low1=[]
    low2=[]
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input))
    for evt in readARIANNAData.get_events():
        run=evt.get_run_number()
        stn = evt.get_station(51)
        time= stn.get_station_time().datetime
        save1=True
        save2=False
        X_list=[]
        for i in [4,5,6]:
            channel = stn.get_channel(i)
            Chi=np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr']))
            low1.append(Chi)
            X_list.append(Chi)
        low2.append(max(X_list))
    ic(min(low1),min(low2))
input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/SNR_cut1'
Analyze_X(input_path)