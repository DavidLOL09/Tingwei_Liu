import os
import send2trash
import NuRadioReco.modules.io.eventWriter
eventWriter = NuRadioReco.modules.io.eventWriter.eventWriter()
import numpy as np
from NuRadioReco.framework.parameters import channelParameters as chp
from NuRadioReco.utilities import units
import datetime
import NuRadioReco

def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir
def set_writer(output,filename):
    output_file = os.path.join(output,filename)
    try:
        os.makedirs(output_file)
    except(FileExistsError):
        send2trash.send2trash(output_file)
        os.makedirs(output_file)
    eventWriter.begin(os.path.join(output_file,f'{filename}.nur'))
    return eventWriter

def get_Xcorr(stn:NuRadioReco.framework.station.Station,used_chn:list):
    Xcorr=[]
    for i in used_chn:
        channel = stn.get_channel(i)
        Xcorr.append(np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr'])))
    Xcorr = np.array(Xcorr)
    Xcorr=np.max(Xcorr)
    return Xcorr

def get_Max_trace(stn:NuRadioReco.framework.station.Station,used_chn:list):
    trace_max    = []
    for channel in stn.iter_channels(use_channels=used_chn):
        trace_max.append(np.max(np.abs(channel.get_trace()/units.mV)))
    return np.max(trace_max)

def get_id_info(evt:NuRadioReco.framework.event.Event):
    return f'R{evt.get_run_number()}E{evt.get_id()}'

