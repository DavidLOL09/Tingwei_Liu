import A00_SlurmUtil
import numpy as np
from pathlib import Path
import os
import shutil
import send2trash
from icecream import ic



n_cores     =   200    #10 Temp    #1000 Sim
num_icetop  =   30      #10 Temp    #30   Sim  

working_folder = '/pub/tingwel4/output/CR_BL_Simulation/'
working_filename = 'Stn51_IceTop'
batch_path='/pub/tingwel4/Tingwei_Liu/Simulation/evtRateCalc'
run_py_file='get_Sim_distribution'


# Make directory if it doesn't exist
# Path(output_folder).mkdir(parents=True, exist_ok=True)


min_energy = 16.0
max_energy = 18.6
# max_energy = 16.5
# max_energy=17.5
# min_energy=17.0

e_range = np.arange(min_energy, max_energy, 0.1)
sin2Val = np.arange(0, 1.01, 0.1)
# ic(len(e_range)*len(sin2Val))
# for ie, e in enumerate(e_range[:-1]):
#     for iS,s in enumerate(sin2Val[:-1]):
#         print(f'{working_filename}_{e}-{e+0.1}eV_{s:.1f}sin2_{n_cores}cores')
#     print()
# exit()

# python get_Sim_distribution.py --working_file --n_cores --energy_min --energy_max --sin2 --num_icetop

try:
    os.mkdir(batch_path)
except(FileExistsError):
    shutil.rmtree(batch_path)
    os.makedirs(batch_path)
for iE,e in enumerate(e_range[:-1]):
    for iS,sin2 in enumerate(sin2Val[:-1]):
        # e = 18.4
        # sin2 = 0.0
        # ic('here')
        cmd = f'python {run_py_file}.py --working_dir {working_folder} --working_file {working_filename}_{e:.1f}-{e+0.1:.1f}eV_{sin2:.1f}sin2_{n_cores}cores --low_e {e} --high_e {e+0.1} --sin2V {sin2} --num_icetop {num_icetop}'
        A00_SlurmUtil.makeAndRunJob(cmd, f'Stn51_{e:.1f}_{sin2:.1f}sin2', runDirectory=batch_path, partition='standard')
        # quit()

# working_dir = args.working_dir
# working_file = args.working_file
# n_cores = args.n_cores
# min_energy = args.min_energy
# max_energy = args.max_energy
# sin2 = args.sin2
# num_icetop = args.num_icetop
# sim_amp = args.sim_amp
# add_noise = args.add_noise