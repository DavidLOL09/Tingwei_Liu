# Trig-Freqs-X-SNR-Zen-Ratio
import sys
# sys.path.insert(0,'/Users/david/PycharmProjects/Demo1/Research/Repository/NuRadioMC')
from NuRadioReco.modules.io import NuRadioRecoio
import NuRadioReco.modules.io.eventWriter
from NuRadioReco.framework.parameters import channelParameters as chp
eventWriter = NuRadioReco.modules.io.eventWriter.eventWriter()
import NuRadioReco.utilities.units as units
import os
import numpy as np
from NuRadioReco.framework.parameters import stationParameters as stnp
json_file_origin=f'/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/Stn51_sim_inAir/station51.json'
from NuRadioReco.detector import detector
det=detector.Detector(json_filename=json_file_origin)
import send2trash
from icecream import ic
import NuRadioReco.modules.templateDirectionFitter
templateDirectionFitter = NuRadioReco.modules.templateDirectionFitter.templateDirectionFitter()
templateDirectionFitter.begin()
import NuRadioReco.utilities.fft as fft
from NuRadioReco.modules.channelStopFilter import channelStopFilter
channelStopFilter=channelStopFilter()
import NuRadioReco.modules.channelTemplateCorrelation
from NuRadioReco.modules.ARIANNA import hardwareResponseIncorporator as ChardwareResponseIncorporator
channelTemplateCorrelation = NuRadioReco.modules.channelTemplateCorrelation.channelTemplateCorrelation(template_directory='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/templates/')
channelTemplateCorrelation.begin(debug=False)
import NuRadioReco.modules.channelBandPassFilter
channelBandPassFilter = NuRadioReco.modules.channelBandPassFilter.channelBandPassFilter()
hardwareResponseIncorporator = ChardwareResponseIncorporator.hardwareResponseIncorporator()
hardwareResponseIncorporator.begin(debug=False)
import NuRadioReco.modules.channelResampler
channelResampler = NuRadioReco.modules.channelResampler.channelResampler()
Vrms=(9.71+9.66+8.94)/3
def set_writer(output,filename):
    output_file = os.path.join(output,filename)
    try:
        os.makedirs(output_file)
    except(FileExistsError):
        send2trash.send2trash(output_file)
        os.makedirs(output_file)
    eventWriter.begin(os.path.join(output_file,f'{filename}.nur'))
    return eventWriter,output_file
def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir

# input_path = '/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Trig_Freqs_X_SNR'
output_path = '/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/'
# eventWriter=set_output(output_path,'Trig_SNR_Freqs_X')

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

def Analyze_Ratio(input_path,filename='Trig_Freqs_X_SNR_Ratio'):
    Data=NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    ic(input_path)
    eventWriter,Ratio=set_writer(output_path,filename)
    for evt in Data.get_events():
        stn = evt.get_station(51)
        time = stn.get_station_time().datetime
        det.update(time)
        trace_up  = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3,4,5,6,7]):
            trace_up.append(np.max(np.abs(channel.get_trace()/units.mV)))
        trace_down    = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3]):
            trace_down.append(np.max(np.abs(channel.get_trace()/units.mV))) 
        channel=stn.get_channel(7)
        trace_bic=np.max(np.abs(channel.get_trace()/units.mV)) 
        trace_up    = np.max(trace_up)
        trace_down  = np.max(trace_down)
        if trace_up/trace_bic<=log_cut_line_BicR(trace_up) or trace_up/trace_down<=log_cut_line_UDR(trace_up):
            continue
        eventWriter.run(evt)
    return Ratio

def Analyze_3Xcorr(input_path):
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    filename='Trig_Freqs_X'
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
        hardwareResponseIncorporator.run(evt, stn, det, sim_to_data=True)
        eventWriter.run(evt)
    ic('X Completed')
    return sig

def make_Xcorr(input_path):
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    filename='raw_with_X'
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
        hardwareResponseIncorporator.run(evt, stn, det, sim_to_data=True)
        eventWriter.run(evt)
    ic('X Completed')
    return sig

def SNR_cut_line(x):
    k=0.3
    y=k*np.log10(x)+0.2
    return y

def Analyze_SNR(input_path):
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    eventWriter,filename=set_writer(output_path,'Trig_Freqs_X_SNR')
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        run=evt.get_run_number()
        id=evt.get_id()
        Xcorr=[]     
        for i in [4,5,6]:
            channel = stn.get_channel(i)
            Xcorr.append(np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr'])))
        X=np.max(Xcorr)
        trace_up    = []
        for channel in stn.iter_channels(use_channels=[4,5,6]):
            trace_up.append(np.max(np.abs(channel.get_trace()/units.mV)))
        trace_up=max(trace_up)
        X_exp=SNR_cut_line(trace_up/Vrms)
        if X<=X_exp:
            continue
        eventWriter.run(evt)
    return filename

def Analyze_zen(input,filename='Trig_Freqs_X_SNR_Zen'):
    # Zen,<=85deg
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input))
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
def set_direct(input,filename='Candi_with_direct'):
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input))
    direct_path = os.path.join(output_path,filename)
    try:
        os.makedirs(direct_path)
    except(FileExistsError):
        send2trash.send2trash(direct_path)
        os.makedirs(direct_path)
    eventWriter.begin(os.path.join(direct_path,f'{filename}.nur'))
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        time= stn.get_station_time().datetime
        det.update(time)
        templateDirectionFitter.run(evt,stn,det,channels_to_use=[4,5,6], cosmic_ray=True)
        eventWriter.run(evt)

