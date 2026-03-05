
from NuRadioReco.utilities import units
# import NuRadioReco.modules.io.coreas.readCoREAS
import readCoREASStationGrid
import NuRadioReco.modules.io.coreas.simulationSelector
import efield2VoltageConverter_CR_reflect
import efieldToVoltageConverter_old
import NuRadioReco.modules.channelGenericNoiseAdder
import NuRadioReco.modules.channelBandPassFilter
import NuRadioReco.modules.electricFieldBandPassFilter
import NuRadioReco.modules.eventTypeIdentifier
import NuRadioReco.modules.channelStopFilter
import NuRadioReco.modules.channelResampler
import NuRadioReco.modules.trigger.highLowThreshold
import NuRadioReco.modules.trigger.simpleThreshold
import NuRadioReco.modules.ARIANNA.hardwareResponseIncorporator
import NuRadioReco.modules.channelAddCableDelay
import NuRadioReco.modules.channelLengthAdjuster
import NuRadioReco.modules.triggerTimeAdjuster
import astropy
import argparse
import NuRadioReco.modules.io.eventWriter
import numpy as np
import os
import datetime
from icecream import ic
from scipy import constants

# /data/homezvol3/tingwel4/.local/lib/python3.8/site-packages/

from NuRadioReco.detector import detector
ic(NuRadioReco.__path__)
ic(NuRadioReco.__version__)
det = detector.Detector(json_filename=f'/pub/tingwel4/Tingwei_Liu/Simulation/station51_InfAir.json', assume_inf=False, antenna_by_depth=False)
det.update(astropy.time.Time('2018-1-1'))

import logging
logger=logging.getLogger("module")
logger.setLevel(logging.WARNING)

from NuRadioReco.detector import detector
from NuRadioReco.detector import generic_detector
import modifyEfieldForSurfaceReflection
# from modifyEfieldForSurfaceReflection import modifyEfieldForSurfaceReflection, getVoltageFFTFromEfield
from NuRadioReco.framework.parameters import showerParameters as shp

# class Tester:
#     def __init__(self):
#         pass
#     def repeat1(self,para1,para2):
#         return para2
#     def repeat1(self,para1):
#         return para1
    
# Test1=Tester()
# ic(Test1.repeat1('Test1','Test2'))
# ic(Test1.repeat1('Test1'))



icetop_sin = -1
min_energy=17.0
max_energy=18.1
num_icetop=10
input_files=[]
i = min_energy
while i < max_energy:
    #Currently just iterating through all sin's equally. Can separate sin bins if needed
    if icetop_sin == -1:
        sin2Val = np.arange(0, 1.01, 0.1)
    else:
        sin2Val = [icetop_sin]
    for sin2 in sin2Val:
        num_in_bin = 0
        folder = f'../../../../../dfs8/sbarwick_lab/arianna/SIM/southpole/IceTop/lgE_{i:.1f}/sin2_{sin2:.1f}/'
        for (dirpath, dirnames, filenames) in os.walk(folder):
            for file in filenames:
                if num_in_bin == num_icetop:
                    continue
                if not 'highlevel' in file:
                    file = os.path.join(folder, file)
                    input_files.append(file)
                    num_in_bin += 1
    i += 0.1
ic(input_files)
n_cores = 10
readCoREAS = readCoREASStationGrid.readCoREAS()
distance = 2 * units.km
readCoREAS.begin(input_files, -(distance)/2, (distance)/2, -(distance)/2, (distance)/2, n_cores=n_cores, shape='radial', seed=None, log_level=logging.WARNING)

ic(NuRadioReco.__path__)
# exit()
for ie,evt in enumerate(readCoREAS.run(detector=det)):
    ic(ie)
    for key,item in vars(evt).items():
        ic(f'{key}:{item}')
    #     break
    break


# for key,item in vars(readCoREAS).items():
#     ic(f'{key}:{item}')
