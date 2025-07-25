# Trig-X-SNR-Zen-Ratio
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
from NuRadioReco.framework.parameters import eventParameters as evtp
import datetime
import NuRadioReco.modules.io.eventWriter
import matplotlib.pyplot as plt
import datetime
import send2trash
from icecream import ic
import os
import datetime
from NuRadioReco.framework.parameters import channelParameters as chp
templateDirectionFitter = NuRadioReco.modules.templateDirectionFitter.templateDirectionFitter()
templateDirectionFitter.begin()
import NuRadioReco.utilities.fft as fft
from NuRadioReco.modules.channelStopFilter import channelStopFilter
channelStopFilter=channelStopFilter()
import NuRadioReco.modules.channelTemplateCorrelation
channelTemplateCorrelation = NuRadioReco.modules.channelTemplateCorrelation.channelTemplateCorrelation(template_directory='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/templates/')
channelTemplateCorrelation.begin(debug=False)
import NuRadioReco.modules.channelBandPassFilter
channelBandPassFilter = NuRadioReco.modules.channelBandPassFilter.channelBandPassFilter()
hardwareResponseIncorporator = ChardwareResponseIncorporator.hardwareResponseIncorporator()
hardwareResponseIncorporator.begin(debug=False)
import NuRadioReco.modules.channelResampler
channelResampler = NuRadioReco.modules.channelResampler.channelResampler()

json_file_origin=f'/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/Stn51_sim_inAir/station51.json'
det=detector.Detector(json_filename=json_file_origin)
eventWriter = NuRadioReco.modules.io.eventWriter.eventWriter()
input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_with_weights'
output_path  ='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig'
Vrms=(9.71+9.66+8.94)/3
def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir
input_dir=get_input(input_path)

def Analyze_zen(input):
    # Zen,<=85deg
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input))
    filename='X_SNR_Zen'
    zen_path = os.path.join(output_path,filename)
    try:
        os.makedirs(zen_path)
    except(FileExistsError):
        send2trash.send2trash(zen_path)
        os.makedirs(zen_path)
    eventWriter.begin(os.path.join(zen_path,f'{filename}.nur'))
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        time= stn.get_station_time().datetime
        det.update(time)
        templateDirectionFitter.run(evt,stn,det,channels_to_use=[4,5,6], cosmic_ray=True)
        zenith=stn.get_parameter(stnp.zenith)/units.deg
        if zenith>85:
            continue
        eventWriter.run(evt)
    ic('Zen Complete')
    return zen_path

def Analyze_3Xcorr(input_path):
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    filename='X'
    sig = os.path.join(output_path,filename)
    try:
        os.makedirs(sig)
    except(FileExistsError):
        send2trash.send2trash(sig)
        os.makedirs(sig)
    eventWriter.begin(os.path.join(sig,f'{filename}.nur'))
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        save0=True
        time= stn.get_station_time().datetime
        det.update(time)
        channelStopFilter.run(evt,stn,det,append=0,prepend=0)
        channelBandPassFilter.run(evt, stn, det, passband=[80 * units.MHz, 500 * units.MHz], filter_type='butter', order = 10)
        hardwareResponseIncorporator.run(evt, stn, det, sim_to_data=False)
        channelTemplateCorrelation.run(evt,stn,det,cosmic_ray=True,n_templates=1, channels_to_use=[4,5,6])
        Xcorr=[]
        for i in [4,5,6]:
            channel = stn.get_channel(i)
            Xmax=np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr']))
            if Xmax<0.4:
                save0=False
                break
            Xcorr.append(Xmax)
        if save0 == False:
            continue
        if max(Xcorr)>=0.4:
            hardwareResponseIncorporator.run(evt, stn, det, sim_to_data=True)
            eventWriter.run(evt)
    ic('X Completed')
    return sig

def log_cut_line_UDR(x):
    # UD:
    k=3.358751507788999
    y=k*np.log10(x)-5.067864845613618
    return y
def log_cut_line_BicR(x):
    # Bic:
    k=3.9015114425732005
    y=k*np.log10(x)-6.360165150568652
    return y

def Analyze_Ratio(input_path):
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    filename='X_SNR_Zen_Ratio'
    Ratio = os.path.join(output_path,filename)
    try:
        os.makedirs(Ratio)
    except:
        send2trash.send2trash(Ratio)
        os.makedirs(Ratio)
    eventWriter.begin(os.path.join(Ratio,f'{filename}.nur'))
    for evt in readARIANNAData.get_events():
        stn=evt.get_station(51)
        trace_down=[]
        for channel in stn.iter_channels(use_channels=[0,1,2,3]):
            trace_down.append(np.max(np.abs(channel.get_trace()/units.mV)))
        trace_down=np.max(trace_down)
        trace_max    = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3,4,5,6,7]):
            trace_max.append(np.max(np.abs(channel.get_trace()/units.mV)))
        trace_max=np.max(trace_max)
        channel = stn.get_channel(7)
        trace_bic = np.max(np.abs(channel.get_trace()/units.mV))
        ratio_bic=trace_max/trace_bic
        ratio_UD =trace_max/trace_down
        if ratio_bic<=log_cut_line_BicR(trace_max):
            continue
        if ratio_UD<=log_cut_line_UDR(trace_max):
            continue
        evt.set_parameter(evtp.UD_Ratio,trace_max/trace_down)
        evt.set_parameter(evtp.Bic_Ratio,trace_max/trace_bic)
        eventWriter.run(evt)
    ic('Ratio_complete')
    return Ratio

