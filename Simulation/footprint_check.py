
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

from NuRadioReco.detector import detector
det = detector.Detector(json_filename=f'/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/Stn51_sim_inAir/station51.json', assume_inf=False, antenna_by_depth=False)
det.update(astropy.time.Time('2018-1-1'))

import logging
logger=logging.getLogger("module")
logger.setLevel(logging.WARNING)

from NuRadioReco.detector import detector
from NuRadioReco.detector import generic_detector
import modifyEfieldForSurfaceReflection
# from modifyEfieldForSurfaceReflection import modifyEfieldForSurfaceReflection, getVoltageFFTFromEfield
from NuRadioReco.framework.parameters import showerParameters as shp

icetop_sin = -1
min_energy=16.0
max_energy=18.5
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
        folder = f'/Users/david/PycharmProjects/Demo1/Research/Repository/lgE_{i:.1f}/sin2_{sin2:.1f}/'
        for (dirpath, dirnames, filenames) in os.walk(folder):
            for file in filenames:
                if num_in_bin == num_icetop:
                    continue
                if not 'highlevel' in file:
                    file = os.path.join(folder, file)
                    input_files.append(file)
                    num_in_bin += 1
    i += 0.1

n_cores = 10
readCoREAS = readCoREASStationGrid.readCoREAS()
distance = 2 * units.km
readCoREAS.begin(input_files, -(distance)/2, (distance)/2, -(distance)/2, (distance)/2, n_cores=n_cores, shape='radial', seed=None, log_level=logging.WARNING)

ic(NuRadioReco.__path__)
# exit()

for ie,evt in enumerate(readCoREAS.run(detector=det)):
    for key,item in vars(evt).items():
        ic(f'{key}:{item}')
        break
    break

# for key,item in vars(readCoREAS).items():
#     ic(f'{key}:{item}')
