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
try:
    os.makedirs(output_path)
except(FileExistsError):
    send2trash.send2trash(output_path)
    os.makedirs(output_path)

eventWriter = NuRadioReco.modules.io.eventWriter.eventWriter()
Vrms=(9.71+9.66+8.94)/3



def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir
input_dir=get_input(input_path)

def Analyze_sig(input):
    # 3_of_3
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input))
    sig = os.path.join(output_path,'X_335sig')
    try:
        os.makedirs(sig)
    except(FileExistsError):
        send2trash.send2trash(sig)
        os.makedirs(sig)
    eventWriter.begin(os.path.join(sig,'X_335sig.nur'))
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        vrms= 0
        time = stn.get_station_time().datetime
        det.update(time)
        for i in [4,5,6]:
            channel = stn.get_channel(i)
            if np.max(np.abs(channel.get_trace()))/units.mV<=Vrms*5:
                vrms+=1
                break
        if not vrms==0:
            continue
        eventWriter.run(evt)
    print('3_of_3 5sig Completed')
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
        trace_bic=[]
        trace_bic.append(np.max(np.abs(stn.get_channel(7).get_trace()/units.mV)))
        if np.max(trace_bic)/np.max(trace_up)>=0.333 and np.max(trace_bic)>=3*Vrms:
            continue
        # if np.max(trace_bic)/np.max(trace_up)
        eventWriter.run(evt)
    print('Ratio Completed')
    return Ratio

def Analyze_X(input):
    # X
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input))
    X = os.path.join(output_path,'X')
    try:
        os.makedirs(X)
    except(FileExistsError):
        send2trash.send2trash(X)
        os.makedirs(X)
    eventWriter.begin(os.path.join(X,'X.nur'))
    for evt in readARIANNAData.get_events():
        run=evt.get_run_number()
        stn = evt.get_station(51)
        time= stn.get_station_time().datetime
        det.update(time)
        channelStopFilter.run(evt,stn,det,append=0,prepend=0)
        channelBandPassFilter.run(evt, stn, det, passband=[80 * units.MHz, 500 * units.MHz], filter_type='butter', order = 10)
        hardwareResponseIncorporator.run(evt, stn, det, sim_to_data=False)
        channelTemplateCorrelation.run(evt,stn,det,cosmic_ray=True,n_templates=1, channels_to_use=[4,5,6])
        save1=True
        save2=False
        X_list=[]
        for i in [4,5,6]:
            channel = stn.get_channel(i)
            if np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr']))<0.3:
                save=False
                break
            else:
                X_list.append(np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr'])))
        for i in X_list:
            if i>0.4:
                save2=True
                break
        if save1 and save2:
            hardwareResponseIncorporator.run(evt,stn,det,sim_to_data=True)
            templateDirectionFitter.run(evt,stn,det,channels_to_use=[4,5,6], cosmic_ray=True)
            eventWriter.run(evt)
    print('X Completed')
    return X


def Analyze_zen(input):
    # Zen,<=85deg
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input))
    zen_path = os.path.join(output_path,'X_Zen')
    try:
        os.makedirs(zen_path)
    except(FileExistsError):
        send2trash.send2trash(zen_path)
        os.makedirs(zen_path)
    eventWriter.begin(os.path.join(zen_path,'X_Zen.nur'))
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

# if os.path.isdir(output_path):
#     os.makedirs(output_path)

def Analyze(input):
    Xcorr=Analyze_X(input)
    # sig=Analyze_sig(Xcorr)
    # Ratio=Analyze_Ratio()
    Zen=Analyze_zen(Xcorr)
Analyze(input_path)



