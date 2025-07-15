import sys
from icecream import ic
sys.path.insert(0,'/Users/david/PycharmProjects/Demo1/Research/Repository/NuRadioMC')
# The old raw file asking for a specific version of NuRadioMC to read
from NuRadioReco.modules.io import NuRadioRecoio
import datetime
import NuRadioReco.modules.io.eventWriter
import matplotlib.pyplot as plt
import datetime
import os
import NuRadioReco.modules.correlationDirectionFitter
from NuRadioReco.framework.parameters import ARIANNAParameters as apt
input='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw'
# input_path=../raw/station_51_run_00242.root.nur
# input file need to be clustered by run 
import ToolsPac
import numpy as np
output='/Users/david/PycharmProjects/Demo1/Research/Repository/live_time'
if not os.path.isdir(output):
    os.makedirs(output)
def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir
goso=[242,243,247,249,256,260,263,264,266]
# Goso run list


Dead_time = datetime.timedelta(minutes=60/8)
# Dead_time per Goso event

def Live_time(input_dir):
    T_interval=datetime.timedelta(seconds=0)
    # identity:R111S222
    Time_list=[]
    for run in get_input(input_dir):
        readARIANNAData = NuRadioRecoio.NuRadioRecoio(run)
        count = 0
        run_id=0
        run_n=readARIANNAData.get_n_events()
        start_time=None
        for evt in readARIANNAData.get_events():
            # if evt.get_run_number() in goso:
            #     continue
            if count == 0:
                stn=evt.get_station(51)
                # start_time  = stn.get_parameter(apt.seq_start_time   )
                start_time = stn.get_parameter(apt.seq_start_time)
                ic(start_time)
                exit()
            count+=1
            if count == run_n:
                stn=evt.get_station(51)
                stop_time   = stn.get_parameter(apt.seq_stop_time    )
                run_id = evt.get_run_number()
        if run_id in goso:
            T_interval+=stop_time-start_time-(Dead_time*run_n)
        else:
            continue
            T_interval+=(stop_time-start_time)*0.8
    return T_interval
# total1 = Live_time(input)

def Live_time_in_run(readARIANNAData:NuRadioRecoio.NuRadioRecoio,critTime:datetime.datetime,run):
    # Total live time in Goso run: run_stop - run_start - (evt_num * dead_time)
    start=None
    stop=None
    count=0
    total = readARIANNAData.get_n_events()
    # ic(run,total,   run in goso)
    for i in readARIANNAData.get_events():
        if count == 0:
            stn = i.get_station(51)
            start = stn.get_parameter(apt.seq_start_time)
            if critTime<start:
                return datetime.timedelta(seconds=0)
        if count == total-1:
            stn = i.get_station(51)
            stop= stn.get_parameter(apt.seq_stop_time)
            if critTime<stop:
                stop=critTime
        count+=1

    if run in goso:
        # this is for Goso run
        count=0
        for evt in readARIANNAData.get_events():
            stn = evt.get_station(51)
            t = stn.get_station_time()
            if t <critTime:
                count+=1
            else:
                break
        return stop-start-Dead_time*count
    else:
        # This is for Non-Goso run
        return datetime.timedelta(seconds=0)
        # Abandon all the Non-Goso events, live time=0

        return (stop-start)*0.8


def Live_time_before(critTime,input_dir):
    T_interval=datetime.timedelta(seconds=0)
    for run in get_input(input_dir):
        readARIANNAData = NuRadioRecoio.NuRadioRecoio(run)
        run_id=0
        for evt in readARIANNAData.get_events():
            run_id = evt.get_run_number()
            break
        T_interval+=Live_time_in_run(readARIANNAData,critTime,run_id)
    return T_interval

def get_liveT_for_raw(raw_input):
    Data=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(raw_input))
    Live_time_lst=[]
    for evt in Data.get_events():
        stn=evt.get_station(51)
        time = stn.get_station_time().datetime
        live_time=Live_time_before(time,raw_input)
        Live_time_lst.append(live_time)
    return Live_time_lst

def Trig_rate(critLTime:datetime,liveT_lst:list):
    error=datetime.timedelta(minutes=30)
    count=-1
    for t in liveT_lst:
        if np.abs(t-critLTime)<=error:
            count+=1
    return count


time=datetime.datetime(2020, 1, 1, 00, 00, 00)
# find the live time before this moment

# with_goso=Live_time_before(time,input)
# ic(with_goso)
Candi='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Final_Candi'
Data=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(Candi))
Raw_data=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input))
Time_lst=[]
for evt in Raw_data.get_events():
    stn=evt.get_station(51)
    time=stn.get_station_time().datetime
    Time_lst.append(time)
error = datetime.timedelta(minutes=30)
for evt in Data.get_events():
    stn=evt.get_station(51)
    time=stn.get_station_time().datetime
    count=-1
    for t in Time_lst:
        if np.abs(t-time)<=error:
            count+=1
    id_info=str(ToolsPac.get_id_info(evt))
    ic(f'{id_info}  : {count}')
ic(Data.get_n_events())
        


