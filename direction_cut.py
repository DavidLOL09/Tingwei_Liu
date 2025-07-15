from NuRadioReco.modules.io import NuRadioRecoio
from NuRadioReco.framework.parameters import eventParameters as evtp
import NuRadioReco.modules.io.eventWriter
eventWriter = NuRadioReco.modules.io.eventWriter.eventWriter()
import numpy as np
from NuRadioReco.utilities import units
from NuRadioReco.framework.parameters import channelParameters as chp
from icecream import ic
import os
import send2trash
from NuRadioReco.framework.parameters import stationParameters as stnp
Vrms=(9.71+9.66+8.94)/3
def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir
input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/SNR_cut/'
Zen_sim='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output/X_335sig_Ratio_Zen'
output_path='/Users/david/PycharmProjects/Demo1/Research/Repository/direction/'
try:
    os.makedirs(output_path)
except(FileExistsError):
    send2trash.send2trash(output_path)
    os.makedirs(output_path)
eventWriter.begin(os.path.join(output_path,'SNR_cut.nur'))
aban=['R266E2085','R266E2092','R256E13','R247E1482']
readARIANNAData=NuRadioRecoio.NuRadioRecoio(get_input(input_path))
candi=[]
events=[]
for evt in readARIANNAData.get_events():
    stn = evt.get_station(51)
    run=evt.get_run_number()
    id=evt.get_id()
    if f'R{run}E{id}' in aban:
            continue
    zen = stn.get_parameter(stnp.zenith)/units.rad
    azi = stn.get_parameter(stnp.azimuth)/units.rad
    events.append([evt,np.array([zen,azi])])
candidate=[]
def correlation_Normal(d1,d2):
    length=np.sqrt(np.dot(d1,d1)*np.dot(d2,d2))
    return np.dot(d1,d2)/length
for evt in readARIANNAData.get_events():
    stn = evt.get_station(51)
    run=evt.get_run_number()
    id=evt.get_id()
    if f'R{run}E{id}' in aban:
            continue
    zen = stn.get_parameter(stnp.zenith)/units.rad
    azi = stn.get_parameter(stnp.azimuth)/units.rad
    direction=np.array([zen,azi])
    count=0
    for i in events:
        compare_dirct=i[1]
        if correlation_Normal(direction,compare_dirct)==1:
                count+=1
        if count>=2:
                break
    if count==1:
         eventWriter.run(evt)
    


        