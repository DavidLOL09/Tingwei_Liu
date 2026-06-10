from typing_extensions import Self
import sys
sys.path.insert(0,'/Users/david/PycharmProjects/Demo1/Research/Repository/Simulation/')
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
from NuRadioReco.detector import detector
from icecream import ic
import os
import datetime
from NuRadioReco.framework.parameters import channelParameters as chp
import NuRadioReco.modules.correlationDirectionFitter
import NuRadioReco.modules.channelLengthAdjuster
import ToolsPac

import NuRadioReco.utilities.fft as fft

channelLengthAdjuster = NuRadioReco.modules.channelLengthAdjuster.channelLengthAdjuster()
channelLengthAdjuster.begin()

hardwareResponseIncorporator = ChardwareResponseIncorporator.hardwareResponseIncorporator()
hardwareResponseIncorporator.begin(debug=False)

import NuRadioReco.modules.channelResampler
channelResampler = NuRadioReco.modules.channelResampler.channelResampler()
# channelResampler.begin(debug=False)

from NuRadioReco.modules.channelStopFilter import channelStopFilter
channelStopFilter=channelStopFilter()

import NuRadioReco.modules.channelSignalReconstructor
channelSignalReconstructor = NuRadioReco.modules.channelSignalReconstructor.channelSignalReconstructor()

import NuRadioReco.modules.channelBandPassFilter
channelBandPassFilter = NuRadioReco.modules.channelBandPassFilter.channelBandPassFilter()

template_path_2_backlobe = '/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/CR_BL_2backlope_Template_final'
import custimizedTemplateCorrelation
custimizedTemplateCorrelation = custimizedTemplateCorrelation.custimizedTemplateCorrelation()
custimizedTemplateCorrelation.begin(template_path_2_backlobe)

templateDirectionFitter = NuRadioReco.modules.templateDirectionFitter.templateDirectionFitter()
templateDirectionFitter.begin()

json_file_origin=f'/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/Stn51_sim_inAir/station51.json'
ic(json_file_origin)
det=detector.Detector(json_filename=json_file_origin)
det.update(datetime.datetime(2018,10,1))
import send2trash

input_path   = '/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw'
output_path  = '/Users/david/PycharmProjects/Demo1/Research/Repository/aftResample'

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

def filter_freqs_chi(reader:NuRadioReco.modules.io.NuRadioRecoio.NuRadioRecoio,failed_save = False):
    pass_evt = []
    fail_evt = []
    for evt in reader.get_events():
        stn=evt.get_station(51)

        channelBandPassFilter.run(evt, stn, det, passband=[80 * units.MHz, 500 * units.MHz], filter_type='butter', order = 10)
        channelStopFilter.run(evt,stn,det,append=0,prepend=0)
        custimizedTemplateCorrelation.run(evt,[4,5,6])
        Xcorr=[]
        for i in [4,5,6]:
            channel = stn.get_channel(i)
            Xmax=np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr']))
            Xcorr.append(Xmax)
        if max(Xcorr)>=0.4:
            if min(Xcorr)>=0.3:
                pass_evt.append(evt)
            else:
                fail_evt.append(evt)
                continue
        else:
            fail_evt.append(evt)
    if failed_save:
        return pass_evt,fail_evt
    else:
        return pass_evt
        
        
def Logeqs(k,b,x):
    return k*np.log10(x)+b
def SNR_cut(SNR,Xcorr):
    # 2 backlope
    x=SNR
    y1=np.full_like(x[x<6.566],0.46)

    x2=x[(x>6.566)&(x<8.32)]
    y2=Logeqs(k=0.86557,b=-0.24743,x=x2)

    x3=x[(x>8.32)&(x<8.822)]
    y3=Logeqs(k=0.62884,b=-0.02961,x=x3)

    x4=x[(x>8.822)&(x<11.306)]
    y4=Logeqs(k=1.37365,b=-0.73388,x=x4)
    
    x5=x[(x>11.306)&(x<14.541)]
    y5=Logeqs(k=0.48497,b=0.20218,x=x5)

    y6=np.full_like(x[x>14.541],0.766)
    y=np.concatenate((y1,y2,y3,y4,y5,y6))
    return Xcorr>y
