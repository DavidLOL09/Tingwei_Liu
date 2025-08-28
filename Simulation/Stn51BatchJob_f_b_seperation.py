import A00_SlurmUtil
import numpy as np
from pathlib import Path
import os
import shutil
import send2trash
import time
from icecream import ic
import inspect

n_cores     =   10    #10 Temp    #1000 Sim
num_icetop  =   10      #10 Temp    #30   Sim  
amp = True
add_noise = False
# output_folder = '/pub/tingwel4/output/CR_BL_Simulation_demo/'
output_origin = '/pub/tingwel4/output/CR_BL_Sim_Temp/front_back_sep'
# output_backlope='/pub/tingwel4/output/CR_BL_Sim_Temp/backlope'
output_filename = 'Stn51_IceTop'

# Make directory if it doesn't exist
# Path(output_folder).mkdir(parents=True, exist_ok=True)
try:
    os.makedirs(output_origin)
except(FileExistsError):
    shutil.rmtree(output_origin)
    os.makedirs(output_origin)

min_energy = 16.0
max_energy = 18.6
min_energy = 17.5
max_energy = 17.6

e_range = np.arange(min_energy, max_energy, 0.1)
sin2Val = np.arange(0, 1.01, 0.1)
sin2Val = np.arange(0.5,0.6,0.1)


# try:
#     os.mkdir('run')
# except(FileExistsError):
#     shutil.rmtree('run')
#     os.makedirs('run')
for e in e_range:
    for sin2 in sin2Val:
        # e = 18.4
        # sin2 = 0.0
        # ic(f'line {inspect.currentframe().f_lineno} in {os.path.basename(__file__)}:{time.perf_counter()}')
        cmd = f'python Stn51Sim_front_backlope_seperation.py --output_filename {output_filename}_{e:.1f}-{e+0.1:.1f}eV_{sin2:.1f}sin2_{n_cores}cores {n_cores} --min_energy {e:.1f} --max_energy {e+0.1:.1f} --sin2 {sin2:.1f} --num_icetop {num_icetop} --output_path {output_origin}'
        A00_SlurmUtil.makeAndRunJob(cmd, f'Stn51_{e:.1f}_{sin2:.1f}sin2', runDirectory='run_front_backlope_sep', partition='standard')
        # ic(f'line {inspect.currentframe().f_lineno} in {os.path.basename(__file__)}:{time.perf_counter()}')
        # quit()
