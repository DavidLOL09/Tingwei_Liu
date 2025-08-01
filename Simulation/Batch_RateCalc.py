import A00_SlurmUtil
import numpy as np
from pathlib import Path
import os
import shutil
import send2trash
from icecream import ic






n_cores     =   200    #10 Temp    #1000 Sim
num_icetop  =   30      #10 Temp    #30   Sim  

working_folder = '/pub/tingwel4/output/CR_BL_Simulation_demo/'
working_filename = 'Stn51_IceTop'
batch_path='/pub/tingwel4/Tingwei_Liu/Simulation/evtRateCalc'
run_py_file='get_Sim_distribution'


# Make directory if it doesn't exist
# Path(output_folder).mkdir(parents=True, exist_ok=True)


min_energy = 16.0
max_energy = 18.6
max_energy = 16.2

e_range = np.arange(min_energy, max_energy, 0.1)
sin2Val = np.arange(0, 1.01, 0.1)

# python get_Sim_distribution.py --working_file --n_cores --energy_min --energy_max --sin2 --num_icetop

try:
    os.mkdir(batch_path)
except(FileExistsError):
    shutil.rmtree(batch_path)
    os.makedirs(batch_path)
for e in e_range:
    for sin2 in sin2Val:
        # e = 18.4
        # sin2 = 0.0
        ic('here')
        cmd = f'python {run_py_file}.py --working_dir {working_folder} --working_file {working_filename}_{e:.1f}-{e+0.1:.1f}eV_{sin2:.1f}sin2_{n_cores}cores'
        A00_SlurmUtil.makeAndRunJob(cmd, f'Stn51_{e:.1f}_{sin2:.1f}sin2', runDirectory=batch_path, partition='standard')
        # quit()