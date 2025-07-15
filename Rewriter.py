import sys
sys.path.insert(0,'/Users/david/PycharmProjects/Demo1/Research/Repository/NuRadioMC')
from NuRadioReco.modules.io import NuRadioRecoio
from NuRadioReco.modules.io import eventWriter
import NuRadioReco.modules.io.eventWriter
import os
from NuRadioReco.utilities import units
import send2trash
eventWriter = eventWriter.eventWriter()
import datetime
from NuRadioReco.detector import detector
from icecream import ic
import os
import datetime
from NuRadioReco.framework.parameters import channelParameters as chp
import NuRadioReco.modules.correlationDirectionFitter
import NuRadioReco.modules.channelLengthAdjuster
channelLengthAdjuster = NuRadioReco.modules.channelLengthAdjuster.channelLengthAdjuster()
channelLengthAdjuster.begin()

from NuRadioReco.modules.ARIANNA import hardwareResponseIncorporator as ChardwareResponseIncorporator
hardwareResponseIncorporator = ChardwareResponseIncorporator.hardwareResponseIncorporator()
hardwareResponseIncorporator.begin(debug=False)

import NuRadioReco.modules.channelResampler
channelResampler = NuRadioReco.modules.channelResampler.channelResampler()
# channelResampler.begin(debug=False)

import NuRadioReco.modules.channelBandPassFilter
channelBandPassFilter = NuRadioReco.modules.channelBandPassFilter.channelBandPassFilter()

from NuRadioReco.modules.channelStopFilter import channelStopFilter
channelStopFilter=channelStopFilter()

import NuRadioReco.modules.channelTemplateCorrelation
channelTemplateCorrelation = NuRadioReco.modules.channelTemplateCorrelation.channelTemplateCorrelation(template_directory='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/templates/')
channelTemplateCorrelation.begin(debug=False)

import NuRadioReco.modules.channelSignalReconstructor
channelSignalReconstructor = NuRadioReco.modules.channelSignalReconstructor.channelSignalReconstructor()

from NuRadioReco.modules import channelTimeWindow as cTWindow
cTW=cTWindow.channelTimeWindow()
cTW.begin(debug=False)

import NuRadioReco.modules.channelBandPassFilter
channelBandPassFilter = NuRadioReco.modules.channelBandPassFilter.channelBandPassFilter()

import NuRadioReco.modules.templateDirectionFitter
templateDirectionFitter = NuRadioReco.modules.templateDirectionFitter.templateDirectionFitter()
templateDirectionFitter.begin()

json_file_origin=f'/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/Stn51_sim_inAir/station51.json'
det=detector.Detector(json_filename=json_file_origin)
from icecream import ic
def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir
def set_writer(output_path,filename):
    sig = os.path.join(output_path,f'{filename}')
    try:
        os.makedirs(sig)
    except(FileExistsError):
        send2trash.send2trash(sig)
        os.makedirs(sig)
    eventWriter.begin(os.path.join(sig,f'{filename}.nur'))
    return eventWriter

output='/Users/david/PycharmProjects/Demo1/Research/Repository/'
raw_goso='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw'
raw_ngoso='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_non_goso'
dir_1=get_input(raw_goso)
# dir_1.extend(get_input(raw_ngoso))
Reader=NuRadioRecoio.NuRadioRecoio(dir_1)
Writer=set_writer(output,'Raw_detected')
n=Reader.get_n_events()
count=0
for evt in Reader.get_events():
    count+=1
    ic(f'{100*count/n:.2f}')
    stn = evt.get_station(51)
    time= stn.get_station_time().datetime
    det.update(time)
    channelStopFilter.run(evt,stn,det,append=0,prepend=0)
    channelBandPassFilter.run(evt, stn, det, passband=[80 * units.MHz, 500 * units.MHz], filter_type='butter', order = 10)
    hardwareResponseIncorporator.run(evt, stn, det, sim_to_data=False)
    channelTemplateCorrelation.run(evt,stn,det,cosmic_ray=True,n_templates=1, channels_to_use=[4,5,6])
    hardwareResponseIncorporator.run(evt,stn,det,sim_to_data=True)
    templateDirectionFitter.run(evt,stn,det,channels_to_use=[4,5,6], cosmic_ray=True)
    Writer.run(evt)