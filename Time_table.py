import sys
from icecream import ic
sys.path.insert(0,'/Users/david/PycharmProjects/Demo1/Research/Repository/NuRadioMC')
from NuRadioReco.modules.io import NuRadioRecoio
import datetime
import NuRadioReco.modules.io.eventWriter
eventWriter = NuRadioReco.modules.io.eventWriter.eventWriter()
import matplotlib.pyplot as plt
import datetime
import os
import NuRadioReco.modules.correlationDirectionFitter
import send2trash
from NuRadioReco.framework.parameters import ARIANNAParameters as apt
from NuRadioReco.framework.parameters import eventParameters as evtp
import pandas as pd
import ToolsPac
Data={}

input_dir='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw'
output='/Users/david/PycharmProjects/Demo1/Research/Repository/'
goso=[242,243,247,249,256,260,263,264,266]
num_per_h=8
Dead_time = datetime.timedelta(hours=1)/num_per_h
start_time=datetime.datetime(2018,1,1,0,0,0)
stop_time=datetime.datetime(2018,10,1,0,0,0)
abandoned_period=[]

def sort_time(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[0]  # choose first element as pivot
    less = [x for x in arr[1:] if x <= pivot]
    greater = [x for x in arr[1:] if x > pivot]
    return sort_time(less) + [pivot] + sort_time(greater)
hour=datetime.timedelta(hours=1)

def get_time_axis(start:datetime.datetime,stop:datetime.datetime):
    T_axis=[start]
    while T_axis[-1]<=stop:
        start+=hour
        T_axis.append(start)
    return T_axis
def get_abandoned_periods(evt_time_lst,run_start,run_stop):
    a_period=[]
    T_axis=get_time_axis(run_start,run_stop)
    num_per_h_lst={}
    for i in T_axis[:-1]:
        num_per_h_lst[i]=[]
    for evT in evt_time_lst:
        input_hour=int((evT-run_start)/hour)*hour+run_start
        num_per_h_lst[input_hour].append(evT)
    for i in num_per_h_lst:
        if len(num_per_h_lst[i])>num_per_h:
            a_period.append(i)
    return a_period
def get_available_events_num(evt_time_lst,run_start,run_stop):
    a_period=get_abandoned_periods(evt_time_lst,run_start,run_stop)
    count=0
    for i in evt_time_lst:
        for j in a_period:
            if i-j>=datetime.timedelta(hours=0) and i-j<=datetime.timedelta(hours=1):
                count+=1
                break
    return len(evt_time_lst)-count


def get_run_time_aft_cut(evt_time_lst,run_start,run_stop):
    run_time=run_stop-run_start
    a_hour=len(get_abandoned_periods(evt_time_lst,run_start,run_stop))*hour
    # ic(a_hour)
    return run_time-a_hour



input_files=[]
for i in os.listdir(input_dir):
    if not i.endswith('.nur'):
        continue
    input_files.append(os.path.join(input_dir,i))



run_period=[]
target=264
for run in input_files:
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(run)
    Seq_T=[]
    run_id=0
    for evt in readARIANNAData.get_events():
        stn=evt.get_station(51)
        run_id=evt.get_run_number()
        start = stn.get_parameter(apt.seq_start_time)
        stop  = stn.get_parameter(apt.seq_start_time)
        Seq_T.extend([start,stop])
    run_period.append([min(Seq_T),max(Seq_T),run_id])
run_period=sort_time(run_period)
# ic(run_period)

events_T_lst={}
for run in input_files:
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(run)
    run_id=0
    for evt in readARIANNAData.get_events():
        stn=evt.get_station(51)
        try:    
            events_T_lst[evt.get_run_number()].append(stn.get_station_time().datetime)
        except(KeyError):
            events_T_lst[evt.get_run_number()]=[stn.get_station_time().datetime]
Run_time=datetime.timedelta(hours=0)
passed_events=0
for i in run_period:
    run_start   = i[0]
    run_stop    = i[1]
    run         = i[2]
    events_T    = events_T_lst[run]
    run_t       = get_run_time_aft_cut(events_T,run_start,run_stop)
    pass_evt=get_available_events_num(events_T,run_start,run_stop)
    ic(run,pass_evt)
    passed_events+=pass_evt
    # ic(run_t)
    Run_time+=run_t
ic(Run_time)
ic(passed_events)
ic(Run_time-passed_events*Dead_time)

# Trig_rate='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate'
# Trig_rate=ToolsPac.get_input(Trig_rate)
# for i in Trig_rate:
#     readARIANNAData=NuRadioRecoio.NuRadioRecoio(i)
#     n_events=readARIANNAData.get_n_events()
#     for evt in readARIANNAData.get_events():
#         run=evt.get_run_number()
#         ic(f'{run}:{n_events}')
#         break



# 242
# 264






    