def filter_freqs_chi_snr(reader:NuRadioReco.modules.io.NuRadioRecoio.NuRadioRecoio, failed_save = False):
    pass_evt = []
    fail_evt = []
    for evt in reader.get_events():
        stn=evt.get_station(51)
        trace_max    = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3,4,5,6,7]):
            trace_max.append(np.max(np.abs(channel.get_trace()/units.mV)))
        trace_max=np.max(trace_max)/Vrms
        Xcorr=[]
        for i in [4,5,6]:
            channel = stn.get_channel(i)
            Xmax=np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr']))
            Xcorr.append(Xmax)
        Xcorr=np.max(Xcorr)
        if not SNR_cut(trace_max,Xcorr):
            fail_evt.append(evt)
            continue
        pass_evt.append(evt)
    if failed_save:
        return pass_evt,fail_evt
    else:
        return pass_evt     

def filter_has_triggered(reader:NuRadioReco.modules.io.NuRadioRecoio.NuRadioRecoio,fail_save = False):
    pass_evt    = []
    bad_evt     = []
    run_lst     = []
    for evt in reader.get_events():
        stn = evt.get_station(51)
        run = evt.get_run_number()
        if stn.has_triggered():
            pass_evt.append(evt)
        else:
            if run not in run_lst:
                run_lst.append(run)
            bad_evt.append(evt)
    ic(run_lst)
    exit()
    if fail_save:
        return pass_evt,bad_evt
    else:
        return pass_evt

def get_trace(evt_lst):
    trace_lst = []
    for evt in evt_lst:
        stn = evt.get_station(51)
        for i in [4,5,6]:
            chn = stn.get_channel(i)
            trace_lst.append(np.abs(chn.get_trace()/units.mV))
    return np.array(trace_lst)

def apply_BandPassFilter(evt,min_freqs=50,max_freqs=500):
    stn = evt.get_station(51)
    time = stn.get_station_time().datetime
    det.update(time)
    channelBandPassFilter.run(evt, stn, det, passband=[min_freqs * units.MHz, max_freqs * units.MHz], filter_type='butter', order = 10)
    return

def filter_cluster(reader:NuRadioReco.modules.io.NuRadioRecoio.NuRadioRecoio, criti_space_angle, criti_time:datetime.timedelta):
    criti_time = criti_time.total_seconds()
    def sph2carti(zen,azi):
        x = np.cos(zen)*np.sin(azi)
        y = np.sin(zen)*np.sin(azi)
        z = np.cos(azi)
        return [x,y,z]
    def get_space_angle(vec1,vec2):
        cos = np.dot(vec1,vec2)
        if cos>1:
            cos = 1
        angel_diff = np.arccos(cos)
        if np.isnan(angel_diff):
            ic(vec1,vec2,np.dot(vec1,vec2))
        return angel_diff
    evt_lst = []
    evt_lst1= []
    for evt in reader.get_events():
        stn = evt.get_station(51)
        zen = stn.get_parameter(stnp.zenith)/units.rad
        azi = stn.get_parameter(stnp.azimuth)/units.rad
        time = stn.get_station_time().datetime
        id = f'R{evt.get_run_number()}E{evt.get_id()}'
        vec = sph2carti(zen,azi)
        evt_lst.append([id,vec,time,evt])
        evt_lst1.append([vec,time,id])
    passed_evt = []
    for e1,evt1 in enumerate(evt_lst):
        vec1 = evt1[1]
        time1= evt1[2]
        count = -1
        for e2,evt2 in enumerate(evt_lst1):
            vec_diff = np.abs(get_space_angle(vec1,evt2[0]))
            time_diff= np.abs((time1-evt2[1]).total_seconds())
            # ic(time_diff/(datetime.timedelta(days=1).total_seconds()))
            # id = evt2[-1]
            # if id == evt1[0]:
            #     ic(vec_diff,time_diff)
            if vec_diff<criti_space_angle:
                if time_diff<criti_time:
                    count+=1
        ic(evt1[0],count)
        ic('\n')
        if count<2:
            passed_evt.append(evt1[3])
        else:
            ic(evt1[0])

    return passed_evt
    



            
    
        


