# replace 335sig to 33 0.4 X
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
import send2trash
from icecream import ic
import os
import datetime
from NuRadioReco.framework.parameters import channelParameters as chp
json_file_origin=f'/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/Stn51_sim_inAir/station51.json'
det=detector.Detector(json_filename=json_file_origin)
eventWriter = NuRadioReco.modules.io.eventWriter.eventWriter()
input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_3Xcorr/X_33Xcorr'
output_path  = '/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Bicone'
Vrms=(9.71+9.66+8.94)/3
def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir
input_dir=get_input(input_path)

def Analyze_3Xcorr(input_path):
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    print(readARIANNAData.get_n_events())
    exit()
    sig = os.path.join(output_path,'X')
    try:
        os.makedirs(sig)
    except(FileExistsError):
        send2trash.send2trash(sig)
        os.makedirs(sig)
    eventWriter.begin(os.path.join(sig,'33Xcorr.nur'))
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        save0=True
        Xcorr=[]
        for i in [4,5,6]:
            channel = stn.get_channel(i)
            Xmax=np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr']))
            if Xmax<0.3:
                save0=False
                break
            Xcorr.append(Xmax)
        if save0 == False:
            continue
        if max(Xcorr)>=0.4:
            eventWriter.run(evt)
    print('X Completed')
    return sig
def Analyze_Ratio(input):
    # 33Vrms_Ratio
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input))
    Ratio = os.path.join(output_path,'X_Ratio')
    try:
        os.makedirs(Ratio)
    except(FileExistsError):
        send2trash.send2trash(Ratio)
        os.makedirs(Ratio)
    eventWriter.begin(os.path.join(Ratio,'X_Ratio.nur'))
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        time = stn.get_station_time().datetime
        det.update(time)
        trace_down  = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3]):
            trace_down.append(np.max(np.abs(channel.get_trace()/units.mV)))
        trace_up    = []
        for channel in stn.iter_channels(use_channels=[4,5,6]):
            trace_up.append(np.max(np.abs(channel.get_trace()/units.mV)))   
        if np.max(trace_down)/np.max(trace_up)>=0.5:
            continue
        # trace_bic=[]
        # trace_bic.append(np.max(np.abs(stn.get_channel(7).get_trace()/units.mV)))
        # if np.max(trace_bic)/np.max(trace_up)>=0.333 and np.max(trace_bic)>=3*Vrms:
        #     continue
        # if np.max(trace_bic)/np.max(trace_up)
        eventWriter.run(evt)
    print('Ratio Completed')
    return Ratio
def Analyze_zen(input):
    # Zen,<=85deg
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input))
    zen_path = os.path.join(output_path,'X_Ratio_Zen')
    try:
        os.makedirs(zen_path)
    except(FileExistsError):
        send2trash.send2trash(zen_path)
        os.makedirs(zen_path)
    eventWriter.begin(os.path.join(zen_path,'X_Ratio_Zen.nur'))
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        time= stn.get_station_time().datetime
        det.update(time)
        zenith=stn.get_parameter(stnp.zenith)/units.deg
        if zenith>85:
            continue
        eventWriter.run(evt)
    print('Zen Complete')
    return zen_path
# X=Analyze_3Xcorr(input_path)
Ratio=Analyze_Ratio(input_path)
# Zen=Analyze_zen(Ratio)


