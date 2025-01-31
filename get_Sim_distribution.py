import sys
import os
from NuRadioReco.utilities import units
import healpy
import Stn51RateCalc
import pandas as pd
import Stn51RateCalc as S51RC

def get_PPE(sim_file,trigger_name,output_path):
    return S51RC.getParametersPerEvent(sim_file,trigger_name,output_path, 2) 
'''
trig_energy, trig_zenith, trig_azimuth, trig_weight, events_id=get_PPE(simulation_files_folder, trigger_name, e_bins=None, zen_bins=None, rate_per_bin=None, n_trig_per_bin=None):
'''
raw_sim = '/dfs8/sbarwick_lab/ariannaproject/rricesmi/simStn51/1.23.25/'
test_raw= '/Users/david/PycharmProjects/Demo1/test_files'
# output  = '/pub/tingwel4/station_51/sim_with_weights'
output='/Users/david/PycharmProjects/Demo1/test_files'
thresh23_3      ='direct_LPDA_2of3_3.5sigma'
for a in os.listdir(test_raw):
    if a.endswith('.nur'):
        print(a)
# trig_energy, trig_zenith, trig_azimuth, trig_weight = get_PPE(sim_folder, trigger_names[0], e_range, sin2Val, rate_per_bin, n_trig_per_bin)
if not os.path.isdir(output):
    os.makedirs(output)
E,Z,A,W,I=get_PPE(test_raw,thresh23_3,output)
dic = {
    'Trig_id':I,
    'Trig_energy':E,
    'Trig_zenith':Z,
    'Trig_azimuth':A,
    'Trig_weight':W
}
df = pd.DataFrame(dic)
df.to_excel(os.path.join(output,'Data_output.xlsx'))
