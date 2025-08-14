import A00_SlurmUtil
import numpy as np
from pathlib import Path
import os
import shutil
import send2trash

n_cores     =   20    #10 Temp    #1000 Sim
num_icetop  =   30      #10 Temp    #30   Sim  
amp = True
add_noise = True
# output_folder = '/pub/tingwel4/output/CR_BL_Simulation_demo/'
output_origin = '/pub/tingwel4/output/CR_BL_Sim_Temp/origin'
output_backlope='/pub/tingwel4/output/CR_BL_Sim_Temp/backlope'
output_filename = 'Stn51_IceTop'

# Make directory if it doesn't exist
# Path(output_folder).mkdir(parents=True, exist_ok=True)
for output_folder in [output_origin,output_backlope]:
    try:
        os.makedirs(output_folder)
    except(FileExistsError):
        shutil.rmtree(output_folder)
        os.makedirs(output_folder)

min_energy = 16.0
max_energy = 18.6
max_energy = 16.2

e_range = np.arange(min_energy, max_energy, 0.1)
sin2Val = np.arange(0, 1.01, 0.1)
sin2Val = np.array([0,0.1,0.2])


try:
    os.mkdir('run')
except(FileExistsError):
    shutil.rmtree('run')
    os.makedirs('run')
for e in e_range:
    for sin2 in sin2Val:
        # e = 18.4
        # sin2 = 0.0
        cmd = f'python Stn51Sim_origin_backlope.py --output_filename {output_filename}_{e:.1f}-{e+0.1:.1f}eV_{sin2:.1f}sin2_{n_cores}cores {n_cores} --min_energy {e:.1f} --max_energy {e+0.1:.1f} --sin2 {sin2:.1f} --num_icetop {num_icetop} --output_origin {output_origin} --output_backlope {output_backlope}'
        A00_SlurmUtil.makeAndRunJob(cmd, f'Stn51_{e:.1f}_{sin2:.1f}sin2', runDirectory='run_backlope', partition='standard')
        # quit()
