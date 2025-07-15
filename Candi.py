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
Vrms=(9.71+9.66+8.94)/3
def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir
input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/direction'
output_path='/Users/david/PycharmProjects/Demo1/Research/Repository/candidate'
fail=['R256E2274','R263E509','R263E608','R263E734','R263E762','R264E8','R264E120','R264E127','R264E244','R264E412','R264E476','R264E496','R266E1423','R266E1517','R266E2181','R266E2254']
try:
    os.makedirs(output_path)
except(FileExistsError):
    send2trash.send2trash(output_path)
    os.makedirs(output_path)
eventWriter.begin(os.path.join(output_path,'Candi.nur'))
readARIANNAData=NuRadioRecoio.NuRadioRecoio(get_input(input_path))
for evt in readARIANNAData.get_events():
    run=evt.get_run_number()
    id=evt.get_id()
    if f'R{run}E{id}' in fail:
        continue
    eventWriter.run(evt)