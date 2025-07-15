import sys
from icecream import ic
sys.path.insert(0,'/Users/david/PycharmProjects/Demo1/Research/Repository/NuRadioMC')
import datetime
from cProfile import label
from turtle import title
from typing_extensions import Self
from NuRadioReco.detector import detector 
from NuRadioReco.utilities import units
from NuRadioReco.modules.ARIANNA import hardwareResponseIncorporator as ChardwareResponseIncorporator
import NuRadioReco.modules.templateDirectionFitter
from NuRadioReco.framework.parameters import stationParameters as stnp
from NuRadioReco.modules.io import NuRadioRecoio
import numpy as np
import datetime
import matplotlib.pyplot as plt
import datetime
import os
from NuRadioReco.framework.parameters import channelParameters as chp
import NuRadioReco.modules.correlationDirectionFitter
from NuRadioReco.framework.parameters import ARIANNAParameters as apt
import NuRadioReco.modules.io.eventWriter
eventWriter = NuRadioReco.modules.io.eventWriter.eventWriter()
import os
import send2trash

candidates= []
goso=[242,243,247,249,256,260,263,264,266]
raw='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw'
raw_nGOSO='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_non_goso'
input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_cut/X_33Vrms_Ratio_Zen'
goso_only='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_output/goso_only'
candidate=raw
output_path  = '/Users/david/PycharmProjects/Demo1/Research/Repository'
def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir
num_per_h=8
Dead_time = datetime.timedelta(hours=1)/num_per_h
Dead_time = 0
ic(Dead_time)
def Live_time_in_run(readARIANNAData:NuRadioRecoio.NuRadioRecoio,critTime:datetime.datetime,run):
    start=None
    stop=None
    count=0
    total = readARIANNAData.get_n_events()
    ic(run,total,   run in goso)
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
        count=0
        for evt in readARIANNAData.get_events():
            stn = evt.get_station(51)
            t = stn.get_station_time()
            if t <critTime:
                count+=1
            else:
                break
        # return datetime.timedelta(seconds=0)
        # return stop-start-Dead_time*count
        return stop-start
    else:
        # return datetime.timedelta(seconds=0)
        # print(run)
        # return (stop-start)*0.8
        return stop-start


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


id_lst=[]
readARIANNAData=NuRadioRecoio.NuRadioRecoio(get_input(candidate))
ic(readARIANNAData.get_n_events())
for evt in readARIANNAData.get_events():
    run = evt.get_run_number()
    id = evt.get_id()
    stn=evt.get_station(51)
    time = stn.get_station_time().datetime
    candidates.append([f'R{run}E{id}',time])
    
readARIANNAData=NuRadioRecoio.NuRadioRecoio(get_input(raw))
hour=datetime.timedelta(hours=1)
percentage=0
for i in candidates:
    tar_time=i[1]
    ic(f'{percentage/len(candidates):.2f}')
    count=0
    for evt in readARIANNAData.get_events():
        stn=evt.get_station(51)
        if evt.get_run_number() not in goso:
            continue
        time=stn.get_station_time().datetime
        if abs(tar_time-time)<=hour/2:
            count+=1
    i.append(count)
    percentage+=1
pass_trig=[]
for i in candidates:
    if i[2]<=num_per_h:
        pass_trig.append(i[0])
readARIANNAData=NuRadioRecoio.NuRadioRecoio(get_input(candidate))
output_path=f'/Users/david/PycharmProjects/Demo1/Research/Repository/det_swch_Ord/TrigR{num_per_h}_cut'
try:
    os.makedirs(output_path)
except(FileExistsError):
    send2trash.send2trash(output_path)
    os.makedirs(output_path)
eventWriter.begin(os.path.join(output_path,f'TrigR{num_per_h}_cut.nur'))
for evt in readARIANNAData.get_events():
    run=evt.get_run_number()
    id=evt.get_id()
    if f'R{run}E{id}' in pass_trig:
        eventWriter.run(evt)

exit()

raw_run_time='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_non_goso'
Live_time=Live_time_before(datetime.datetime(2020,1,1),raw)
ic(Live_time)
exit()
# ic(len(pass_trig))
readARIANNAData=NuRadioRecoio.NuRadioRecoio(get_input(raw))
ic(readARIANNAData.get_n_events())
ic(Live_time,Dead_time,num_per_h)
simulation=1012.2692338013674
ic(Live_time*simulation/datetime.timedelta(365))
# ic| Live_time_before(datetime.datetime(2020,1,1),raw): datetime.timedelta(days=38, seconds=75651)
# len=24
# n=10

# ic| len(pass_trig): 29
# ic| readARIANNAData.get_n_events(): 157
# ic| Live_time: datetime.timedelta(days=38, seconds=75651)
#     Dead_time: datetime.timedelta(seconds=300)
#     num_per_h: 12
# ic| Live_time*254/datetime.timedelta(356): 27.73707845661673

# ic| len(pass_trig): 24
# ic| readARIANNAData.get_n_events(): 157
# ic| Live_time: datetime.timedelta(days=32, seconds=69891)
#     Dead_time: datetime.timedelta(seconds=360)
#     num_per_h: 10
# ic| Live_time*254/datetime.timedelta(356): 23.408614037141074

# ic| len(pass_trig): 21
# ic| readARIANNAData.get_n_events(): 158
# ic| Live_time: datetime.timedelta(days=23, seconds=61251)
#     Dead_time: datetime.timedelta(seconds=450)
#     num_per_h: 8
# ic| Live_time*254/datetime.timedelta(356): 16.91591740792759

# ic| len(pass_trig): 14
# ic| readARIANNAData.get_n_events(): 157
# ic| Live_time: datetime.timedelta(days=8, seconds=46851)
#     Dead_time: datetime.timedelta(seconds=600)
#     num_per_h: 6
# ic| Live_time*254/datetime.timedelta(356): 6.094756359238452