def filter_freqs(reader:NuRadioReco.modules.io.NuRadioRecoio.NuRadioRecoio, criti_freqs = 80, cut_ratio = 0.115,failed_save = False):
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
    passed_evt = []
    failed_evt = []
    for evt in reader.get_events():
        stn = evt.get_station(51)
        run = evt.get_run_number()
        id = evt.get_id()
        largest=[0,0]
        time = stn.get_station_time().datetime
        det.update(time)
        # channelBandPassFilter.run(evt, stn, det, passband=[50 * units.MHz, 500 * units.MHz], filter_type='butter', order = 10)
        # largest:[max_amp,ratio]
        # flatVolt_remove(evt)
        for i in range(4,7):
            spectrum,freqs,ratio=get_low_amp_ratio(criti_freqs,evt,i)
            if ratio>largest[1]:
                stn=evt.get_station(51)
                chn=stn.get_channel(i)
                trace=np.max(np.abs(chn.get_trace()/units.MeV))
                largest=[trace,ratio]
        if largest[1]<=cut_ratio:
            passed_evt.append(evt)
        else:
            failed_evt.append(evt)
    if failed_save:
        return passed_evt,failed_evt
    else:
        return passed_evt
    
# input_path = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335'
# # output_path= '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335'
# ic(get_input(input_path))
# reader = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
# writer = ToolsPac.set_writer(input_path,filename='BandPass_50')
# for evt in reader.get_events():
#     apply_BandPassFilter(evt)
#     writer.run(evt)

input_path = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs_X_direct/new_phase_algorithm'
output_path = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/'
reader = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))
writer = ToolsPac.set_writer(output_path,filename = 'Trig_335_Freqs_X_cluster')
passed_evt = filter_cluster(reader,criti_space_angle=np.deg2rad(10),criti_time=datetime.timedelta(days = 1))
ic(len(passed_evt))
for evt in passed_evt:
    writer.run(evt)
writer.end()
exit()

# input_path = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335'
# output = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs'
# reader = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
# passed_evt,failed_evt = filter_freqs(reader,failed_save=True)
# writer = ToolsPac.set_writer(output,filename='Trig_335_Freqs_failed')
# ic(len(failed_evt))
# for evt in failed_evt:
#     writer.run(evt)

# input_path = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs/Trig_335_Freqs_failed'
# output = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs_X'
# reader = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
# passed_evt = filter_freqs_chi(reader)
# writer = ToolsPac.set_writer(output,filename='Trig_335_Freqs_X_failed')
# for evt in passed_evt:
#     writer.run(evt)

# input_path = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs_X/Trig_335_Freqs_X_failed'
# output = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs_X_SNR'
# reader = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
# passed_evt = filter_freqs_chi_snr(reader)
# writer = ToolsPac.set_writer(output,filename='Trig_335_Freqs_X_SNR_failed')
# ic(len(passed_evt))
# for evt in passed_evt:
#     writer.run(evt)

# input_path = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs'
# reader = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
# ic(reader.get_n_events())
# input_path = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs/Trig_335_Freqs_failed'
# reader = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
# ic(reader.get_n_events())
# input_path = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs_X'
# reader = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
# ic(reader.get_n_events())
# input_path = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs_X/Trig_335_Freqs_X_failed'
# reader = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
# ic(reader.get_n_events())
# input_path = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs_X_SNR'
# reader = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
# ic(reader.get_n_events())
# input_path = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs_X_SNR/Trig_335_Freqs_X_SNR_failed'
# reader = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
# ic(reader.get_n_events())
Vrms=(9.71+9.66+8.94)/3

# input_path = '/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_non_goso'
# reader = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
# good_evt,bad_evt = filter_has_triggered(reader,True)
# ic()
# ic(len(good_evt),len(bad_evt))
# good_trace = get_trace(good_evt)
# bad_trace = get_trace(bad_evt)
# ic(np.mean(good_trace),np.mean(bad_trace))

# ic| len(good_evt): 116364, len(bad_evt): 40925
# ic| np.mean(good_trace): np.float32(19.50501)
    # np.mean(bad_trace): np.float32(9.437466)









