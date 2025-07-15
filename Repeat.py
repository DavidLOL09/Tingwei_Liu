
from icecream import ic
from NuRadioReco.modules.io import NuRadioRecoio
import os
def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir
num_p_h=8-2
input_path=f'/Users/david/PycharmProjects/Demo1/Research/Repository/raw_X_output/X_Ratio_Zen_TrigR{num_p_h}_cut/SNR_cut'
readARIANNAData=NuRadioRecoio.NuRadioRecoio(get_input(input_path))
Good_this_time=[]
for evt in readARIANNAData.get_events():
    run=evt.get_run_number()
    id=evt.get_id()
    Good_this_time.append(f'R{run}E{id}.png')
repeat=0
Good_Visual=os.listdir('/Users/david/Desktop/Good')
ic(Good_Visual)
for i in Good_this_time:
    if i in Good_Visual:
        repeat+=1
        ic(i)
repeat+=1
ic(num_p_h)
Accuracy=repeat/(1+len(Good_this_time))
ic(Accuracy)
ic(repeat)
ic(len(Good_Visual))
ic(len(Good_this_time))

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
