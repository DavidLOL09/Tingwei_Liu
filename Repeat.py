
from icecream import ic
from NuRadioReco.modules.io import NuRadioRecoio
import os
def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir
import ToolsPac

# input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/CR_BL_Test/'
# readARIANNAData=NuRadioRecoio.NuRadioRecoio(get_input(input_path))
# trigger='direct_LPDA_3of3_5sigma'
# for evt in readARIANNAData.get_events():
#     station_ids = evt.get_station_ids()
#     for stn_id in station_ids:
#         station = evt.get_station(stn_id)
#         ic(stn_id)
#         if not station.has_triggered():
#             ic('Not Triggered')
#             continue
#         trigger_names=station.get_trigger_names()
#         ic(trigger_names)
# exit()


latest='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Trig_X_335_SNR_Ratio_Freqs'
input_path2='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Trig_Freqs_X_SNR_Ratio'

reader_latest   = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(latest))
reader2         = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path2))


iden=[]
for evt in reader_latest.get_events():
    iden.append(f'R{evt.get_run_number()}E{evt.get_id()}')
repeat=0
for evt in reader2.get_events():
    id=f'R{evt.get_run_number()}E{evt.get_id()}'
    if id in iden:
        repeat+=1
ic(reader_latest.get_n_events())
ic(reader2.get_n_events())
ic(repeat)


# ic| num_p_h: 12
# ic| Accuracy: 0.25
# ic| repeat: 5
# ic| len(Good_Visual): 19
# ic| len(Good_this_time): 19

# ic| num_p_h: 10
# ic| Accuracy: 0.3125
# ic| repeat: 5
# ic| len(Good_Visual): 19
# ic| len(Good_this_time): 15

# ic| num_p_h: 8
# ic| Accuracy: 0.35714285714285715
# ic| repeat: 5
# ic| len(Good_Visual): 19
# ic| len(Good_this_time): 13

# ic| num_p_h: 6
# ic| Accuracy: 0.45454545454545453
# ic| repeat: 5
# ic| len(Good_Visual): 19
# ic| len(Good_this_time): 10
