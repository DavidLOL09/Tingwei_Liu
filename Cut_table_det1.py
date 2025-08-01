from typing_extensions import Self
import sys
# sys.path.insert(0,'/Users/david/PycharmProjects/Demo1/Research/Repository/NuRadioMC')
from NuRadioReco.detector import detector 
from NuRadioReco.utilities import units
from NuRadioReco.modules.ARIANNA import hardwareResponseIncorporator as ChardwareResponseIncorporator
import NuRadioReco.modules.templateDirectionFitter
from NuRadioReco.framework.parameters import stationParameters as stnp
from NuRadioReco.modules.io import NuRadioRecoio
from NuRadioReco.framework.parameters import eventParameters as evtp
import NuRadioReco.framework.event
from icecream import ic
import numpy as np
import datetime
import NuRadioReco.modules.io.eventWriter
import matplotlib.pyplot as plt
import datetime
from NuRadioReco.detector import detector
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

import NuRadioReco.modules.channelTemplateCorrelation as CTC

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
ic(json_file_origin)
det=detector.Detector(json_filename=json_file_origin)
# det.update(datetime.datetime(2018,10,1))
import send2trash

input_path   = '/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw'
output_path  = '/Users/david/PycharmProjects/Demo1/Research/Repository/aftResample'

if not os.path.isdir(output_path):
    os.makedirs(output_path)

eventWriter = NuRadioReco.modules.io.eventWriter.eventWriter()
Vrms=(9.71+9.66+8.94)/3

goso=[242,243,247,249,256,260,263,264,266]

def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir
input_dir=get_input(input_path)


def SNR_cut_line_cut(x:np.array):
    k=0.21622342843989703
    y=k*np.log10(x)+0.2444278883161825
    y=np.zeros_like(x)
    for i,elmt in enumerate(x):
        if elmt >= 10:
            y[i] = SNR_cut_line_cut_10_2753(x[i])
        if elmt < 10:
            y[i] = SNR_cut_line_cut_0_10(x[i])
    y[y <= 0.35] = 0.35
    y[y >= 0.6] = 0.6
    return y

def SNR_cut_line_cut_10_2753(x):
    k=0.3183220163182149
    y=k*np.log10(x)+0.14167798368178514
    return y

def SNR_cut_line_cut_0_10(x):
    k=0.7101265859394174
    y=k*np.log10(x)-0.2501265859394173
    return y

def UD_Ratio_cut_line(x):
    k=3.358751507788999
    y=k*np.log10(x)-5.067864845613618
    return y
def Bic_Ratio_cut_line(x):
    k=3.9015114425732005
    y=k*np.log10(x)-6.360165150568652
    return y

def not_has_triggered(evt:NuRadioReco.framework.event.Event):
    # 2/3 of 4.5 sigma threshold
    stn=evt.get_station(51)
    threshold=0
    for channel in stn.iter_channels(use_channels=[4,5,6]):
        trace = np.max(np.abs(channel.get_trace()/units.mV))
        if trace/Vrms>=4.5:
            threshold+=1
    return threshold<2


def Analyze_Ratio(input):
    # 33Vrms_Ratio
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input))
    Ratio = os.path.join(output_path,'3X_SNR_Ratio')
    try:
        os.makedirs(Ratio)
    except(FileExistsError):
        send2trash.send2trash(Ratio)
        os.makedirs(Ratio)
    eventWriter.begin(os.path.join(Ratio,'SNR_Ratio.nur'))
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        if not_has_triggered(evt):
            continue
        if not evt[evtp.Pass_cut_line]['R243E512']:
            continue
        time = stn.get_station_time().datetime
        det.update(time)
        trace_down  = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3]):
            trace_down.append(np.max(np.abs(channel.get_trace()/units.mV)))
        trace_down=np.max(np.array(trace_down))
        trace_max    = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3,4,5,6,7]):
            trace_max.append(np.max(np.abs(channel.get_trace()/units.mV)))  
        trace_max=np.max(np.array(trace_max)) 
        chn=stn.get_channel(7)
        trace_bic=np.max(np.abs(chn.get_trace()/units.mV))
        Ratio_UD = trace_max/trace_down
        Ratio_Bic= trace_max/trace_bic
        if Ratio_UD<=UD_Ratio_cut_line(trace_max) or Ratio_Bic<=Bic_Ratio_cut_line(trace_max):
            continue
        # trace_bic=[]
        # trace_bic.append(np.max(np.abs(stn.get_channel(7).get_trace()/units.mV)))
        # if np.max(trace_bic)/np.max(trace_up)>=0.333 and np.max(trace_bic)>=3*Vrms:
        #     continue
        eventWriter.run(evt)
    print('Ratio Completed')
    return Ratio

