goso=[242,243,247,249,256,260,263,264,266]
from NuRadioReco.modules.io import NuRadioRecoio
import os
import NuRadioReco.modules.io.eventWriter


def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir
input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_output/X_335sig_Ratio_Zen'
output='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_output/goso_only'
os.makedirs(output)
Reader=NuRadioRecoio.NuRadioRecoio(get_input(input_path))
eventWriter = NuRadioReco.modules.io.eventWriter.eventWriter()
eventWriter.begin(os.path.join(output,'goso_only.nur'))
for evt in Reader.get_events():
    run=evt.get_run_number()
    if run in goso:
        eventWriter.run(evt)
        