from NuRadioReco.modules.io import NuRadioRecoio
import datetime
import NuRadioReco.modules.io.eventWriter
import matplotlib.pyplot as plt
import datetime
import os
import NuRadioReco.modules.correlationDirectionFitter
from NuRadioReco.framework.parameters import ARIANNAParameters as apt
input_dir='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw'
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
# readARIANNAData=NuRadioRecoio.NuRadioRecoio(get_input(input_dir))
live_time_lst=[]
T_interval=datetime.timedelta(seconds=0)
identity_list = []
Dead_time = datetime.timedelta(minutes=10)
# identity:R111S222
for run in get_input(input_dir):
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(run)
    count = 0
    run_id=0
    run_n=readARIANNAData.get_n_events()
    start_time=None
    for evt in readARIANNAData.get_events():
        if count == 0:
            stn=evt.get_station(51)
            start_time  =stn.get_ARIANNA_parameter(apt.seq_start_time   )
        count+=1
        if count == run_n:
            stn=evt.get_station(51)
            stop_time   =stn.get_ARIANNA_parameter(apt.seq_stop_time    )
            run_id = evt.get_run_number()
    if run_id in goso:
        T_interval+=stop_time-start_time-(Dead_time*run_n)
    else:
        T_interval+=(stop_time-start_time)*0.8
print(T_interval)
exit()
# dead_time for goso:
for evt in readARIANNAData.get_events():
    run_id=evt.get_run_number()
    if run_id in goso:
        T_interval-=Dead_time
    print('loop2')
# dead_time for non-goso:
id_n_goso=[]
ng_dead=datetime.timedelta(seconds=0)
for evt in readARIANNAData.get_events():
    print('loop3')
    run_id=evt.get_run_number()
    if run_id in goso:
        continue
    stn = evt.get_station(51)
    start_time  =stn.get_ARIANNA_parameter(apt.seq_start_time   )
    stop_time   =stn.get_ARIANNA_parameter(apt.seq_stop_time    )
    num         =stn.get_ARIANNA_parameter(apt.seq_num          )
    identity = f'R{run_id}S{num}'
    if identity not in id_n_goso:
        id_n_goso.append(identity)
        ng_dead+=stop_time-start_time
ng_dead_time=ng_dead*0.2
T_interval-=ng_dead_time
print(T_interval)




        
