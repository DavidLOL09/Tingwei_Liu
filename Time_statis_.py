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
Trigger_rate = 8
Dead_time = datetime.timedelta(hours=1)/Trigger_rate
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
            count+=1
            if count == run_n:
                stn=evt.get_station(51)
                stop_time   = stn.get_parameter(apt.seq_stop_time)
                run_id = evt.get_run_number()
        if run_id in goso:
            T_interval+=stop_time-start_time-(Dead_time*run_n)
        else:
            # continue
            T_interval+=(stop_time-start_time)*0.8
    return T_interval
# total1 = Live_time(input)

def Live_time_in_run(readARIANNAData:NuRadioRecoio.NuRadioRecoio,critTime:datetime.datetime,run):
    # Total live time in Goso run: run_stop - run_start - (evt_num * dead_time)
    start=None
    stop=None
    count=0
    total = readARIANNAData.get_n_events()
    ic(run,total,   run in goso)
    time_list = []
    for i in readARIANNAData.get_events():
        stn = i.get_station(51)
        time = stn.get_station_time().datetime
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
        time_list.append((time - start)/datetime.timedelta(hours=1))

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
        hours = (stop-start)/datetime.timedelta(hours=1)
        time_list = np.array(time_list)
        time_list = time_list.astype(int)
        tot_interval = stop-start
        for hour in range(0,int(hours)+1):
            evt_num = np.count_nonzero(time_list==hour)
            if evt_num > 8:
                evt_num = 8
            tot_interval -= evt_num*Dead_time
        return tot_interval
    else:
        # This is for Non-Goso run
        # return datetime.timedelta(seconds=0)
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



time=datetime.datetime(2020, 1, 1, 00, 00, 00)
# find the live time before this moment
# ic(745.26*(datetime.timedelta(days=23, seconds=61251).total_seconds()/datetime.timedelta(days=365).total_seconds()))
reader = NuRadioRecoio.NuRadioRecoio(['/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_non_goso/station_51_run_00248.root.nur'])
forced_trigger = Live_time_in_run(reader,time,248)
ic(forced_trigger)
ic(forced_trigger/datetime.timedelta(hours=1))
exit()
with_goso=Live_time_before(time,input)
days = with_goso.total_seconds()/datetime.timedelta(days=1).total_seconds()
ic(with_goso,days)
