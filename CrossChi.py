from NuRadioReco.modules.io import NuRadioRecoio
import os
import send2trash
import numpy as np
from NuRadioReco.framework.parameters import channelParameters as chp
import NuRadioReco
import NuRadioReco.modules.io.eventWriter
eventWriter = NuRadioReco.modules.io.eventWriter.eventWriter()
from NuRadioReco.framework.parameters import stationParameters as stnp
from NuRadioReco.utilities import units

def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir

def Analyze_X(input,output_path):
    # X
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input))
    X = os.path.join(output_path,'X')
    try:
        os.makedirs(X)
    except(FileExistsError):
        send2trash.send2trash(X)
        os.makedirs(X)
    eventWriter.begin(os.path.join(X,'X.nur'))
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        Xcorr=[]
        save0=True
        for i in [4,5,6]:
            channel = stn.get_channel(i)
            Xmax=np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr']))
            if Xmax<0.3:
                save0=False
                break
            Xcorr.append(Xmax)
        if save0 == False:
            continue
        if max(Xcorr)>=0.4:
            eventWriter.run(evt)
    print('X Completed')
    return X
def Analyze_zen(input,output_path):
    # Zen,<=85deg
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input))
    zen_path = os.path.join(output_path,'Trig_X_Zen')
    try:
        os.makedirs(zen_path)
    except(FileExistsError):
        send2trash.send2trash(zen_path)
        os.makedirs(zen_path)
    eventWriter.begin(os.path.join(zen_path,'X_Ratio_Zen.nur'))
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        time= stn.get_station_time().datetime
        zenith=stn.get_parameter(stnp.zenith)/units.deg
        if zenith>85:
            continue
        eventWriter.run(evt)
    print('Zen Complete')
    return zen_path

input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/X'
output_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate'
Analyze_zen(input_path,output_path)