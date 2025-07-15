from NuRadioReco.modules.io import NuRadioRecoio
import NuRadioReco.modules.io.eventWriter
eventWriter = NuRadioReco.modules.io.eventWriter.eventWriter()
import os
import ToolsPac
from plot_waveform import plot_wave

def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir
def set_output(output_path,file_name):
    import send2trash
    import NuRadioReco.modules.io.eventWriter
    eventWriter = NuRadioReco.modules.io.eventWriter.eventWriter()
    try:
        os.makedirs(output_path)
    except(FileExistsError):
        send2trash.send2trash(output_path)
        os.makedirs(output_path)
    eventWriter.begin(os.path.join(output_path,file_name))
    return eventWriter

input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Candi_with_direct'
output='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Candi_with_direct/event_sep'
# os.makedirs(output)
# eventWriter.begin(os.path.join(output,'R263E365.nur'))
readARIANNAData=NuRadioRecoio.NuRadioRecoio(get_input(input_path))
# eventWriter=ToolsPac.set_writer(output,'event_sep')
for evt in readARIANNAData.get_events():
    run = evt.get_run_number()
    id  = evt.get_id()
    eventWriter=ToolsPac.set_writer(output,f'R{run}E{id}')
    eventWriter.run(evt)



