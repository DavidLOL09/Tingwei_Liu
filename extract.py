event1='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_output/extract/R236E18344'
event2='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_output/extract/R236E19312'
import NuRadioReco.modules.io.NuRadioRecoio as NuRadioRecoio
import NuRadioReco.modules.io.eventWriter
import NuRadioReco.utilities.units as units
from icecream import ic
import numpy as np
import ToolsPac
eventWriter_1 = NuRadioReco.modules.io.eventWriter.eventWriter()
eventWriter_2 = NuRadioReco.modules.io.eventWriter.eventWriter()
import send2trash
import os
from NuRadioReco.detector import detector
input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_output/X_335sig'
output = '/Users/david/PycharmProjects/Demo1/Research/Repository/raw_output/extract'
json_file_origin=f'/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/Stn51_sim_inAir/station51.json'
det=detector.Detector(json_filename=json_file_origin)
def get_events_from(candi_lst,raw_data,output_path):
    id_lst=[]
    for path in candi_lst:
        reader  = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(path))
        for evt in reader.get_events():
            iden    = ToolsPac.get_id_info(evt)
            if iden not in id_lst:
                id_lst.append(iden)
    writer  = ToolsPac.set_writer(output_path,'candidates')
    reader  = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(raw_data))
    for evt in reader.get_events():
        iden    = ToolsPac.get_id_info(evt)
        if iden in id_lst:
            writer.run(evt)
input_path=[
    '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs_X_SNR',
    '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze1/det/Trig_335_Freqs_X_SNR',
    '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze/det/Trig_335_Freqs_X_SNR'
]
output_path='/Users/david/PycharmProjects/Demo1/Research/Repository/candidate_events'
raw_input='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate'
get_events_from(input_path,raw_input,output_path)

    