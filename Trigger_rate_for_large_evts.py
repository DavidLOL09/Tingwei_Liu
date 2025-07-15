import sys
sys.path.insert(0,'/Users/david/PycharmProjects/Demo1/Research/Repository/NuRadioMC')
import datetime
import numpy as np
import datetime
from icecream import ic
import NuRadioReco.modules.io.eventWriter
eventWriter = NuRadioReco.modules.io.eventWriter.eventWriter()
import os
import re
import send2trash
from NuRadioReco.modules.io.NuRadioRecoio import NuRadioRecoio
from NuRadioReco.framework.parameters import ARIANNAParameters as apt
today=datetime.datetime(2018,4,11,11,38)

from NuRadioReco.detector import detector
json_file_origin=f'/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/Stn51_sim_inAir/station51.json'
det=detector.Detector(json_filename=json_file_origin)
import NuRadioReco.modules.channelTemplateCorrelation
channelTemplateCorrelation = NuRadioReco.modules.channelTemplateCorrelation.channelTemplateCorrelation(template_directory='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/templates/')
channelTemplateCorrelation.begin(debug=False)
import NuRadioReco.modules.channelResampler
channelResampler = NuRadioReco.modules.channelResampler.channelResampler()
import NuRadioReco.modules.channelBandPassFilter
channelBandPassFilter = NuRadioReco.modules.channelBandPassFilter.channelBandPassFilter()
from NuRadioReco.modules.channelStopFilter import channelStopFilter
channelStopFilter=channelStopFilter()
from NuRadioReco.modules.ARIANNA import hardwareResponseIncorporator as ChardwareResponseIncorporator
hardwareResponseIncorporator = ChardwareResponseIncorporator.hardwareResponseIncorporator()
hardwareResponseIncorporator.begin(debug=False)
from NuRadioReco.utilities import units
import NuRadioReco.modules.templateDirectionFitter
templateDirectionFitter = NuRadioReco.modules.templateDirectionFitter.templateDirectionFitter()
templateDirectionFitter.begin()




# ic(datetime.datetime(2018,4,11,11,0,0,0,))
def round_in_time(time:datetime.datetime):
    return datetime.datetime(time.year,time.month,time.day,time.hour)

def hist(time_list,bins:dict):
    for i in time_list:
        bins[round_in_time(i)].append(i)
    return bins

input_path='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw'
def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir

def get_time_bins(start:datetime.datetime,stop:datetime.datetime):
    start=round_in_time(start)
    stop=round_in_time(stop)
    bins=[start]
    while bins[-1]<=stop:
        bins.append(bins[-1]+datetime.timedelta(hours=1))
    bins_dic={}
    for i in bins:
        bins_dic[i]=[]
    return bins_dic

def get_run_time_list(Reader:NuRadioRecoio):
    time_list=[]
    start=datetime.datetime(2020,1,1)
    stop=datetime.datetime(2018,1,1)
    for evt in Reader.get_events():
        stn=evt.get_station(51)
        time_list.append(stn.get_station_time().datetime)
        str = stn.get_parameter(apt.seq_start_time)
        stp = stn.get_parameter(apt.seq_stop_time)
        if str<=start:
            start=str
        if stp>=stop:
            stop=stp
    return start,stop,time_list
def Writing_setting(output_path):
    try:
        os.makedirs(output_path)
    except(FileExistsError):
        send2trash.send2trash(output_path)
        os.makedirs(output_path)
    return output_path
def write_evt(Reader:NuRadioRecoio,time_bins:dict,num_per_h,eventWriter):
    for evt in Reader.get_events():
        stn=evt.get_station(51)
        time=stn.get_station_time().datetime
        time=round_in_time(time)
        if len(time_bins[time])>num_per_h:
            continue
        det.update(time)
        # eventWriter.run(evt)

def extract_run_num(path):
    match = re.search(r'run_(\d+)', path)
    if match:
        run_number = int(match.group(1))  # This will give you 242 as an integer
        return run_number
    

def Time_trigger_rate(input_path,output_path,num_per_h):
    path_list=get_input(input_path)
    path_list.sort()
    # output_path=Writing_setting(os.path.join(output_path,'Trig_rate'))
    for i in path_list:
        run=extract_run_num(i)
        if run!=264:
            continue
        Reader=NuRadioRecoio([i])
        start,stop,time_list=get_run_time_list(Reader)
        time_bins=get_time_bins(start,stop)
        time_bins=hist(time_list,time_bins)
        count=0
        for key,value in time_bins.items():
            if len(value)>=8:
                continue
            ic(f'{key}——{len(value)}')
            count+=len(value)
        ic(count)
        exit()
        eventWriter.begin(os.path.join(output_path,f'R{run}_TrigR{num_per_h}_cut.nur'))
        write_evt(Reader,time_bins,num_per_h,eventWriter)
output_path='/Users/david/PycharmProjects/Demo1/Research/Repository'
Time_trigger_rate(input_path,output_path,8)


