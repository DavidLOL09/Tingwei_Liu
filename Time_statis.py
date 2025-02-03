from NuRadioReco.modules.io import NuRadioRecoio
import datetime
import NuRadioReco.modules.io.eventWriter
import matplotlib.pyplot as plt
import datetime
import os
import NuRadioReco.modules.correlationDirectionFitter
from NuRadioReco.framework.parameters import ARIANNAParameters as apt
input='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw'
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
Dead_time = datetime.timedelta(minutes=5)

# readARIANNAData=NuRadioRecoio.NuRadioRecoio(get_input(input_dir))
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
            if count == 0:
                stn=evt.get_station(51)
                start_time  = stn.get_ARIANNA_parameter(apt.seq_start_time   )
            count+=1
            if count == run_n:
                stn=evt.get_station(51)
                stop_time   = stn.get_ARIANNA_parameter(apt.seq_stop_time    )
                run_id = evt.get_run_number()
        if run_id in goso:
            T_interval+=stop_time-start_time-(Dead_time*run_n)
        else:
            T_interval+=(stop_time-start_time)*0.8
    return T_interval
# total1 = Live_time(input)

def Live_time_in_run(readARIANNAData:NuRadioRecoio.NuRadioRecoio,critTime:datetime.datetime,run):

    start=None
    stop=None
    count=0
    total = readARIANNAData.get_n_events()
    for i in readARIANNAData.get_events():
        if count == 0:
            stn = i.get_station(51)
            start=stn.get_ARIANNA_parameter(apt.seq_start_time)
            if critTime<start:
                return datetime.timedelta(seconds=0)
        if count == total-1:
            stn = i.get_station(51)
            stop= stn.get_ARIANNA_parameter(apt.seq_stop_time)
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
        return stop-start-Dead_time*count
    else:
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




time=datetime.datetime(2018, 7, 20, 12, 22, 58)
total2=Live_time_before(time,input)
time2=datetime.datetime(2018,8,6,22,46,48)
total3=Live_time_before(time2,input)
# total1=Live_time(input)
# print(total1)
print(total2)
print(total3)

[266, datetime.datetime(2018, 7, 26, 22, 21, 12), datetime.datetime(2018, 7, 26, 22, 21, 27)]
[260, datetime.datetime(2018, 7, 19, 0, 4, 42), datetime.datetime(2018, 7, 19, 0, 5, 26)]
[249, datetime.datetime(2018, 5, 1, 3, 28, 37), datetime.datetime(2018, 5, 1, 6, 22, 8)]
[248, datetime.datetime(2018, 4, 25, 21, 30, 2), datetime.datetime(2018, 4, 25, 21, 35, 2)]
[243, datetime.datetime(2018, 3, 1, 0, 45, 44), datetime.datetime(2018, 3, 1, 0, 54, 18)]
[242, datetime.datetime(2018, 2, 27, 23, 14, 36), datetime.datetime(2018, 2, 27, 23, 24, 12)]
[264, datetime.datetime(2018, 7, 24, 18, 2, 26), datetime.datetime(2018, 7, 24, 18, 2, 32)]
[247, datetime.datetime(2018, 4, 10, 1, 29, 37), datetime.datetime(2018, 4, 10, 4, 7, 48)]
[241, datetime.datetime(2018, 2, 25, 0, 55, 16), datetime.datetime(2018, 2, 25, 1, 15, 15)]
[237, datetime.datetime(2018, 2, 15, 1, 25, 21), datetime.datetime(2018, 2, 15, 1, 25, 41)]
[236, datetime.datetime(2018, 2, 14, 6, 0, 41), datetime.datetime(2018, 2, 14, 6, 20, 41)]
[257, datetime.datetime(2018, 7, 18, 21, 9, 19), datetime.datetime(2018, 7, 18, 21, 9, 46)]
[256, datetime.datetime(2018, 7, 4, 0, 11, 38), datetime.datetime(2018, 7, 4, 1, 25, 2)]
[263, datetime.datetime(2018, 7, 20, 12, 17, 59), datetime.datetime(2018, 7, 20, 12, 22, 58)]
