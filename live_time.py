from ast import Num
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
import NuRadioReco.modules.io.eventWriter
import matplotlib.pyplot as plt
import datetime
import os
from NuRadioReco.framework.parameters import channelParameters as chp
import NuRadioReco.modules.correlationDirectionFitter
from NuRadioReco.framework.parameters import ARIANNAParameters as apt
Good='r241e26100 r243e329 r243e531 r243e623 r243e1033 r243e1142 r243e1403 r243e1720 r248e19890 r247e1482 r249e326 r256e13 r263e122 r266e1720'
Sus='R247E17 R247E26 r248e87715 r248e100306 r247e1281 r256e389 r256e489 r256e1636 r256e1973 r263e368 r266e317 r266e2118'
Good_E_lst=[]
for i in Good.lower().split():
    Good_E_lst.append(i)
Sus_E_lst=[]
for i in Sus.lower().split():
    Sus_E_lst.append(i)
print(Good_E_lst)
print(Sus_E_lst)

input_dir='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw'
output='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/Xcut_5VrmsCut_TimeCut/live_time/'

if(not os.path.exists(output)):
    os.makedirs(output)
input_files=[]
goso=[242,243,247,249,256,260,263,264,266]


for i in os.listdir(input_dir):
    if not i.endswith('.nur'):
        continue
    input_files.append(os.path.join(input_dir,i))
# readARIANNAData = NuRadioRecoio.NuRadioRecoio(input_files)

live_time_lst=[]
for run in input_files:
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(run)
    lst=[]
    run_id=0
    T_list=[]
    count=0
    Good_E=[]
    Sus_E=[]    
    for evt in readARIANNAData.get_events():
        count+=1
        run_id=evt.get_run_number()
        stn=evt.get_station(51)
        e_num=evt.get_id()
        time=stn.get_station_time().datetime
        identity=f'r{run_id}e{e_num}'
        start_time  =stn.get_ARIANNA_parameter(apt.seq_start_time   )
        stop_time   =stn.get_ARIANNA_parameter(apt.seq_stop_time    )
        num         =stn.get_ARIANNA_parameter(apt.seq_num          )
        print(num,run_id)
        lst.append([num,start_time,stop_time])
        if len(lst)>=2 and lst[-2][0]==num:
            lst.pop(-1)
        T_list.append(time)
        if identity in Good_E_lst:
            Good_E.append(time)
        elif identity in Sus_E_lst:
            Sus_E.append(time)

    final_start=lst[0][1]
    final_stop=lst[-1][1]
    if not run_id in goso:
        live_time_lst.append(0.8*(final_stop-final_start))
        continue
    # for i in lst:
    #     print(i[1],i[2])
    # print(run_id)
    # break
    com_win=datetime.timedelta(minutes=10)
    dead_time=len(T_list)*com_win
    live_time_lst.append((final_stop-final_start-dead_time))



    hour=datetime.timedelta(hours=1)
    time_bins=int((final_stop-final_start)/hour)
    time=final_start
    # time_list=[[hours_start,deadtime,sequence_down]]
    for i in T_list:
        print(i,type(i))
    fig,(ax1)= plt.subplots(constrained_layout=True)
    print(run_id)
    ax1.hist(T_list, bins=time_bins,
         lw=2,label='Dead_time\nbin=1h', edgecolor="0.7",color='0.7')
    if len(Good_E)>0:
        ax1.hist(Good_E, bins=time_bins, #histtype='step'
            lw=2,label=f'Good Event counts{len(Good_E)}',edgecolor="red",color='r')
    if len(Sus_E)>0:
        ax1.hist(Sus_E, bins=time_bins, 
            lw=2,label=f'Suspucious Event counts{len(Sus_E)}', edgecolor="blue",color='b')
    # ax1.set_ylim(0,500)
    ax1.set_title(f'Dead_time={round((100*(len(T_list)*5)/1440))/100}Days Live_time={round((100*((((final_stop-final_start).total_seconds())/60-len(T_list)*5)/1440)))/100}Days')
    plt.xticks(rotation=-45)
    ax1.set_xlabel('Time')
    ax1.set_ylabel('counts')
    ax1.legend()
    ax1.grid()
    # plt.savefig(os.path.join(output,f'Dead_Live_run_{run_id}.png'))
total_livetime=datetime.timedelta(seconds=0)
for i in live_time_lst:
    total_livetime+=i
print(total_livetime)


    
    # time_list.pop(-1)
    # for i in lst:
    #     print(i)
    # for i in time_list:
    #     print(i)
    # print(run_id)
    # print(final_stop)
    # break

    # for evt in readARIANNAData.get_events():
    #     stn=evt.get_station(51)
    #     if not stn.has_triggered():
    #         continue
    #     time=stn.get_station_time().datetime
    #     triggered_events[run_id].append(time)




# for evt in readARIANNAData.get_events():
#     stn = evt.get_station(51)
#     start_time  =stn.get_ARIANNA_parameter(apt.seq_start_time)
#     stop_time   =stn.get_ARIANNA_parameter(apt.seq_stop_time)
#     num         =stn.get_ARIANNA_parameter(apt.seq_num)
#     run_id      =evt.get_run_number()
#     print(start_time,stop_time,num,run_id)
    # break
