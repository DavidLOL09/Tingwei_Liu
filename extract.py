event1='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_output/extract/R236E18344'
event2='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_output/extract/R236E19312'
import NuRadioReco.modules.io.NuRadioRecoio as NuRadioRecoio
import NuRadioReco.modules.io.eventWriter
import NuRadioReco.utilities.units as units
from icecream import ic
import numpy as np
eventWriter_1 = NuRadioReco.modules.io.eventWriter.eventWriter()
eventWriter_2 = NuRadioReco.modules.io.eventWriter.eventWriter()
import send2trash
import os
from NuRadioReco.detector import detector
input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_output/X_335sig'
output = '/Users/david/PycharmProjects/Demo1/Research/Repository/raw_output/extract'
json_file_origin=f'/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/Stn51_sim_inAir/station51.json'
det=detector.Detector(json_filename=json_file_origin)
# try:
#     os.makedirs(output)
# except(FileExistsError):
#     send2trash.send2trash(output)
#     os.makedirs(output)
def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir
def get_event_trace(input_):
    Reader=NuRadioRecoio.NuRadioRecoio(get_input(input_))
    count=0
    trace=[]
    id_lst=[]
    for evt in Reader.get_events():
        run=evt.get_run_number()
        id=evt.get_id()
        id_lst.append(f'R{run}E{id}')
        count+=1
        stn=evt.get_station(51)
        chn=stn.get_channel(4)
        trace.append(np.array(chn.get_trace()/units.mV))
    return trace,id_lst



def Xcorrelation(trace1,trace2):
    Xcorr=[]
    for i in range(0,len(trace1)):
        first=trace1[0:i]
        last=trace1[i:len(trace1)]
        trace=np.concatenate((last,first))
        correlate=np.dot(trace,trace2)/np.sqrt(np.dot(trace,trace)*np.dot(trace2,trace2))
        Xcorr.append(np.abs(correlate))
    return np.max(np.array(Xcorr))
trace,id_lst=get_event_trace(output)
ic(id_lst)
ic(Xcorrelation(trace[0],trace[1]))
ic(1-np.arccos(Xcorrelation(trace[1],trace[2]))/(np.pi/2))
ic(Xcorrelation(trace[0],trace[2]))
ic(1-(np.arccos(Xcorrelation(trace[0],trace[1]))%(np.pi/2))/(np.pi/2))
ic(id_lst[0],id_lst[1],1-2*(np.arccos(Xcorrelation(trace[0],trace[1])))/np.pi,Xcorrelation(trace[0],trace[1]))
ic(id_lst[1],id_lst[2],1-2*(np.arccos(Xcorrelation(trace[1],trace[2])))/np.pi,Xcorrelation(trace[1],trace[2]))
ic(id_lst[0],id_lst[2],1-2*(np.arccos(Xcorrelation(trace[0],trace[2])))/np.pi,Xcorrelation(trace[0],trace[2]))



# trace1,trace2=get_event_trace(input_path)
# ic(np.arccos(Xcorrelation(trace1,trace2)))
# ic(1-np.arccos(Xcorrelation(trace1,trace2))/np.pi)

# Reader=NuRadioRecoio.NuRadioRecoio(get_input(input_path))
# eventWriter_1.begin(os.path.join(output,'R234E512.nur'))
# Vrms=(9.71+9.66+8.94)
# def Analyze_Ratio(input):
#     # 33Vrms_Ratio
#     readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input))
#     for evt in readARIANNAData.get_events():
#         stn = evt.get_station(51)
#         time = stn.get_station_time().datetime
#         det.update(time)
#         trace_down  = []
#         for channel in stn.iter_channels(use_channels=[0,1,2,3]):
#             trace_down.append(np.max(np.abs(channel.get_trace()/units.mV)))
#         trace_up    = []
#         for channel in stn.iter_channels(use_channels=[4,5,6]):
#             trace_up.append(np.max(np.abs(channel.get_trace()/units.mV)))   
#         if np.max(trace_down)/np.max(trace_up)>=0.5:
#             ic(np.max(trace_down)/np.max(trace_up))
#             continue
#         trace_bic=[]
#         trace_bic.append(np.max(np.abs(stn.get_channel(7).get_trace()/units.mV)))
    
#         if np.max(trace_bic)/np.max(trace_up)>=0.333 and np.max(trace_bic)>=3*Vrms:
#             ic(np.max(trace_bic)/np.max(trace_up),np.max(trace_bic))
#             continue
#     print('Ratio Completed')
# Analyze_Ratio('/Users/david/PycharmProjects/Demo1/Research/Repository/raw_output/extract/')


    