def SNR_cut_line(x):
    k=0.3
    y=k*np.log10(x)+0.2
    return y


def get_trace_by_chn(i,evt):
    stn=evt.get_station(51)
    chn=stn.get_channel(i)
    trace_spectrum=chn.get_frequency_spectrum()
    return trace_spectrum
def normalize_wave(trace):
    trace=np.abs(trace)
    return trace/np.sqrt(np.dot(trace,trace))
def find_closest_index(criti_num,arr:np.array):
    try:
        for i in range(len(arr)):
            if criti_num-arr[i]<=0:
                return i
        raise ValueError
    except ValueError:
        ic('Critical Number is bigger than every elemtns in array')
def get_low_amp_ratio(criti_amp,evt,chn_num):
    sample_rate=1*units.GHz
    spectrum = normalize_wave(get_trace_by_chn(chn_num,evt))
    freqs = fft.freqs(256,sample_rate)/units.MHz
    index=find_closest_index(criti_amp,freqs)-1
    tot_amp = np.sum(spectrum)
    low_amp = np.sum(spectrum[0:index+1])
    ratio = low_amp/tot_amp
    return spectrum,freqs,ratio

def Analyze_Freqs(input_path):
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    filename='Freqs'
    output = os.path.join(output_path,filename)
    try:
        os.makedirs(output)
    except(FileExistsError):
        send2trash.send2trash(output)
        os.makedirs(output)
    eventWriter.begin(os.path.join(output,f'{filename}.nur'))
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        run = evt.get_run_number()
        id = evt.get_id()
        largest=[0,0]
        time = stn.get_station_time().datetime
        # largest:[max_amp,ratio]
        for i in range(4,7):
            spectrum,freqs,ratio=get_low_amp_ratio(80,evt,i)
            if ratio>largest[1]:
                stn=evt.get_station(51)
                chn=stn.get_channel(i)
                trace=np.max(np.abs(chn.get_trace()/units.MeV))
                largest=[trace,ratio]
        if largest[1]>=0.115:
            continue
        eventWriter.run(evt)
    ic('Freqs Complete')
    return output

def Analyze_SNR(input_path):
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    filename='X_SNR'
    SNR = os.path.join(output_path,filename)
    try:
        os.makedirs(SNR)
    except(FileExistsError):
        send2trash.send2trash(SNR)
        os.makedirs(SNR)
    eventWriter.begin(os.path.join(SNR,f'{filename}.nur'))
    for evt in readARIANNAData.get_events():
        stn=evt.get_station(51)
        trace_max    = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3,4,5,6,7]):
            trace_max.append(np.max(np.abs(channel.get_trace()/units.mV)))
        trace_max=np.max(trace_max)
        Xcorr=[]
        for i in [4,5,6]:
            channel = stn.get_channel(i)
            Xmax=np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr']))
            Xcorr.append(Xmax)
        Xcorr=np.max(Xcorr)
        if Xcorr<=SNR_cut_line(trace_max/Vrms):
            continue
        eventWriter.run(evt)
    ic('SNR Complete')
    return SNR

def Incop_check(input_path):
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    trace=[]
    for evt in readARIANNAData.get_events():
        stn=evt.get_station(51)
        trace_max    = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3,4,5,6,7]):
            trace_max.append(np.max(np.abs(channel.get_trace()/units.mV)))
        trace_max=np.max(trace_max)
        ic(trace_max)
        trace.append(trace_max)
    trace=np.array(trace)
    ic(np.median(trace))


def get_total_weights(input_path):
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    weights=[]
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        weights.append(evt.get_parameter(evtp.event_rate))
    weights=np.array(weights)
    return np.sum(weights)
# Incop_check(input_path)
# ic(get_total_weights(input_path))
# Freqs=Analyze_Freqs(input_path)
Freqs='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Freqs'
# ic(get_total_weights(Freqs))
# Freqs_X=Analyze_3Xcorr(Freqs)

# ic(get_total_weights(Freqs_X))
# Freqs_X_SNR=Analyze_SNR(Freqs_X)

# ic(get_total_weights(Freqs_X_SNR))
# Freqs_X_SNR_Zen=Analyze_zen(Freqs_X_SNR)

# ic(get_total_weights(Freqs_X_SNR_Zen))
# Freqs_X_SNR_Zen_Ratio=Analyze_Ratio(Freqs_X_SNR_Zen)


def remove_some_evts(input_path,remove_iden):
    readARIANNAData=NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    filename='Final_Candi'
    SNR = os.path.join(output_path,filename)
    try:
        os.makedirs(SNR)
    except(FileExistsError):
        send2trash.send2trash(SNR)
        os.makedirs(SNR)
    eventWriter.begin(os.path.join(SNR,f'{filename}32.nur'))
    for evt in readARIANNAData.get_events():
        if f'R{evt.get_run_number()}E{evt.get_id()}' in remove_iden:
            continue
        eventWriter.run(evt)
input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Trig_Freqs_X_SNR_Ratio_Zen'
remove_iden=['R247E17','R247E1762','R263E739','R263E749']
remove_some_evts(input_path,remove_iden)


# ic(get_total_weights(Freqs_X_SNR_Zen_Ratio))



# Incop_check(X)







        
        


