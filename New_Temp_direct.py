import numpy as np
import NuRadioReco.utilities.units as units
from icecream import ic
import matplotlib
import NuRadioReco
from NuRadioReco.framework.parameters import stationParameters as stnp
from NuRadioReco.framework.parameters import channelParameters as chp
import datetime
import matplotlib.pyplot as plt
import NuRadioReco.modules.io.NuRadioRecoio as NuRadioRecoio
from NuRadioReco.detector import detector
from NuRadioReco.detector import generic_detector
import send2trash
import matplotlib.pyplot as plt
from NuRadioReco.framework.parameters import eventParameters as evtp
from NuRadioReco.modules.channelStopFilter import channelStopFilter
import ToolsPac
import NuRadioReco.modules.templateDirectionFitter
templateDirectionFitter = NuRadioReco.modules.templateDirectionFitter.templateDirectionFitter()
templateDirectionFitter.begin()
channelStopFilter=channelStopFilter()
from NuRadioReco.framework.parameters import stationParameters as stnp
import NuRadioReco.modules.channelBandPassFilter
channelBandPassFilter = NuRadioReco.modules.channelBandPassFilter.channelBandPassFilter()
json_file_origin=f'/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/Stn51_sim_inAir/station51.json'
det=detector.Detector(json_filename=json_file_origin)
import NuRadioReco.modules.io.eventWriter
eventWriter = NuRadioReco.modules.io.eventWriter.eventWriter()
input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Candi_with_direct/event_sep/R243E512'
# output_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Candi_with_direct/event_sep/Template'
output_path='/Users/david/PycharmProjects/Demo1/Research/Repository/simulation_New_Temp'

def split_to_template(input,output,Temp_id):
    writer = ToolsPac.set_writer(output,f'Template_{Temp_id}')
    reader = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input))
    for ie,evt in enumerate(reader.get_events()):
        trace_lst=[]
        stn = evt.get_station(51)
        sampling_rate=0
        for i in [4,5,6]:
            chn = stn.get_channel(i)
            trace = chn.get_trace()
            trace_lst.append(trace)
            sampling_rate=chn.get_sampling_rate()
        for tar in range(3):
            for i in [4,5,6]:
                chn = stn.get_channel(i)
                sampling_rate = chn.get_sampling_rate()
                chn.set_trace(trace=trace_lst[tar],sampling_rate=sampling_rate)
            writer.run(evt)

def check_Incop(input_path):
    Reader=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))
    for evt in Reader.get_events():
        id=ToolsPac.get_id_info(evt)
        stn=evt.get_station(51)
        for i in [4,5,6]:
            chn=stn.get_channel(i)
            trace = chn.get_trace()
    exit()

def trace_check(input):
    reader = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input))
    # ic(type(reader))
    for ie,evt in enumerate(reader.get_events()):
        # ic(type(evt))
        stn = evt.get_station(51)
        for i in [4,5,6]:
            chn = stn.get_channel(i)
            trace = chn.get_trace()/units.mV
            ic(np.max(np.abs(trace)))
        print()
temp_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Candi_with_direct/event_sep/Template/Template_R243E512'
# candi_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Trig_Freqs_X_SNR_Ratio'
candi_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate'
candi_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_with_weights'

candi_reader = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(candi_path))
temp_reader = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(temp_path))

writer=ToolsPac.set_writer(output_path,'Trig')
for evt in candi_reader.get_events():
    stn=evt.get_station(51)
    time=stn.get_station_time().datetime
    det.update(time)
    channelStopFilter.run(evt,stn,det,append=0,prepend=0)
    channelBandPassFilter.run(evt, stn, det, passband=[80 * units.MHz, 500 * units.MHz], filter_type='butter', order = 10)
    ToolsPac.channelTemplateCorrelation_custimized(evt,51,temp_reader,[4,5,6])
    stn = evt.get_station(51)
    # chn=stn.get_channel(4)
    # ic(chn[chp.cr_xcorrelations]['cr_ref_xcorr_time'])
    # ic(chn[chp.cr_xcorrelations]['cr_ref_xcorr'])
    time = stn.get_station_time().datetime
    det.update(time)
    # templateDirectionFitter.run(evt,stn,det,channels_to_use=[4,5,6], cosmic_ray=True)
    writer.run(evt)


# exit()
# split_to_template(input_path,output_path,'R243E512')




# xcorrelations['{}_ref_xcorr'.format(ref_str)] = np.abs(xcorrs_ch).mean()
# xcorrelations['{}_ref_xcorr_all'.format(ref_str)] = np.abs(xcorrs_ch)
# xcorrelations['{}_ref_xcorr_max'.format(ref_str)] = np.abs(xcorrs_ch[np.argmax(np.abs(xcorrs_ch))])
# xcorrelations['{}_ref_xcorr_time'.format(ref_str)] = np.mean(xcorrpos_ch[np.argmax(np.abs(xcorrs_ch))]) * dt
# xcorrelations['{}_ref_xcorr_template'.format(ref_str)] = template_key[np.argmax(np.abs(xcorrs_ch))]
# channel[chp.cr_xcorrelations] = xcorrelations