def Analyze_X(input):
    # X
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input))
    n=readARIANNAData.get_n_events()
    X = os.path.join(output_path,'SNR_Ratio_3X')
    try:
        os.makedirs(X)
    except(FileExistsError):
        send2trash.send2trash(X)
        os.makedirs(X)
    eventWriter.begin(os.path.join(X,'SNR_Ratio_3X.nur'))
    for evt in readARIANNAData.get_events():
        run=evt.get_run_number()
        # if run not in goso:
        #     continue
        stn = evt.get_station(51)
        time= stn.get_station_time().datetime
        det.update(time)
        save0=True
        for i in [4,5,6]:
            channel = stn.get_channel(i)
            # Xmax=channel[chp.Chi_Temp]['R243E512']['chi_max']
            Xmax=channel[chp.cr_xcorrelations]['cr_ref_xcorr']
            if Xmax<0.35:
                save0=False
                break
        if not save0:
            continue
        templateDirectionFitter.run(evt,stn,det,channels_to_use=[4,5,6], cosmic_ray=True)
        eventWriter.run(evt)
        break
    # ic(n,c)
    print('3X Completed')
    return X

def Analyze_SNR(input):
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input))
    X = os.path.join(output_path,'3X_SNR')
    try:
        os.makedirs(X)
    except(FileExistsError):
        send2trash.send2trash(X)
        os.makedirs(X)
    eventWriter.begin(os.path.join(X,'3X_SNR.nur'))
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        Xcorr=[]    
        for i in [4,5,6]:
            channel = stn.get_channel(i)
            Xcorr.append(np.max(np.abs(channel[chp.Chi_Temp]['R243E512']['chi_max'])))
        trace_up    = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3,4,5,6,7]):
            trace_up.append(np.max(np.abs(channel.get_trace()/units.mV)))
        Xcorr=np.array([np.max(Xcorr)])
        trace_up=np.array([np.max(trace_up)])/Vrms
        exp_X=SNR_cut_line_cut(trace_up)
        # ic(exp_X,Xcorr,trace_up)
        if Xcorr<SNR_cut_line_cut(trace_up):
            ic(exp_X,Xcorr,trace_up)
            continue
        eventWriter.run(evt)
    ic('SNR Completed')
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
        # det.update(time)
        zenith=stn.get_parameter(stnp.zenith)/units.deg
        if zenith>85:
            continue
        eventWriter.run(evt)
    print('Zen Complete')
    return zen_path

input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/New_temp_Xcorr/Trig/without_Freqs/3X_SNR_Ratio'
input_sim='/Users/david/PycharmProjects/Demo1/Research/Repository/simulation_New_Temp/SNR_cut'
# output_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/New_temp_Xcorr/Trig/'
# for detect data
output_path='/Users/david/PycharmProjects/Demo1/Research/Repository/simulation_New_Temp/'
# if os.path.isdir(output_path):
#     os.makedirs(output_path)
# X=Analyze_X(input_path)
# Ratio=Analyze_Ratio(input_path)
# SNR=Analyze_SNR(X)
# Ratio=Analyze_Ratio(input_sim)
X=Analyze_X(input_sim)