def Analyze_Freqs(input_path):
    eventWriter,Freqs=set_writer(output_path,'Trig_Freqs')
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        largest=[0,0]
        # largest:[max_amp,ratio]
        for i in range(4,7):
            spectrum,freqs,ratio=get_low_amp_ratio(80,evt,i)
            if ratio>largest[1]:
                stn=evt.get_station(51)
                chn=stn.get_channel(i)
                trace=np.max(np.abs(chn.get_trace()/units.MeV))
                largest=[trace,ratio]
        if largest[1]<=0.115:
            eventWriter.run(evt)
    ic('Freqs Complete')
    return Freqs

def get_total(input_path):
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    return readARIANNAData.get_n_events()

def get_removed_evts(input_path1,input_path2,filename='zen_diff'):
    # input_1:before
    # input_2:after
    readARIANNAData1=NuRadioRecoio.NuRadioRecoio(get_input(input_path1))
    readARIANNAData2=NuRadioRecoio.NuRadioRecoio(get_input(input_path2))
    Writer,zen_diff=set_writer(output_path,filename)
    iden=[]
    for evt in readARIANNAData2.get_events():
        iden.append(f'R{evt.get_run_number()}E{evt.get_id()}')
    for evt in readARIANNAData1.get_events():
        if f'R{evt.get_run_number()}E{evt.get_id()}' not in iden:
            stn=evt.get_station(51)
            time=stn.get_station_time().datetime
            det.update(time)
            templateDirectionFitter.run(evt,stn,det,channels_to_use=[4,5,6], cosmic_ray=True)
            Writer.run(evt)
    Writer.end()

    


def Incop_check(input_path):
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
    trace=[]
    for evt in readARIANNAData.get_events():
        stn=evt.get_station(51)
        trace_max    = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3,4,5,6,7]):
            trace_max.append(np.max(np.abs(channel.get_trace()/units.mV)))
        trace_max=np.max(trace_max)
        trace.append(trace_max)
        ic(trace_max)
    trace=np.array(trace)
    ic(np.median(trace))


# ic(f'Trig                       : {get_total(input_path)}')
# # ic(Incop_check(input_path))
# Freqs                   = Analyze_Freqs(input_path)
# # Freqs='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Trig_Freqs'
# ic(f'Trig_Freqs                 : {get_total(Freqs)}')
# Freqs_X                 = Analyze_3Xcorr(Freqs)  
# # Freqs_X='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Trig_Freqs_X'
# ic(f'Trig_Freqs_X               : {get_total(Freqs_X)}')
# Freqs_X_SNR             = Analyze_SNR(Freqs_X)
# # Freqs_X_SNR='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Trig_Freqs_X_SNR'
# ic(f'Trig_Freqs_X_SNR           : {get_total(Freqs_X_SNR)}')
# Freqs_X_SNR_Zen         = Analyze_zen(Freqs_X_SNR)
# Freqs_X_SNR_Zen='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Trig_Freqs_X_SNR_Zen'
# ic(f'Trig_Freqs_X_SNR_Zen       : {get_total(Freqs_X_SNR_Zen)}')
# Freqs_X_SNR_Zen_Ratio   = Analyze_Ratio(Freqs_X_SNR_Zen)
# # Freqs_X_SNR_Zen_Ratio='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Trig_Freqs_X_SNR_Zen_Ratio'
# ic(f'Trig_Freqs_X_SNR_Zen_Ratio : {get_total(Freqs_X_SNR_Zen_Ratio)}')


# SNR_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Trig_Freqs_X_SNR'
# ic(f'SNR    :{get_total(SNR_path)}')
# Ratio = Analyze_Ratio(SNR_path,'Trig_Freqs_X_SNR_Ratio')
# ic(f'Ratio  :{get_total(Ratio)}')
# Zen = Analyze_zen(Ratio,'Trig_Freqs_X_SNR_Ratio_Zen')
# ic(f'Zen    :{get_total(Zen)}')

Ratio='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Trig_Freqs_X_SNR_Ratio'
input_raw='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw'
Zen='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Trig_Freqs_X_SNR_Ratio_Zen'
sim_SNR='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Trig_Freqs_X_SNR'
sim_Ratio='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Trig_Freqs_X_SNR_Ratio'
candi='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Final_Candi'
# make_Xcorr(input_raw)
# Ratio = Analyze_Ratio(sim_SNR)
set_direct(candi)