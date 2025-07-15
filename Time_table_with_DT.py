import sys
sys.path.insert(0,'/Users/david/PycharmProjects/Demo1/Research/Repository/NuRadioMC')
from NuRadioReco.detector import detector 
from NuRadioReco.utilities import units
from NuRadioReco.modules.ARIANNA import hardwareResponseIncorporator as ChardwareResponseIncorporator
from NuRadioReco.framework.parameters import stationParameters as stnp
from NuRadioReco.modules.io import NuRadioRecoio
import numpy as np
from brokenaxes import brokenaxes
import datetime
import NuRadioReco.modules.io.eventWriter
import matplotlib.pyplot as plt
import datetime
import os
from NuRadioReco.framework.parameters import channelParameters as chp
import NuRadioReco.modules.correlationDirectionFitter
from icecream import ic
candi='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Final_Candi'
input_dir='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw'
# output='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_X_output/X_Ratio_Zen_TrigR8_cut/SNR_cut'
output='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/sus_wave_only'
def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir
readARIANNAData=NuRadioRecoio.NuRadioRecoio(get_input(candi))

goso=[242,243,247,249,256,260,263,264,266]

def sort_time(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[0]  # choose first element as pivot
    less = [x for x in arr[1:] if x <= pivot]
    greater = [x for x in arr[1:] if x > pivot]
    return sort_time(less) + [pivot] + sort_time(greater)


input_files=[]
for i in os.listdir(input_dir):
    if not i.endswith('.nur'):
        continue
    input_files.append(os.path.join(input_dir,i))
triggered_events={}
candi_time=[]
ic(input_files)
# exit()
start_time=datetime.datetime(2018,1,1,0,0,0)
stop_time=datetime.datetime(2018,10,1,0,0,0)
for run in input_files:
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(run)
    run_id=0
    for evt in readARIANNAData.get_events():
        stn=evt.get_station(51)
        time=stn.get_station_time().datetime
        if time<start_time or time>stop_time:
            continue
        run_id=evt.get_run_number()
        triggered_events[run_id]=[]
        break
    for evt in readARIANNAData.get_events():
        stn=evt.get_station(51)
        if not stn.has_triggered():
            continue
        time=stn.get_station_time().datetime
        run = evt.get_run_number()
        id = evt.get_id()
        if time<start_time or time>stop_time:
            continue
        triggered_events[run_id].append(time)
        run=evt.get_run_number()
        id=evt.get_id()
Reader=NuRadioRecoio.NuRadioRecoio(get_input(candi))
candi_time=[]
strange=[]
for evt in Reader.get_events():
    stn = evt.get_station(51)
    run = evt.get_run_number()
    id  = evt.get_id()
    candi_time.append(stn.get_station_time().datetime)
hour=datetime.timedelta(hours=1)
Time_xaxis=[]
for run in triggered_events.keys():
    time_list=triggered_events[run]
    # time_bin=1+int((max(time_list)-min(time_list))/hour)
    Time_xaxis.append([min(time_list),max(time_list)])
for i in Time_xaxis:
    ic(i)
print('before sort')
Time_xaxis=sort_time(Time_xaxis)
for i in Time_xaxis:
    ic(i)
print('after sort')
Time_hours=1+int((Time_xaxis[-1][-1]-Time_xaxis[0][0])/hour)
Time_bins=[Time_xaxis[0][0]]
for i in range(0,Time_hours):
    right_n=Time_bins[-1]
    Time_bins.append(right_n+hour)
fig = plt.figure(figsize=(16,8),constrained_layout=True)
bax = brokenaxes(xlims=Time_xaxis, wspace=0.05)
bax.set_title('Trigger-rate',fontsize=28)
hist=[]
for run in triggered_events.keys():
    time_list=triggered_events[run]
    bax.hist(time_list,Time_bins,lw=2, label=f'evts_count={len(time_list)}',color='skyblue')
    hist.append(np.histogram(time_list,Time_bins))
for ax in bax.axs:
    for label in ax.get_xticklabels():
        label.set_rotation(-45)
        label.set_ha('right') 
    # ax.grid()
# bax.set_xlabel('time',fontsize=28)
# bax.tick_params(axis='y', labelsize=28)
for ax in bax.axs:
    for label in ax.get_xticklabels():
        label.set_rotation(45)
        label.set_horizontalalignment('right')
bax.set_xlabel("time")   
bax.set_ylabel("counts") 

# bax.axvline(candi_time,color='red',alpha=0.5,label=len(candi_time))
count=0
for i in candi_time:
    ic(i)
    bax.axvline(i,color='red',alpha=0.5)
    # count+=1
    # if count == 6:
    #     break
ic(len(candi_time))


    # plot_candi=[]
    # for i in candi_time:
    #     # ic(i,max(time_list))
    #     if i<=max(time_list) and i>=min(time_list):
    #         plot_candi.append(i)
    # for i in plot_candi:
    #     ax.axvline(i,color='r',alpha=0.3)
plt.subplots_adjust(bottom=0.25, left=0.15)
# plt.show()
plt.savefig('/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Trig-rate.png')
# ic| candi_time: [datetime.datetime(2018, 7, 31, 16, 44, 49),
#                  datetime.datetime(2018, 8, 2, 0, 41, 27),
#                  datetime.datetime(2018, 3, 6, 12, 25, 42),
#                  datetime.datetime(2018, 3, 6, 17, 18, 25),
#                  datetime.datetime(2018, 3, 7, 5, 43, 48),
#                  datetime.datetime(2018, 3, 7, 6, 13, 57),
#                  datetime.datetime(2018, 3, 11, 4, 22, 20),
#                  datetime.datetime(2018, 3, 14, 17, 22, 5),
#                  datetime.datetime(2018, 4, 22, 15, 53, 49),
#                  datetime.datetime(2018, 4, 23, 1, 53, 51),
#                  datetime.datetime(2018, 7, 7, 10, 10, 23),
#                  datetime.datetime(2018, 7, 14, 22, 15, 9),
#                  datetime.datetime(2018, 7, 23, 2, 47, 25)]