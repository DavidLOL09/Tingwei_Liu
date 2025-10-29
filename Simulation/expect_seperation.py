import sys
sys.path.append('/Users/david/PycharmProjects/Demo1/Research/Repository/')
from NuRadioReco.modules.io import NuRadioRecoio
from icecream import ic
from NuRadioReco.modules.channelLengthAdjuster import channelLengthAdjuster
import numpy as np
from NuRadioReco.framework.parameters import showerParameters as shp
from NuRadioReco.utilities import units
from NuRadioReco.modules.channelStopFilter import channelStopFilter
channelStopFilter=channelStopFilter()
from NuRadioReco.framework.parameters import eventParameters as evtp
import NuRadioReco.utilities.fft as fft
import matplotlib
import datetime
import send2trash
import os
import plot_waveform
from pathlib import Path
savename = 'Tingwei_Stn51'
trigger_name = 'direct_LPDA_3of3_3.5sigma'
save_channels = [4, 5, 6]
station_id = 51
import matplotlib.pyplot as plt
import NuRadioReco.modules.channelResampler
import NuRadioReco.modules.channelStopFilter
channelStopFilter = NuRadioReco.modules.channelStopFilter.channelStopFilter()
channelResampler = NuRadioReco.modules.channelResampler.channelResampler()
channelResampler.begin()
from NuRadioReco.framework.parameters import stationParameters as stnp
from NuRadioReco.framework.parameters import channelParameters as chp
import astropy
from NuRadioReco.detector import detector
det = detector.Detector(json_filename=f'/Users/david/PycharmProjects/Demo1/Research/Repository/Simulation/station51_InfAir.json', assume_inf=False, antenna_by_depth=False)
det.update(astropy.time.Time('2018-1-1'))
channels_to_use=[4,5,6]
import ToolsPac
bad_evts=['R247E831','R263E708','R263E734','R263E735','R263E736','R263E737']
