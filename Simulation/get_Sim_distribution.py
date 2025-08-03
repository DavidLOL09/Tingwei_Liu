import sys
import os
from NuRadioReco.utilities import units
import healpy
import Stn51RateCalc
import pandas as pd
import Stn51RateCalc as S51RC
import argparse
from icecream import ic
import shutil
import numpy as np


def get_PPE(sim_file,trigger_name,output_path,filename,high_e,low_e,sin2V):
    return S51RC.getParametersPerEvent(sim_file,trigger_name,output_path, filename,e_bins=[low_e,high_e],sin2Val=[sin2V,sin2V+0.1])
'''
trig_energy, trig_zenith, trig_azimuth, trig_weight, events_id=get_PPE(simulation_files_folder, trigger_name, e_bins=None, zen_bins=None, rate_per_bin=None, n_trig_per_bin=None):
'''

# output='/Users/david/PycharmProjects/Demo1/test_files'
thresh23_3      ='direct_LPDA_2of3_3.5sigma'



# python get_Sim_distribution.py --working_dir --working_file --n_cores --low_e --high_e --sin2 --num_icetop
parser = argparse.ArgumentParser(description='Run Cosmic Ray simulation for Station 51')
parser.add_argument('--working_dir',type=str, help='working directory of simulation')
parser.add_argument('--working_file', type=str, help='working filename for simulation')
parser.add_argument('--low_e', type=float, default=16.0, help='Minimum energy for simulation')
parser.add_argument('--high_e', type=float, default=18.5, help='Maximum energy for simulation')
parser.add_argument('--sin2V', type=float, default=-1, help='Sin^2(zenith) value for simulation, range from 0.0-1.0')
parser.add_argument('--num_icetop', type=int, default=10, help='Number of IceTop footprints to simulate per bin')


args = parser.parse_args()
working_dir = args.working_dir
working_file = args.working_file
low_e = args.low_e
high_e = args.high_e
sin2 = args.sin2V
num_icetop = args.num_icetop





def get_input(start_with,stop_with,directory=os.getcwd()):
    input_files=[]
    for i in os.listdir(directory):
        abspath=os.path.abspath(i)
        if abspath.startswith(start_with) and abspath.endswith(stop_with):
            input_files.append(abspath)
    return input_files

def remove_files(files):
    for file in files:
        shutil.rmtree(file)
    

start=os.path.join(working_dir,working_file)
directory='/pub/tingwel4/output/CR_BL_Simulation_demo'
input_files=get_input(start,'.nur',directory)
output='/pub/tingwel4/output/CR_BL_Simulation_weighted'
# trig_energy, trig_zenith, trig_azimuth, trig_weight = get_PPE(sim_folder, trigger_names[0], e_range, sin2Val, rate_per_bin, n_trig_per_bin)
os.makedirs(output,exist_ok=True)
# E,Z,A,W,I=get_PPE(input_files,thresh23_3,output,working_file,high_e,low_e,sin2)
E,Z,A,W,I=get_PPE(directory,thresh23_3,output,working_file,high_e,low_e,sin2)
dic = {
    'Trig_id':I,
    'Trig_energy':E,
    'Trig_zenith':Z,
    'Trig_azimuth':A,
    'Trig_weight':W
}
df = pd.DataFrame(dic)
df.to_excel(os.path.join(output,'Data_output.xlsx'))
remove_files(input_files)